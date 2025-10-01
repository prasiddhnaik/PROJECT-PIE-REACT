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
import sqlite3
import json
import os
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DB_PATH = Path(__file__).parent / "stock_data.db"

def init_database():
    """Initialize SQLite database for persistent storage"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables for historical data and user portfolios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historical_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            date DATE NOT NULL,
            open_price REAL,
            high_price REAL,
            low_price REAL,
            close_price REAL,
            volume INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, date)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            shares INTEGER NOT NULL,
            purchase_price REAL,
            purchase_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            added_date DATE DEFAULT CURRENT_DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, symbol)
        )
    ''')

    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

def save_historical_data(symbol, data):
    """Save historical data to database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        for record in data:
            cursor.execute('''
                INSERT OR REPLACE INTO historical_data
                (symbol, date, open_price, high_price, low_price, close_price, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol.upper(),
                record['date'],
                record['open'],
                record['high'],
                record['low'],
                record['close'],
                record.get('volume', 0)
            ))

        conn.commit()
        conn.close()
        logger.info(f"Saved {len(data)} historical records for {symbol}")
        return True
    except Exception as e:
        logger.error(f"Error saving historical data: {e}")
        return False

def get_saved_historical_data(symbol, start_date=None, end_date=None):
    """Retrieve historical data from database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        query = "SELECT date, open_price, high_price, low_price, close_price, volume FROM historical_data WHERE symbol = ?"
        params = [symbol.upper()]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " ORDER BY date ASC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        historical_data = []
        for row in rows:
            historical_data.append({
                "date": row[0],
                "open": row[1],
                "high": row[2],
                "low": row[3],
                "close": row[4],
                "volume": row[5]
            })

        return historical_data
    except Exception as e:
        logger.error(f"Error retrieving historical data: {e}")
        return []

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
    
    # Try database first
    saved_data = get_saved_historical_data(symbol)
    if saved_data:
        logger.info(f"Database hit for {symbol} historical data")
        cache[cache_key] = {
            "symbol": symbol.upper(),
            "period": period,
            "data": saved_data,
            "timestamp": datetime.now().isoformat(),
            "source": "database"
        }
        return jsonify(cache[cache_key])

    # Fetch fresh data if not in database
    data = fetch_historical_data(symbol, period)

    if data:
        # Save to database for future use
        save_historical_data(symbol, data['data'])
        cache[cache_key] = data
        logger.info(f"Fetched and saved historical data for {symbol} ({period})")
        return jsonify(data)
    else:
        return jsonify({"error": f"Could not fetch historical data for {symbol}"}), 404

@app.route('/portfolio/<user_id>', methods=['GET'])
def get_portfolio(user_id):
    """Get user's portfolio"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT symbol, shares, purchase_price, purchase_date
            FROM portfolios
            WHERE user_id = ?
            ORDER BY purchase_date DESC
        ''', (user_id,))

        rows = cursor.fetchall()
        conn.close()

        portfolio = []
        for row in rows:
            portfolio.append({
                "symbol": row[0],
                "shares": row[1],
                "purchase_price": row[2],
                "purchase_date": row[3]
            })

        return jsonify({
            "user_id": user_id,
            "portfolio": portfolio,
            "total_stocks": len(portfolio)
        })
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        return jsonify({"error": "Could not retrieve portfolio"}), 500

@app.route('/portfolio/<user_id>', methods=['POST'])
def add_to_portfolio(user_id):
    """Add stock to user's portfolio"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        shares = data.get('shares', 0)
        purchase_price = data.get('purchase_price', 0.0)

        if not symbol or shares <= 0 or purchase_price <= 0:
            return jsonify({"error": "Invalid data provided"}), 400

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO portfolios
            (user_id, symbol, shares, purchase_price, purchase_date)
            VALUES (?, ?, ?, ?, CURRENT_DATE)
        ''', (user_id, symbol, shares, purchase_price))

        conn.commit()
        conn.close()

        logger.info(f"Added {shares} shares of {symbol} to portfolio for user {user_id}")
        return jsonify({"message": f"Added {shares} shares of {symbol} to portfolio"})
    except Exception as e:
        logger.error(f"Error adding to portfolio: {e}")
        return jsonify({"error": "Could not add to portfolio"}), 500

@app.route('/watchlist/<user_id>', methods=['GET'])
def get_watchlist(user_id):
    """Get user's watchlist"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT symbol, added_date
            FROM watchlist
            WHERE user_id = ?
            ORDER BY added_date DESC
        ''', (user_id,))

        rows = cursor.fetchall()
        conn.close()

        watchlist = []
        for row in rows:
            watchlist.append({
                "symbol": row[0],
                "added_date": row[1]
            })

        return jsonify({
            "user_id": user_id,
            "watchlist": watchlist,
            "total_symbols": len(watchlist)
        })
    except Exception as e:
        logger.error(f"Error getting watchlist: {e}")
        return jsonify({"error": "Could not retrieve watchlist"}), 500

@app.route('/watchlist/<user_id>/<symbol>', methods=['POST'])
def add_to_watchlist(user_id, symbol):
    """Add symbol to user's watchlist"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR IGNORE INTO watchlist
            (user_id, symbol, added_date)
            VALUES (?, ?, CURRENT_DATE)
        ''', (user_id, symbol.upper()))

        conn.commit()
        conn.close()

        logger.info(f"Added {symbol} to watchlist for user {user_id}")
        return jsonify({"message": f"Added {symbol} to watchlist"})
    except Exception as e:
        logger.error(f"Error adding to watchlist: {e}")
        return jsonify({"error": "Could not add to watchlist"}), 500

