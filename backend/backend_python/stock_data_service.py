#!/usr/bin/env python3
"""
Real Stock Data Service
=====================

Provides real stock market data using multiple APIs with fallback mechanisms.
Focused on Indian NSE stocks and global stocks with high reliability.
"""

import asyncio
import aiohttp
import yfinance as yf
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import time
import pandas as pd
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Keys (from memories)
ALPHA_VANTAGE_KEY = "22TNS9NWXVD5CPVF"
FINNHUB_KEY = "d16k039r01qvtdbj2gtgd16k039r01qvtdbj2gu0"
POLYGON_KEY = "SavZMeuTDTxjWJuFzBO6zES7mBFK68RJ"

# NSE Stock Symbols (Indian stocks) - Using correct Yahoo Finance symbols
NSE_SYMBOLS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS", 
    "ICICIBANK.NS", "KOTAKBANK.NS", "LT.NS", "SBIN.NS", "BHARTIARTL.NS", 
    "WIPRO.NS", "MARUTI.NS", "ASIANPAINT.NS", "HCLTECH.NS", "BAJFINANCE.NS", 
    "TITAN.NS", "ULTRACEMCO.NS", "POWERGRID.NS", "NESTLEIND.NS", "DIVISLAB.NS"
]

# US Stock Symbols (More reliable with free APIs)
US_SYMBOLS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", 
    "JPM", "V", "MA", "UNH", "JNJ", "WMT", "PG", "HD", "BAC", "XOM",
    "INTC", "CSCO", "KO", "PFE", "T", "VZ", "DIS", "ADBE", "CRM", "ORCL"
]

# Combined symbols for better data availability
STOCK_SYMBOLS = US_SYMBOLS + NSE_SYMBOLS[:10]  # Mix of US and top NSE stocks

