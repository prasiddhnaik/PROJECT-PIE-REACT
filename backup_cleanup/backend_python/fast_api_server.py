#!/usr/bin/env python3
"""
Fast Financial Data API Server
==============================

Optimized version with better performance and faster response times.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os
import asyncio
import concurrent.futures
from functools import lru_cache
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from simplified_multi_source import create_simple_provider
    import yfinance as yf
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

# Global provider instance for better performance
provider = create_simple_provider()

# Cache for fast responses
@lru_cache(maxsize=1000)
def get_cached_stock_price(symbol, cache_key):
    """Fast cached stock price lookup"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        if not hist.empty:
            return {
                "symbol": symbol,
                "price": round(float(hist['Close'].iloc[-1]), 2),
                "change": round(float(hist['Close'].iloc[-1] - hist['Open'].iloc[-1]), 2),
                "volume": int(hist['Volume'].iloc[-1]),
                "timestamp": time.time(),
                "source": "yahoo_fast"
            }
    except:
        pass
    return None

def get_fast_stock_data(symbol):
    """Get stock data with optimized performance"""
    # Use current minute as cache key for 1-minute caching
    cache_key = int(time.time() / 60)
    
    # Try cached version first
    cached_data = get_cached_stock_price(symbol, cache_key)
    if cached_data:
        return cached_data
    
    # Fallback to full provider
    try:
        data = provider.get_comprehensive_stock_data(symbol)
        return data.get('primary_data')
    except:
        return None

@app.route('/')
def home():
    """Fast API documentation"""
    return jsonify({
        "message": "⚡ Fast Financial Data API",
        "version": "2.0.0",
        "performance": "optimized",
        "endpoints": {
            "/health": "Health check",
            "/fast/stock/{symbol}": "Fast stock data",
            "/fast/stocks": "Multiple stocks (POST)",
            "/fast/popular": "Popular stocks",
            "/api/test/quick": "Quick API test"
        }
    })

@app.route('/health')
def health():
    """Fast health check"""
    return jsonify({"status": "fast", "latency": "low"})

@app.route('/fast/stock/<symbol>')
def fast_stock(symbol):
    """Ultra-fast stock data endpoint"""
    start_time = time.time()
    
    try:
        data = get_fast_stock_data(symbol.upper())
        response_time = round((time.time() - start_time) * 1000, 2)
        
        if data:
            return jsonify({
                "success": True,
                "data": data,
                "response_time_ms": response_time,
                "cached": data.get('timestamp', 0) > time.time() - 60
            })
        else:
            return jsonify({
                "success": False,
                "error": "No data available",
                "response_time_ms": response_time
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "response_time_ms": round((time.time() - start_time) * 1000, 2)
        }), 500

@app.route('/fast/stocks', methods=['POST'])
def fast_multiple_stocks():
    """Fast multiple stocks endpoint"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({"error": "No symbols provided"}), 400
        
        # Limit to 10 symbols for performance
        symbols = symbols[:10]
        
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_symbol = {
                executor.submit(get_fast_stock_data, symbol.upper()): symbol.upper() 
                for symbol in symbols
            }
            
            for future in concurrent.futures.as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    data = future.result(timeout=3)  # 3 second timeout per symbol
                    results[symbol] = data
                except Exception as e:
                    results[symbol] = {"error": str(e)}
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return jsonify({
            "success": True,
            "data": results,
            "response_time_ms": response_time,
            "symbols_count": len(symbols)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "response_time_ms": round((time.time() - start_time) * 1000, 2)
        }), 500

@app.route('/fast/popular')
def popular_stocks():
    """Get popular stocks data quickly"""
    popular_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
    
    start_time = time.time()
    results = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_symbol = {
            executor.submit(get_fast_stock_data, symbol): symbol 
            for symbol in popular_symbols
        }
        
        for future in concurrent.futures.as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                data = future.result(timeout=2)
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

@app.route('/api/test/quick')
def quick_test():
    """Quick API functionality test"""
    start_time = time.time()
    
    try:
        # Test with AAPL
        data = get_fast_stock_data('AAPL')
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return jsonify({
            "test": "passed" if data else "failed",
            "response_time_ms": response_time,
            "sample_data": data,
            "timestamp": time.time()
        })
        
    except Exception as e:
        return jsonify({
            "test": "failed",
            "error": str(e),
            "response_time_ms": round((time.time() - start_time) * 1000, 2)
        })

@app.route('/metrics')
def metrics():
    """Performance metrics"""
    return jsonify({
        "cache_info": get_cached_stock_price.cache_info()._asdict(),
        "server_uptime": time.time(),
        "optimization": "enabled"
    })

if __name__ == '__main__':
    print("⚡ Starting FAST Financial Data API Server...")
    print("🚀 Performance: OPTIMIZED")
    print("📡 Endpoints:")
    print("   ⚡ Fast Stock: http://localhost:4000/fast/stock/AAPL")
    print("   📊 Popular: http://localhost:4000/fast/popular")
    print("   🧪 Quick Test: http://localhost:4000/api/test/quick")
    print("   📈 Health: http://localhost:4000/health")
    print()
    
    # Quick startup test
    try:
        test_data = get_fast_stock_data("AAPL")
        if test_data:
            print(f"✅ Startup test passed: AAPL @ ${test_data.get('price', 'N/A')}")
        else:
            print("⚠️  Startup test: No data (may work in browser)")
    except Exception as e:
        print(f"⚠️  Startup test warning: {e}")
    
    print("🔥 Demo server starting on port 4000 to avoid frontend conflicts...")
    
    # Use port 4000 to avoid conflicts with Next.js frontend on port 3000
    app.run(host='0.0.0.0', port=4000, debug=False, threaded=True) 