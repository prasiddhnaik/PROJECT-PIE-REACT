import os
from typing import Optional

class APIConfig:
    """Configuration for all financial data APIs"""
    
    # Alpha Vantage API
    ALPHA_VANTAGE_KEY: str = "K2BDU6HV1QBZAG5E"
    ALPHA_VANTAGE_BASE_URL: str = "https://www.alphavantage.co/query"
    
    # Twelve Data API
    TWELVE_DATA_KEY: str = "2df82f24652f4fb08d90fcd537a97e9c"
    TWELVE_DATA_BASE_URL: str = "https://api.twelvedata.com"
    
    # CoinGecko API (Free tier - no key required)
    COINGECKO_BASE_URL: str = "https://api.coingecko.com/api/v3"
    
    # Finnhub API
    FINNHUB_KEY: str = "d16k039r01qvtdbj2gtgd16k039r01qvtdbj2gu0"
    FINNHUB_BASE_URL: str = "https://finnhub.io/api/v1"
    
    # Polygon.io API
    POLYGON_KEY: str = "SavZMeuTDTxjWJuFzBO6zES7mBFK68RJ"
    POLYGON_BASE_URL: str = "https://api.polygon.io"
    
    # IEX Cloud API  
    IEX_CLOUD_KEY: Optional[str] = os.getenv("IEX_CLOUD_API_KEY")
    IEX_CLOUD_BASE_URL: str = "https://cloud.iexapis.com/stable"
    
    # Yahoo Finance (via yfinance - no key required)
    YAHOO_FINANCE_AVAILABLE: bool = True
    
    # Fred Economic Data API
    FRED_API_KEY: str = "ad8f3f64b13b3990119177b793f4d483"
    FRED_BASE_URL: str = "https://api.stlouisfed.org/fred"
    
    # Quandl API
    QUANDL_API_KEY: Optional[str] = os.getenv("QUANDL_API_KEY")
    QUANDL_BASE_URL: str = "https://www.quandl.com/api/v3"
    
    # World Bank API (no key required)
    WORLD_BANK_BASE_URL: str = "https://api.worldbank.org/v2"
    
    # Rate limiting settings
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 500
    
    # Cache settings
    DEFAULT_CACHE_MINUTES: int = 15
    MARKET_DATA_CACHE_MINUTES: int = 5
    CRYPTO_CACHE_MINUTES: int = 10
    
    # Update intervals
    BACKGROUND_UPDATE_INTERVAL_MINUTES: int = 13
    
    # Backup API configuration
    USE_FALLBACK_DATA: bool = True
    FALLBACK_DATA_CONFIDENCE: float = 0.6
    
    @classmethod
    def get_available_apis(cls) -> dict:
        """Return a dictionary of available APIs and their status"""
        return {
            'alpha_vantage': bool(cls.ALPHA_VANTAGE_KEY and cls.ALPHA_VANTAGE_KEY != "demo"),
            'twelve_data': bool(cls.TWELVE_DATA_KEY and cls.TWELVE_DATA_KEY != "demo"),
            'coingecko': True,  # Always available (free tier)
            'finnhub': bool(cls.FINNHUB_KEY and cls.FINNHUB_KEY != "demo"),
            'polygon': bool(cls.POLYGON_KEY),
            'iex_cloud': bool(cls.IEX_CLOUD_KEY),
            'yahoo_finance': cls.YAHOO_FINANCE_AVAILABLE,
            'fred': bool(cls.FRED_API_KEY),
            'quandl': bool(cls.QUANDL_API_KEY),
            'world_bank': True  # Always available (free)
        }
    
    @classmethod
    def get_api_count(cls) -> int:
        """Return the number of available APIs"""
        return sum(1 for available in cls.get_available_apis().values() if available)
    
    @classmethod
    def validate_configuration(cls) -> dict:
        """Validate the current API configuration"""
        available_apis = cls.get_available_apis()
        total_apis = cls.get_api_count()
        
        # Check if we have enough APIs for redundancy
        critical_apis = ['alpha_vantage', 'twelve_data', 'yahoo_finance']
        critical_available = sum(1 for api in critical_apis if available_apis.get(api, False))
        
        return {
            'total_apis': total_apis,
            'available_apis': available_apis,
            'critical_apis_available': critical_available,
            'redundancy_sufficient': critical_available >= 2,
            'configuration_valid': total_apis >= 3
        }

# Default symbols for tracking
DEFAULT_STOCK_SYMBOLS = [
    'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
    'JPM', 'JNJ', 'V', 'PG', 'UNH', 'HD', 'MA', 'BAC'
]

DEFAULT_CRYPTO_SYMBOLS = [
    'bitcoin', 'ethereum', 'binancecoin', 'cardano', 'solana',
    'polkadot', 'chainlink', 'litecoin', 'polygon', 'avalanche-2'
]

MAJOR_INDICES = {
    'SPY': 'S&P 500 ETF',
    'QQQ': 'NASDAQ 100 ETF',
    'DIA': 'Dow Jones ETF',
    'IWM': 'Russell 2000 ETF',
    'VTI': 'Total Stock Market ETF',
    'EFA': 'MSCI EAFE ETF'
}

# API prioritization for different data types
API_PRIORITY = {
    'stock_quotes': ['yahoo_finance', 'alpha_vantage', 'twelve_data', 'finnhub', 'iex_cloud'],
    'crypto_data': ['coingecko', 'twelve_data'],
    'market_indices': ['yahoo_finance', 'alpha_vantage', 'twelve_data'],
    'economic_data': ['fred', 'world_bank', 'alpha_vantage'],
    'historical_data': ['yahoo_finance', 'alpha_vantage', 'twelve_data', 'polygon']
} 