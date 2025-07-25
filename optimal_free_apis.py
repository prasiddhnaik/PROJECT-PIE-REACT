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

# Import API key manager
try:
    from api_key_manager import api_keys
    logger.info("API key manager imported successfully")
except ImportError:
    logger.warning("API key manager not found, using default keys")
    api_keys = None

class OptimalFreeAPIs:
    def __init__(self):
        # Get API keys from the key manager if available
        if api_keys:
            self.finnhub_key = api_keys.get_key('finnhub')
            self.twelve_data_key = api_keys.get_key('twelve_data')
            self.alpha_vantage_key = api_keys.get_key('alpha_vantage')
            self.polygon_key = api_keys.get_key('polygon')
            self.marketstack_key = api_keys.get_key('marketstack')
        else:
            # Fallback to hardcoded keys
            self.finnhub_key = "YOUR_FINNHUB_KEY"  # Get from finnhub.io
            self.twelve_data_key = "YOUR_TWELVE_DATA_KEY"  # Get from twelvedata.com
            self.alpha_vantage_key = "3J52FQXN785RGJX0"  # From memory
            self.polygon_key = "SavZMeuTDTxjWJuFzBO6zES7mBFK68RJ"
            self.marketstack_key = "10ca00f0992844c25ea3722d5913825c"
        
        # Track API usage
        self.api_calls = {
            'yahoo': [],  # No limit, but be respectful
            'finnhub': [],  # 60/minute
            'twelve_data': {'minute': [], 'daily': 0, 'reset_time': None},  # 8/min, 800/day
            'alpha_vantage': [],  # 5/minute, 500/day
            'polygon': [],  # 5/minute
            'marketstack': {'monthly': 0},  # 100/month
            'coingecko': []  # ~30/minute
        }
        
        logger.info("Optimal Free APIs initialized with rate limiting")
    
    def _can_call_api(self, api_name: str) -> bool:
        """Check if we can call the API without hitting rate limits"""
        now = time.time()
        
        # If API key manager is available, use it to check availability
        if api_keys and api_name != 'yahoo' and api_name != 'coingecko':
            return api_keys.can_call_api(api_name)
        
        # Otherwise, use our internal tracking
        if api_name == 'yahoo':
            # Self-imposed limit of 100/minute to be respectful
            self.api_calls['yahoo'] = [t for t in self.api_calls['yahoo'] if t > now - 60]
            return len(self.api_calls['yahoo']) < 100
        
        elif api_name == 'finnhub':
            # 60 per minute
            self.api_calls['finnhub'] = [t for t in self.api_calls['finnhub'] if t > now - 60]
            return len(self.api_calls['finnhub']) < 60 and self.finnhub_key
        
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
                    self.api_calls['twelve_data']['daily'] < 800 and
                    self.twelve_data_key)
        
        elif api_name == 'alpha_vantage':
            # 5 per minute, 500 per day
            self.api_calls['alpha_vantage'] = [t for t in self.api_calls['alpha_vantage'] if t > now - 60]
            return len(self.api_calls['alpha_vantage']) < 5 and self.alpha_vantage_key
            
        elif api_name == 'polygon':
            # 5 per minute
            self.api_calls['polygon'] = [t for t in self.api_calls['polygon'] if t > now - 60]
            return len(self.api_calls['polygon']) < 5 and self.polygon_key
            
        elif api_name == 'marketstack':
            # 100 per month
            return self.api_calls['marketstack']['monthly'] < 100 and self.marketstack_key
        
        elif api_name == 'coingecko':
            # ~30 per minute (unofficial)
            self.api_calls['coingecko'] = [t for t in self.api_calls['coingecko'] if t > now - 60]
            return len(self.api_calls['coingecko']) < 30
        
        return False
    
    def _record_api_call(self, api_name: str):
        """Record that we made an API call"""
        now = time.time()
        
        # If API key manager is available, use it to record the call
        if api_keys and api_name != 'yahoo' and api_name != 'coingecko':
            api_keys.record_api_call(api_name)
            return
        
        # Otherwise, use our internal tracking
        if api_name == 'yahoo':
            self.api_calls['yahoo'].append(now)
        elif api_name == 'finnhub':
            self.api_calls['finnhub'].append(now)
        elif api_name == 'twelve_data':
            self.api_calls['twelve_data']['minute'].append(now)
            self.api_calls['twelve_data']['daily'] += 1
        elif api_name == 'alpha_vantage':
            self.api_calls['alpha_vantage'].append(now)
        elif api_name == 'polygon':
            self.api_calls['polygon'].append(now)
        elif api_name == 'marketstack':
            self.api_calls['marketstack']['monthly'] += 1
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
        if not self._can_call_api('finnhub'):
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
        if not self._can_call_api('twelve_data'):
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
        if not self._can_call_api('alpha_vantage'):
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
    
    async def get_stock_polygon(self, symbol: str) -> Optional[Dict]:
        """Polygon.io - Another source (5/min free)"""
        if not self._can_call_api('polygon'):
            logger.warning(f"Polygon rate limit reached or no API key, skipping request for {symbol}")
            return None
        
        try:
            self._record_api_call('polygon')
            logger.info(f"Fetching {symbol} from Polygon")
            
            url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?apiKey={self.polygon_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('status') == 'OK' and data.get('results'):
                            result = data['results'][0]
                            
                            logger.info(f"Successfully fetched {symbol} from Polygon: ${float(result.get('c', 0)):.2f}")
                            
                            return {
                                'symbol': symbol,
                                'price': float(result.get('c', 0)),  # close price
                                'change': float(result.get('c', 0)) - float(result.get('o', result.get('c', 0))),
                                'change_percent': ((float(result.get('c', 0)) / float(result.get('o', 1)) - 1) * 100) if float(result.get('o', 0)) > 0 else 0,
                                'volume': int(result.get('v', 0)),
                                'source': 'polygon',
                                'timestamp': datetime.now().isoformat()
                            }
                        else:
                            logger.warning(f"Polygon returned invalid data for {symbol}")
                            return None
                    else:
                        logger.warning(f"Polygon returned status {response.status} for {symbol}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching {symbol} from Polygon: {str(e)}")
            return None
    
    async def get_stock_marketstack(self, symbol: str) -> Optional[Dict]:
        """Marketstack - Limited source (100/month free)"""
        if not self._can_call_api('marketstack'):
            logger.warning(f"Marketstack rate limit reached or no API key, skipping request for {symbol}")
            return None
        
        try:
            self._record_api_call('marketstack')
            logger.info(f"Fetching {symbol} from Marketstack")
            
            url = f"http://api.marketstack.com/v1/eod/latest?access_key={self.marketstack_key}&symbols={symbol}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('data') and len(data['data']) > 0:
                            stock_data = data['data'][0]
                            
                            logger.info(f"Successfully fetched {symbol} from Marketstack: ${float(stock_data.get('close', 0)):.2f}")
                            
                            return {
                                'symbol': symbol,
                                'price': float(stock_data.get('close', 0)),
                                'change': float(stock_data.get('close', 0)) - float(stock_data.get('open', stock_data.get('close', 0))),
                                'change_percent': ((float(stock_data.get('close', 0)) / float(stock_data.get('open', 1)) - 1) * 100) if float(stock_data.get('open', 0)) > 0 else 0,
                                'volume': int(stock_data.get('volume', 0)),
                                'source': 'marketstack',
                                'timestamp': stock_data.get('date', datetime.now().isoformat())
                            }
                        else:
                            logger.warning(f"Marketstack returned invalid data for {symbol}")
                            return None
                    else:
                        logger.warning(f"Marketstack returned status {response.status} for {symbol}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching {symbol} from Marketstack: {str(e)}")
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
            
        # 5. Polygon (5/min)
        data = await self.get_stock_polygon(symbol)
        if data:
            return data
            
        # 6. Marketstack (100/month) - Use sparingly!
        data = await self.get_stock_marketstack(symbol)
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
        
        # If API key manager is available, use it to get status
        if api_keys:
            return api_keys.get_usage_summary()
        
        # Otherwise, use our internal tracking
        return {
            'yahoo': {
                'calls_last_minute': len([t for t in self.api_calls['yahoo'] if t > now - 60]),
                'limit_per_minute': 100,  # self-imposed
                'official_limit': 'None (unofficial API)'
            },
            'finnhub': {
                'calls_last_minute': len([t for t in self.api_calls['finnhub'] if t > now - 60]),
                'limit_per_minute': 60,
                'remaining': 60 - len([t for t in self.api_calls['finnhub'] if t > now - 60]),
                'has_key': bool(self.finnhub_key)
            },
            'twelve_data': {
                'calls_last_minute': len([t for t in self.api_calls['twelve_data']['minute'] if t > now - 60]),
                'limit_per_minute': 8,
                'daily_usage': self.api_calls['twelve_data']['daily'],
                'daily_limit': 800,
                'daily_remaining': 800 - self.api_calls['twelve_data']['daily'],
                'has_key': bool(self.twelve_data_key)
            },
            'alpha_vantage': {
                'calls_last_minute': len([t for t in self.api_calls['alpha_vantage'] if t > now - 60]),
                'limit_per_minute': 5,
                'remaining': 5 - len([t for t in self.api_calls['alpha_vantage'] if t > now - 60]),
                'has_key': bool(self.alpha_vantage_key)
            },
            'polygon': {
                'calls_last_minute': len([t for t in self.api_calls['polygon'] if t > now - 60]),
                'limit_per_minute': 5,
                'remaining': 5 - len([t for t in self.api_calls['polygon'] if t > now - 60]),
                'has_key': bool(self.polygon_key)
            },
            'marketstack': {
                'monthly_usage': self.api_calls['marketstack']['monthly'],
                'monthly_limit': 100,
                'monthly_remaining': 100 - self.api_calls['marketstack']['monthly'],
                'has_key': bool(self.marketstack_key)
            },
            'coingecko': {
                'calls_last_minute': len([t for t in self.api_calls['coingecko'] if t > now - 60]),
                'limit_per_minute': 30,  # unofficial
                'remaining': 30 - len([t for t in self.api_calls['coingecko'] if t > now - 60])
            }
        }

# Create a singleton instance
optimal_apis = OptimalFreeAPIs() 