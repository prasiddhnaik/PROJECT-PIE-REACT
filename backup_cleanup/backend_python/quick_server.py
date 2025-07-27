#!/usr/bin/env python3
"""
Quick and Simple Flask Server for Stock Data
No complex cache system - just basic functionality
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import logging
from datetime import datetime
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Simple cache dict
cache = {}
CACHE_DURATION = 60  # 1 minute

def get_cached_or_fetch(symbol, fetch_func):
    """Simple cache helper"""
    cache_key = f"{symbol}_{int(time.time() // CACHE_DURATION)}"
    
    if cache_key in cache:
        logger.info(f"Cache hit for {symbol}")
        return cache[cache_key]
    
    try:
        data = fetch_func(symbol)
        if data:
            cache[cache_key] = data
            # Clean old cache entries
            if len(cache) > 100:
                old_keys = list(cache.keys())[:-50]  # Keep last 50
                for key in old_keys:
                    cache.pop(key, None)
            logger.info(f"Cached fresh data for {symbol}")
        return data
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}")
        return None

def fetch_stock_data(symbol):
    """Fetch stock data using yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="2d")
        
        if hist.empty:
            return None
            
        current_price = float(hist['Close'].iloc[-1])
        volume = int(hist['Volume'].iloc[-1])
        
        # Calculate change if we have previous day
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
            "timestamp": datetime.now().isoformat(),
            "source": "yahoo_finance"
        }
    except Exception as e:
        logger.error(f"Yahoo Finance error for {symbol}: {e}")
        return None

def fetch_historical_data(symbol, period="1mo"):
    """Fetch historical stock data for charts"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            return None
            
        historical_data = []
        for date, row in hist.iterrows():
            historical_data.append({
                "date": date.strftime('%Y-%m-%d'),
                "open": round(float(row['Open']), 2),
                "high": round(float(row['High']), 2), 
                "low": round(float(row['Low']), 2),
                "close": round(float(row['Close']), 2),
                "volume": int(row['Volume'])
            })
        
        return {
            "symbol": symbol.upper(),
            "period": period,
            "data": historical_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Historical data error for {symbol}: {e}")
        return None

@app.route('/test')
def test():
    """Test endpoint"""
    return jsonify({
        "status": "success",
        "message": "Quick server is running!",
        "timestamp": datetime.now().isoformat(),
        "cache_size": len(cache),
        "features": ["real-time quotes", "historical data", "960s auto-refresh"]
    })

@app.route('/stock/<symbol>')
def get_stock(symbol):
    """Get single stock data"""
    symbol = symbol.upper().strip()
    
    if not symbol:
        return jsonify({"error": "Symbol required"}), 400
    
    data = get_cached_or_fetch(symbol, fetch_stock_data)
    
    if data:
        return jsonify(data)
    else:
        return jsonify({"error": f"Could not fetch data for {symbol}"}), 404

@app.route('/stock/<symbol>/history')
def get_stock_history(symbol):
    """Get historical stock data for charts"""
    symbol = symbol.upper().strip()
    period = request.args.get('period', '1mo')  # Default to 1 month
    
    # Validate period
    valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    if period not in valid_periods:
        return jsonify({"error": f"Invalid period. Valid options: {valid_periods}"}), 400
    
    if not symbol:
        return jsonify({"error": "Symbol required"}), 400
    
    # Cache historical data for longer (5 minutes)
    cache_key = f"hist_{symbol}_{period}_{int(time.time() // 300)}"
    
    if cache_key in cache:
        logger.info(f"Historical cache hit for {symbol}")
        return jsonify(cache[cache_key])
    
    data = fetch_historical_data(symbol, period)
    
    if data:
        cache[cache_key] = data
        logger.info(f"Fetched historical data for {symbol} ({period})")
        return jsonify(data)
    else:
        return jsonify({"error": f"Could not fetch historical data for {symbol}"}), 404

@app.route('/stocks', methods=['POST'])
def get_multiple_stocks():
    """Get multiple stocks data"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({"error": "Symbols array required"}), 400
        
        results = {}
        for symbol in symbols[:10]:  # Limit to 10 symbols
            symbol = symbol.upper().strip()
            stock_data = get_cached_or_fetch(symbol, fetch_stock_data)
            results[symbol] = stock_data if stock_data else {"error": "No data"}
        
        return jsonify({
            "symbols": results,
            "timestamp": datetime.now().isoformat(),
            "count": len(results)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/popular')
def get_popular():
    """Get popular stocks"""
    popular_symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
    
    results = {}
    for symbol in popular_symbols:
        stock_data = get_cached_or_fetch(symbol, fetch_stock_data)
        if stock_data:
            results[symbol] = stock_data
    
    return jsonify({
        "popular_stocks": results,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/clear-cache')
def clear_cache():
    """Clear the cache"""
    cache.clear()
    return jsonify({
        "message": "Cache cleared",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/status')
def server_status():
    """Get server status and stats"""
    return jsonify({
        "status": "running",
        "uptime": "continuous",
        "cache_entries": len(cache),
        "features": {
            "real_time_quotes": True,
            "historical_data": True,
            "auto_refresh": "960 seconds",
            "popular_stocks": True,
            "charts_ready": True
        },
        "endpoints": {
            "GET /test": "Test server",
            "GET /stock/<symbol>": "Get single stock",
            "GET /stock/<symbol>/history": "Get historical data",
            "POST /stocks": "Get multiple stocks",
            "GET /popular": "Get popular stocks",
            "GET /clear-cache": "Clear cache",
            "GET /status": "Server status"
        },
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting Enhanced Stock Data Server...")
    print("📊 Available endpoints:")
    print("   GET  /test                     - Test server")
    print("   GET  /stock/<symbol>           - Get single stock")
    print("   GET  /stock/<symbol>/history   - Get historical data") 
    print("   POST /stocks                   - Get multiple stocks")
    print("   GET  /popular                  - Get popular stocks")
    print("   GET  /status                   - Server status")
    print("   GET  /clear-cache              - Clear cache")
    print("🔄 Auto-refresh: 960 seconds (16 minutes)")
    print("📈 Charts: Historical data support added")
    print("🌐 Server starting on http://localhost:4000")
    
    app.run(host='0.0.0.0', port=4000, debug=False) 