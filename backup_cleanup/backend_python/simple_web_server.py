#!/usr/bin/env python3
"""
Simple Web Server for Financial Data APIs
=========================================

A lightweight Flask server to serve financial data from our multi-API provider
via HTTP endpoints for easy browser access.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from simplified_multi_source import (
        get_stock_data, 
        test_all_apis, 
        get_api_status,
        benchmark_apis,
        get_cache_info,
        clear_all_cache,
        create_simple_provider
    )
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

@app.route('/')
def home():
    """Home page with API documentation"""
    return jsonify({
        "message": "Multi-Source Financial Data API Server",
        "version": "1.0.0",
        "endpoints": {
            "/": "This documentation",
            "/health": "Server health check",
            "/api/status": "API configuration status",
            "/api/test": "Test all APIs",
            "/api/stock/{symbol}": "Get stock data for symbol",
            "/api/stocks": "Get multiple stocks (POST with symbols array)",
            "/api/benchmark": "Benchmark all APIs",
            "/api/cache/stats": "Cache statistics",
            "/api/cache/clear": "Clear cache"
        },
        "examples": {
            "single_stock": "/api/stock/AAPL",
            "test_apis": "/api/test?symbol=AAPL",
            "multiple_stocks": "POST /api/stocks with {'symbols': ['AAPL', 'GOOGL']}"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "apis_configured": 7,
        "cache_system": "enhanced"
    })

@app.route('/api/status')
def api_status():
    """Get API configuration status"""
    try:
        status = get_api_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/test')
def test_apis():
    """Test all APIs"""
    symbol = request.args.get('symbol', 'AAPL')
    try:
        results = test_all_apis(symbol)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stock/<symbol>')
def get_stock(symbol):
    """Get comprehensive stock data for a symbol"""
    try:
        data = get_stock_data(symbol.upper())
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stocks', methods=['POST'])
def get_stocks():
    """Get data for multiple stocks"""
    try:
        data = request.get_json()
        if not data or 'symbols' not in data:
            return jsonify({"error": "Please provide 'symbols' array in request body"}), 400
        
        symbols = data['symbols']
        if not isinstance(symbols, list):
            return jsonify({"error": "'symbols' must be an array"}), 400
        
        provider = create_simple_provider()
        results = provider.get_multiple_stocks_data([s.upper() for s in symbols])
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/benchmark')
def benchmark():
    """Benchmark all APIs"""
    symbols_param = request.args.get('symbols', 'AAPL,GOOGL,MSFT')
    symbols = [s.strip().upper() for s in symbols_param.split(',')]
    
    try:
        results = benchmark_apis(symbols)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cache/stats')
def cache_stats():
    """Get cache statistics"""
    try:
        stats = get_cache_info()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear cache"""
    try:
        count = clear_all_cache()
        return jsonify({"message": f"Cleared {count} cache entries"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/technical/<symbol>')
def get_technical(symbol):
    """Get technical analysis for a symbol"""
    try:
        provider = create_simple_provider()
        data = provider.calculate_simple_technical_indicators(symbol.upper())
        if data:
            return jsonify(data)
        else:
            return jsonify({"error": f"No technical data available for {symbol}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("🚀 Starting Multi-Source Financial Data API Server...")
    print("📡 Available endpoints:")
    print("   Home: http://localhost:5000/")
    print("   Test APIs: http://localhost:5000/api/test")
    print("   Stock Data: http://localhost:5000/api/stock/AAPL")
    print("   API Status: http://localhost:5000/api/status")
    print("   Health Check: http://localhost:5000/health")
    print()
    print("💡 Visit http://localhost:5000/ for full API documentation")
    print("🔄 Press Ctrl+C to stop the server")
    print()
    
    # Test if APIs are working on startup
    try:
        print("🧪 Testing APIs on startup...")
        test_result = test_all_apis("AAPL")
        working = test_result['summary']['working_apis']
        total = test_result['summary']['total_apis']
        print(f"✅ {working}/{total} APIs working ({test_result['summary']['success_rate']}% success rate)")
    except Exception as e:
        print(f"⚠️  Warning: API test failed on startup: {e}")
    
    print()
    app.run(host='0.0.0.0', port=5000, debug=True) 