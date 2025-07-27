import logging
import random
import time
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

# Import configuration
from config import APIConfig, DEFAULT_STOCK_SYMBOLS, API_PRIORITY

# Configure logging
logger = logging.getLogger(__name__)

# Import API keys from config
ALPHA_VANTAGE_KEY = APIConfig.ALPHA_VANTAGE_KEY
TWELVE_DATA_KEY = APIConfig.TWELVE_DATA_KEY

class APIManager:
    """
    Manages API calls with rate limiting, fallback mechanisms, and load balancing
    """
    
    def __init__(self):
        self.api_keys = {
            'alpha_vantage': ALPHA_VANTAGE_KEY,
            'twelve_data': TWELVE_DATA_KEY,
            'polygon': APIConfig.POLYGON_KEY
        }
        
        self.api_base_urls = {
            'alpha_vantage': APIConfig.ALPHA_VANTAGE_BASE_URL,
            'twelve_data': APIConfig.TWELVE_DATA_BASE_URL,
            'polygon': APIConfig.POLYGON_BASE_URL
        }
        
        # Track API call counts for rate limiting
        self.api_calls = {
            'alpha_vantage': {'count': 0, 'reset_time': time.time() + 60},
            'twelve_data': {'count': 0, 'reset_time': time.time() + 60},
            'polygon': {'count': 0, 'reset_time': time.time() + 60}
        }
        
        # API rate limits
        self.rate_limits = {
            'alpha_vantage': 5,  # 5 calls per minute (free tier)
            'twelve_data': 8,    # 8 calls per minute (free tier)
            'polygon': 5         # 5 calls per minute (free tier)
        }
    
    async def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get stock data using the optimal API source with fallbacks
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with stock data
        """
        # Try APIs in order of priority
        for api_name in API_PRIORITY['stock_quotes']:
            if api_name not in self.api_keys or not self.api_keys[api_name]:
                continue
                
            if api_name == 'alpha_vantage' and self._can_use_api('alpha_vantage'):
                try:
                    data = await self._get_alpha_vantage_data(symbol)
                    if data:
                        return data
                except Exception as e:
                    logger.warning(f"Alpha Vantage API failed for {symbol}: {e}")
            
            elif api_name == 'twelve_data' and self._can_use_api('twelve_data'):
                try:
                    data = await self._get_twelve_data(symbol)
                    if data:
                        return data
                except Exception as e:
                    logger.warning(f"Twelve Data API failed for {symbol}: {e}")
            
            elif api_name == 'polygon' and self._can_use_api('polygon'):
                try:
                    data = await self._get_polygon_data(symbol)
                    if data:
                        return data
                except Exception as e:
                    logger.warning(f"Polygon API failed for {symbol}: {e}")
        
        # If all APIs fail, raise an exception
        raise HTTPException(status_code=503, detail=f"Unable to fetch stock data for {symbol}")
    
    async def get_batch_stock_data(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get data for multiple stock symbols with load balancing across APIs
        
        Args:
            symbols: List of stock ticker symbols
            
        Returns:
            Dictionary mapping symbols to their data
        """
        results = {}
        
        # Determine which APIs to use based on available keys and rate limits
        available_apis = []
        for api_name in API_PRIORITY['stock_quotes']:
            if api_name in self.api_keys and self.api_keys[api_name]:
                available_apis.append(api_name)
        
        if not available_apis:
            raise HTTPException(status_code=503, detail="No APIs available")
        
        # Distribute symbols across available APIs
        api_assignments = {}
        for i, symbol in enumerate(symbols):
            api_name = available_apis[i % len(available_apis)]
            if api_name not in api_assignments:
                api_assignments[api_name] = []
            api_assignments[api_name].append(symbol)
        
        # Process each API's symbols
        tasks = []
        for api_name, api_symbols in api_assignments.items():
            if api_name == 'alpha_vantage':
                tasks.append(self._batch_alpha_vantage(api_symbols))
            elif api_name == 'twelve_data':
                tasks.append(self._batch_twelve_data(api_symbols))
            elif api_name == 'polygon':
                tasks.append(self._batch_polygon(api_symbols))
        
        # Wait for all tasks to complete
        api_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        for result in api_results:
            if isinstance(result, Exception):
                logger.error(f"API batch request failed: {result}")
                continue
            
            results.update(result)
        
        # Check for missing symbols and try to fetch them individually
        missing_symbols = [s for s in symbols if s not in results]
        if missing_symbols:
            for symbol in missing_symbols:
                try:
                    data = await self.get_stock_data(symbol)
                    results[symbol] = data
                except Exception as e:
                    logger.error(f"Failed to fetch data for {symbol}: {e}")
                    # Add minimal placeholder data
                    results[symbol] = {
                        "source": "error",
                        "symbol": symbol,
                        "price": 0,
                        "change": 0,
                        "change_percent": 0,
                        "error": str(e)
                    }
        
        return results
    
    async def _get_alpha_vantage_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch stock data from Alpha Vantage API"""
        self._increment_api_call('alpha_vantage')
        
        # Remove ^ character for indices if present
        clean_symbol = symbol.replace('^', '')
        
        # Construct API URL
        url = f"{self.api_base_urls['alpha_vantage']}?function=GLOBAL_QUOTE&symbol={clean_symbol}&apikey={self.api_keys['alpha_vantage']}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'Global Quote' in data and data['Global Quote']:
                        quote = data['Global Quote']
                        return {
                            "source": "alpha_vantage",
                            "symbol": symbol,
                            "price": float(quote.get('05. price', 0)),
                            "change": float(quote.get('09. change', 0)),
                            "change_percent": float(quote.get('10. change percent', '0%').replace('%', '')),
                            "volume": int(quote.get('06. volume', 0)),
                            "timestamp": quote.get('07. latest trading day', '')
                        }
        
        return None
    
    async def _get_twelve_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch stock data from Twelve Data API"""
        self._increment_api_call('twelve_data')
        
        # Remove ^ character for indices if present
        clean_symbol = symbol.replace('^', '')
        
        # Construct API URL
        url = f"{self.api_base_urls['twelve_data']}/quote?symbol={clean_symbol}&apikey={self.api_keys['twelve_data']}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'close' in data and 'symbol' in data:
                        return {
                            "source": "twelve_data",
                            "symbol": symbol,
                            "price": float(data.get('close', 0)),
                            "change": float(data.get('change', 0)),
                            "change_percent": float(data.get('percent_change', 0)),
                            "volume": int(data.get('volume', 0)),
                            "timestamp": data.get('datetime', '')
                        }
        
        return None
    
    async def _get_polygon_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch stock data from Polygon API"""
        self._increment_api_call('polygon')
        
        # Remove ^ character for indices if present
        clean_symbol = symbol.replace('^', '')
        
        # Construct API URL
        url = f"{self.api_base_urls['polygon']}/v2/aggs/ticker/{clean_symbol}/prev?apiKey={self.api_keys['polygon']}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'results' in data and data['results']:
                        result = data['results'][0]
                        prev_close = result.get('c', 0)
                        open_price = result.get('o', prev_close)
                        change = prev_close - open_price
                        change_percent = (change / open_price * 100) if open_price > 0 else 0
                        
                        return {
                            "source": "polygon",
                            "symbol": symbol,
                            "price": float(prev_close),
                            "change": float(change),
                            "change_percent": float(change_percent),
                            "volume": int(result.get('v', 0)),
                            "timestamp": result.get('t', '')
                        }
        
        return None
    
    async def _batch_alpha_vantage(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Batch process symbols with Alpha Vantage API"""
        results = {}
        
        # Alpha Vantage doesn't support true batch requests in free tier
        # Process each symbol individually with a delay to avoid rate limits
        for i, symbol in enumerate(symbols):
            try:
                data = await self._get_alpha_vantage_data(symbol)
                if data:
                    results[symbol] = data
            except Exception as e:
                logger.error(f"Alpha Vantage failed for {symbol}: {e}")
            
            # Add a small delay between requests
            if i < len(symbols) - 1:
                await asyncio.sleep(0.25)  # 250ms delay
        
        return results
    
    async def _batch_twelve_data(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Batch process symbols with Twelve Data API"""
        results = {}
        
        # Twelve Data has a batch endpoint for premium users only
        # For free tier, process each symbol individually
        for i, symbol in enumerate(symbols):
            try:
                data = await self._get_twelve_data(symbol)
                if data:
                    results[symbol] = data
            except Exception as e:
                logger.error(f"Twelve Data failed for {symbol}: {e}")
            
            # Add a small delay between requests
            if i < len(symbols) - 1:
                await asyncio.sleep(0.25)  # 250ms delay
        
        return results
    
    async def _batch_polygon(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Batch process symbols with Polygon API"""
        results = {}
        
        # Polygon supports true batch requests, but we'll still process individually for consistency
        for i, symbol in enumerate(symbols):
            try:
                data = await self._get_polygon_data(symbol)
                if data:
                    results[symbol] = data
            except Exception as e:
                logger.error(f"Polygon failed for {symbol}: {e}")
            
            # Add a small delay between requests
            if i < len(symbols) - 1:
                await asyncio.sleep(0.25)  # 250ms delay
        
        return results
    
    def _can_use_api(self, api_name: str) -> bool:
        """Check if an API can be used based on rate limits"""
        now = time.time()
        
        # Reset counter if the reset time has passed
        if now > self.api_calls[api_name]['reset_time']:
            self.api_calls[api_name]['count'] = 0
            self.api_calls[api_name]['reset_time'] = now + 60  # Reset after 1 minute
        
        # Check if we're under the rate limit
        return self.api_calls[api_name]['count'] < self.rate_limits[api_name]
    
    def _increment_api_call(self, api_name: str) -> None:
        """Increment the API call counter"""
        now = time.time()
        
        # Reset counter if the reset time has passed
        if now > self.api_calls[api_name]['reset_time']:
            self.api_calls[api_name]['count'] = 0
            self.api_calls[api_name]['reset_time'] = now + 60  # Reset after 1 minute
        
        # Increment the counter
        self.api_calls[api_name]['count'] += 1

# Create a singleton instance
api_manager = APIManager() 