"""
Simplified Multi-Source Financial Data Provider
==============================================

Essential multi-source data integration using only core dependencies
for immediate deployment and testing.
"""

import yfinance as yf
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import sqlite3
import json
from typing import Dict, List, Optional, Any, Tuple
import time
import os
import threading

logger = logging.getLogger(__name__)

class EnhancedCacheSystem:
    """
    Enhanced cache system with better performance and features
    """
    
    def __init__(self, cache_file: str = "enhanced_market_cache.db", max_size_mb: int = 100):
        self.cache_file = cache_file
        self.max_size_mb = max_size_mb
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self._lock = threading.Lock()
        self._init_cache_db()

    def _init_cache_db(self):
        """Initialize enhanced SQLite cache with better schema"""
        try:
            with self._lock:
                conn = sqlite3.connect(self.cache_file)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS enhanced_cache (
                        key TEXT PRIMARY KEY,
                        data TEXT NOT NULL,
                        timestamp REAL NOT NULL,
                        access_count INTEGER DEFAULT 1,
                        last_accessed REAL NOT NULL,
                        data_size INTEGER NOT NULL,
                        category TEXT DEFAULT 'general',
                        expires_at REAL
                    )
                """)
                
                # Create indexes for better performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON enhanced_cache(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_expires_at ON enhanced_cache(expires_at)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON enhanced_cache(category)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON enhanced_cache(last_accessed)")
                
                conn.commit()
                conn.close()
                
                # Clean up expired entries on startup
                self._cleanup_expired()
                
        except Exception as e:
            logger.error(f"Enhanced cache init error: {e}")

    def get(self, key: str, max_age: int = 300) -> Optional[Dict]:
        """Get cached data with enhanced tracking"""
        try:
            with self._lock:
                conn = sqlite3.connect(self.cache_file)
                cursor = conn.execute("""
                    SELECT data, timestamp, expires_at, access_count 
                    FROM enhanced_cache 
                    WHERE key = ?
                """, (key,))
                row = cursor.fetchone()
                
                if row:
                    data, timestamp, expires_at, access_count = row
                    current_time = time.time()
                    
                    # Check if data is still valid
                    is_valid = True
                    if expires_at and current_time > expires_at:
                        is_valid = False
                    elif current_time - timestamp > max_age:
                        is_valid = False
                    
                    if is_valid:
                        # Update access statistics
                        conn.execute("""
                            UPDATE enhanced_cache 
                            SET access_count = access_count + 1, last_accessed = ? 
                            WHERE key = ?
                        """, (current_time, key))
                        conn.commit()
                        conn.close()
                        
                        try:
                            parsed_data = json.loads(data)
                            parsed_data["_cache_hit"] = True
                            parsed_data["_access_count"] = access_count + 1
                            return parsed_data
                        except json.JSONDecodeError:
                            logger.error(f"JSON decode error for key: {key}")
                            return None
                    else:
                        # Remove expired data
                        conn.execute("DELETE FROM enhanced_cache WHERE key = ?", (key,))
                        conn.commit()
                
                conn.close()
                return None
                
        except Exception as e:
            logger.error(f"Cache get error for {key}: {e}")
            return None

    def set(self, key: str, data: Dict, category: str = "general", ttl: Optional[int] = None):
        """Set cached data with enhanced features"""
        try:
            json_data = json.dumps(data)
            data_size = len(json_data.encode('utf-8'))
            current_time = time.time()
            expires_at = current_time + ttl if ttl else None
            
            with self._lock:
                conn = sqlite3.connect(self.cache_file)
                
                # Check if we need to make space
                self._ensure_cache_size(conn, data_size)
                
                conn.execute("""
                    INSERT OR REPLACE INTO enhanced_cache 
                    (key, data, timestamp, last_accessed, data_size, category, expires_at, access_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """, (key, json_data, current_time, current_time, data_size, category, expires_at))
                
                conn.commit()
                conn.close()
                
        except Exception as e:
            logger.error(f"Cache set error for {key}: {e}")

    def _ensure_cache_size(self, conn: sqlite3.Connection, new_data_size: int):
        """Ensure cache doesn't exceed size limits"""
        try:
            # Get current cache size
            cursor = conn.execute("SELECT SUM(data_size) FROM enhanced_cache")
            current_size = cursor.fetchone()[0] or 0
            
            # If adding new data would exceed limit, remove oldest least-accessed items
            if current_size + new_data_size > self.max_size_bytes:
                target_size = self.max_size_bytes * 0.8  # Remove to 80% capacity
                
                # Get items sorted by last_accessed (oldest first)
                cursor = conn.execute("""
                    SELECT key, data_size FROM enhanced_cache 
                    ORDER BY last_accessed ASC
                """)
                
                removed_size = 0
                for key, size in cursor.fetchall():
                    if current_size - removed_size <= target_size:
                        break
                    
                    conn.execute("DELETE FROM enhanced_cache WHERE key = ?", (key,))
                    removed_size += size
                    logger.info(f"Removed cache entry {key} to free space")
                
        except Exception as e:
            logger.error(f"Cache size management error: {e}")

    def _cleanup_expired(self):
        """Remove expired cache entries"""
        try:
            with self._lock:
                conn = sqlite3.connect(self.cache_file)
                current_time = time.time()
                
                cursor = conn.execute("""
                    DELETE FROM enhanced_cache 
                    WHERE expires_at IS NOT NULL AND expires_at < ?
                """, (current_time,))
                
                deleted_count = cursor.rowcount
                conn.commit()
                conn.close()
                
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} expired cache entries")
                    
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")

    def invalidate(self, key_pattern: str = None, category: str = None):
        """Invalidate cache entries by pattern or category"""
        try:
            with self._lock:
                conn = sqlite3.connect(self.cache_file)
                
                if key_pattern:
                    cursor = conn.execute("""
                        DELETE FROM enhanced_cache 
                        WHERE key LIKE ?
                    """, (f"%{key_pattern}%",))
                elif category:
                    cursor = conn.execute("""
                        DELETE FROM enhanced_cache 
                        WHERE category = ?
                    """, (category,))
                else:
                    cursor = conn.execute("DELETE FROM enhanced_cache")
                
                deleted_count = cursor.rowcount
                conn.commit()
                conn.close()
                
                logger.info(f"Invalidated {deleted_count} cache entries")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return 0

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        try:
            with self._lock:
                conn = sqlite3.connect(self.cache_file)
                
                # Basic stats
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_entries,
                        SUM(data_size) as total_size,
                        AVG(access_count) as avg_access_count,
                        MAX(access_count) as max_access_count,
                        COUNT(DISTINCT category) as categories_count
                    FROM enhanced_cache
                """)
                
                stats = cursor.fetchone()
                
                # Category breakdown
                cursor = conn.execute("""
                    SELECT category, COUNT(*), SUM(data_size)
                    FROM enhanced_cache
                    GROUP BY category
                """)
                
                categories = {row[0]: {"count": row[1], "size": row[2]} for row in cursor.fetchall()}
                
                conn.close()
                
                return {
                    "total_entries": stats[0] or 0,
                    "total_size_bytes": stats[1] or 0,
                    "total_size_mb": round((stats[1] or 0) / (1024 * 1024), 2),
                    "avg_access_count": round(stats[2] or 0, 2),
                    "max_access_count": stats[3] or 0,
                    "categories_count": stats[4] or 0,
                    "categories": categories,
                    "cache_file": self.cache_file,
                    "max_size_mb": self.max_size_mb,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"error": str(e)}

    def clear_all(self):
        """Clear all cache entries"""
        return self.invalidate()

    def get_file_size(self) -> Tuple[int, str]:
        """Get cache file size"""
        try:
            if os.path.exists(self.cache_file):
                size_bytes = os.path.getsize(self.cache_file)
                size_mb = round(size_bytes / (1024 * 1024), 2)
                return size_bytes, f"{size_mb} MB"
            return 0, "0 MB"
        except Exception as e:
            logger.error(f"Error getting cache file size: {e}")
            return 0, "Error"

class SimplifiedDataProvider:
    """
    Simplified financial data provider with enhanced multi-source fallback
    using only core dependencies that are already available.
    """
    
    def __init__(self):
        self.cache = EnhancedCacheSystem()
        
        # API endpoints and keys
        self.finnhub_base = "https://finnhub.io/api/v1"
        self.alpha_vantage_base = "https://www.alphavantage.co/query"
        self.alpha_vantage_key = "22TNS9NWXVD5CPVF"  # Your new Alpha Vantage key
        self.iex_base = "https://cloud.iexapis.com/stable"
        self.polygon_base = "https://api.polygon.io/v2"
        self.fmp_base = "https://financialmodelingprep.com/api/v3"
        self.twelve_data_base = "https://api.twelvedata.com"
        self.yahoo_query_base = "https://query1.finance.yahoo.com/v8/finance/chart"
        
        # Google Finance alternatives
        self.marketstack_base = "http://api.marketstack.com/v1"
        self.quandl_base = "https://www.quandl.com/api/v3"
        self.tiingo_base = "https://api.tiingo.com/tiingo"
        self.worldtradingdata_base = "https://api.worldtradingdata.com/api/v1"
        
        # API keys - Updated with your real keys
        self.api_keys = {
            "alpha_vantage": self.alpha_vantage_key,
            "iex": "demo",  # Free tier available
            "polygon": "SavZMeuTDTxjWJuFzBO6zES7mBFK68RJ",  # Your Polygon.io key
            "fmp": "demo",  # Free tier available
            "twelve_data": "demo",  # Free tier available
            "finnhub": "d16k039r01qvtdbj2gtgd16k039r01qvtdbj2gu0",  # Your Finnhub key
            
            # Google Finance alternatives (free tiers available)
            "marketstack": "demo",  # Free tier: 1000 requests/month
            "quandl": "demo",  # Free tier available
            "tiingo": "demo",  # Free tier: 500 requests/day
            "worldtradingdata": "demo"  # Free tier available
        }
        
        # Simple rate limiting using time tracking
        self.last_request_time = {}
        self.min_interval = 1.0  # 1 second between requests
        
        # API priority order (best to worst)
        self.api_priority = [
            "yahoo",
            "alpha_vantage", 
            "polygon",
            "iex",
            "tiingo",
            "twelve_data",
            "fmp",
            "marketstack",
            "finnhub"
        ]
        
        logger.info("Multi-source data provider initialized with 9 APIs (including Google Finance alternatives) and enhanced cache")

    def _rate_limit(self, source: str):
        """Simple rate limiting"""
        if source in self.last_request_time:
            elapsed = time.time() - self.last_request_time[source]
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
        self.last_request_time[source] = time.time()

    def fetch_yahoo_data(self, symbol: str) -> Optional[Dict]:
        """Fetch data from Yahoo Finance (primary source)"""
        try:
            # Check cache first
            cached = self.cache.get(f"yahoo_{symbol}", max_age=300)
            if cached:
                return cached

            self._rate_limit("yahoo")
            
            ticker = yf.Ticker(symbol)
            
            # Get basic info first
            try:
                info = ticker.info
            except:
                info = {}
            
            # Get historical data
            hist = ticker.history(period="5d")
            if hist.empty:
                return None
                
            current_price = float(hist['Close'].iloc[-1])
            volume = int(hist['Volume'].iloc[-1])
            
            # Calculate change
            if len(hist) > 1:
                prev_close = float(hist['Close'].iloc[-2])
                change = current_price - prev_close
                change_percent = (change / prev_close) * 100
            else:
                change = 0
                change_percent = 0
            
            data = {
                "symbol": symbol,
                "current_price": round(current_price, 2),
                "volume": volume,
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "high": round(float(hist['High'].iloc[-1]), 2),
                "low": round(float(hist['Low'].iloc[-1]), 2),
                "open": round(float(hist['Open'].iloc[-1]), 2),
                "market_cap": info.get('marketCap'),
                "pe_ratio": info.get('trailingPE'),
                "sector": info.get('sector', 'Unknown'),
                "industry": info.get('industry', 'Unknown'),
                "timestamp": datetime.now().isoformat(),
                "source": "yahoo"
            }
            
            # Cache the data with 5 minute TTL
            self.cache.set(f"yahoo_{symbol}", data, category="stock_data", ttl=300)
            
            logger.info(f"Yahoo data fetched for {symbol}: ${current_price}")
            return data
            
        except Exception as e:
            logger.error(f"Yahoo error for {symbol}: {e}")
            return None

    def fetch_alpha_vantage_data(self, symbol: str) -> Optional[Dict]:
        """Fetch data from Alpha Vantage"""
        try:
            cached = self.cache.get(f"alpha_vantage_{symbol}", max_age=300)
            if cached:
                return cached

            self._rate_limit("alpha_vantage")
            
            url = self.alpha_vantage_base
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_keys["alpha_vantage"]
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data_json = response.json()
                quote_data = data_json.get("Global Quote", {})
                
                if quote_data and quote_data.get("05. price"):
                    current_price = float(quote_data["05. price"])
                    change = float(quote_data.get("09. change", 0))
                    change_percent = float(quote_data.get("10. change percent", "0%").replace("%", ""))
                    
                    data = {
                        "symbol": symbol,
                        "current_price": round(current_price, 2),
                        "volume": int(quote_data.get("06. volume", 0)) if quote_data.get("06. volume") else None,
                        "change": round(change, 2),
                        "change_percent": round(change_percent, 2),
                        "high": round(float(quote_data.get("03. high", 0)), 2),
                        "low": round(float(quote_data.get("04. low", 0)), 2),
                        "open": round(float(quote_data.get("02. open", 0)), 2),
                        "previous_close": round(float(quote_data.get("08. previous close", 0)), 2),
                        "timestamp": datetime.now().isoformat(),
                        "source": "alpha_vantage"
                    }
                    
                    self.cache.set(f"alpha_vantage_{symbol}", data, category="stock_data", ttl=300)
                    logger.info(f"Alpha Vantage data fetched for {symbol}: ${current_price}")
                    return data
                    
        except Exception as e:
            logger.error(f"Alpha Vantage error for {symbol}: {e}")
            return None

    def fetch_iex_data(self, symbol: str) -> Optional[Dict]:
        """Fetch data from IEX Cloud"""
        try:
            cached = self.cache.get(f"iex_{symbol}", max_age=300)
            if cached:
                return cached

            self._rate_limit("iex")
            
            url = f"{self.iex_base}/stock/{symbol}/quote"
            params = {"token": self.api_keys["iex"]}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                quote_data = response.json()
                
                if quote_data.get('latestPrice'):
                    data = {
                        "symbol": symbol,
                        "current_price": round(float(quote_data['latestPrice']), 2),
                        "volume": int(quote_data.get('latestVolume', 0)) if quote_data.get('latestVolume') else None,
                        "change": round(float(quote_data.get('change', 0)), 2),
                        "change_percent": round(float(quote_data.get('changePercent', 0)) * 100, 2),
                        "high": round(float(quote_data.get('high', 0)), 2),
                        "low": round(float(quote_data.get('low', 0)), 2),
                        "open": round(float(quote_data.get('open', 0)), 2),
                        "previous_close": round(float(quote_data.get('previousClose', 0)), 2),
                        "market_cap": quote_data.get('marketCap'),
                        "pe_ratio": quote_data.get('peRatio'),
                        "timestamp": datetime.now().isoformat(),
                        "source": "iex"
                    }
                    
                    self.cache.set(f"iex_{symbol}", data, category="stock_data", ttl=300)
                    logger.info(f"IEX data fetched for {symbol}: ${data['current_price']}")
                    return data
                    
        except Exception as e:
            logger.error(f"IEX error for {symbol}: {e}")
            return None

    def fetch_twelve_data(self, symbol: str) -> Optional[Dict]:
        """Fetch data from Twelve Data"""
        try:
            cached = self.cache.get(f"twelve_data_{symbol}", max_age=300)
            if cached:
                return cached

            self._rate_limit("twelve_data")
            
            url = f"{self.twelve_data_base}/price"
            params = {
                "symbol": symbol,
                "apikey": self.api_keys["twelve_data"]
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data_json = response.json()
                
                if data_json.get('price'):
                    # Get additional quote data
                    quote_url = f"{self.twelve_data_base}/quote"
                    quote_response = requests.get(quote_url, params=params, timeout=10)
                    quote_data = quote_response.json() if quote_response.status_code == 200 else {}
                    
                    current_price = float(data_json['price'])
                    
                    data = {
                        "symbol": symbol,
                        "current_price": round(current_price, 2),
                        "volume": int(quote_data.get('volume', 0)) if quote_data.get('volume') else None,
                        "change": round(float(quote_data.get('change', 0)), 2),
                        "change_percent": round(float(quote_data.get('percent_change', 0)), 2),
                        "high": round(float(quote_data.get('high', 0)), 2),
                        "low": round(float(quote_data.get('low', 0)), 2),
                        "open": round(float(quote_data.get('open', 0)), 2),
                        "previous_close": round(float(quote_data.get('previous_close', 0)), 2),
                        "timestamp": datetime.now().isoformat(),
                        "source": "twelve_data"
                    }
                    
                    self.cache.set(f"twelve_data_{symbol}", data, category="stock_data", ttl=300)
                    logger.info(f"Twelve Data fetched for {symbol}: ${current_price}")
                    return data
                    
        except Exception as e:
            logger.error(f"Twelve Data error for {symbol}: {e}")
            return None

    def fetch_fmp_data(self, symbol: str) -> Optional[Dict]:
        """Fetch data from Financial Modeling Prep"""
        try:
            cached = self.cache.get(f"fmp_{symbol}", max_age=300)
            if cached:
                return cached

            self._rate_limit("fmp")
            
            url = f"{self.fmp_base}/quote/{symbol}"
            params = {"apikey": self.api_keys["fmp"]}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data_json = response.json()
                
                if data_json and isinstance(data_json, list) and len(data_json) > 0:
                    quote_data = data_json[0]
                    
                    data = {
                        "symbol": symbol,
                        "current_price": round(float(quote_data.get('price', 0)), 2),
                        "volume": int(quote_data.get('volume', 0)) if quote_data.get('volume') else None,
                        "change": round(float(quote_data.get('change', 0)), 2),
                        "change_percent": round(float(quote_data.get('changesPercentage', 0)), 2),
                        "high": round(float(quote_data.get('dayHigh', 0)), 2),
                        "low": round(float(quote_data.get('dayLow', 0)), 2),
                        "open": round(float(quote_data.get('open', 0)), 2),
                        "previous_close": round(float(quote_data.get('previousClose', 0)), 2),
                        "market_cap": quote_data.get('marketCap'),
                        "pe_ratio": quote_data.get('pe'),
                        "timestamp": datetime.now().isoformat(),
                        "source": "fmp"
                    }
                    
                    self.cache.set(f"fmp_{symbol}", data, category="stock_data", ttl=300)
                    logger.info(f"FMP data fetched for {symbol}: ${data['current_price']}")
                    return data
                    
        except Exception as e:
            logger.error(f"FMP error for {symbol}: {e}")
            return None

    def fetch_polygon_data(self, symbol: str) -> Optional[Dict]:
        """Fetch data from Polygon.io"""
        try:
            cached = self.cache.get(f"polygon_{symbol}", max_age=300)
            if cached:
                return cached

            self._rate_limit("polygon")
            
            # Get previous business day data
            from datetime import datetime, timedelta
            yesterday = datetime.now() - timedelta(days=1)
            date_str = yesterday.strftime('%Y-%m-%d')
            
            url = f"{self.polygon_base}/aggs/ticker/{symbol}/range/1/day/{date_str}/{date_str}"
            params = {"apikey": self.api_keys["polygon"]}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data_json = response.json()
                
                if data_json.get('results') and len(data_json['results']) > 0:
                    result = data_json['results'][0]
                    
                    current_price = float(result.get('c', 0))  # close price
                    open_price = float(result.get('o', 0))
                    change = current_price - open_price
                    change_percent = (change / open_price * 100) if open_price > 0 else 0
                    
                    data = {
                        "symbol": symbol,
                        "current_price": round(current_price, 2),
                        "volume": int(result.get('v', 0)) if result.get('v') else None,
                        "change": round(change, 2),
                        "change_percent": round(change_percent, 2),
                        "high": round(float(result.get('h', 0)), 2),
                        "low": round(float(result.get('l', 0)), 2),
                        "open": round(float(result.get('o', 0)), 2),
                        "timestamp": datetime.now().isoformat(),
                        "source": "polygon"
                    }
                    
                    self.cache.set(f"polygon_{symbol}", data, category="stock_data", ttl=300)
                    logger.info(f"Polygon data fetched for {symbol}: ${current_price}")
                    return data
                    
        except Exception as e:
            logger.error(f"Polygon error for {symbol}: {e}")
            return None

    def fetch_finnhub_data(self, symbol: str) -> Optional[Dict]:
        """Fetch data from Finnhub (fallback source)"""
        try:
            cached = self.cache.get(f"finnhub_{symbol}", max_age=300)
            if cached:
                return cached

            self._rate_limit("finnhub")
            
            # Finnhub API with your key
            url = f"{self.finnhub_base}/quote"
            params = {"symbol": symbol, "token": self.api_keys["finnhub"]}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                quote_data = response.json()
                
                if quote_data.get('c') and quote_data.get('c') > 0:
                    data = {
                        "symbol": symbol,
                        "current_price": round(float(quote_data['c']), 2),
                        "volume": None,
                        "change": round(float(quote_data.get('d', 0)), 2),
                        "change_percent": round(float(quote_data.get('dp', 0)), 2),
                        "high": round(float(quote_data.get('h', 0)), 2),
                        "low": round(float(quote_data.get('l', 0)), 2),
                        "open": round(float(quote_data.get('o', 0)), 2),
                        "previous_close": round(float(quote_data.get('pc', 0)), 2),
                        "timestamp": datetime.now().isoformat(),
                        "source": "finnhub"
                    }
                    
                    self.cache.set(f"finnhub_{symbol}", data, category="stock_data", ttl=300)
                    logger.info(f"Finnhub data fetched for {symbol}: ${data['current_price']}")
                    return data
                    
        except Exception as e:
            logger.error(f"Finnhub error for {symbol}: {e}")
            return None

    def fetch_tiingo_data(self, symbol: str) -> Optional[Dict]:
        """Fetch data from Tiingo (Google Finance alternative)"""
        try:
            cached = self.cache.get(f"tiingo_{symbol}", max_age=300)
            if cached:
                return cached

            self._rate_limit("tiingo")
            
            # Tiingo daily prices endpoint
            url = f"{self.tiingo_base}/daily/{symbol}/prices"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Token {self.api_keys["tiingo"]}'
            }
            params = {"format": "json"}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data_json = response.json()
                
                if data_json and len(data_json) > 0:
                    latest = data_json[-1]  # Most recent data
                    
                    current_price = float(latest.get('close', 0))
                    open_price = float(latest.get('open', 0))
                    change = current_price - open_price
                    change_percent = (change / open_price * 100) if open_price > 0 else 0
                    
                    data = {
                        "symbol": symbol,
                        "current_price": round(current_price, 2),
                        "volume": int(latest.get('volume', 0)) if latest.get('volume') else None,
                        "change": round(change, 2),
                        "change_percent": round(change_percent, 2),
                        "high": round(float(latest.get('high', 0)), 2),
                        "low": round(float(latest.get('low', 0)), 2),
                        "open": round(open_price, 2),
                        "date": latest.get('date'),
                        "timestamp": datetime.now().isoformat(),
                        "source": "tiingo"
                    }
                    
                    self.cache.set(f"tiingo_{symbol}", data, category="stock_data", ttl=300)
                    logger.info(f"Tiingo data fetched for {symbol}: ${current_price}")
                    return data
                    
        except Exception as e:
            logger.error(f"Tiingo error for {symbol}: {e}")
            return None

    def fetch_marketstack_data(self, symbol: str) -> Optional[Dict]:
        """Fetch data from Marketstack (Google Finance alternative)"""
        try:
            cached = self.cache.get(f"marketstack_{symbol}", max_age=300)
            if cached:
                return cached

            self._rate_limit("marketstack")
            
            # Marketstack latest endpoint
            url = f"{self.marketstack_base}/eod/latest"
            params = {
                "access_key": self.api_keys["marketstack"],
                "symbols": symbol
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data_json = response.json()
                
                if data_json.get('data') and len(data_json['data']) > 0:
                    stock_data = data_json['data'][0]
                    
                    current_price = float(stock_data.get('close', 0))
                    open_price = float(stock_data.get('open', 0))
                    change = current_price - open_price
                    change_percent = (change / open_price * 100) if open_price > 0 else 0
                    
                    data = {
                        "symbol": symbol,
                        "current_price": round(current_price, 2),
                        "volume": int(stock_data.get('volume', 0)) if stock_data.get('volume') else None,
                        "change": round(change, 2),
                        "change_percent": round(change_percent, 2),
                        "high": round(float(stock_data.get('high', 0)), 2),
                        "low": round(float(stock_data.get('low', 0)), 2),
                        "open": round(open_price, 2),
                        "date": stock_data.get('date'),
                        "timestamp": datetime.now().isoformat(),
                        "source": "marketstack"
                    }
                    
                    self.cache.set(f"marketstack_{symbol}", data, category="stock_data", ttl=300)
                    logger.info(f"Marketstack data fetched for {symbol}: ${current_price}")
                    return data
                    
        except Exception as e:
            logger.error(f"Marketstack error for {symbol}: {e}")
            return None

    def get_comprehensive_stock_data(self, symbol: str) -> Dict:
        """
        Get stock data with intelligent fallback between all sources
        """
        result = {
            "symbol": symbol,
            "primary_data": None,
            "fallback_data": [],
            "sources_used": [],
            "sources_failed": [],
            "reliability_score": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        # API fetch methods mapping
        api_methods = {
            "yahoo": self.fetch_yahoo_data,
            "alpha_vantage": self.fetch_alpha_vantage_data,
            "polygon": self.fetch_polygon_data,
            "iex": self.fetch_iex_data,
            "tiingo": self.fetch_tiingo_data,
            "twelve_data": self.fetch_twelve_data,
            "fmp": self.fetch_fmp_data,
            "marketstack": self.fetch_marketstack_data,
            "finnhub": self.fetch_finnhub_data
        }
        
        # Try each API in priority order
        for api_name in self.api_priority:
            try:
                if api_name in api_methods:
                    data = api_methods[api_name](symbol)
                    if data:
                        if result["primary_data"] is None:
                            # First successful API becomes primary
                            result["primary_data"] = data
                            result["sources_used"].append(api_name)
                            
                            # Score based on API quality and cache status
                            if api_name == "yahoo":
                                result["reliability_score"] += 50
                            elif api_name == "alpha_vantage":
                                result["reliability_score"] += 45
                            elif api_name == "iex":
                                result["reliability_score"] += 40
                            elif api_name == "twelve_data":
                                result["reliability_score"] += 35
                            elif api_name == "fmp":
                                result["reliability_score"] += 30
                            elif api_name == "polygon":
                                result["reliability_score"] += 25
                            else:
                                result["reliability_score"] += 20
                            
                            # Bonus for fresh data
                            if not data.get("_cache_hit"):
                                result["reliability_score"] += 15
                        else:
                            # Additional sources for validation
                            result["fallback_data"].append(data)
                            result["sources_used"].append(api_name)
                            result["reliability_score"] += 5
                    else:
                        result["sources_failed"].append(api_name)
                        
            except Exception as e:
                logger.error(f"Error with {api_name} for {symbol}: {e}")
                result["sources_failed"].append(api_name)
        
        # Add cross-validation if multiple sources available
        if len(result["fallback_data"]) > 0 and result["primary_data"]:
            result["cross_validation"] = self._cross_validate_data(
                result["primary_data"], result["fallback_data"]
            )
            if result["cross_validation"]["confidence"] > 0.8:
                result["reliability_score"] += 10
        
        # Add market status
        try:
            market_status = self.get_market_status("NASDAQ" if not symbol.endswith(('.NS', '.BO')) else "NSE")
            result["market_status"] = market_status
            result["reliability_score"] += 5
        except:
            pass
        
        # Summary
        result["summary"] = {
            "total_sources_tried": len(self.api_priority),
            "successful_sources": len(result["sources_used"]),
            "failed_sources": len(result["sources_failed"]),
            "has_primary_data": result["primary_data"] is not None,
            "has_fallback_data": len(result["fallback_data"]) > 0
        }
        
        logger.info(f"Multi-API data for {symbol}: {len(result['sources_used'])}/{len(self.api_priority)} sources successful, score: {result['reliability_score']}")
        return result

    def _cross_validate_data(self, primary: Dict, fallback_list: List[Dict]) -> Dict:
        """Cross-validate data from multiple sources"""
        if not fallback_list:
            return {"confidence": 0.5, "validation": "no_fallback"}
        
        primary_price = primary.get("current_price", 0)
        if primary_price == 0:
            return {"confidence": 0.3, "validation": "no_primary_price"}
        
        # Compare prices from different sources
        price_differences = []
        for fallback in fallback_list:
            fallback_price = fallback.get("current_price", 0)
            if fallback_price > 0:
                diff_percent = abs(primary_price - fallback_price) / primary_price * 100
                price_differences.append(diff_percent)
        
        if not price_differences:
            return {"confidence": 0.4, "validation": "no_comparable_prices"}
        
        avg_difference = sum(price_differences) / len(price_differences)
        max_difference = max(price_differences)
        
        # Calculate confidence based on price agreement
        if avg_difference < 1.0:  # Less than 1% average difference
            confidence = 0.95
        elif avg_difference < 2.0:  # Less than 2% average difference
            confidence = 0.85
        elif avg_difference < 5.0:  # Less than 5% average difference
            confidence = 0.70
        else:
            confidence = 0.50
        
        return {
            "confidence": confidence,
            "validation": "cross_validated",
            "avg_price_difference_percent": round(avg_difference, 2),
            "max_price_difference_percent": round(max_difference, 2),
            "sources_compared": len(price_differences)
        }

    def get_multiple_stocks_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get data for multiple stocks with batching"""
        results = {}
        
        for i, symbol in enumerate(symbols):
            try:
                result = self.get_comprehensive_stock_data(symbol)
                results[symbol] = result
                
                # Small delay between requests to be respectful
                if i < len(symbols) - 1:
                    time.sleep(0.5)
                    
            except Exception as e:
                logger.error(f"Batch error for {symbol}: {e}")
                results[symbol] = {"error": str(e)}
        
        return results

    def calculate_simple_technical_indicators(self, symbol: str) -> Optional[Dict]:
        """Calculate basic technical indicators using pandas"""
        try:
            cached = self.cache.get(f"tech_{symbol}", max_age=300)
            if cached:
                return cached
            
            # Get historical data
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="3mo")
            
            if df.empty or len(df) < 20:
                return None
            
            # Calculate basic indicators manually
            close = df['Close']
            
            # Simple Moving Averages
            sma_20 = close.rolling(window=20).mean().iloc[-1]
            sma_50 = close.rolling(window=50).mean().iloc[-1] if len(df) >= 50 else None
            
            # RSI calculation (simplified)
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # Volume analysis
            volume = df['Volume']
            avg_volume = volume.rolling(window=20).mean().iloc[-1]
            volume_ratio = volume.iloc[-1] / avg_volume if avg_volume > 0 else 1
            
            # Price position analysis
            current_price = close.iloc[-1]
            high_52w = close.rolling(window=252).max().iloc[-1] if len(df) >= 252 else close.max()
            low_52w = close.rolling(window=252).min().iloc[-1] if len(df) >= 252 else close.min()
            
            indicators = {
                "symbol": symbol,
                "current_price": round(float(current_price), 2),
                "rsi": round(float(rsi.iloc[-1]), 2) if not pd.isna(rsi.iloc[-1]) else None,
                "sma_20": round(float(sma_20), 2) if not pd.isna(sma_20) else None,
                "sma_50": round(float(sma_50), 2) if sma_50 and not pd.isna(sma_50) else None,
                "volume_ratio": round(float(volume_ratio), 2),
                "high_52w": round(float(high_52w), 2),
                "low_52w": round(float(low_52w), 2),
                "price_position": round(((current_price - low_52w) / (high_52w - low_52w)) * 100, 1) if high_52w > low_52w else 50,
                "timestamp": datetime.now().isoformat()
            }
            
            # Generate simple signals
            signals = []
            if indicators["rsi"]:
                if indicators["rsi"] < 30:
                    signals.append("RSI Oversold")
                elif indicators["rsi"] > 70:
                    signals.append("RSI Overbought")
            
            if indicators["sma_20"] and current_price > indicators["sma_20"]:
                signals.append("Above SMA 20")
            
            if indicators["volume_ratio"] > 1.5:
                signals.append("High Volume")
            
            indicators["signals"] = signals
            indicators["signal_count"] = len(signals)
            
            self.cache.set(f"tech_{symbol}", indicators, category="technical_analysis", ttl=300)
            logger.info(f"Technical analysis for {symbol}: {len(signals)} signals")
            return indicators
            
        except Exception as e:
            logger.error(f"Technical analysis error for {symbol}: {e}")
            return None

    def get_market_status(self, exchange: str = "NASDAQ") -> Dict:
        """Get basic market status"""
        now = datetime.now()
        
        if exchange.upper() == "NASDAQ":
            # NASDAQ hours: 9:30 AM - 4:00 PM EST
            market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
            timezone = "EST"
        elif exchange.upper() == "NSE":
            # NSE hours: 9:15 AM - 3:30 PM IST  
            market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
            market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
            timezone = "IST"
        else:
            # Default to NASDAQ
            market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
            timezone = "EST"
        
        is_weekend = now.weekday() >= 5  # Saturday = 5, Sunday = 6
        is_market_hours = market_open <= now <= market_close
        is_open = is_market_hours and not is_weekend
        
        return {
            "exchange": exchange.upper(),
            "is_open": is_open,
            "is_weekend": is_weekend,
            "current_time": now.isoformat(),
            "market_open": market_open.time().isoformat(),
            "market_close": market_close.time().isoformat(),
            "timezone": timezone,
            "timestamp": datetime.now().isoformat()
        }

    def get_cache_stats(self) -> Dict:
        """Get detailed cache statistics"""
        return self.cache.get_stats()

    def clear_cache(self, category: str = None, pattern: str = None) -> int:
        """Clear cache entries by category or pattern"""
        if category:
            return self.cache.invalidate(category=category)
        elif pattern:
            return self.cache.invalidate(key_pattern=pattern)
        else:
            return self.cache.clear_all()

    def cleanup_expired_cache(self):
        """Manually trigger cache cleanup"""
        self.cache._cleanup_expired()

