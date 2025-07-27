#!/usr/bin/env python3
"""
🇮🇳 Official NSE Stock Data Server
Using real NSE JSON API endpoints with proper headers
"""

import asyncio
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title="Official NSE Stock Data Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# NSE API Configuration
NSE_BASE_URL = "https://www.nseindia.com/api"
NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

class NSEDataProvider:
    def __init__(self):
        self.session = None
        self.nifty_50_symbols = [
            "RELIANCE", "TCS", "HDFCBANK", "INFY", "HINDUNILVR", "ICICIBANK",
            "KOTAKBANK", "LT", "SBIN", "BHARTIARTL", "WIPRO", "MARUTI",
            "ASIANPAINT", "HCLTECH", "BAJFINANCE", "TITAN", "ULTRACEMCO",
            "POWERGRID", "NESTLEIND", "DIVISLAB", "AXISBANK", "ADANIPORTS",
            "TATASTEEL", "JSWSTEEL", "SUNPHARMA", "ONGC", "NTPC", "COALINDIA",
            "HINDALCO", "BAJAJFINSV", "TECHM", "GRASIM", "EICHERMOT",
            "HEROMOTOCO", "CIPLA", "DRREDDY", "APOLLOHOSP", "BAJAJ-AUTO",
            "BRITANNIA", "TATAMOTORS", "SHREECEM", "INDUSINDBK", "TATACONSUM",
            "BPCL", "HDFCLIFE", "SBILIFE", "ADANIENT", "ADANIGREEN", "IOC"
        ]
    
    def get_session(self):
        if self.session is None:
            self.session = requests.Session()
            self.session.headers.update(NSE_HEADERS)
            # Initialize session with cookies by visiting NSE homepage
            try:
                self.session.get("https://www.nseindia.com", timeout=10)
                print("✅ NSE session initialized with cookies")
            except Exception as e:
                print(f"⚠️ Warning: Failed to initialize NSE session: {e}")
        return self.session
    
    def fetch_nifty_50_data(self) -> List[Dict]:
        """Fetch NIFTY 50 index data"""
        session = self.get_session()
        try:
            url = f"{NSE_BASE_URL}/equity-stockIndices?index=NIFTY%2050"
            response = session.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                stocks = data.get('data', [])
                print(f"✅ Fetched {len(stocks)} NIFTY 50 stocks from NSE API")
                return stocks
            else:
                print(f"❌ NSE API returned status {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error fetching NIFTY 50 data: {e}")
            return []
    
    def fetch_stock_quote(self, symbol: str) -> Optional[Dict]:
        """Fetch individual stock quote"""
        session = self.get_session()
        try:
            url = f"{NSE_BASE_URL}/quote-equity?symbol={symbol}"
            response = session.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Fetched quote for {symbol}")
                return data
            else:
                print(f"❌ Failed to fetch {symbol}: status {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error fetching {symbol}: {e}")
            return None
    
    def format_stock_data(self, nifty_data: List[Dict]) -> List[Dict]:
        """Format NSE data to our standard format"""
        formatted_stocks = []
        
        for stock in nifty_data:
            try:
                # Extract data from NSE format
                symbol = stock.get('symbol', 'N/A')
                price = float(stock.get('lastPrice', 0))
                change = float(stock.get('change', 0))
                change_percent = float(stock.get('pChange', 0))
                
                # Calculate additional metrics
                prev_close = float(stock.get('previousClose', price))
                high = float(stock.get('dayHigh', price))
                low = float(stock.get('dayLow', price))
                
                # Skip if no valid price data
                if price == 0:
                    continue
                
                # Format stock data
                stock_data = {
                    "symbol": symbol,
                    "name": symbol.replace('-', ' ').title() + " Ltd",
                    "price": price,
                    "change": change,
                    "changePercent": change_percent,
                    "volume": int(stock.get('totalTradedVolume', 0)),
                    "marketCap": int(stock.get('marketCap', 0)) if stock.get('marketCap') else 0,
                    "pe": float(stock.get('pe', 0)) if stock.get('pe') else 0,
                    "previousClose": prev_close,
                    "dayHigh": high,
                    "dayLow": low,
                    "rsi": self.calculate_rsi(price, prev_close),
                    "sector": "NSE Listed",
                    "source": "official_nse_api",
                    "timestamp": datetime.now().isoformat()
                }
                
                formatted_stocks.append(stock_data)
                
            except Exception as e:
                print(f"❌ Error formatting stock {stock.get('symbol', 'Unknown')}: {e}")
                continue
        
        print(f"✅ Formatted {len(formatted_stocks)} stocks successfully")
        return formatted_stocks
    
    def calculate_rsi(self, current_price: float, prev_close: float) -> float:
        """Simple RSI calculation based on price change"""
        try:
            change = current_price - prev_close
            if change > 0:
                return min(70 + (change / prev_close) * 100, 100)
            else:
                return max(30 + (change / prev_close) * 100, 0)
        except:
            return 50.0
    
    def screen_stocks(self, stocks: List[Dict], criteria: str) -> List[Dict]:
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
            return [s for s in stocks if s['price'] > s['previousClose'] * 1.02]
        
        elif criteria == "momentum":
            return [s for s in stocks if s['rsi'] > 50 and s['rsi'] < 70 and s['changePercent'] > 0]
        
        return stocks[:10]

