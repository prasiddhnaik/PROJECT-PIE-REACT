import aiohttp
import asyncio
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from config import APIConfig

logger = logging.getLogger(__name__)

class EnhancedAPIClient:
    """Enhanced API client with multiple financial data sources"""
    
    def __init__(self):
        self.session = None
        self.rate_limiter = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _make_request(self, url: str, headers: Dict = None, timeout: int = 10) -> Optional[Dict]:
        """Make HTTP request with error handling"""
        try:
            async with self.session.get(url, headers=headers, timeout=timeout) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"API request failed: {response.status} for {url}")
                    return None
        except Exception as e:
            logger.error(f"Request error for {url}: {str(e)}")
            return None
    
    async def get_stock_quote_alpha_vantage(self, symbol: str) -> Optional[Dict]:
        """Get stock quote from Alpha Vantage"""
        if not APIConfig.ALPHA_VANTAGE_KEY or APIConfig.ALPHA_VANTAGE_KEY == "demo":
            return None
            
        url = f"{APIConfig.ALPHA_VANTAGE_BASE_URL}?function=GLOBAL_QUOTE&symbol={symbol}&apikey={APIConfig.ALPHA_VANTAGE_KEY}"
        data = await self._make_request(url)
        
        if data and 'Global Quote' in data and '05. price' in data['Global Quote']:
            quote = data['Global Quote']
            return {
                'symbol': symbol,
                'current_price': float(quote['05. price']),
                'previous_close': float(quote['08. previous close']),
                'change': float(quote['09. change']),
                'change_percent': float(quote['10. change percent'].rstrip('%')),
                'volume': int(quote['06. volume']) if quote['06. volume'].isdigit() else 0,
                'source': 'alpha_vantage',
                'timestamp': datetime.now().isoformat()
            }
        return None
    
    async def get_stock_quote_twelve_data(self, symbol: str) -> Optional[Dict]:
        """Get stock quote from Twelve Data"""
        if not APIConfig.TWELVE_DATA_KEY or APIConfig.TWELVE_DATA_KEY == "demo":
            return None
            
        url = f"{APIConfig.TWELVE_DATA_BASE_URL}/quote?symbol={symbol}&apikey={APIConfig.TWELVE_DATA_KEY}"
        data = await self._make_request(url)
        
        if data and 'close' in data:
            return {
                'symbol': symbol,
                'current_price': float(data['close']),
                'previous_close': float(data['previous_close']) if 'previous_close' in data else float(data['close']),
                'change': float(data['change']) if 'change' in data else 0,
                'change_percent': float(data['percent_change']) if 'percent_change' in data else 0,
                'volume': int(data['volume']) if 'volume' in data and str(data['volume']).isdigit() else 0,
                'source': 'twelve_data',
                'timestamp': datetime.now().isoformat()
            }
        return None
    
    async def get_crypto_data_coingecko(self, crypto_id: str, currency: str = "usd") -> Optional[Dict]:
        """Get cryptocurrency data from CoinGecko"""
        url = f"{APIConfig.COINGECKO_BASE_URL}/simple/price?ids={crypto_id}&vs_currencies={currency}&include_24hr_change=true&include_market_cap=true&include_24hr_vol=true"
        data = await self._make_request(url)
        
        if data and crypto_id in data:
            crypto_data = data[crypto_id]
            return {
                'symbol': crypto_id,
                'current_price': float(crypto_data[currency]),
                'change_24h': float(crypto_data.get(f'{currency}_24h_change', 0)),
                'market_cap': float(crypto_data.get(f'{currency}_market_cap', 0)),
                'volume_24h': float(crypto_data.get(f'{currency}_24h_vol', 0)),
                'source': 'coingecko',
                'timestamp': datetime.now().isoformat()
            }
        return None
    
    async def get_crypto_data_coinmarketcap(self, symbol: str, currency: str = "USD") -> Optional[Dict]:
        """Get cryptocurrency data from CoinMarketCap"""
        if not APIConfig.COINMARKETCAP_KEY:
            return None

        headers = {"X-CMC_PRO_API_KEY": APIConfig.COINMARKETCAP_KEY}
        url = f"{APIConfig.COINMARKETCAP_BASE_URL}/cryptocurrency/quotes/latest?symbol={symbol.upper()}&convert={currency.upper()}"
        data = await self._make_request(url, headers=headers)

        if data and "data" in data and symbol.upper() in data["data"]:
            quote = data["data"][symbol.upper()]["quote"][currency.upper()]
            return {
                "symbol": symbol.lower(),
                "current_price": float(quote.get("price", 0)),
                "change_24h": float(quote.get("percent_change_24h", 0)),
                "market_cap": float(quote.get("market_cap", 0)),
                "volume_24h": float(quote.get("volume_24h", 0)),
                "source": "coinmarketcap",
                "timestamp": datetime.now().isoformat()
            }
        return None
    
    async def get_economic_data_fred(self, series_id: str) -> Optional[Dict]:
        """Get economic data from FRED API"""
        if not APIConfig.FRED_API_KEY:
            return None
            
        url = f"{APIConfig.FRED_BASE_URL}/series/observations?series_id={series_id}&api_key={APIConfig.FRED_API_KEY}&file_type=json&limit=1&sort_order=desc"
        data = await self._make_request(url)
        
        if data and 'observations' in data and len(data['observations']) > 0:
            latest = data['observations'][0]
            return {
                'series_id': series_id,
                'value': float(latest['value']) if latest['value'] != '.' else None,
                'date': latest['date'],
                'source': 'fred',
                'timestamp': datetime.now().isoformat()
            }
        return None
    
    async def get_world_bank_data(self, indicator: str, country: str = "US") -> Optional[Dict]:
        """Get data from World Bank API"""
        url = f"{APIConfig.WORLD_BANK_BASE_URL}/country/{country}/indicator/{indicator}?format=json&per_page=1&date=2020:2024"
        data = await self._make_request(url)
        
        if data and isinstance(data, list) and len(data) > 1 and len(data[1]) > 0:
            latest = data[1][0]
            return {
                'indicator': indicator,
                'country': country,
                'value': float(latest['value']) if latest['value'] else None,
                'date': latest['date'],
                'source': 'world_bank',
                'timestamp': datetime.now().isoformat()
            }
        return None
    
    async def get_market_indices(self) -> Dict[str, Any]:
        """Get major market indices from multiple sources"""
        indices_data = {}
        
        # Major indices to track
        indices = {
            'SPY': 'S&P 500 ETF',
            'QQQ': 'NASDAQ 100 ETF', 
            'DIA': 'Dow Jones ETF',
            'IWM': 'Russell 2000 ETF',
            'VTI': 'Total Stock Market ETF'
        }
        
        tasks = []
        for symbol, name in indices.items():
            tasks.append(self._get_index_data(symbol, name))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, dict) and 'symbol' in result:
                indices_data[result['symbol']] = result
        
        return indices_data
    
    async def _get_index_data(self, symbol: str, name: str) -> Optional[Dict]:
        """Get individual index data with fallbacks"""
        # Try Alpha Vantage first
        data = await self.get_stock_quote_alpha_vantage(symbol)
        if data:
            data['name'] = name
            return data
        
        # Try Twelve Data fallback
        data = await self.get_stock_quote_twelve_data(symbol)
        if data:
            data['name'] = name
            return data
        
        # Generate realistic mock data as final fallback
        base_prices = {'SPY': 605.40, 'QQQ': 531.94, 'DIA': 430.33, 'IWM': 210.84, 'VTI': 245.67}
        base_price = base_prices.get(symbol, 400.0)
        
        import random
        current_price = base_price + random.uniform(-2, 2)
        change = random.uniform(-3, 3)
        change_percent = (change / current_price) * 100
        
        return {
            'symbol': symbol,
            'name': name,
            'current_price': round(current_price, 2),
            'previous_close': round(current_price - change, 2),
            'change': round(change, 2),
            'change_percent': round(change_percent, 2),
            'volume': random.randint(10000000, 100000000),
            'source': 'mock_fallback',
            'timestamp': datetime.now().isoformat()
        }
    
    async def get_economic_indicators(self) -> Dict[str, Any]:
        """Get key economic indicators from multiple sources"""
        indicators = {}
        
        # FRED indicators (if available)
        if APIConfig.FRED_API_KEY:
            fred_indicators = {
                'DGS10': 'treasury_yield_10y',
                'VIXCLS': 'vix',
                'UNRATE': 'unemployment_rate',
                'CPIAUCSL': 'inflation_rate'
            }
            
            tasks = []
            for series_id, key in fred_indicators.items():
                tasks.append(self._get_fred_indicator(series_id, key))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, dict) and 'key' in result:
                    indicators[result['key']] = result
        
        # World Bank indicators
        wb_indicators = {
            'NY.GDP.MKTP.CD': 'gdp',
            'FP.CPI.TOTL.ZG': 'inflation_wb'
        }
        
        tasks = []
        for indicator_id, key in wb_indicators.items():
            tasks.append(self._get_wb_indicator(indicator_id, key))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, dict) and 'key' in result:
                indicators[result['key']] = result
        
        # Generate fallback indicators if APIs unavailable
        if not indicators:
            import random
            indicators = {
                'treasury_yield_10y': {
                    'key': 'treasury_yield_10y',
                    'value': round(4.3 + random.uniform(-0.3, 0.7), 2),
                    'source': 'mock_fallback'
                },
                'vix': {
                    'key': 'vix',
                    'value': round(18.5 + random.uniform(-3, 7), 2),
                    'source': 'mock_fallback'
                }
            }
        
        return indicators
    
    async def _get_fred_indicator(self, series_id: str, key: str) -> Optional[Dict]:
        """Get FRED economic indicator"""
        data = await self.get_economic_data_fred(series_id)
        if data and data['value'] is not None:
            return {
                'key': key,
                'value': data['value'],
                'date': data['date'],
                'source': 'fred'
            }
        return None
    
    async def _get_wb_indicator(self, indicator_id: str, key: str) -> Optional[Dict]:
        """Get World Bank indicator"""
        data = await self.get_world_bank_data(indicator_id)
        if data and data['value'] is not None:
            return {
                'key': key,
                'value': data['value'],
                'date': data['date'],
                'source': 'world_bank'
            }
        return None
    
    async def get_trending_stocks(self) -> List[Dict]:
        """Get trending stocks from multiple sources"""
        # Popular stocks to track
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
        
        tasks = []
        for symbol in symbols:
            tasks.append(self._get_trending_stock_data(symbol))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        trending_stocks = []
        for result in results:
            if isinstance(result, dict) and 'symbol' in result:
                trending_stocks.append(result)
        
        return trending_stocks
    
    async def _get_trending_stock_data(self, symbol: str) -> Optional[Dict]:
        """Get individual trending stock data"""
        # Try multiple sources
        data = await self.get_stock_quote_alpha_vantage(symbol)
        if not data:
            data = await self.get_stock_quote_twelve_data(symbol)
        
        if data:
            # Add additional info for trending display
            stock_names = {
                'AAPL': 'Apple Inc.',
                'GOOGL': 'Alphabet Inc.',
                'MSFT': 'Microsoft Corporation',
                'AMZN': 'Amazon.com Inc.',
                'TSLA': 'Tesla Inc.',
                'META': 'Meta Platforms Inc.',
                'NVDA': 'NVIDIA Corporation',
                'NFLX': 'Netflix Inc.'
            }
            
            return {
                'symbol': symbol,
                'name': stock_names.get(symbol, f"{symbol} Corporation"),
                'price': data['current_price'],
                'change_percent': data['change_percent'],
                'volume': data['volume'],
                'source': data['source']
            }
        
        return None