# Enhanced utility functions
def create_simple_provider() -> SimplifiedDataProvider:
    """Factory function to create simplified provider with enhanced cache"""
    return SimplifiedDataProvider()

def get_stock_data(symbol: str) -> Dict:
    """Quick function to get stock data"""
    provider = create_simple_provider()
    return provider.get_comprehensive_stock_data(symbol)

def get_multiple_stocks(symbols: List[str]) -> Dict:
    """Quick function to get multiple stocks data"""
    provider = create_simple_provider()
    return provider.get_multiple_stocks_data(symbols) 

def get_cache_info() -> Dict:
    """Quick function to get cache statistics"""
    provider = create_simple_provider()
    return provider.get_cache_stats()

def clear_all_cache() -> int:
    """Quick function to clear all cache"""
    provider = create_simple_provider()
    return provider.clear_cache()

def clear_stock_cache() -> int:
    """Quick function to clear only stock data cache"""
    provider = create_simple_provider()
    return provider.clear_cache(category="stock_data")

def clear_technical_cache() -> int:
    """Quick function to clear only technical analysis cache"""
    provider = create_simple_provider()
    return provider.clear_cache(category="technical_analysis")

def test_all_apis(symbol: str = "AAPL") -> Dict:
    """Test all APIs individually to check their status"""
    provider = create_simple_provider()
    results = {
        "symbol": symbol,
        "timestamp": datetime.now().isoformat(),
        "api_tests": {},
        "summary": {
            "total_apis": len(provider.api_priority),
            "working_apis": 0,
            "failed_apis": 0
        }
    }
    
    # Test each API individually
    api_methods = {
        "yahoo": provider.fetch_yahoo_data,
        "alpha_vantage": provider.fetch_alpha_vantage_data,
        "polygon": provider.fetch_polygon_data,
        "iex": provider.fetch_iex_data,
        "tiingo": provider.fetch_tiingo_data,
        "twelve_data": provider.fetch_twelve_data,
        "fmp": provider.fetch_fmp_data,
        "marketstack": provider.fetch_marketstack_data,
        "finnhub": provider.fetch_finnhub_data
    }
    
    for api_name in provider.api_priority:
        if api_name in api_methods:
            try:
                start_time = time.time()
                data = api_methods[api_name](symbol)
                end_time = time.time()
                
                if data:
                    results["api_tests"][api_name] = {
                        "status": "success",
                        "response_time_ms": round((end_time - start_time) * 1000, 2),
                        "price": data.get("current_price"),
                        "cached": data.get("_cache_hit", False),
                        "source": data.get("source")
                    }
                    results["summary"]["working_apis"] += 1
                else:
                    results["api_tests"][api_name] = {
                        "status": "no_data",
                        "response_time_ms": round((end_time - start_time) * 1000, 2),
                        "error": "No data returned"
                    }
                    results["summary"]["failed_apis"] += 1
                    
            except Exception as e:
                results["api_tests"][api_name] = {
                    "status": "error",
                    "error": str(e)
                }
                results["summary"]["failed_apis"] += 1
    
    results["summary"]["success_rate"] = round(
        results["summary"]["working_apis"] / results["summary"]["total_apis"] * 100, 1
    )
    
    return results

