#!/usr/bin/env python3
"""
Multi-API Specialized Server
============================
Different APIs for different purposes:
- Yahoo Finance: Stock real-time data
- Alpha Vantage: Charts & technical analysis
- CoinGecko: Crypto data & charts
- Fixer.io: Forex rates
- Polygon: Advanced stock graphs
- TradingView: Chart widgets
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import requests
import logging
from datetime import datetime, timedelta
import time
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Simple cache dict
cache = {}
CACHE_DURATION = 300  # 5 minutes for most data

# API Configuration
class APIConfig:
    # Primary APIs for different purposes
    ALPHA_VANTAGE_KEY = "3J52FQXN785RGJX0"
    
    # API Endpoints
    ALPHA_VANTAGE_BASE = "https://www.alphavantage.co/query"
    COINGECKO_BASE = "https://api.coingecko.com/api/v3"
    FIXER_BASE = "https://api.fixer.io/v1"
    POLYGON_BASE = "https://api.polygon.io/v2"
    FINNHUB_BASE = "https://finnhub.io/api/v1"
    
    # API Specializations
    STOCK_DATA_API = "yahoo"           # Real-time stock prices
    STOCK_CHARTS_API = "alpha_vantage" # Technical charts
    STOCK_GRAPHS_API = "polygon"       # Advanced graphs
    CRYPTO_API = "coingecko"           # Crypto data & charts
    FOREX_API = "fixer"                # Forex rates
    NEWS_API = "finnhub"               # Financial news

config = APIConfig()

def get_cached_or_fetch(cache_key, fetch_func, cache_duration=CACHE_DURATION):
    """Enhanced cache with different durations"""
    timestamp_key = f"{cache_key}_{int(time.time() // cache_duration)}"
    
    if timestamp_key in cache:
        logger.info(f"Cache hit: {cache_key}")
        return cache[timestamp_key]
    
    try:
        data = fetch_func()
        if data:
            cache[timestamp_key] = data
            # Clean old cache entries
            if len(cache) > 200:
                old_keys = list(cache.keys())[:-100]
                for key in old_keys:
                    cache.pop(key, None)
            logger.info(f"Cached: {cache_key}")
        return data
    except Exception as e:
        logger.error(f"Error fetching {cache_key}: {e}")
        return None

# =============================================================================
# STOCK APIs - Real-time Data, Charts, and Advanced Graphs
# =============================================================================

def fetch_stock_realtime_data(symbol):
    """Yahoo Finance: Real-time stock data (fastest, most reliable)"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="2d")
        info = ticker.info
        
        if hist.empty:
            return None
            
        current_price = float(hist['Close'].iloc[-1])
        volume = int(hist['Volume'].iloc[-1])
        
        if len(hist) > 1:
            prev_close = float(hist['Close'].iloc[-2])
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100
        else:
            change = 0
            change_percent = 0
        
        return {
            "symbol": symbol.upper(),
            "current_price": round(current_price, 2),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "volume": volume,
            "high": round(float(hist['High'].iloc[-1]), 2),
            "low": round(float(hist['Low'].iloc[-1]), 2),
            "market_cap": info.get('marketCap'),
            "pe_ratio": info.get('trailingPE'),
            "sector": info.get('sector'),
            "timestamp": datetime.now().isoformat(),
            "source": "yahoo_finance",
            "api_purpose": "realtime_data"
        }
    except Exception as e:
        logger.error(f"Yahoo Finance error for {symbol}: {e}")
        return None

