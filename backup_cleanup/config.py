import os
from typing import Optional

class FinancialAPIConfig:
    """Configuration class for Financial Analytics Hub API keys and settings"""
    
    # Alpha Vantage Configuration
    ALPHA_VANTAGE_API_KEY = "K2BDU6HV1QBZAG5E"
    ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
    
    # Other API Keys (to be configured as obtained)
    POLYGON_API_KEY: Optional[str] = None
    TWELVE_DATA_API_KEY: Optional[str] = None
    FINNHUB_API_KEY: Optional[str] = None
    IEX_CLOUD_API_KEY: Optional[str] = None
    MARKETSTACK_API_KEY: Optional[str] = None
    FMP_API_KEY: Optional[str] = None
    TRADING_ECONOMICS_KEY: Optional[str] = None
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_SECRET_KEY: Optional[str] = None
    
    # API Endpoints
    COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
    POLYGON_BASE_URL = "https://api.polygon.io"
    TWELVE_DATA_BASE_URL = "https://api.twelvedata.com"
    FINNHUB_BASE_URL = "https://finnhub.io/api/v1"
    IEX_CLOUD_BASE_URL = "https://cloud.iexapis.com/stable"
    
    # Rate Limiting (requests per minute)
    ALPHA_VANTAGE_RATE_LIMIT = 5  # Free tier: 5 requests per minute
    COINGECKO_RATE_LIMIT = 30     # Public API: 30 requests per minute
    
    # Cache Settings
    CACHE_DURATION_MINUTES = 5
    
    @classmethod
    def get_configured_apis(cls) -> list[str]:
        """Return list of APIs that have been configured with valid keys"""
        configured = []
        
        if cls.ALPHA_VANTAGE_API_KEY:
            configured.append("Alpha Vantage")
        if cls.POLYGON_API_KEY:
            configured.append("Polygon.io")
        if cls.TWELVE_DATA_API_KEY:
            configured.append("Twelve Data")
        if cls.FINNHUB_API_KEY:
            configured.append("Finnhub")
        if cls.IEX_CLOUD_API_KEY:
            configured.append("IEX Cloud")
        if cls.MARKETSTACK_API_KEY:
            configured.append("MarketStack")
        if cls.FMP_API_KEY:
            configured.append("Financial Modeling Prep")
        if cls.TRADING_ECONOMICS_KEY:
            configured.append("Trading Economics")
        if cls.BINANCE_API_KEY and cls.BINANCE_SECRET_KEY:
            configured.append("Binance")
        
        # Always available (no key required)
        configured.extend(["CoinGecko", "Yahoo Finance"])
        
        return configured
    
    @classmethod
    def is_api_configured(cls, api_name: str) -> bool:
        """Check if a specific API is configured"""
        api_checks = {
            "alpha_vantage": bool(cls.ALPHA_VANTAGE_API_KEY),
            "polygon": bool(cls.POLYGON_API_KEY),
            "twelve_data": bool(cls.TWELVE_DATA_API_KEY),
            "finnhub": bool(cls.FINNHUB_API_KEY),
            "iex_cloud": bool(cls.IEX_CLOUD_API_KEY),
            "marketstack": bool(cls.MARKETSTACK_API_KEY),
            "fmp": bool(cls.FMP_API_KEY),
            "trading_economics": bool(cls.TRADING_ECONOMICS_KEY),
            "binance": bool(cls.BINANCE_API_KEY and cls.BINANCE_SECRET_KEY),
            "coingecko": True,  # No key required
            "yahoo_finance": True,  # No key required
        }
        
        return api_checks.get(api_name.lower(), False) 