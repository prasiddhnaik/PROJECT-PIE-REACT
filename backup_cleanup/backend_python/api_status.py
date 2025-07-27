#!/usr/bin/env python3
"""
API Status Checker for Financial Analytics Hub
Checks the status and connectivity of all configured financial APIs
"""

import requests
import json
import os
from datetime import datetime

# Configuration
class FinancialAPIConfig:
    """Configuration class for Financial Analytics Hub API keys and settings"""
    
    # Alpha Vantage Configuration
    ALPHA_VANTAGE_API_KEY = "K2BDU6HV1QBZAG5E"
    ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
    
    # Other API Keys (to be configured as obtained)
    POLYGON_API_KEY = None
    TWELVE_DATA_API_KEY = "2df82f24652f4fb08d90fcd537a97e9c"
    FINNHUB_API_KEY = None
    IEX_CLOUD_API_KEY = None
    MARKETSTACK_API_KEY = None
    FMP_API_KEY = None
    TRADING_ECONOMICS_KEY = None
    BINANCE_API_KEY = None
    BINANCE_SECRET_KEY = None
    
    # API Endpoints
    COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
    POLYGON_BASE_URL = "https://api.polygon.io"
    TWELVE_DATA_BASE_URL = "https://api.twelvedata.com"
    FINNHUB_BASE_URL = "https://finnhub.io/api/v1"
    IEX_CLOUD_BASE_URL = "https://cloud.iexapis.com/stable"
    
    @classmethod
    def get_configured_apis(cls):
        """Return list of APIs that have been configured with valid keys"""
        configured = []
        
        if cls.ALPHA_VANTAGE_API_KEY:
            configured.append("Alpha Vantage")
        if cls.POLYGON_API_KEY:
            configured.append("Polygon.io")
        if cls.TWELVE_DATA_API_KEY:
            configured.append("Twelve Data")
        if cls.FINNHUB_API_KEY:
            configured.append("Finnhub")
        if cls.IEX_CLOUD_API_KEY:
            configured.append("IEX Cloud")
        if cls.MARKETSTACK_API_KEY:
            configured.append("MarketStack")
        if cls.FMP_API_KEY:
            configured.append("Financial Modeling Prep")
        if cls.TRADING_ECONOMICS_KEY:
            configured.append("Trading Economics")
        if cls.BINANCE_API_KEY and cls.BINANCE_SECRET_KEY:
            configured.append("Binance")
        
        # Always available (no key required)
        configured.extend(["CoinGecko", "Yahoo Finance"])
        
        return configured

def test_alpha_vantage():
    """Test Alpha Vantage API connectivity"""
    try:
        url = f"{FinancialAPIConfig.ALPHA_VANTAGE_BASE_URL}?function=GLOBAL_QUOTE&symbol=AAPL&apikey={FinancialAPIConfig.ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'Global Quote' in data and '05. price' in data['Global Quote']:
                return {
                    'status': 'ACTIVE',
                    'price': data['Global Quote']['05. price'],
                    'symbol': 'AAPL',
                    'response_time': response.elapsed.total_seconds()
                }
            elif 'Error Message' in data:
                return {'status': 'ERROR', 'error': data['Error Message']}
            elif 'Note' in data:
                return {'status': 'RATE_LIMITED', 'note': data['Note']}
            else:
                return {'status': 'INVALID_RESPONSE', 'data': data}
        else:
            return {'status': 'HTTP_ERROR', 'code': response.status_code}
    except Exception as e:
        return {'status': 'CONNECTION_ERROR', 'error': str(e)}

def test_coingecko():
    """Test CoinGecko API connectivity"""
    try:
        url = f"{FinancialAPIConfig.COINGECKO_BASE_URL}/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'bitcoin' in data and 'usd' in data['bitcoin']:
                return {
                    'status': 'ACTIVE',
                    'price': data['bitcoin']['usd'],
                    'symbol': 'BTC',
                    'response_time': response.elapsed.total_seconds()
                }
            else:
                return {'status': 'INVALID_RESPONSE', 'data': data}
        else:
            return {'status': 'HTTP_ERROR', 'code': response.status_code}
    except Exception as e:
        return {'status': 'CONNECTION_ERROR', 'error': str(e)}

def test_yahoo_finance():
    """Test Yahoo Finance API via yfinance"""
    try:
        import yfinance as yf
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        
        if info and 'currentPrice' in info or 'regularMarketPrice' in info:
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            return {
                'status': 'ACTIVE',
                'price': price,
                'symbol': 'AAPL'
            }
        else:
            return {'status': 'NO_DATA', 'available_fields': list(info.keys())[:10]}
    except Exception as e:
        return {'status': 'CONNECTION_ERROR', 'error': str(e)}