def fetch_stock_chart_data(symbol, interval="daily"):
    """Alpha Vantage: Technical charts and indicators"""
    try:
        function_map = {
            "daily": "TIME_SERIES_DAILY",
            "intraday": "TIME_SERIES_INTRADAY",
            "weekly": "TIME_SERIES_WEEKLY"
        }
        
        params = {
            "function": function_map.get(interval, "TIME_SERIES_DAILY"),
            "symbol": symbol,
            "apikey": config.ALPHA_VANTAGE_KEY,
            "outputsize": "compact"
        }
        
        if interval == "intraday":
            params["interval"] = "5min"
        
        response = requests.get(config.ALPHA_VANTAGE_BASE, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract time series data
            time_series_key = None
            for key in data.keys():
                if "Time Series" in key:
                    time_series_key = key
                    break
            
            if not time_series_key or time_series_key not in data:
                return None
                
            time_series = data[time_series_key]
            chart_data = []
            
            for date, values in list(time_series.items())[:30]:  # Last 30 periods
                chart_data.append({
                    "date": date,
                    "open": float(values.get("1. open", 0)),
                    "high": float(values.get("2. high", 0)),
                    "low": float(values.get("3. low", 0)),
                    "close": float(values.get("4. close", 0)),
                    "volume": int(values.get("5. volume", 0))
                })
            
            # Add technical indicators
            sma_params = {
                "function": "SMA",
                "symbol": symbol,
                "interval": "daily",
                "time_period": 20,
                "series_type": "close",
                "apikey": config.ALPHA_VANTAGE_KEY
            }
            
            sma_response = requests.get(config.ALPHA_VANTAGE_BASE, params=sma_params, timeout=10)
            sma_data = sma_response.json() if sma_response.status_code == 200 else {}
            
            return {
                "symbol": symbol.upper(),
                "interval": interval,
                "chart_data": chart_data,
                "technical_indicators": {
                    "sma_20": sma_data.get("Technical Analysis: SMA", {})
                },
                "timestamp": datetime.now().isoformat(),
                "source": "alpha_vantage",
                "api_purpose": "charts_technical"
            }
            
    except Exception as e:
        logger.error(f"Alpha Vantage chart error for {symbol}: {e}")
        return None

def fetch_stock_advanced_graphs(symbol):
    """Polygon: Advanced stock graphs and analytics"""
    try:
        # Get aggregates for advanced charting
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        url = f"{config.POLYGON_BASE}/aggs/ticker/{symbol}/range/1/day/{start_date}/{end_date}"
        params = {"apikey": "demo"}  # Using demo key
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('results'):
                graph_data = []
                for result in data['results']:
                    graph_data.append({
                        "timestamp": result.get('t'),
                        "date": datetime.fromtimestamp(result.get('t', 0) / 1000).strftime('%Y-%m-%d'),
                        "open": result.get('o'),
                        "high": result.get('h'),
                        "low": result.get('l'),
                        "close": result.get('c'),
                        "volume": result.get('v'),
                        "vwap": result.get('vw'),  # Volume Weighted Average Price
                        "transactions": result.get('n')  # Number of transactions
                    })
                
                return {
                    "symbol": symbol.upper(),
                    "graph_data": graph_data,
                    "analytics": {
                        "total_periods": len(graph_data),
                        "avg_volume": sum(d.get('volume', 0) for d in graph_data) / len(graph_data),
                        "price_range": {
                            "high": max(d.get('high', 0) for d in graph_data),
                            "low": min(d.get('low', 0) for d in graph_data)
                        }
                    },
                    "timestamp": datetime.now().isoformat(),
                    "source": "polygon",
                    "api_purpose": "advanced_graphs"
                }
                
    except Exception as e:
        logger.error(f"Polygon graph error for {symbol}: {e}")
        return None

# =============================================================================
# CRYPTO APIs - Data and Charts
# =============================================================================

def fetch_crypto_data(symbol):
    """CoinGecko: Comprehensive crypto data"""
    try:
        # Convert symbol to CoinGecko ID format
        symbol_map = {
            "BTC": "bitcoin",
            "ETH": "ethereum", 
            "ADA": "cardano",
            "DOT": "polkadot",
            "SOL": "solana",
            "MATIC": "polygon",
            "AVAX": "avalanche-2"
        }
        
        crypto_id = symbol_map.get(symbol.upper(), symbol.lower())
        
        # Get current price data
        price_url = f"{config.COINGECKO_BASE}/simple/price"
        price_params = {
            "ids": crypto_id,
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_market_cap": "true"
        }
        
        price_response = requests.get(price_url, params=price_params, timeout=10)
        
        if price_response.status_code == 200:
            price_data = price_response.json()
            
            if crypto_id in price_data:
                crypto_info = price_data[crypto_id]
                
                return {
                    "symbol": symbol.upper(),
                    "name": crypto_id.replace("-", " ").title(),
                    "current_price": crypto_info.get('usd'),
                    "change_24h": crypto_info.get('usd_24h_change'),
                    "volume_24h": crypto_info.get('usd_24h_vol'),
                    "market_cap": crypto_info.get('usd_market_cap'),
                    "timestamp": datetime.now().isoformat(),
                    "source": "coingecko",
                    "api_purpose": "crypto_data"
                }
                
    except Exception as e:
        logger.error(f"CoinGecko error for {symbol}: {e}")
        return None

def fetch_crypto_charts(symbol, days=30):
    """CoinGecko: Crypto price charts"""
    try:
        symbol_map = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "ADA": "cardano",
            "DOT": "polkadot",
            "SOL": "solana"
        }
        
        crypto_id = symbol_map.get(symbol.upper(), symbol.lower())
        
        chart_url = f"{config.COINGECKO_BASE}/coins/{crypto_id}/market_chart"
        chart_params = {
            "vs_currency": "usd",
            "days": days
        }
        
        chart_response = requests.get(chart_url, params=chart_params, timeout=10)
        
        if chart_response.status_code == 200:
            chart_data = chart_response.json()
            
            prices = chart_data.get('prices', [])
            volumes = chart_data.get('total_volumes', [])
            
            chart_points = []
            for i, price_point in enumerate(prices):
                volume_point = volumes[i] if i < len(volumes) else [price_point[0], 0]
                
                chart_points.append({
                    "timestamp": price_point[0],
                    "date": datetime.fromtimestamp(price_point[0] / 1000).strftime('%Y-%m-%d'),
                    "price": price_point[1],
                    "volume": volume_point[1]
                })
            
            return {
                "symbol": symbol.upper(),
                "chart_data": chart_points,
                "period_days": days,
                "timestamp": datetime.now().isoformat(),
                "source": "coingecko",
                "api_purpose": "crypto_charts"
            }
            
    except Exception as e:
        logger.error(f"CoinGecko chart error for {symbol}: {e}")
        return None