# Initialize NSE data provider
nse_provider = NSEDataProvider()

@app.get("/")
async def root():
    return {
        "message": "Official NSE Stock Data Server",
        "status": "running",
        "exchange": "NSE",
        "data_source": "official_nse_api",
        "endpoints": [
            "/api/stocks/list",
            "/api/stocks/screen/{criteria}",
            "/api/stocks/quote/{symbol}"
        ]
    }

@app.get("/api/stocks/list")
def get_stocks():
    """Get all NIFTY 50 stocks with live data"""
    try:
        nifty_data = nse_provider.fetch_nifty_50_data()
        if not nifty_data:
            raise HTTPException(status_code=503, detail="Unable to fetch NSE data")
        
        stocks = nse_provider.format_stock_data(nifty_data)
        
        return {
            "success": True,
            "data": stocks,
            "count": len(stocks),
            "exchange": "NSE",
            "source": "official_nse_api",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Error fetching NSE data: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get("/api/stocks/screen/{criteria}")
def screen_stocks(criteria: str):
    """Screen stocks based on criteria"""
    try:
        # Get all stocks first
        nifty_data = nse_provider.fetch_nifty_50_data()
        if not nifty_data:
            raise HTTPException(status_code=503, detail="Unable to fetch NSE data")
        
        stocks = nse_provider.format_stock_data(nifty_data)
        screened_stocks = nse_provider.screen_stocks(stocks, criteria)
        
        return {
            "success": True,
            "data": screened_stocks,
            "count": len(screened_stocks),
            "criteria": criteria,
            "exchange": "NSE",
            "source": "official_nse_api",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
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
    """Get detailed quote for a specific stock"""
    try:
        quote_data = nse_provider.fetch_stock_quote(symbol.upper())
        if not quote_data:
            raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
        
        return {
            "success": True,
            "data": quote_data,
            "symbol": symbol.upper(),
            "exchange": "NSE",
            "source": "official_nse_api",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Error fetching quote for {symbol}: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )

@app.on_event("shutdown")
def shutdown_event():
    """Cleanup on shutdown"""
    if nse_provider.session:
        nse_provider.session.close()

if __name__ == "__main__":
    print("🇮🇳 Starting Official NSE Stock Data Server...")
    print("📈 Using real NSE JSON API endpoints")
    print("🔗 Data source: https://www.nseindia.com/api")
    print("📊 Serving NIFTY 50 stocks with live data")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    ) 