# Utility functions for API management
async def test_api_connectivity() -> Dict[str, bool]:
    """Test connectivity to all configured APIs"""
    async with EnhancedAPIClient() as client:
        results = {}
        
        # Test Alpha Vantage
        try:
            data = await client.get_stock_quote_alpha_vantage('AAPL')
            results['alpha_vantage'] = data is not None
        except:
            results['alpha_vantage'] = False
        
        # Test Twelve Data
        try:
            data = await client.get_stock_quote_twelve_data('AAPL')
            results['twelve_data'] = data is not None
        except:
            results['twelve_data'] = False
        
        # Test CoinGecko
        try:
            data = await client.get_crypto_data_coingecko('bitcoin')
            results['coingecko'] = data is not None
        except:
            results['coingecko'] = False
        
        # Test FRED (if configured)
        if APIConfig.FRED_API_KEY:
            try:
                data = await client.get_economic_data_fred('DGS10')
                results['fred'] = data is not None
            except:
                results['fred'] = False
        else:
            results['fred'] = False
        
        # Test World Bank
        try:
            data = await client.get_world_bank_data('NY.GDP.MKTP.CD')
            results['world_bank'] = data is not None
        except:
            results['world_bank'] = False
    
    return results

async def get_api_status_summary() -> Dict[str, Any]:
    """Get comprehensive API status summary"""
    connectivity = await test_api_connectivity()
    config_status = APIConfig.validate_configuration()
    
    return {
        'connectivity_test': connectivity,
        'configuration': config_status,
        'total_working_apis': sum(1 for working in connectivity.values() if working),
        'critical_apis_working': sum(1 for api in ['alpha_vantage', 'twelve_data'] if connectivity.get(api, False)),
        'timestamp': datetime.now().isoformat()
    } 