# =============================================================================
# FOREX APIs - Currency Exchange Rates
# =============================================================================

def fetch_forex_rates(base_currency="USD"):
    """Fixer.io: Real-time forex rates"""
    try:
        # Using free tier (may need API key for production)
        url = f"http://data.fixer.io/api/latest"
        params = {
            "access_key": "demo",  # Replace with real key
            "base": base_currency,
            "symbols": "EUR,GBP,JPY,CHF,CAD,AUD,NZD,CNY,INR"
        }
        
        # Fallback to a free forex API
        fallback_url = "https://api.exchangerate-api.com/v4/latest/USD"
        
        try:
            response = requests.get(fallback_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                return {
                    "base_currency": data.get('base', base_currency),
                    "rates": data.get('rates', {}),
                    "timestamp": datetime.now().isoformat(),
                    "source": "exchangerate-api",
                    "api_purpose": "forex_rates"
                }
        except:
            pass
        
        # Manual fallback rates for demo
        return {
            "base_currency": base_currency,
            "rates": {
                "EUR": 0.85,
                "GBP": 0.73,
                "JPY": 110.50,
                "CHF": 0.92,
                "CAD": 1.25,
                "AUD": 1.35,
                "CNY": 6.45,
                "INR": 74.30
            },
            "timestamp": datetime.now().isoformat(),
            "source": "demo_rates",
            "api_purpose": "forex_rates"
        }
        
    except Exception as e:
        logger.error(f"Forex rates error: {e}")
        return None

# =============================================================================
# FINANCIAL NEWS API
# =============================================================================

def fetch_financial_news(symbol=None):
    """Finnhub: Financial news"""
    try:
        if symbol:
            url = f"{config.FINNHUB_BASE}/company-news"
            params = {
                "symbol": symbol,
                "from": (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                "to": datetime.now().strftime('%Y-%m-%d'),
                "token": "demo"
            }
        else:
            url = f"{config.FINNHUB_BASE}/news"
            params = {
                "category": "general",
                "token": "demo"
            }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            news_data = response.json()
            
            # Format news items
            formatted_news = []
            for item in news_data[:10]:  # Top 10 news items
                formatted_news.append({
                    "headline": item.get('headline'),
                    "summary": item.get('summary'),
                    "source": item.get('source'),
                    "url": item.get('url'),
                    "datetime": datetime.fromtimestamp(item.get('datetime', 0)).isoformat(),
                    "image": item.get('image')
                })
            
            return {
                "symbol": symbol if symbol else "general",
                "news": formatted_news,
                "timestamp": datetime.now().isoformat(),
                "source": "finnhub",
                "api_purpose": "financial_news"
            }
            
    except Exception as e:
        logger.error(f"Finnhub news error: {e}")
        return None

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route('/test')
def test():
    """Test all API specializations"""
    return jsonify({
        "status": "success",
        "message": "Multi-API server running!",
        "api_specializations": {
            "stock_data": config.STOCK_DATA_API,
            "stock_charts": config.STOCK_CHARTS_API,
            "stock_graphs": config.STOCK_GRAPHS_API,
            "crypto": config.CRYPTO_API,
            "forex": config.FOREX_API,
            "news": config.NEWS_API
        },
        "cache_size": len(cache),
        "timestamp": datetime.now().isoformat()
    })

# Stock Endpoints
@app.route('/stock/<symbol>/data')
def get_stock_data(symbol):
    """Yahoo Finance: Real-time stock data"""
    data = get_cached_or_fetch(
        f"stock_data_{symbol}",
        lambda: fetch_stock_realtime_data(symbol),
        60  # 1 minute cache
    )
    return jsonify(data) if data else jsonify({"error": "No data available"}), 404

@app.route('/stock/<symbol>/charts')
def get_stock_charts(symbol):
    """Alpha Vantage: Technical charts"""
    interval = request.args.get('interval', 'daily')
    data = get_cached_or_fetch(
        f"stock_charts_{symbol}_{interval}",
        lambda: fetch_stock_chart_data(symbol, interval),
        900  # 15 minute cache
    )
    return jsonify(data) if data else jsonify({"error": "No chart data available"}), 404

@app.route('/stock/<symbol>/graphs')
def get_stock_graphs(symbol):
    """Polygon: Advanced graphs"""
    data = get_cached_or_fetch(
        f"stock_graphs_{symbol}",
        lambda: fetch_stock_advanced_graphs(symbol),
        1800  # 30 minute cache
    )
    return jsonify(data) if data else jsonify({"error": "No graph data available"}), 404

# Crypto Endpoints
@app.route('/crypto/<symbol>/data')
def get_crypto_data(symbol):
    """CoinGecko: Crypto data"""
    data = get_cached_or_fetch(
        f"crypto_data_{symbol}",
        lambda: fetch_crypto_data(symbol),
        300  # 5 minute cache
    )
    return jsonify(data) if data else jsonify({"error": "No crypto data available"}), 404

@app.route('/crypto/<symbol>/charts')
def get_crypto_charts(symbol):
    """CoinGecko: Crypto charts"""
    days = request.args.get('days', 30)
    data = get_cached_or_fetch(
        f"crypto_charts_{symbol}_{days}",
        lambda: fetch_crypto_charts(symbol, int(days)),
        600  # 10 minute cache
    )
    return jsonify(data) if data else jsonify({"error": "No crypto chart data available"}), 404

# Forex Endpoints
@app.route('/forex/rates')
def get_forex_rates():
    """Exchange rates"""
    base = request.args.get('base', 'USD')
    data = get_cached_or_fetch(
        f"forex_rates_{base}",
        lambda: fetch_forex_rates(base),
        3600  # 1 hour cache
    )
    return jsonify(data) if data else jsonify({"error": "No forex data available"}), 404

# News Endpoints
@app.route('/news')
def get_general_news():
    """General financial news"""
    data = get_cached_or_fetch(
        "general_news",
        lambda: fetch_financial_news(),
        1800  # 30 minute cache
    )
    return jsonify(data) if data else jsonify({"error": "No news available"}), 404

@app.route('/news/<symbol>')
def get_symbol_news(symbol):
    """Symbol-specific news"""
    data = get_cached_or_fetch(
        f"news_{symbol}",
        lambda: fetch_financial_news(symbol),
        1800  # 30 minute cache
    )
    return jsonify(data) if data else jsonify({"error": "No news available"}), 404

# Combined Endpoints
@app.route('/dashboard/<symbol>')
def get_complete_dashboard(symbol):
    """Complete dashboard data for a symbol"""
    symbol = symbol.upper()
    
    # Fetch from all relevant APIs
    stock_data = get_cached_or_fetch(f"stock_data_{symbol}", lambda: fetch_stock_realtime_data(symbol), 60)
    stock_charts = get_cached_or_fetch(f"stock_charts_{symbol}_daily", lambda: fetch_stock_chart_data(symbol, "daily"), 900)
    stock_graphs = get_cached_or_fetch(f"stock_graphs_{symbol}", lambda: fetch_stock_advanced_graphs(symbol), 1800)
    news = get_cached_or_fetch(f"news_{symbol}", lambda: fetch_financial_news(symbol), 1800)
    
    return jsonify({
        "symbol": symbol,
        "real_time_data": stock_data,
        "technical_charts": stock_charts,
        "advanced_graphs": stock_graphs,
        "news": news,
        "timestamp": datetime.now().isoformat(),
        "api_sources": {
            "data": "yahoo_finance",
            "charts": "alpha_vantage", 
            "graphs": "polygon",
            "news": "finnhub"
        }
    })

@app.route('/status')
def server_status():
    """Server status with API specializations"""
    return jsonify({
        "status": "running",
        "specializations": {
            "stocks": {
                "real_time_data": "yahoo_finance",
                "technical_charts": "alpha_vantage",
                "advanced_graphs": "polygon"
            },
            "crypto": {
                "data_and_charts": "coingecko"
            },
            "forex": {
                "exchange_rates": "exchangerate-api"
            },
            "news": {
                "financial_news": "finnhub"
            }
        },
        "cache_entries": len(cache),
        "endpoints": {
            "stocks": ["/stock/<symbol>/data", "/stock/<symbol>/charts", "/stock/<symbol>/graphs"],
            "crypto": ["/crypto/<symbol>/data", "/crypto/<symbol>/charts"],
            "forex": ["/forex/rates"],
            "news": ["/news", "/news/<symbol>"],
            "dashboard": ["/dashboard/<symbol>"]
        },
        "auto_refresh": "960 seconds",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting Multi-API Specialized Server...")
    print("📊 API Specializations:")
    print("   📈 Stocks Data:      Yahoo Finance (real-time)")
    print("   📊 Stocks Charts:    Alpha Vantage (technical)")
    print("   📉 Stocks Graphs:    Polygon (advanced)")
    print("   ₿  Crypto:           CoinGecko (data & charts)")
    print("   💱 Forex:            ExchangeRate-API (rates)")
    print("   📰 News:             Finnhub (financial news)")
    print("🌐 Server starting on http://localhost:4001")
    
    app.run(host='0.0.0.0', port=4001, debug=False) 