@app.route('/export/<symbol>')
def export_historical_data(symbol):
    """Export historical data as CSV"""
    try:
        data = get_saved_historical_data(symbol)

        if not data:
            return jsonify({"error": "No historical data found"}), 404

        # Create CSV content
        csv_content = "Date,Open,High,Low,Close,Volume\n"
        for record in data:
            csv_content += f"{record['date']},{record['open']},{record['high']},{record['low']},{record['close']},{record.get('volume', 0)}\n"

        from flask import Response
        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={symbol}_historical.csv"}
        )
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return jsonify({"error": "Could not export data"}), 500

@app.route('/stats/<symbol>')
def get_stock_stats(symbol):
    """Get statistical analysis of historical data"""
    try:
        data = get_saved_historical_data(symbol)

        if not data or len(data) < 2:
            return jsonify({"error": "Insufficient data for analysis"}), 400

        closes = [float(record['close']) for record in data]
        volumes = [int(record.get('volume', 0)) for record in data]

        # Calculate basic statistics
        current_price = closes[-1]
        previous_price = closes[0]
        price_change = current_price - previous_price
        percent_change = (price_change / previous_price) * 100 if previous_price > 0 else 0

        # Simple moving averages
        sma_5 = sum(closes[-5:]) / min(5, len(closes)) if closes else 0
        sma_20 = sum(closes[-20:]) / min(20, len(closes)) if closes else 0

        # Volume average
        avg_volume = sum(volumes) / len(volumes) if volumes else 0

        # Trend analysis
        recent_closes = closes[-10:] if len(closes) >= 10 else closes
        trend = "up" if recent_closes[-1] > recent_closes[0] else "down" if recent_closes[-1] < recent_closes[0] else "sideways"

        return jsonify({
            "symbol": symbol.upper(),
            "current_price": current_price,
            "price_change": round(price_change, 2),
            "percent_change": round(percent_change, 2),
            "sma_5": round(sma_5, 2),
            "sma_20": round(sma_20, 2),
            "avg_volume": int(avg_volume),
            "trend": trend,
            "data_points": len(data),
            "date_range": f"{data[0]['date']} to {data[-1]['date']}"
        })
    except Exception as e:
        logger.error(f"Error calculating stats: {e}")
        return jsonify({"error": "Could not calculate statistics"}), 500

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
    # Initialize database
    init_database()

    print("🚀 Starting Enhanced Stock Data Server with Database Support...")
    print("💾 Database: SQLite with persistent storage")
    print("📊 Available endpoints:")
    print("   GET  /test                     - Test server")
    print("   GET  /stock/<symbol>           - Get single stock")
    print("   GET  /stock/<symbol>/history   - Get historical data")
    print("   POST /stocks                   - Get multiple stocks")
    print("   GET  /popular                  - Get popular stocks")
    print("   GET  /status                   - Server status")
    print("   GET  /clear-cache              - Clear cache")
    print("   GET  /portfolio/<user_id>      - Get user portfolio")
    print("   POST /portfolio/<user_id>      - Add to portfolio")
    print("   GET  /watchlist/<user_id>      - Get user watchlist")
    print("   POST /watchlist/<user_id>/<symbol> - Add to watchlist")
    print("   GET  /export/<symbol>          - Export historical data as CSV")
    print("   GET  /stats/<symbol>           - Get stock statistics")
    print("🔄 Auto-refresh: 960 seconds (16 minutes)")
    print("💾 Data Persistence: Historical data saved to SQLite database")
    print("📊 Features: Portfolio tracking, watchlists, data export, statistics")
    print("🌐 Server starting on http://localhost:4000")

    app.run(host='0.0.0.0', port=4000, debug=False) 