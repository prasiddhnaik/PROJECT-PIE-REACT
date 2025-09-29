import asyncio
import aiohttp
import yfinance as yf
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time
from fastapi import HTTPException

# Configure logging
logger = logging.getLogger(__name__)

class OptimalFreeAPIs:
    def __init__(self):
        self.finnhub_key = "YOUR_FINNHUB_KEY"  # Get from finnhub.io
        self.twelve_data_key = "YOUR_TWELVE_DATA_KEY"  # Get from twelvedata.com
        self.alpha_vantage_key = "3J52FQXN785RGJX0"  # From memory
        
        # Track API usage
        self.api_calls = {
            'yahoo': [],  # No limit, but be respectful
            'finnhub': [],  # 60/minute
            'twelve_data': {'minute': [], 'daily': 0, 'reset_time': None},  # 8/min, 800/day
            'alpha_vantage': [],  # 5/minute, 500/day
            'coingecko': []  # ~30/minute
        }
        
        logger.info("Optimal Free APIs initialized with rate limiting")
    
    def _can_call_api(self, api_name: str) -> bool:
        """Check if we can call the API without hitting rate limits"""
        now = time.time()
        
        if api_name == 'yahoo':
            # Self-imposed limit of 100/minute to be respectful
            self.api_calls['yahoo'] = [t for t in self.api_calls['yahoo'] if t > now - 60]
            return len(self.api_calls['yahoo']) < 100
        
        elif api_name == 'finnhub':
            # 60 per minute
            self.api_calls['finnhub'] = [t for t in self.api_calls['finnhub'] if t > now - 60]
            return len(self.api_calls['finnhub']) < 60
        
        elif api_name == 'twelve_data':
            # 8 per minute, 800 per day
            # Reset daily counter if needed
            if not self.api_calls['twelve_data']['reset_time'] or \
               datetime.now() > self.api_calls['twelve_data']['reset_time']:
                self.api_calls['twelve_data']['daily'] = 0
                self.api_calls['twelve_data']['reset_time'] = datetime.now().replace(
                    hour=0, minute=0, second=0
                ) + timedelta(days=1)
            
            # Check both minute and daily limits
            self.api_calls['twelve_data']['minute'] = [
                t for t in self.api_calls['twelve_data']['minute'] if t > now - 60
            ]
            return (len(self.api_calls['twelve_data']['minute']) < 8 and 
                    self.api_calls['twelve_data']['daily'] < 800)
        
        elif api_name == 'alpha_vantage':
            # 5 per minute, 500 per day
            self.api_calls['alpha_vantage'] = [t for t in self.api_calls['alpha_vantage'] if t > now - 60]
            return len(self.api_calls['alpha_vantage']) < 5
        
        elif api_name == 'coingecko':
            # ~30 per minute (unofficial)
            self.api_calls['coingecko'] = [t for t in self.api_calls['coingecko'] if t > now - 60]
            return len(self.api_calls['coingecko']) < 30
        
        return False
    
    def _record_api_call(self, api_name: str):
        """Record that we made an API call"""
        now = time.time()
        
        if api_name == 'yahoo':
            self.api_calls['yahoo'].append(now)
        elif api_name == 'finnhub':
            self.api_calls['finnhub'].append(now)
        elif api_name == 'twelve_data':
            self.api_calls['twelve_data']['minute'].append(now)
            self.api_calls['twelve_data']['daily'] += 1
        elif api_name == 'alpha_vantage':
            self.api_calls['alpha_vantage'].append(now)
        elif api_name == 'coingecko':
            self.api_calls['coingecko'].append(now)
    
    async def get_stock_yahoo(self, symbol: str) -> Optional[Dict]:
        """Yahoo Finance - Primary source (no limits)"""
        if not self._can_call_api('yahoo'):
            logger.warning(f"Yahoo Finance rate limit reached, skipping request for {symbol}")
            return None
        
        try:
            self._record_api_call('yahoo')
            logger.info(f"Fetching {symbol} from Yahoo Finance")
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or len(info) < 5:  # Basic validation
                logger.warning(f"Yahoo Finance returned insufficient data for {symbol}")
                return None
            
            # Get the latest price data
            hist = ticker.history(period="2d")
            if hist.empty:
                logger.warning(f"Yahoo Finance returned no historical data for {symbol}")
                return None
                
            # Calculate change from previous close if available
            current_price = float(hist['Close'].iloc[-1]) if not hist.empty else info.get('currentPrice', 0)
            previous_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else info.get('previousClose', current_price)
            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close > 0 else 0
            
            logger.info(f"Successfully fetched {symbol} from Yahoo Finance: ${current_price:.2f}")
            
            return {
                'symbol': symbol,
                'price': current_price,
                'change': change,
                'change_percent': change_percent,
                'volume': int(hist['Volume'].iloc[-1]) if not hist.empty and 'Volume' in hist else info.get('volume', 0),
                'source': 'yahoo',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching {symbol} from Yahoo Finance: {str(e)}")
            return None
    
    async def get_stock_finnhub(self, symbol: str) -> Optional[Dict]:
        """Finnhub - Secondary source (60/min free)"""
        if not self._can_call_api('finnhub') or not self.finnhub_key:
            logger.warning(f"Finnhub rate limit reached or no API key, skipping request for {symbol}")
            return None
        
        try:
            self._record_api_call('finnhub')
            logger.info(f"Fetching {symbol} from Finnhub")
            
            url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={self.finnhub_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Basic validation
                        if 'c' not in data or data['c'] == 0:
                            logger.warning(f"Finnhub returned invalid data for {symbol}")
                            return None
                        
                        logger.info(f"Successfully fetched {symbol} from Finnhub: ${data.get('c', 0):.2f}")
                        
                        return {
                            'symbol': symbol,
                            'price': data.get('c', 0),  # current price
                            'change': data.get('d', 0),  # change
                            'change_percent': data.get('dp', 0),  # percent change
                            'high': data.get('h', 0),
                            'low': data.get('l', 0),
                            'open': data.get('o', 0),
                            'previous_close': data.get('pc', 0),
                            'source': 'finnhub',
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        logger.warning(f"Finnhub returned status {response.status} for {symbol}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching {symbol} from Finnhub: {str(e)}")
            return None
    
    async def get_stock_twelve_data(self, symbol: str) -> Optional[Dict]:
        """Twelve Data - Tertiary source (8/min, 800/day free)"""
        if not self._can_call_api('twelve_data') or not self.twelve_data_key:
            logger.warning(f"Twelve Data rate limit reached or no API key, skipping request for {symbol}")
            return None
        
        try:
            self._record_api_call('twelve_data')
            logger.info(f"Fetching {symbol} from Twelve Data")
            
            # Remove ^ character for indices if present
            clean_symbol = symbol.replace('^', '')
            
            url = f"https://api.twelvedata.com/quote?symbol={clean_symbol}&apikey={self.twelve_data_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Basic validation
                        if 'close' not in data or 'symbol' not in data:
                            logger.warning(f"Twelve Data returned invalid data for {symbol}")
                            return None
                        
                        logger.info(f"Successfully fetched {symbol} from Twelve Data: ${float(data.get('close', 0)):.2f}")
                        
                        return {
                            'symbol': symbol,
                            'price': float(data.get('close', 0)),
                            'change': float(data.get('change', 0)),
                            'change_percent': float(data.get('percent_change', 0)),
                            'volume': int(data.get('volume', 0)),
                            'source': 'twelve_data',
                            'timestamp': data.get('datetime', datetime.now().isoformat())
                        }
                    else:
                        logger.warning(f"Twelve Data returned status {response.status} for {symbol}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching {symbol} from Twelve Data: {str(e)}")
            return None
    
    async def get_stock_alpha_vantage(self, symbol: str) -> Optional[Dict]:
        """Alpha Vantage - Quaternary source (5/min, 500/day free)"""
        if not self._can_call_api('alpha_vantage') or not self.alpha_vantage_key:
            logger.warning(f"Alpha Vantage rate limit reached or no API key, skipping request for {symbol}")
            return None
        
        try:
            self._record_api_call('alpha_vantage')
            logger.info(f"Fetching {symbol} from Alpha Vantage")
            
            # Remove ^ character for indices if present
            clean_symbol = symbol.replace('^', '')
            
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={clean_symbol}&apikey={self.alpha_vantage_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'Global Quote' in data and data['Global Quote']:
                            quote = data['Global Quote']
                            
                            logger.info(f"Successfully fetched {symbol} from Alpha Vantage: ${float(quote.get('05. price', 0)):.2f}")
                            
                            return {
                                'symbol': symbol,
                                'price': float(quote.get('05. price', 0)),
                                'change': float(quote.get('09. change', 0)),
                                'change_percent': float(quote.get('10. change percent', '0%').replace('%', '')),
                                'volume': int(quote.get('06. volume', 0)),
                                'source': 'alpha_vantage',
                                'timestamp': quote.get('07. latest trading day', datetime.now().isoformat())
                            }
                        else:
                            logger.warning(f"Alpha Vantage returned invalid data for {symbol}")
                            return None
                    else:
                        logger.warning(f"Alpha Vantage returned status {response.status} for {symbol}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching {symbol} from Alpha Vantage: {str(e)}")
            return None
    
    async def get_crypto_coingecko(self, crypto_id: str, vs_currency: str = 'usd') -> Optional[Dict]:
        """CoinGecko - Primary crypto source (30/min free)"""
        if not self._can_call_api('coingecko'):
            logger.warning(f"CoinGecko rate limit reached, skipping request for {crypto_id}")
            return None
        
        try:
            self._record_api_call('coingecko')
            logger.info(f"Fetching {crypto_id} from CoinGecko")
            
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies={vs_currency}&include_24hr_change=true&include_market_cap=true&include_last_updated_at=true"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if crypto_id in data:
                            crypto_data = data[crypto_id]
                            price = crypto_data.get(vs_currency, 0)
                            change_24h = crypto_data.get(f"{vs_currency}_24h_change", 0)
                            
                            logger.info(f"Successfully fetched {crypto_id} from CoinGecko: ${float(price):.2f}")
                            
                            return {
                                'symbol': crypto_id,
                                'price': float(price),
                                'change_percent': float(change_24h),
                                'market_cap': crypto_data.get(f"{vs_currency}_market_cap", 0),
                                'last_updated': datetime.fromtimestamp(crypto_data.get('last_updated_at', time.time())).isoformat(),
                                'source': 'coingecko',
                                'timestamp': datetime.now().isoformat()
                            }
                        else:
                            logger.warning(f"CoinGecko returned invalid data for {crypto_id}")
                            return None
                    else:
                        logger.warning(f"CoinGecko returned status {response.status} for {crypto_id}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching {crypto_id} from CoinGecko: {str(e)}")
            return None
    
    async def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get stock data using the optimal API source with fallbacks
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with stock data
        """
        logger.info(f"Fetching data for {symbol} using optimal API strategy")
        
        # Try APIs in order of priority
        # 1. Yahoo Finance (unlimited, but unofficial)
        data = await self.get_stock_yahoo(symbol)
        if data:
            return data
        
        # 2. Finnhub (60/min)
        data = await self.get_stock_finnhub(symbol)
        if data:
            return data
        
        # 3. Twelve Data (8/min, 800/day)
        data = await self.get_stock_twelve_data(symbol)
        if data:
            return data
        
        # 4. Alpha Vantage (5/min, 500/day)
        data = await self.get_stock_alpha_vantage(symbol)
        if data:
            return data
        
        # If all APIs fail, raise an exception
        logger.error(f"All APIs failed for {symbol}")
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
        
        # Process in small batches to avoid overwhelming any single API
        batch_size = 5
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i+batch_size]
            
            # Process each symbol in the batch
            batch_tasks = [self.get_stock_data(symbol) for symbol in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Process results
            for j, result in enumerate(batch_results):
                symbol = batch[j]
                if isinstance(result, Exception):
                    logger.error(f"Failed to fetch data for {symbol}: {result}")
                    # Add minimal placeholder data
                    results[symbol] = {
                        "source": "error",
                        "symbol": symbol,
                        "price": 0,
                        "change": 0,
                        "change_percent": 0,
                        "error": str(result)
                    }
                else:
                    results[symbol] = result
            
            # Add a small delay between batches to avoid rate limits
            if i + batch_size < len(symbols):
                await asyncio.sleep(1)
        
        return results
    
    def get_api_status(self) -> Dict:
        """Get current API usage status"""
        now = time.time()
        
        return {
            'yahoo': {
                'calls_last_minute': len([t for t in self.api_calls['yahoo'] if t > now - 60]),
                'limit_per_minute': 100,  # self-imposed
                'official_limit': 'None (unofficial API)'
            },
            'finnhub': {
                'calls_last_minute': len([t for t in self.api_calls['finnhub'] if t > now - 60]),
                'limit_per_minute': 60,
                'remaining': 60 - len([t for t in self.api_calls['finnhub'] if t > now - 60])
            },
            'twelve_data': {
                'calls_last_minute': len(self.api_calls['twelve_data']['minute']),
                'limit_per_minute': 8,
                'daily_usage': self.api_calls['twelve_data']['daily'],
                'daily_limit': 800,
                'daily_remaining': 800 - self.api_calls['twelve_data']['daily']
            },
            'alpha_vantage': {
                'calls_last_minute': len([t for t in self.api_calls['alpha_vantage'] if t > now - 60]),
                'limit_per_minute': 5,
                'remaining': 5 - len([t for t in self.api_calls['alpha_vantage'] if t > now - 60])
            },
            'coingecko': {
                'calls_last_minute': len([t for t in self.api_calls['coingecko'] if t > now - 60]),
                'limit_per_minute': 30,  # unofficial
                'remaining': 30 - len([t for t in self.api_calls['coingecko'] if t > now - 60])
            }
        }

# Create a singleton instance
optimal_apis = OptimalFreeAPIs()
