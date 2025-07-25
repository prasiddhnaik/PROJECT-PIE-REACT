#!/usr/bin/env python3
"""
Simple Crypto Server
===================
Basic crypto data server using only standard library + requests
"""

import json
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import requests

class CryptoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse URL
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Enable CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        try:
            if path == '/test':
                self.handle_test()
            elif path.startswith('/crypto/'):
                symbol = path.split('/')[-1]
                self.handle_crypto(symbol)
            elif path == '/status':
                self.handle_status()
            else:
                self.send_error(404, "Endpoint not found")
        except Exception as e:
            self.send_error(500, str(e))
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def handle_test(self):
        response = {
            "status": "success",
            "message": "Simple crypto server is running!",
            "timestamp": datetime.now().isoformat(),
            "available_apis": ["coingecko", "binance"]
        }
        self.send_json_response(response)
    
    def handle_crypto(self, symbol):
        try:
            # Try CoinGecko first
            data = self.fetch_coingecko(symbol)
            if not data:
                # Fallback to Binance
                data = self.fetch_binance(symbol)
            
            if data:
                response = {
                    "status": "success",
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                }
                self.send_json_response(response)
            else:
                self.send_json_response({
                    "status": "error",
                    "error": f"No data available for {symbol}"
                }, 404)
                
        except Exception as e:
            self.send_json_response({
                "status": "error",
                "error": str(e)
            }, 500)
    
    def handle_status(self):
        response = {
            "status": "running",
            "server": "simple-crypto",
            "port": 5001,
            "timestamp": datetime.now().isoformat()
        }
        self.send_json_response(response)
    
    def fetch_coingecko(self, symbol):
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': symbol.lower(),
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_market_cap': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if symbol.lower() in data:
                    crypto_data = data[symbol.lower()]
                    return {
                        "symbol": symbol.upper(),
                        "name": symbol.title(),
                        "current_price": crypto_data.get('usd', 0),
                        "price_change_24h": crypto_data.get('usd_24h_change', 0),
                        "volume_24h": crypto_data.get('usd_24h_vol', 0),
                        "market_cap": crypto_data.get('usd_market_cap', 0),
                        "timestamp": datetime.now().isoformat(),
                        "source": "coingecko"
                    }
        except Exception as e:
            print(f"CoinGecko error for {symbol}: {e}")
        return None
    
    def fetch_binance(self, symbol):
        try:
            symbol_pair = f"{symbol.upper()}USDT"
            url = f"https://api.binance.com/api/v3/ticker/24hr"
            params = {'symbol': symbol_pair}
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "symbol": symbol.upper(),
                    "name": symbol.title(),
                    "current_price": float(data.get('lastPrice', 0)),
                    "price_change_24h": float(data.get('priceChangePercent', 0)),
                    "volume_24h": float(data.get('volume', 0)),
                    "high_24h": float(data.get('highPrice', 0)),
                    "low_24h": float(data.get('lowPrice', 0)),
                    "timestamp": datetime.now().isoformat(),
                    "source": "binance"
                }
        except Exception as e:
            print(f"Binance error for {symbol}: {e}")
        return None
    
    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        # Custom log format
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

def run_server(port=5001):
    server_address = ('', port)
    httpd = HTTPServer(server_address, CryptoHandler)
    
    print("🚀 Simple Crypto Server Starting...")
    print("📊 Available endpoints:")
    print("   GET  /test                - Test server")
    print("   GET  /crypto/<symbol>     - Get crypto data")
    print("   GET  /status              - Server status")
    print(f"🌐 Server running on http://localhost:{port}")
    print("Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.server_close()

if __name__ == '__main__':
    run_server() 