def get_api_status() -> Dict:
    """Get status of all configured APIs"""
    provider = create_simple_provider()
    
    status = {
        "timestamp": datetime.now().isoformat(),
        "total_apis": len(provider.api_priority),
        "api_priority": provider.api_priority,
        "api_endpoints": {
            "yahoo": "yfinance library",
            "alpha_vantage": provider.alpha_vantage_base,
            "polygon": provider.polygon_base,
            "iex": provider.iex_base,
            "tiingo": provider.tiingo_base,
            "twelve_data": provider.twelve_data_base,
            "fmp": provider.fmp_base,
            "marketstack": provider.marketstack_base,
            "finnhub": provider.finnhub_base
        },
        "api_keys_configured": {
            api: "configured" if key != "demo" else "demo/free tier"
            for api, key in provider.api_keys.items()
        }
    }
    
    return status

def benchmark_apis(symbols: List[str] = ["AAPL", "GOOGL", "MSFT", "TSLA"]) -> Dict:
    """Benchmark all APIs with multiple symbols"""
    provider = create_simple_provider()
    results = {
        "timestamp": datetime.now().isoformat(),
        "symbols_tested": symbols,
        "api_performance": {},
        "summary": {}
    }
    
    api_methods = {
        "yahoo": provider.fetch_yahoo_data,
        "alpha_vantage": provider.fetch_alpha_vantage_data,
        "polygon": provider.fetch_polygon_data,
        "iex": provider.fetch_iex_data,
        "tiingo": provider.fetch_tiingo_data,
        "twelve_data": provider.fetch_twelve_data,
        "fmp": provider.fetch_fmp_data,
        "marketstack": provider.fetch_marketstack_data,
        "finnhub": provider.fetch_finnhub_data
    }
    
    for api_name in provider.api_priority:
        if api_name in api_methods:
            api_results = {
                "success_count": 0,
                "failure_count": 0,
                "total_time_ms": 0,
                "avg_time_ms": 0,
                "symbols_tested": []
            }
            
            for symbol in symbols:
                try:
                    start_time = time.time()
                    data = api_methods[api_name](symbol)
                    end_time = time.time()
                    
                    response_time = (end_time - start_time) * 1000
                    api_results["total_time_ms"] += response_time
                    
                    if data:
                        api_results["success_count"] += 1
                        api_results["symbols_tested"].append({
                            "symbol": symbol,
                            "status": "success",
                            "response_time_ms": round(response_time, 2),
                            "price": data.get("current_price")
                        })
                    else:
                        api_results["failure_count"] += 1
                        api_results["symbols_tested"].append({
                            "symbol": symbol,
                            "status": "no_data",
                            "response_time_ms": round(response_time, 2)
                        })
                        
                except Exception as e:
                    api_results["failure_count"] += 1
                    api_results["symbols_tested"].append({
                        "symbol": symbol,
                        "status": "error",
                        "error": str(e)
                    })
                
                # Small delay between requests
                time.sleep(0.5)
            
            api_results["avg_time_ms"] = round(
                api_results["total_time_ms"] / len(symbols), 2
            ) if len(symbols) > 0 else 0
            
            api_results["success_rate"] = round(
                api_results["success_count"] / len(symbols) * 100, 1
            )
            
            results["api_performance"][api_name] = api_results
    
    # Calculate overall summary
    total_success = sum(api["success_count"] for api in results["api_performance"].values())
    total_tests = len(symbols) * len(provider.api_priority)
    
    results["summary"] = {
        "total_tests": total_tests,
        "total_successes": total_success,
        "overall_success_rate": round(total_success / total_tests * 100, 1),
        "best_performing_api": max(
            results["api_performance"].items(),
            key=lambda x: (x[1]["success_rate"], -x[1]["avg_time_ms"])
        )[0] if results["api_performance"] else None
    }
    
    return results