def test_polygon():
    """Test Polygon.io API connectivity"""
    if not FinancialAPIConfig.POLYGON_API_KEY:
        return {'status': 'NOT_CONFIGURED', 'note': 'API key not set'}
    
    try:
        url = f"{FinancialAPIConfig.POLYGON_BASE_URL}/v2/last/trade/AAPL?apikey={FinancialAPIConfig.POLYGON_API_KEY}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and data['results']:
                return {
                    'status': 'ACTIVE',
                    'price': data['results'].get('p'),
                    'symbol': 'AAPL',
                    'response_time': response.elapsed.total_seconds()
                }
            else:
                return {'status': 'NO_DATA', 'data': data}
        elif response.status_code == 401:
            return {'status': 'AUTH_ERROR', 'note': 'Invalid API key'}
        else:
            return {'status': 'HTTP_ERROR', 'code': response.status_code}
    except Exception as e:
        return {'status': 'CONNECTION_ERROR', 'error': str(e)}

def test_twelve_data():
    """Test Twelve Data API connectivity"""
    if not FinancialAPIConfig.TWELVE_DATA_API_KEY:
        return {'status': 'NOT_CONFIGURED', 'note': 'API key not set'}
    
    try:
        url = f"{FinancialAPIConfig.TWELVE_DATA_BASE_URL}/quote?symbol=AAPL&apikey={FinancialAPIConfig.TWELVE_DATA_API_KEY}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'close' in data:
                return {
                    'status': 'ACTIVE',
                    'price': data['close'],
                    'symbol': 'AAPL',
                    'response_time': response.elapsed.total_seconds()
                }
            else:
                return {'status': 'INVALID_RESPONSE', 'data': data}
        elif response.status_code == 401:
            return {'status': 'AUTH_ERROR', 'note': 'Invalid API key'}
        else:
            return {'status': 'HTTP_ERROR', 'code': response.status_code}
    except Exception as e:
        return {'status': 'CONNECTION_ERROR', 'error': str(e)}

def test_finnhub():
    """Test Finnhub API connectivity"""
    if not FinancialAPIConfig.FINNHUB_API_KEY:
        return {'status': 'NOT_CONFIGURED', 'note': 'API key not set'}
    
    try:
        url = f"{FinancialAPIConfig.FINNHUB_BASE_URL}/quote?symbol=AAPL&token={FinancialAPIConfig.FINNHUB_API_KEY}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'c' in data and data['c'] > 0:
                return {
                    'status': 'ACTIVE',
                    'price': data['c'],
                    'symbol': 'AAPL',
                    'response_time': response.elapsed.total_seconds()
                }
            else:
                return {'status': 'NO_DATA', 'data': data}
        elif response.status_code == 401:
            return {'status': 'AUTH_ERROR', 'note': 'Invalid API key'}
        else:
            return {'status': 'HTTP_ERROR', 'code': response.status_code}
    except Exception as e:
        return {'status': 'CONNECTION_ERROR', 'error': str(e)}

def main():
    """Run comprehensive API status check"""
    print("🚀 Financial Analytics Hub - API Status Check")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test all APIs
    apis = {
        'Alpha Vantage': test_alpha_vantage,
        'CoinGecko': test_coingecko,
        'Yahoo Finance': test_yahoo_finance,
        'Polygon.io': test_polygon,
        'Twelve Data': test_twelve_data,
        'Finnhub': test_finnhub,
    }
    
    results = {}
    active_count = 0
    
    for api_name, test_func in apis.items():
        print(f"Testing {api_name}...")
        result = test_func()
        results[api_name] = result
        
        status = result['status']
        if status == 'ACTIVE':
            print(f"  ✅ {api_name}: ACTIVE")
            if 'price' in result:
                print(f"     Price: ${result['price']} ({result['symbol']})")
            if 'response_time' in result:
                print(f"     Response time: {result['response_time']:.2f}s")
            active_count += 1
        elif status == 'NOT_CONFIGURED':
            print(f"  ⚪ {api_name}: NOT CONFIGURED")
            print(f"     Note: {result.get('note', 'API key required')}")
        elif status == 'RATE_LIMITED':
            print(f"  ⚠️  {api_name}: RATE LIMITED")
            print(f"     Note: {result.get('note', 'Too many requests')}")
        elif status == 'AUTH_ERROR':
            print(f"  🔐 {api_name}: AUTHENTICATION ERROR")
            print(f"     Note: {result.get('note', 'Invalid API key')}")
        elif status == 'CONNECTION_ERROR':
            print(f"  ❌ {api_name}: CONNECTION ERROR")
            print(f"     Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"  ⚠️  {api_name}: {status}")
            if 'error' in result:
                print(f"     Error: {result['error']}")
        print()
    
    # Summary
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Total APIs: {len(apis)}")
    print(f"Active: {active_count}")
    print(f"Not Configured: {sum(1 for r in results.values() if r['status'] == 'NOT_CONFIGURED')}")
    print(f"Errors: {sum(1 for r in results.values() if r['status'] not in ['ACTIVE', 'NOT_CONFIGURED'])}")
    print()
    
    configured_apis = FinancialAPIConfig.get_configured_apis()
    print(f"📋 Configured APIs: {', '.join(configured_apis)}")
    print()
    
    if active_count > 0:
        print("✅ System Status: OPERATIONAL")
        print(f"   Real-time data available from {active_count} source(s)")
    else:
        print("⚠️  System Status: LIMITED")
        print("   No active data sources - using fallback mechanisms")
    
    return results

if __name__ == "__main__":
    main() 