class StockDataService:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        self.session = None
        
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
        
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _is_cache_valid(self, symbol: str) -> bool:
        """Check if cached data is still valid"""
        if symbol not in self.cache:
            return False
        
        cache_time = self.cache[symbol].get('timestamp', 0)
        return time.time() - cache_time < self.cache_duration
    
    def _get_cached_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached data if valid"""
        if self._is_cache_valid(symbol):
            return self.cache[symbol]['data']
        return None
    
    def _set_cache(self, symbol: str, data: Dict[str, Any]):
        """Set cache data"""
        self.cache[symbol] = {
            'data': data,
            'timestamp': time.time()
        }
    
    async def get_stock_data_yahoo(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch stock data from Yahoo Finance"""
        try:
            # Check cache first
            cached_data = self._get_cached_data(symbol)
            if cached_data:
                return cached_data
            
            # Use symbol as is - NSE symbols already have .NS suffix
            yahoo_symbol = symbol
            
            ticker = yf.Ticker(yahoo_symbol)
            hist = ticker.history(period="2d")
            info = ticker.info
            
            if hist.empty:
                return None
            
            current_price = float(hist['Close'].iloc[-1])
            volume = int(hist['Volume'].iloc[-1]) if 'Volume' in hist and not hist['Volume'].empty else 0
            
            # Calculate change
            if len(hist) > 1:
                prev_close = float(hist['Close'].iloc[-2])
                change = current_price - prev_close
                change_percent = (change / prev_close) * 100
            else:
                change = 0
                change_percent = 0
            
            # Calculate RSI (simplified)
            rsi = self._calculate_rsi(hist['Close']) if len(hist) >= 14 else 50.0
            
            # Display symbol without .NS suffix for clarity
            display_symbol = symbol.replace('.NS', '')
            
            stock_data = {
                "symbol": display_symbol,
                "name": info.get('shortName', display_symbol),
                "price": round(current_price, 2),
                "change": round(change, 2),
                "changePercent": round(change_percent, 2),
                "volume": volume,
                "marketCap": info.get('marketCap', 0),
                "pe": info.get('trailingPE', 0) or 0,
                "rsi": round(rsi, 1),
                "sector": info.get('sector', 'N/A'),
                "source": "yahoo_finance",
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache the data
            self._set_cache(symbol, stock_data)
            currency = "₹" if ".NS" in symbol else "$"
            logger.info(f"Yahoo Finance: {display_symbol} - {currency}{current_price}")
            return stock_data
            
        except Exception as e:
            logger.error(f"Yahoo Finance error for {symbol}: {e}")
            return None
    
    async def get_stock_data_alpha_vantage(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch stock data from Alpha Vantage"""
        try:
            session = await self._get_session()
            
            # Check cache first
            cached_data = self._get_cached_data(symbol)
            if cached_data:
                return cached_data
            
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': ALPHA_VANTAGE_KEY
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'Global Quote' in data:
                        quote = data['Global Quote']
                        
                        current_price = float(quote.get('05. price', 0))
                        change = float(quote.get('09. change', 0))
                        change_percent = float(quote.get('10. change percent', '0%').replace('%', ''))
                        
                        stock_data = {
                            "symbol": symbol,
                            "name": quote.get('01. symbol', symbol),
                            "price": round(current_price, 2),
                            "change": round(change, 2),
                            "changePercent": round(change_percent, 2),
                            "volume": int(quote.get('06. volume', 0)),
                            "marketCap": 0,
                            "pe": 0,
                            "rsi": 50.0,
                            "sector": "N/A",
                            "source": "alpha_vantage",
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        self._set_cache(symbol, stock_data)
                        logger.info(f"Alpha Vantage: {symbol} - ${current_price}")
                        return stock_data
                        
        except Exception as e:
            logger.error(f"Alpha Vantage error for {symbol}: {e}")
            return None
    
    async def get_stock_data_finnhub(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch stock data from Finnhub"""
        try:
            session = await self._get_session()
            
            # Check cache first
            cached_data = self._get_cached_data(symbol)
            if cached_data:
                return cached_data
            
            url = f"https://finnhub.io/api/v1/quote"
            params = {
                'symbol': symbol,
                'token': FINNHUB_KEY
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    current_price = data.get('c', 0)
                    change = data.get('d', 0)
                    change_percent = data.get('dp', 0)
                    
                    if current_price > 0:
                        stock_data = {
                            "symbol": symbol,
                            "name": symbol,
                            "price": round(current_price, 2),
                            "change": round(change, 2),
                            "changePercent": round(change_percent, 2),
                            "volume": 0,
                            "marketCap": 0,
                            "pe": 0,
                            "rsi": 50.0,
                            "sector": "N/A",
                            "source": "finnhub",
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        self._set_cache(symbol, stock_data)
                        logger.info(f"Finnhub: {symbol} - ${current_price}")
                        return stock_data
                        
        except Exception as e:
            logger.error(f"Finnhub error for {symbol}: {e}")
            return None
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI (Relative Strength Index)"""
        try:
            if len(prices) < period:
                return 50.0
            
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
        except:
            return 50.0
    
    async def get_stock_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get stock data with fallback mechanism"""
        # Try Yahoo Finance first (most reliable)
        data = await self.get_stock_data_yahoo(symbol)
        if data:
            return data
        
        # Try Alpha Vantage
        data = await self.get_stock_data_alpha_vantage(symbol)
        if data:
            return data
        
        # Try Finnhub
        data = await self.get_stock_data_finnhub(symbol)
        if data:
            return data
        
        logger.warning(f"All APIs failed for {symbol}")
        return None
    
    async def get_batch_stock_data(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get data for multiple stocks with rate limiting"""
        valid_results = []
        
        # Process symbols in batches to avoid rate limiting
        batch_size = 5
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            tasks = [self.get_stock_data(symbol) for symbol in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, dict) and result:
                    valid_results.append(result)
            
            # Add delay between batches
            if i + batch_size < len(symbols):
                await asyncio.sleep(1)  # 1 second delay between batches
        
        return valid_results
    
    async def get_nse_stocks(self) -> List[Dict[str, Any]]:
        """Get mixed stock data (US + NSE)"""
        return await self.get_batch_stock_data(STOCK_SYMBOLS[:20])  # Top 20 mixed stocks
    
    async def get_global_stocks(self) -> List[Dict[str, Any]]:
        """Get global stock data"""
        return await self.get_batch_stock_data(STOCK_SYMBOLS[:10])  # Top 10 global stocks
    
    async def screen_stocks(self, stocks: List[Dict[str, Any]], criteria: str) -> List[Dict[str, Any]]:
        """Screen stocks based on criteria"""
        if not stocks:
            return []
        
        if criteria == "breakouts":
            return [s for s in stocks if s.get('rsi', 0) > 60 and s.get('changePercent', 0) > 1.5]
        
        elif criteria == "high_volume":
            return sorted([s for s in stocks if s.get('volume', 0) > 1000000], 
                        key=lambda x: x.get('volume', 0), reverse=True)
        
        elif criteria == "rsi_oversold":
            return [s for s in stocks if s.get('rsi', 50) < 30]
        
        elif criteria == "rsi_overbought":
            return [s for s in stocks if s.get('rsi', 50) > 70]
        
        elif criteria == "gainers":
            return sorted([s for s in stocks if s.get('changePercent', 0) > 0], 
                        key=lambda x: x.get('changePercent', 0), reverse=True)[:10]
        
        elif criteria == "losers":
            return sorted([s for s in stocks if s.get('changePercent', 0) < 0], 
                        key=lambda x: x.get('changePercent', 0))[:10]
        
        elif criteria == "low_pe":
            return sorted([s for s in stocks if 0 < s.get('pe', 0) < 20], 
                        key=lambda x: x.get('pe', 0))
        
        elif criteria == "momentum":
            return [s for s in stocks if 50 <= s.get('rsi', 50) <= 70 and s.get('changePercent', 0) > 0]
        
        return stocks

# Global instance
stock_service = StockDataService()

# API endpoints for FastAPI integration
async def get_stock_quote(symbol: str) -> Dict[str, Any]:
    """Get single stock quote"""
    data = await stock_service.get_stock_data(symbol)
    if data:
        return {"success": True, "data": data}
    return {"success": False, "error": f"No data found for {symbol}"}

async def get_stock_list() -> Dict[str, Any]:
    """Get list of stocks"""
    nse_stocks = await stock_service.get_nse_stocks()
    return {"success": True, "data": nse_stocks, "count": len(nse_stocks)}

async def screen_stocks_endpoint(criteria: str) -> Dict[str, Any]:
    """Screen stocks by criteria"""
    stocks = await stock_service.get_nse_stocks()
    screened = await stock_service.screen_stocks(stocks, criteria)
    return {
        "success": True, 
        "data": screened, 
        "count": len(screened),
        "criteria": criteria,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Test the service
    async def test_service():
        service = StockDataService()
        
        # Test individual stock
        data = await service.get_stock_data("RELIANCE")
        print(f"RELIANCE: {data}")
        
        # Test batch
        stocks = await service.get_nse_stocks()
        print(f"NSE Stocks: {len(stocks)} fetched")
        
        # Test screening
        breakouts = await service.screen_stocks(stocks, "breakouts")
        print(f"Breakouts: {len(breakouts)} found")
        
        await service.close_session()
    
    asyncio.run(test_service()) 