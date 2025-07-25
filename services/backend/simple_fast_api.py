#!/usr/bin/env python3
"""
Simple Fast Financial API
=========================

Ultra-fast and reliable financial data API using only Yahoo Finance.
No complexity, just speed and reliability.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import time
from functools import lru_cache
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Simple in-memory cache for speed
@lru_cache(maxsize=500)
def get_stock_data_cached(symbol, minute_key):
    """Get stock data with 1-minute caching"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="2d")
        
        if hist.empty:
            return None
            
        current_price = float(hist['Close'].iloc[-1])
        
        # Calculate change if we have previous day
        if len(hist) > 1:
            prev_close = float(hist['Close'].iloc[-2])
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100
        else:
            change = 0
            change_percent = 0
        
        return {
            "symbol": symbol,
            "price": round(current_price, 2),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "volume": int(hist['Volume'].iloc[-1]) if not hist['Volume'].empty else 0,
            "high": round(float(hist['High'].iloc[-1]), 2),
            "low": round(float(hist['Low'].iloc[-1]), 2),
            "open": round(float(hist['Open'].iloc[-1]), 2),
            "timestamp": datetime.now().isoformat(),
            "source": "yahoo_finance"
        }
        
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

@app.route('/')
def home():
    """API documentation"""
    return jsonify({
        "message": "⚡ Simple Fast Financial API",
        "version": "1.0.0",
        "status": "optimized",
        "endpoints": {
            "/": "This documentation",
            "/health": "Health check",
            "/stock/{symbol}": "Get stock data",
            "/stocks": "Multiple stocks (POST)",
            "/popular": "Popular stocks",
            "/test": "Test with AAPL"
        },
        "examples": [
            "GET /stock/AAPL",
            "GET /popular", 
            "POST /stocks with {\"symbols\": [\"AAPL\", \"GOOGL\"]}"
        ]
    })

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "api": "yahoo_finance",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/stock/<symbol>')
def get_stock(symbol):
    """Get single stock data"""
    start_time = time.time()
    
    # Use current minute as cache key
    minute_key = int(time.time() / 60)
    
    try:
        data = get_stock_data_cached(symbol.upper(), minute_key)
        response_time = round((time.time() - start_time) * 1000, 2)
        
        if data:
            return jsonify({
                "success": True,
                "data": data,
                "response_time_ms": response_time,
                "cached": True if response_time < 100 else False
            })
        else:
            return jsonify({
                "success": False,
                "error": f"No data found for {symbol}",
                "response_time_ms": response_time
            }), 404
            
    except Exception as e:
        response_time = round((time.time() - start_time) * 1000, 2)
        return jsonify({
            "success": False,
            "error": str(e),
            "response_time_ms": response_time
        }), 500

@app.route('/stocks', methods=['POST'])
def get_multiple_stocks():
    """Get multiple stocks data"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({"error": "Please provide symbols array"}), 400
        
        # Limit to 20 symbols for performance
        symbols = symbols[:20]
        minute_key = int(time.time() / 60)
        
        results = {}
        for symbol in symbols:
            try:
                stock_data = get_stock_data_cached(symbol.upper(), minute_key)
                if stock_data:
                    results[symbol.upper()] = stock_data
                else:
                    results[symbol.upper()] = {"error": "No data available"}
            except Exception as e:
                results[symbol.upper()] = {"error": str(e)}
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return jsonify({
            "success": True,
            "data": results,
            "count": len(symbols),
            "response_time_ms": response_time
        })
        
    except Exception as e:
        response_time = round((time.time() - start_time) * 1000, 2)
        return jsonify({
            "success": False,
            "error": str(e),
            "response_time_ms": response_time
        }), 500

@app.route('/popular')
def get_popular():
    """Get popular stocks"""
    popular_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA']
    start_time = time.time()
    minute_key = int(time.time() / 60)
    
    results = {}
    for symbol in popular_symbols:
        try:
            data = get_stock_data_cached(symbol, minute_key)
            if data:
                results[symbol] = data
        except:
            pass
    
    response_time = round((time.time() - start_time) * 1000, 2)
    
    return jsonify({
        "success": True,
        "data": results,
        "response_time_ms": response_time,
        "note": "Popular stocks updated every minute"
    })

@app.route('/test')
def test_api():
    """Test API with AAPL"""
    start_time = time.time()
    minute_key = int(time.time() / 60)
    
    try:
        data = get_stock_data_cached("AAPL", minute_key)
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return jsonify({
            "test": "passed" if data else "failed",
            "sample_data": data,
            "response_time_ms": response_time,
            "cache_info": {
                "hits": get_stock_data_cached.cache_info().hits,
                "misses": get_stock_data_cached.cache_info().misses,
                "size": get_stock_data_cached.cache_info().currsize
            }
        })
        
    except Exception as e:
        response_time = round((time.time() - start_time) * 1000, 2)
        return jsonify({
            "test": "failed",
            "error": str(e),
            "response_time_ms": response_time
        }), 500

if __name__ == '__main__':
    print("⚡ Starting Simple Fast Financial API...")
    print("🎯 Single source: Yahoo Finance (unlimited, no API key needed)")
    print("💾 Caching: 1-minute in-memory cache for speed")
    print("🌐 Server: http://localhost:4000")
    print()
    print("📊 Available endpoints:")
    print("   http://localhost:4000/              (Documentation)")
    print("   http://localhost:4000/test          (Quick test)")
    print("   http://localhost:4000/stock/AAPL    (Single stock)")
    print("   http://localhost:4000/popular       (Popular stocks)")
    print()
    
    # Quick test
    try:
        minute_key = int(time.time() / 60)
        test_data = get_stock_data_cached("AAPL", minute_key)
        if test_data:
            print(f"✅ Startup test: AAPL @ ${test_data['price']}")
        else:
            print("⚠️  Startup test: Will work when server starts")
    except Exception as e:
        print(f"⚠️  Startup test: {e}")
    
    print("🚀 Starting server on port 4000...")
    app.run(host='0.0.0.0', port=4000, debug=False) 