# Cache management CLI functions
def cache_management_cli():
    """Simple CLI for cache management"""
    provider = create_simple_provider()
    
    while True:
        print("\n=== Multi-API Data Provider Management ===")
        print("--- Cache Management ---")
        print("1. View cache statistics")
        print("2. Clear all cache")
        print("3. Clear stock data cache")
        print("4. Clear technical analysis cache")
        print("5. Cleanup expired entries")
        print("6. View cache file size")
        print("--- API Management ---")
        print("7. Test all APIs")
        print("8. View API status")
        print("9. Benchmark APIs")
        print("10. Get stock data (multi-API)")
        print("0. Exit")
        
        try:
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                stats = provider.get_cache_stats()
                print(f"\n--- Cache Statistics ---")
                print(f"Total entries: {stats['total_entries']}")
                print(f"Total size: {stats['total_size_mb']} MB")
                print(f"Average access count: {stats['avg_access_count']}")
                print(f"Categories: {stats['categories_count']}")
                for cat, info in stats['categories'].items():
                    print(f"  {cat}: {info['count']} entries, {round(info['size']/1024/1024, 2)} MB")
                
            elif choice == "2":
                count = provider.clear_cache()
                print(f"Cleared {count} cache entries")
                
            elif choice == "3":
                count = provider.clear_cache(category="stock_data")
                print(f"Cleared {count} stock data cache entries")
                
            elif choice == "4":
                count = provider.clear_cache(category="technical_analysis")
                print(f"Cleared {count} technical analysis cache entries")
                
            elif choice == "5":
                provider.cleanup_expired_cache()
                print("Expired cache entries cleaned up")
                
            elif choice == "6":
                size_bytes, size_str = provider.cache.get_file_size()
                print(f"Cache file size: {size_str}")
                
            elif choice == "7":
                symbol = input("Enter symbol to test (default: AAPL): ").strip() or "AAPL"
                print(f"Testing all APIs for {symbol}...")
                results = test_all_apis(symbol)
                
                print(f"\n--- API Test Results for {symbol} ---")
                print(f"Working APIs: {results['summary']['working_apis']}/{results['summary']['total_apis']}")
                print(f"Success Rate: {results['summary']['success_rate']}%")
                
                for api, result in results['api_tests'].items():
                    status = result['status']
                    if status == "success":
                        price = result.get('price', 'N/A')
                        time_ms = result.get('response_time_ms', 'N/A')
                        cached = " (cached)" if result.get('cached') else ""
                        print(f"  ✅ {api}: ${price} ({time_ms}ms){cached}")
                    else:
                        error = result.get('error', 'Unknown error')
                        print(f"  ❌ {api}: {error}")
                
            elif choice == "8":
                status = get_api_status()
                print(f"\n--- API Configuration Status ---")
                print(f"Total APIs: {status['total_apis']}")
                print(f"Priority Order: {', '.join(status['api_priority'])}")
                
                print(f"\nAPI Keys:")
                for api, key_status in status['api_keys_configured'].items():
                    print(f"  {api}: {key_status}")
                
            elif choice == "9":
                symbols_input = input("Enter symbols separated by commas (default: AAPL,GOOGL,MSFT): ").strip()
                symbols = [s.strip().upper() for s in symbols_input.split(",")] if symbols_input else ["AAPL", "GOOGL", "MSFT"]
                
                print(f"Benchmarking APIs with symbols: {', '.join(symbols)}")
                print("This may take a while...")
                
                results = benchmark_apis(symbols)
                
                print(f"\n--- API Benchmark Results ---")
                print(f"Total Tests: {results['summary']['total_tests']}")
                print(f"Overall Success Rate: {results['summary']['overall_success_rate']}%")
                print(f"Best Performing API: {results['summary']['best_performing_api']}")
                
                print(f"\nPer-API Performance:")
                for api, perf in results['api_performance'].items():
                    print(f"  {api}: {perf['success_rate']}% success, {perf['avg_time_ms']}ms avg")
                
            elif choice == "10":
                symbol = input("Enter symbol (default: AAPL): ").strip() or "AAPL"
                print(f"Fetching comprehensive data for {symbol}...")
                
                data = provider.get_comprehensive_stock_data(symbol)
                
                print(f"\n--- Multi-API Data for {symbol} ---")
                if data['primary_data']:
                    primary = data['primary_data']
                    print(f"Price: ${primary.get('current_price', 'N/A')}")
                    print(f"Change: {primary.get('change', 'N/A')} ({primary.get('change_percent', 'N/A')}%)")
                    print(f"Primary Source: {primary.get('source', 'N/A')}")
                    
                print(f"Sources Used: {', '.join(data['sources_used'])}")
                print(f"Sources Failed: {', '.join(data['sources_failed'])}")
                print(f"Reliability Score: {data['reliability_score']}")
                
                if data.get('cross_validation'):
                    cv = data['cross_validation']
                    print(f"Cross-Validation: {cv['confidence']:.1%} confidence")
                
            elif choice == "0":
                break
                
            else:
                print("Invalid option")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Example usage
    print("Enhanced Multi-Source Financial Data Provider")
    print("Cache System: ✓ Enhanced")
    
    # Test basic functionality
    provider = create_simple_provider()
    
    # Show cache stats
    stats = provider.get_cache_stats()
    print(f"Cache initialized: {stats['total_entries']} entries")
    
    # Run cache management CLI if in interactive mode
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--cache-cli":
        cache_management_cli() 