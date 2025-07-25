#!/usr/bin/env python3
"""
🇮🇳 Simple NSE Stock Server - Using Working NSE API Approach
Exactly as provided by the user with proper session handling
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title="Simple NSE Stock Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_nse_quote(symbol):
    """Get NSE quote using the working method"""
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/",
    }
    session = requests.Session()
    session.headers.update(headers)

    # Do a dummy request to set cookies
    session.get("https://www.nseindia.com")

    # Now get the actual data
    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
    response = session.get(url, timeout=15)
    return response.json()

def get_nifty_50_data():
    """Get NIFTY 50 data using the working method"""
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/",
    }
    session = requests.Session()
    session.headers.update(headers)

    # Initialize session with cookies
    session.get("https://www.nseindia.com", timeout=10)

    # Get NIFTY 50 data
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    response = session.get(url, timeout=15)
    if response.status_code == 200:
        data = response.json()
        return data.get('data', [])
    else:
        print(f"NSE API Error: {response.status_code}")
        return []

def format_stock_data(nse_stocks):
    """Format NSE data to our terminal format"""
    formatted_stocks = []
    
    for stock in nse_stocks:
        try:
            # Skip the index itself
            if stock.get('symbol') == 'NIFTY 50':
                continue
                
            symbol = stock.get('symbol', 'N/A')
            price = float(stock.get('lastPrice', 0))
            change = float(stock.get('change', 0))
            change_percent = float(stock.get('pChange', 0))
            
            if price == 0:
                continue
            
            # Calculate RSI based on change
            rsi = 50.0
            if change > 0:
                rsi = min(70 + (change / price) * 1000, 100)
            elif change < 0:
                rsi = max(30 + (change / price) * 1000, 0)
            
            formatted_stock = {
                "symbol": symbol,
                "name": symbol.replace('-', ' ').title() + " Ltd",
                "price": price,
                "change": change,
                "changePercent": change_percent,
                "volume": int(stock.get('totalTradedVolume', 0)),
                "marketCap": int(stock.get('marketCap', 0)) if stock.get('marketCap') else 0,
                "pe": float(stock.get('pe', 0)) if stock.get('pe') else 0,
                "rsi": rsi,
                "sector": "NSE Listed",
                "source": "official_nse_api",
                "timestamp": datetime.now().isoformat()
            }
            
            formatted_stocks.append(formatted_stock)
            
        except Exception as e:
            print(f"Error formatting {stock.get('symbol', 'Unknown')}: {e}")
            continue
    
    return formatted_stocks

def screen_stocks(stocks, criteria):
    """Screen stocks based on criteria"""
    if not stocks:
        return []
    
    if criteria == "gainers":
        return sorted([s for s in stocks if s['changePercent'] > 0], 
                     key=lambda x: x['changePercent'], reverse=True)[:10]
    
    elif criteria == "losers":
        return sorted([s for s in stocks if s['changePercent'] < 0], 
                     key=lambda x: x['changePercent'])[:10]
    
    elif criteria == "high_volume":
        return sorted(stocks, key=lambda x: x['volume'], reverse=True)[:10]
    
    elif criteria == "low_pe":
        return sorted([s for s in stocks if s['pe'] > 0 and s['pe'] < 20], 
                     key=lambda x: x['pe'])[:10]
    
    elif criteria == "rsi_oversold":
        return [s for s in stocks if s['rsi'] < 30]
    
    elif criteria == "rsi_overbought":
        return [s for s in stocks if s['rsi'] > 70]
    
    elif criteria == "breakouts":
        return [s for s in stocks if s['changePercent'] > 2]
    
    elif criteria == "momentum":
        return [s for s in stocks if s['rsi'] > 50 and s['rsi'] < 70 and s['changePercent'] > 0]
    
    return stocks[:10]

@app.get("/")
def root():
    return {
        "message": "Simple NSE Stock Server",
        "status": "running",
        "exchange": "NSE",
        "data_source": "official_nse_api",
        "method": "working_session_approach"
    }

@app.get("/api/stocks/list")
def get_stocks():
    """Get NIFTY 50 stocks"""
    try:
        print("🔄 Fetching NIFTY 50 data from NSE...")
        nse_data = get_nifty_50_data()
        
        if not nse_data:
            raise HTTPException(status_code=503, detail="Unable to fetch NSE data")
        
        print(f"✅ Retrieved {len(nse_data)} items from NSE")
        stocks = format_stock_data(nse_data)
        print(f"✅ Formatted {len(stocks)} stocks")
        
        return {
            "success": True,
            "data": stocks,
            "count": len(stocks),
            "exchange": "NSE",
            "source": "official_nse_api",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Error fetching NSE data: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get("/api/stocks/screen/{criteria}")
def screen_stocks_endpoint(criteria: str):
    """Screen stocks based on criteria"""
    try:
        print(f"🔍 Screening stocks with criteria: {criteria}")
        nse_data = get_nifty_50_data()
        
        if not nse_data:
            raise HTTPException(status_code=503, detail="Unable to fetch NSE data")
        
        stocks = format_stock_data(nse_data)
        screened = screen_stocks(stocks, criteria)
        
        return {
            "success": True,
            "data": screened,
            "count": len(screened),
            "criteria": criteria,
            "exchange": "NSE",
            "source": "official_nse_api",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Error screening stocks: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get("/api/stocks/quote/{symbol}")
def get_stock_quote(symbol: str):
    """Get individual stock quote"""
    try:
        print(f"📊 Getting quote for {symbol}")
        quote_data = get_nse_quote(symbol.upper())
        
        return {
            "success": True,
            "data": quote_data,
            "symbol": symbol.upper(),
            "exchange": "NSE",
            "source": "official_nse_api",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Error fetching quote: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )

if __name__ == "__main__":
    print("🇮🇳 Starting Simple NSE Stock Server...")
    print("📈 Using working NSE API approach")
    print("🔗 Direct NSE API calls with proper session handling")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    ) 