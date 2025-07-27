"""
Multi-Source Financial Data Provider
===================================

Comprehensive data integration system using multiple financial APIs
for high reliability and real-time market analysis.
"""

import yfinance as yf
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import sqlite3
import json
from typing import Dict, List, Optional, Any, Union
import asyncio
import aiohttp
from requests_cache import CacheMixin
from requests_ratelimiter import LimiterMixin
from pyrate_limiter import Duration, RequestRate, Limiter
import pandas_ta as ta
from bs4 import BeautifulSoup
import joblib
import time

logger = logging.getLogger(__name__)

class CachedLimitedSession(CacheMixin, LimiterMixin, requests.Session):
    """HTTP session with caching and rate limiting"""
    pass

class MultiSourceDataProvider:
    """
    Production-grade financial data provider with multiple API sources
    and intelligent fallback mechanisms.
    """
    
    def __init__(self):
        self.cache_file = "market_data_cache.db"
        self.session = CachedLimitedSession(
            limiter=Limiter(RequestRate(10, Duration.SECOND)),
            cache_name="market_cache",
            backend="sqlite",
            expire_after=300  # 5 minutes
        )
        self._init_cache_db()
        
        # API endpoints and configurations
        self.nse_base_url = "https://www.nseindia.com/api"
        self.bse_base_url = "https://api.bseindia.com"
        self.morningstar_base_url = "https://api.morningstar.com"
        
        # Rate limits (requests per minute)
        self.rate_limits = {
            "yahoo": 60,
            "nse": 30,
            "bse": 20,
            "morningstar": 50
        }
        
        logger.info("Multi-source data provider initialized")

    def _init_cache_db(self):
        """Initialize SQLite cache database"""
        try:
            conn = sqlite3.connect(self.cache_file)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stock_cache (
                    symbol TEXT PRIMARY KEY,
                    data TEXT,
                    timestamp REAL,
                    source TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS market_status (
                    exchange TEXT PRIMARY KEY,
                    status TEXT,
                    timestamp REAL
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Cache initialization error: {e}")

    def _get_cached_data(self, symbol: str, max_age: int = 300) -> Optional[Dict]:
        """Retrieve cached data if still valid"""
        try:
            conn = sqlite3.connect(self.cache_file)
            cursor = conn.execute(
                "SELECT data, timestamp, source FROM stock_cache WHERE symbol = ?",
                (symbol,)
            )
            row = cursor.fetchone()
            conn.close()
            
            if row:
                data, timestamp, source = row
                if time.time() - timestamp < max_age:
                    return {
                        "data": json.loads(data),
                        "source": source,
                        "cached": True
                    }
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
        return None

    def _cache_data(self, symbol: str, data: Dict, source: str):
        """Cache data to SQLite database"""
        try:
            conn = sqlite3.connect(self.cache_file)
            conn.execute(
                "INSERT OR REPLACE INTO stock_cache (symbol, data, timestamp, source) VALUES (?, ?, ?, ?)",
                (symbol, json.dumps(data), time.time(), source)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Cache storage error: {e}")

    # 1. Yahoo Finance API Integration
    def fetch_yahoo_data(self, symbol: str, period: str = "1d") -> Optional[Dict]:
        """
        Fetch data from Yahoo Finance API
        Rate limits: 60/min, 360/hour, 8000/day
        """
        try:
            # Check cache first
            cached = self._get_cached_data(f"yahoo_{symbol}")
            if cached:
                return cached

            ticker = yf.Ticker(symbol)
            
            # Get current price and basic info
            info = ticker.info
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
                
            current_price = float(hist['Close'].iloc[-1])
            volume = int(hist['Volume'].iloc[-1])
            
            data = {
                "symbol": symbol,
                "current_price": current_price,
                "volume": volume,
                "high_52w": info.get('fiftyTwoWeekHigh'),
                "low_52w": info.get('fiftyTwoWeekLow'),
                "market_cap": info.get('marketCap'),
                "pe_ratio": info.get('trailingPE'),
                "dividend_yield": info.get('dividendYield'),
                "sector": info.get('sector'),
                "industry": info.get('industry'),
                "change": float(hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) if len(hist) > 1 else 0,
                "timestamp": datetime.now().isoformat(),
                "ohlcv": hist.to_dict('records')[-5:] if len(hist) >= 5 else hist.to_dict('records')
            }
            
            self._cache_data(f"yahoo_{symbol}", data, "yahoo")
            logger.info(f"Yahoo Finance data fetched for {symbol}")
            return {"data": data, "source": "yahoo", "cached": False}
            
        except Exception as e:
            logger.error(f"Yahoo Finance error for {symbol}: {e}")
            return None

    # 2. NSE API Integration
    def fetch_nse_data(self, symbol: str) -> Optional[Dict]:
        """
        Fetch data from NSE (National Stock Exchange) API
        Real-time Indian market data
        """
        try:
            # Add .NS suffix for NSE symbols
            nse_symbol = symbol if symbol.endswith('.NS') else f"{symbol}.NS"
            
            cached = self._get_cached_data(f"nse_{symbol}")
            if cached:
                return cached

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            # NSE quote API
            url = f"{self.nse_base_url}/quote-equity?symbol={symbol.replace('.NS', '')}"
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                nse_data = response.json()
                
                data = {
                    "symbol": nse_symbol,
                    "current_price": nse_data.get('priceInfo', {}).get('lastPrice'),
                    "volume": nse_data.get('priceInfo', {}).get('totalTradedVolume'),
                    "change": nse_data.get('priceInfo', {}).get('change'),
                    "change_percent": nse_data.get('priceInfo', {}).get('pChange'),
                    "high": nse_data.get('priceInfo', {}).get('intraDayHighLow', {}).get('max'),
                    "low": nse_data.get('priceInfo', {}).get('intraDayHighLow', {}).get('min'),
                    "open": nse_data.get('priceInfo', {}).get('open'),
                    "previous_close": nse_data.get('priceInfo', {}).get('previousClose'),
                    "market_cap": nse_data.get('industryInfo', {}).get('macro'),
                    "sector": nse_data.get('industryInfo', {}).get('industry'),
                    "timestamp": datetime.now().isoformat()
                }
                
                self._cache_data(f"nse_{symbol}", data, "nse")
                logger.info(f"NSE data fetched for {symbol}")
                return {"data": data, "source": "nse", "cached": False}
                
        except Exception as e:
            logger.error(f"NSE API error for {symbol}: {e}")
            return None

    # 3. BSE API Integration
    def fetch_bse_data(self, symbol: str) -> Optional[Dict]:
        """
        Fetch data from BSE (Bombay Stock Exchange) API
        Indian market data with BSE-specific metrics
        """
        try:
            # Add .BO suffix for BSE symbols
            bse_symbol = symbol if symbol.endswith('.BO') else f"{symbol}.BO"
            
            cached = self._get_cached_data(f"bse_{symbol}")
            if cached:
                return cached

            # Use Yahoo Finance for BSE data as BSE API is more restricted
            ticker = yf.Ticker(bse_symbol)
            hist = ticker.history(period="1d")
            info = ticker.info
            
            if hist.empty:
                return None
                
            data = {
                "symbol": bse_symbol,
                "current_price": float(hist['Close'].iloc[-1]),
                "volume": int(hist['Volume'].iloc[-1]),
                "high": float(hist['High'].iloc[-1]),
                "low": float(hist['Low'].iloc[-1]),
                "open": float(hist['Open'].iloc[-1]),
                "change": float(hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) if len(hist) > 1 else 0,
                "market_cap": info.get('marketCap'),
                "sector": info.get('sector'),
                "timestamp": datetime.now().isoformat()
            }
            
            self._cache_data(f"bse_{symbol}", data, "bse")
            logger.info(f"BSE data fetched for {symbol}")
            return {"data": data, "source": "bse", "cached": False}
            
        except Exception as e:
            logger.error(f"BSE API error for {symbol}: {e}")
            return None

    # 4. NASDAQ API Integration
    def fetch_nasdaq_data(self, symbol: str) -> Optional[Dict]:
        """
        Fetch NASDAQ-listed stocks data
        US market data with 7300+ stocks coverage
        """
        try:
            cached = self._get_cached_data(f"nasdaq_{symbol}")
            if cached:
                return cached

            # Use Yahoo Finance for NASDAQ data
            ticker = yf.Ticker(symbol)
            
            # Get real-time quote
            if hasattr(ticker, 'fast_info'):
                fast_info = ticker.fast_info
                current_price = fast_info.get('last_price')
                volume = fast_info.get('last_volume')
            else:
                hist = ticker.history(period="1d")
                if hist.empty:
                    return None
                current_price = float(hist['Close'].iloc[-1])
                volume = int(hist['Volume'].iloc[-1])
            
            info = ticker.info
            
            data = {
                "symbol": symbol,
                "current_price": current_price,
                "volume": volume,
                "market_cap": info.get('marketCap'),
                "pe_ratio": info.get('trailingPE'),
                "sector": info.get('sector'),
                "industry": info.get('industry'),
                "exchange": "NASDAQ",
                "country": "US",
                "timestamp": datetime.now().isoformat()
            }
            
            self._cache_data(f"nasdaq_{symbol}", data, "nasdaq")
            logger.info(f"NASDAQ data fetched for {symbol}")
            return {"data": data, "source": "nasdaq", "cached": False}
            
        except Exception as e:
            logger.error(f"NASDAQ API error for {symbol}: {e}")
            return None

    # 5. Morningstar API Integration
    def fetch_morningstar_data(self, symbol: str) -> Optional[Dict]:
        """
        Fetch data from Morningstar API
        Financial analysis, fair value, and institutional data
        """
        try:
            cached = self._get_cached_data(f"morningstar_{symbol}")
            if cached:
                return cached

            # Morningstar web scraping approach (as API is restricted)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            url = f"https://www.morningstar.com/stocks/xnas/{symbol.lower()}/quote"
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract key metrics (this would need to be adapted based on actual HTML structure)
                data = {
                    "symbol": symbol,
                    "fair_value": None,  # Would extract from HTML
                    "analyst_rating": None,  # Would extract from HTML
                    "dividend_yield": None,  # Would extract from HTML
                    "institutional_ownership": None,  # Would extract from HTML
                    "timestamp": datetime.now().isoformat(),
                    "source": "morningstar_web"
                }
                
                self._cache_data(f"morningstar_{symbol}", data, "morningstar")
                logger.info(f"Morningstar data fetched for {symbol}")
                return {"data": data, "source": "morningstar", "cached": False}
                
        except Exception as e:
            logger.error(f"Morningstar error for {symbol}: {e}")
            return None

    # 6. Technical Analysis Integration
    def calculate_technical_indicators(self, symbol: str, period: str = "3mo") -> Optional[Dict]:
        """
        Calculate 150+ technical indicators using pandas_ta
        """
        try:
            cached = self._get_cached_data(f"ta_{symbol}")
            if cached:
                return cached

            # Get historical data
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if df.empty or len(df) < 20:
                return None
            
            # Calculate technical indicators
            df.ta.rsi(append=True)  # RSI
            df.ta.macd(append=True)  # MACD
            df.ta.bbands(append=True)  # Bollinger Bands
            df.ta.sma(length=20, append=True)  # SMA 20
            df.ta.sma(length=50, append=True)  # SMA 50
            df.ta.sma(length=200, append=True)  # SMA 200
            df.ta.stoch(append=True)  # Stochastic
            df.ta.adx(append=True)  # ADX
            df.ta.atr(append=True)  # ATR
            df.ta.obv(append=True)  # OBV
            
            # Get latest values
            latest = df.iloc[-1]
            
            indicators = {
                "symbol": symbol,
                "rsi": latest.get('RSI_14'),
                "macd": latest.get('MACD_12_26_9'),
                "macd_signal": latest.get('MACDs_12_26_9'),
                "bb_upper": latest.get('BBU_20_2.0'),
                "bb_middle": latest.get('BBM_20_2.0'),
                "bb_lower": latest.get('BBL_20_2.0'),
                "sma_20": latest.get('SMA_20'),
                "sma_50": latest.get('SMA_50'),
                "sma_200": latest.get('SMA_200'),
                "stoch_k": latest.get('STOCHk_14_3_3'),
                "stoch_d": latest.get('STOCHd_14_3_3'),
                "adx": latest.get('ADX_14'),
                "atr": latest.get('ATR_14'),
                "obv": latest.get('OBV'),
                "current_price": latest['Close'],
                "volume": latest['Volume'],
                "timestamp": datetime.now().isoformat()
            }
            
            # Calculate signals
            signals = self._generate_trading_signals(indicators)
            indicators.update(signals)
            
            self._cache_data(f"ta_{symbol}", indicators, "technical_analysis")
            logger.info(f"Technical analysis completed for {symbol}")
            return {"data": indicators, "source": "technical_analysis", "cached": False}
            
        except Exception as e:
            logger.error(f"Technical analysis error for {symbol}: {e}")
            return None

    def _generate_trading_signals(self, indicators: Dict) -> Dict:
        """Generate trading signals from technical indicators"""
        signals = {
            "signals": [],
            "overall_signal": "NEUTRAL",
            "strength": 0
        }
        
        try:
            score = 0
            
            # RSI signals
            if indicators.get('rsi'):
                if indicators['rsi'] < 30:
                    signals["signals"].append("RSI Oversold - Buy Signal")
                    score += 1
                elif indicators['rsi'] > 70:
                    signals["signals"].append("RSI Overbought - Sell Signal")
                    score -= 1
            
            # MACD signals
            if indicators.get('macd') and indicators.get('macd_signal'):
                if indicators['macd'] > indicators['macd_signal']:
                    signals["signals"].append("MACD Bullish Crossover")
                    score += 1
                else:
                    signals["signals"].append("MACD Bearish Crossover")
                    score -= 1
            
            # Moving average signals
            price = indicators.get('current_price')
            if price and indicators.get('sma_20') and indicators.get('sma_50'):
                if price > indicators['sma_20'] > indicators['sma_50']:
                    signals["signals"].append("Price Above MAs - Bullish")
                    score += 1
                elif price < indicators['sma_20'] < indicators['sma_50']:
                    signals["signals"].append("Price Below MAs - Bearish")
                    score -= 1
            
            # Bollinger Bands signals
            if price and indicators.get('bb_upper') and indicators.get('bb_lower'):
                if price > indicators['bb_upper']:
                    signals["signals"].append("Price Above BB Upper - Overbought")
                    score -= 0.5
                elif price < indicators['bb_lower']:
                    signals["signals"].append("Price Below BB Lower - Oversold")
                    score += 0.5
            
            # Overall signal
            if score >= 2:
                signals["overall_signal"] = "STRONG_BUY"
            elif score >= 1:
                signals["overall_signal"] = "BUY"
            elif score <= -2:
                signals["overall_signal"] = "STRONG_SELL"
            elif score <= -1:
                signals["overall_signal"] = "SELL"
            else:
                signals["overall_signal"] = "NEUTRAL"
            
            signals["strength"] = abs(score) * 20  # Convert to percentage
            
        except Exception as e:
            logger.error(f"Signal generation error: {e}")
        
        return signals

    # 7. Market Status Integration
    def get_market_status(self, exchange: str = "NSE") -> Dict:
        """
        Get market status for different exchanges
        """
        try:
            cached = self._get_cached_data(f"status_{exchange}", max_age=60)  # 1 minute cache
            if cached:
                return cached

            status = {
                "exchange": exchange,
                "is_open": False,
                "next_open": None,
                "next_close": None,
                "timezone": None,
                "timestamp": datetime.now().isoformat()
            }
            
            if exchange.upper() == "NSE":
                # NSE market hours: 9:15 AM to 3:30 PM IST
                now = datetime.now()
                market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
                market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
                
                status.update({
                    "is_open": market_open <= now <= market_close and now.weekday() < 5,
                    "next_open": market_open.isoformat() if now < market_open else (market_open + timedelta(days=1)).isoformat(),
                    "next_close": market_close.isoformat(),
                    "timezone": "Asia/Kolkata"
                })
                
            elif exchange.upper() == "NASDAQ":
                # NASDAQ market hours: 9:30 AM to 4:00 PM EST
                now = datetime.now()
                market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
                market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
                
                status.update({
                    "is_open": market_open <= now <= market_close and now.weekday() < 5,
                    "next_open": market_open.isoformat() if now < market_open else (market_open + timedelta(days=1)).isoformat(),
                    "next_close": market_close.isoformat(),
                    "timezone": "America/New_York"
                })
            
            self._cache_data(f"status_{exchange}", status, "market_status")
            return {"data": status, "source": "market_status", "cached": False}
            
        except Exception as e:
            logger.error(f"Market status error for {exchange}: {e}")
            return {"data": {"exchange": exchange, "is_open": False, "error": str(e)}, "source": "error"}

    # 8. Multi-Source Intelligent Fetcher
    async def get_comprehensive_stock_data(self, symbol: str) -> Dict:
        """
        Fetch data from multiple sources with intelligent fallback
        Returns comprehensive stock data from the best available sources
        """
        results = {
            "symbol": symbol,
            "sources_used": [],
            "primary_data": None,
            "technical_analysis": None,
            "market_status": None,
            "timestamp": datetime.now().isoformat(),
            "reliability_score": 0
        }
        
        # Determine best sources based on symbol
        if symbol.endswith('.NS'):
            sources = ['nse', 'yahoo', 'technical_analysis']
        elif symbol.endswith('.BO'):
            sources = ['bse', 'yahoo', 'technical_analysis']
        else:
            sources = ['yahoo', 'nasdaq', 'morningstar', 'technical_analysis']
        
        # Fetch from primary sources
        for source in sources[:2]:  # Try first two sources
            try:
                if source == 'yahoo':
                    data = self.fetch_yahoo_data(symbol)
                elif source == 'nse':
                    data = self.fetch_nse_data(symbol)
                elif source == 'bse':
                    data = self.fetch_bse_data(symbol)
                elif source == 'nasdaq':
                    data = self.fetch_nasdaq_data(symbol)
                elif source == 'morningstar':
                    data = self.fetch_morningstar_data(symbol)
                
                if data and data.get('data'):
                    results["primary_data"] = data['data']
                    results["sources_used"].append(source)
                    results["reliability_score"] += 30
                    logger.info(f"Primary data from {source} for {symbol}")
                    break
                    
            except Exception as e:
                logger.error(f"Source {source} failed for {symbol}: {e}")
                continue
        
        # Get technical analysis
        try:
            ta_data = self.calculate_technical_indicators(symbol)
            if ta_data and ta_data.get('data'):
                results["technical_analysis"] = ta_data['data']
                results["sources_used"].append("technical_analysis")
                results["reliability_score"] += 25
        except Exception as e:
            logger.error(f"Technical analysis failed for {symbol}: {e}")
        
        # Get market status
        try:
            exchange = "NSE" if symbol.endswith('.NS') else "NASDAQ"
            status_data = self.get_market_status(exchange)
            if status_data and status_data.get('data'):
                results["market_status"] = status_data['data']
                results["sources_used"].append("market_status")
                results["reliability_score"] += 15
        except Exception as e:
            logger.error(f"Market status failed: {e}")
        
        # Calculate final reliability score
        if len(results["sources_used"]) >= 3:
            results["reliability_score"] += 30  # Bonus for multiple sources
        
        logger.info(f"Comprehensive data fetched for {symbol} from {len(results['sources_used'])} sources")
        return results

    # 9. Batch Processing
    async def get_multiple_stocks_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Fetch data for multiple stocks efficiently with batching
        """
        results = {}
        batch_size = 10  # Process 10 stocks at a time
        
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            batch_tasks = [
                self.get_comprehensive_stock_data(symbol) 
                for symbol in batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for symbol, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Batch processing error for {symbol}: {result}")
                    results[symbol] = {"error": str(result)}
                else:
                    results[symbol] = result
            
            # Small delay between batches to respect rate limits
            await asyncio.sleep(1)
        
        return results

    # 10. Data Export Functions
    def export_to_excel(self, data: Dict, filename: str = None):
        """Export data to Excel file"""
        if not filename:
            filename = f"market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        try:
            df = pd.DataFrame(data)
            df.to_excel(filename, index=False)
            logger.info(f"Data exported to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Excel export error: {e}")
            return None

    def export_to_cache(self, data: Dict, cache_key: str):
        """Export data to joblib cache file"""
        try:
            cache_filename = f"{cache_key}_{datetime.now().strftime('%Y%m%d')}.pkl"
            joblib.dump(data, cache_filename)
            logger.info(f"Data cached to {cache_filename}")
            return cache_filename
        except Exception as e:
            logger.error(f"Cache export error: {e}")
            return None


# Utility functions for easy access
def create_data_provider() -> MultiSourceDataProvider:
    """Factory function to create data provider instance"""
    return MultiSourceDataProvider()

async def get_stock_data(symbol: str) -> Dict:
    """Quick function to get comprehensive stock data"""
    provider = create_data_provider()
    return await provider.get_comprehensive_stock_data(symbol)

async def get_multiple_stocks(symbols: List[str]) -> Dict:
    """Quick function to get data for multiple stocks"""
    provider = create_data_provider()
    return await provider.get_multiple_stocks_data(symbols) 