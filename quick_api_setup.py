#!/usr/bin/env python3
"""
🚀 Quick API Setup for Financial Analytics Hub
Adds essential free APIs to boost reliability and data coverage
"""

import requests
import streamlit as st
from datetime import datetime
import json

class EnhancedAPIManager:
    """Enhanced API manager with additional free APIs"""
    
    def __init__(self):
        # API keys (get these for free!)
        self.alpha_vantage_key = "demo"  # Get real key from alphavantage.co
        self.coinmarketcap_key = "demo"  # Get real key from coinmarketcap.com
        self.news_api_key = "demo"       # Get real key from newsapi.org
        
    # 🌟 Alpha Vantage - Solves Yahoo Finance rate limits
    def get_alpha_vantage_stock(self, symbol):
        """Get stock data from Alpha Vantage (500 free calls/day)"""
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'Global Quote' in data:
                    quote = data['Global Quote']
                    return {
                        'symbol': symbol,
                        'price': float(quote.get('05. price', 0)),
                        'change_percent': float(quote.get('10. change percent', '0%').replace('%', '')),
                        'volume': int(quote.get('06. volume', 0)),
                        'source': 'Alpha Vantage (Free)',
                        'timestamp': datetime.now().isoformat()
                    }
        except Exception as e:
            print(f"Alpha Vantage error: {e}")
        return None
    
    # 🔥 CoinMarketCap - Better crypto data than failing CoinCap
    def get_coinmarketcap_crypto(self, symbol):
        """Get crypto data from CoinMarketCap (333 free calls/day)"""
        try:
            headers = {
                'X-CMC_PRO_API_KEY': self.coinmarketcap_key,
                'Accept': 'application/json'
            }
            url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
            params = {'symbol': symbol.upper()}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and symbol.upper() in data['data']:
                    crypto = data['data'][symbol.upper()]
                    quote = crypto['quote']['USD']
                    return {
                        'symbol': symbol,
                        'price': quote['price'],
                        'change_24h': quote['percent_change_24h'],
                        'market_cap': quote['market_cap'],
                        'rank': crypto.get('cmc_rank', 0),
                        'source': 'CoinMarketCap (Pro)',
                        'timestamp': datetime.now().isoformat()
                    }
        except Exception as e:
            print(f"CoinMarketCap error: {e}")
        return None
    
    # 🏦 FRED API - Economic data (UNLIMITED free)
    def get_fred_economic_data(self, series_id="GDPC1"):
        """Get economic data from FRED API (unlimited free)"""
        try:
            url = f"https://api.stlouisfed.org/fred/series/observations"
            params = {
                'series_id': series_id,
                'api_key': 'demo',  # FRED allows public demo access
                'file_type': 'json',
                'limit': 10,
                'sort_order': 'desc'
            }
            
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if 'observations' in data:
                    latest = data['observations'][0]
                    return {
                        'series_id': series_id,
                        'value': latest.get('value'),
                        'date': latest.get('date'),
                        'source': 'FRED (Federal Reserve)',
                        'timestamp': datetime.now().isoformat()
                    }
        except Exception as e:
            print(f"FRED API error: {e}")
        return None
    
    # 📰 News API - Market news (1000 free calls/day)
    def get_financial_news(self, query="financial markets"):
        """Get financial news from News API (1000 free calls/day)"""
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'apiKey': self.news_api_key,
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': 5
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = []
                for article in data.get('articles', [])[:3]:
                    articles.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'url': article.get('url', ''),
                        'published': article.get('publishedAt', ''),
                        'source': article.get('source', {}).get('name', '')
                    })
                return {
                    'articles': articles,
                    'total_results': data.get('totalResults', 0),
                    'source': 'News API',
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"News API error: {e}")
        return None
    
    # 🌍 World Bank API - Global economic data (UNLIMITED free)
    def get_world_bank_data(self, country="US", indicator="NY.GDP.MKTP.CD"):
        """Get World Bank economic data (unlimited free)"""
        try:
            url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
            params = {
                'format': 'json',
                'date': '2020:2023',
                'per_page': 5
            }
            
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1 and data[1]:
                    latest = data[1][0]
                    return {
                        'country': country,
                        'indicator': indicator,
                        'value': latest.get('value'),
                        'date': latest.get('date'),
                        'country_name': latest.get('country', {}).get('value', ''),
                        'indicator_name': latest.get('indicator', {}).get('value', ''),
                        'source': 'World Bank Open Data',
                        'timestamp': datetime.now().isoformat()
                    }
        except Exception as e:
            print(f"World Bank API error: {e}")
        return None

# Quick test function
def test_enhanced_apis():
    """Test all enhanced APIs"""
    api_manager = EnhancedAPIManager()
    
    print("🧪 Testing Enhanced APIs...")
    
    # Test Alpha Vantage
    print("\n📈 Testing Alpha Vantage (Stock)...")
    stock_data = api_manager.get_alpha_vantage_stock("AAPL")
    if stock_data:
        print(f"✅ Alpha Vantage Success: AAPL ${stock_data['price']:.2f}")
    else:
        print("❌ Alpha Vantage Failed")
    
    # Test FRED
    print("\n🏦 Testing FRED (Economic Data)...")
    economic_data = api_manager.get_fred_economic_data("GDPC1")  # US GDP
    if economic_data:
        print(f"✅ FRED Success: GDP {economic_data['value']}")
    else:
        print("❌ FRED Failed")
    
    # Test World Bank
    print("\n🌍 Testing World Bank (Global Data)...")
    wb_data = api_manager.get_world_bank_data("US", "NY.GDP.MKTP.CD")
    if wb_data:
        print(f"✅ World Bank Success: {wb_data['country_name']} GDP")
    else:
        print("❌ World Bank Failed")
    
    print("\n🎉 Enhanced API testing complete!")

if __name__ == "__main__":
    test_enhanced_apis() 