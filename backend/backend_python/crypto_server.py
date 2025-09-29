"""
Crypto-Only Data Server
======================

Simple crypto data provider using multiple APIs.
"""

import requests
import json
from datetime import datetime
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class CryptoDataProvider:
    """Simple crypto data provider with multiple sources"""
    
    def __init__(self):
        # Crypto API endpoints
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.coinpaprika_base = "https://api.coinpaprika.com/v1"
        self.cryptocompare_base = "https://min-api.cryptocompare.com/data"
        self.binance_base = "https://api.binance.com/api/v3"
        
        # API priority order
        self.api_priority = [
            "coingecko",
            "binance", 
            "coinpaprika",
            "cryptocompare"
        ]
        
        # Simple cache
        self.cache = {}
        self.cache_ttl = 60  # 1 minute cache
        
        logger.info("Crypto data provider initialized with 4 APIs")

    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache entry is still valid"""
        if key not in self.cache:
            return False
        return time.time() - self.cache[key]['timestamp'] < self.cache_ttl

    def _get_from_cache(self, key: str):
        """Get data from cache if valid"""
        if self._is_cache_valid(key):
            data = self.cache[key]['data'].copy()
            data['_cached'] = True
            return data
        return None

    def _set_cache(self, key: str, data: dict):
        """Set data in cache"""
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }

    def fetch_coingecko_data(self, symbol: str) -> dict:
        """Fetch crypto data from CoinGecko"""
        try:
            # Check cache first
            cache_key = f"coingecko_{symbol.lower()}"
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached

            # CoinGecko API
            url = f"{self.coingecko_base}/simple/price"
            params = {
                'ids': symbol.lower(),
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_market_cap': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data_json = response.json()
                
                if symbol.lower() in data_json:
                    crypto_data = data_json[symbol.lower()]
                    
                    result = {
                        "symbol": symbol.upper(),
                        "name": symbol.title(),
                        "current_price": crypto_data.get('usd', 0),
                        "price_change_24h": crypto_data.get('usd_24h_change', 0),
                        "volume_24h": crypto_data.get('usd_24h_vol', 0),
                        "market_cap": crypto_data.get('usd_market_cap', 0),
                        "timestamp": datetime.now().isoformat(),
                        "source": "coingecko"
                    }
                    
                    self._set_cache(cache_key, result)
                    logger.info(f"CoinGecko: {symbol} = ${result['current_price']}")
                    return result
                    
        except Exception as e:
            logger.error(f"CoinGecko error for {symbol}: {e}")
            return None

    def fetch_binance_data(self, symbol: str) -> dict:
        """Fetch crypto data from Binance"""
        try:
            cache_key = f"binance_{symbol.lower()}"
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached

            # Binance API - 24hr ticker
            symbol_pair = f"{symbol.upper()}USDT"
            url = f"{self.binance_base}/ticker/24hr"
            params = {'symbol': symbol_pair}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data_json = response.json()
                
                result = {
                    "symbol": symbol.upper(),
                    "name": symbol.title(),
                    "current_price": float(data_json.get('lastPrice', 0)),
                    "price_change_24h": float(data_json.get('priceChangePercent', 0)),
                    "volume_24h": float(data_json.get('volume', 0)),
                    "high_24h": float(data_json.get('highPrice', 0)),
                    "low_24h": float(data_json.get('lowPrice', 0)),
                    "timestamp": datetime.now().isoformat(),
                    "source": "binance"
                }
                
                self._set_cache(cache_key, result)
                logger.info(f"Binance: {symbol} = ${result['current_price']}")
                return result
                    
        except Exception as e:
            logger.error(f"Binance error for {symbol}: {e}")
            return None

    def fetch_coinpaprika_data(self, symbol: str) -> dict:
        """Fetch crypto data from CoinPaprika"""
        try:
            cache_key = f"coinpaprika_{symbol.lower()}"
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached

            # CoinPaprika API
            url = f"{self.coinpaprika_base}/tickers/{symbol.lower()}-{symbol.lower()}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data_json = response.json()
                quotes = data_json.get('quotes', {}).get('USD', {})
                
                if quotes:
                    result = {
                        "symbol": symbol.upper(),
                        "name": data_json.get('name', symbol.title()),
                        "current_price": quotes.get('price', 0),
                        "price_change_24h": quotes.get('percent_change_24h', 0),
                        "volume_24h": quotes.get('volume_24h', 0),
                        "market_cap": quotes.get('market_cap', 0),
                        "timestamp": datetime.now().isoformat(),
                        "source": "coinpaprika"
                    }
                    
                    self._set_cache(cache_key, result)
                    logger.info(f"CoinPaprika: {symbol} = ${result['current_price']}")
                    return result
                    
        except Exception as e:
            logger.error(f"CoinPaprika error for {symbol}: {e}")
            return None

    def fetch_cryptocompare_data(self, symbol: str) -> dict:
        """Fetch crypto data from CryptoCompare"""
        try:
            cache_key = f"cryptocompare_{symbol.lower()}"
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached

            # CryptoCompare API
            url = f"{self.cryptocompare_base}/pricemultifull"
            params = {
                'fsyms': symbol.upper(),
                'tsyms': 'USD'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data_json = response.json()
                
                if 'RAW' in data_json and symbol.upper() in data_json['RAW']:
                    crypto_data = data_json['RAW'][symbol.upper()]['USD']
                    
                    result = {
                        "symbol": symbol.upper(),
                        "name": symbol.title(),
                        "current_price": crypto_data.get('PRICE', 0),
                        "price_change_24h": crypto_data.get('CHANGEPCT24HOUR', 0),
                        "volume_24h": crypto_data.get('VOLUME24HOUR', 0),
                        "market_cap": crypto_data.get('MKTCAP', 0),
                        "high_24h": crypto_data.get('HIGH24HOUR', 0),
                        "low_24h": crypto_data.get('LOW24HOUR', 0),
                        "timestamp": datetime.now().isoformat(),
                        "source": "cryptocompare"
                    }
                    
                    self._set_cache(cache_key, result)
                    logger.info(f"CryptoCompare: {symbol} = ${result['current_price']}")
                    return result
                    
        except Exception as e:
            logger.error(f"CryptoCompare error for {symbol}: {e}")
            return None

    def get_crypto_data(self, symbol: str) -> dict:
        """Get crypto data with fallback between APIs"""
        result = {
            "symbol": symbol.upper(),
            "primary_data": None,
            "fallback_data": [],
            "sources_used": [],
            "sources_failed": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # API methods mapping
        api_methods = {
            "coingecko": self.fetch_coingecko_data,
            "binance": self.fetch_binance_data
        }
        
        # Try each API in priority order
        for api_name in self.api_priority[:2]:  # Only use first 2 APIs for simplicity
            try:
                if api_name in api_methods:
                    data = api_methods[api_name](symbol)
                    if data:
                        if result["primary_data"] is None:
                            result["primary_data"] = data
                            result["sources_used"].append(api_name)
                        else:
                            result["fallback_data"].append(data)
                            result["sources_used"].append(api_name)
                    else:
                        result["sources_failed"].append(api_name)
                        
            except Exception as e:
                logger.error(f"Error with {api_name} for {symbol}: {e}")
                result["sources_failed"].append(api_name)
        
        return result

    def get_popular_cryptos(self) -> dict:
        """Get data for popular cryptocurrencies"""
        popular = ["bitcoin", "ethereum", "binancecoin", "cardano", "solana", "polkadot", "dogecoin", "avalanche"]
        results = {}
        
        for crypto in popular:
            try:
                data = self.get_crypto_data(crypto)
                if data["primary_data"]:
                    results[crypto] = data["primary_data"]
                time.sleep(0.2)  # Small delay between requests
            except Exception as e:
                logger.error(f"Error fetching {crypto}: {e}")
        
        return results

# Initialize provider
crypto_provider = CryptoDataProvider()

# Routes
@app.route('/test')
def test_server():
    """Test if server is running"""
    return jsonify({
        "status": "success",
        "message": "Crypto server is running!",
        "timestamp": datetime.now().isoformat(),
        "available_apis": crypto_provider.api_priority
    })

@app.route('/crypto/<symbol>')
def get_crypto(symbol):
    """Get single crypto data"""
    try:
        result = crypto_provider.get_crypto_data(symbol)
        
        if result["primary_data"]:
            return jsonify({
                "status": "success",
                "data": result["primary_data"],
                "sources_used": result["sources_used"],
                "timestamp": result["timestamp"]
            })
        else:
            return jsonify({
                "status": "error",
                "error": f"No data available for {symbol}",
                "sources_failed": result["sources_failed"]
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting crypto {symbol}: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/crypto/popular')
def get_popular():
    """Get popular cryptocurrencies"""
    try:
        popular_data = crypto_provider.get_popular_cryptos()
        
        return jsonify({
            "status": "success",
            "data": popular_data,
            "count": len(popular_data),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting popular cryptos: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/status')
def server_status():
    """Get server status"""
    return jsonify({
        "status": "running",
        "server": "crypto-only",
        "apis": crypto_provider.api_priority,
        "cache_size": len(crypto_provider.cache),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting Crypto-Only Server...")
    print("📊 Available endpoints:")
    print("   GET  /test                - Test server")
    print("   GET  /crypto/<symbol>     - Get single crypto")
    print("   GET  /crypto/popular      - Get popular cryptos")
    print("   GET  /status              - Server status")
    print("🌐 Server starting on http://localhost:5001")
    
    app.run(host='0.0.0.0', port=5001, debug=False) 