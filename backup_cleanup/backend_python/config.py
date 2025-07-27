import os
from typing import Optional, Dict, List
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8001"))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Analytics Configuration
ENABLE_ANALYTICS = os.getenv("ENABLE_ANALYTICS", "True").lower() == "true"
ANALYTICS_MOCK_MODE = os.getenv("ANALYTICS_MOCK_MODE", "False").lower() == "true"

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./financial_analytics.db")

# API Keys and secrets
API_KEYS = {
    # Stock Data Providers
    "ALPHA_VANTAGE_API_KEY": os.getenv("ALPHA_VANTAGE_API_KEY"),
    "FINNHUB_API_KEY": os.getenv("FINNHUB_API_KEY"),
    "POLYGON_API_KEY": os.getenv("POLYGON_API_KEY"),
    "TWELVE_DATA_API_KEY": os.getenv("TWELVE_DATA_API_KEY"),
    "IEX_CLOUD_API_KEY": os.getenv("IEX_CLOUD_API_KEY"),
    
    # Major Crypto Exchanges
    "COINBASE_API_KEY": os.getenv("COINBASE_API_KEY"),
    "BINANCE_API_KEY": os.getenv("BINANCE_API_KEY"),
    "KRAKEN_API_KEY": os.getenv("KRAKEN_API_KEY"),
    "BITFINEX_API_KEY": os.getenv("BITFINEX_API_KEY"),
    "HUOBI_API_KEY": os.getenv("HUOBI_API_KEY"),
    "OKX_API_KEY": os.getenv("OKX_API_KEY"),
    "KUCOIN_API_KEY": os.getenv("KUCOIN_API_KEY"),
    "GATE_IO_API_KEY": os.getenv("GATE_IO_API_KEY"),
    "BYBIT_API_KEY": os.getenv("BYBIT_API_KEY"),
    "BITGET_API_KEY": os.getenv("BITGET_API_KEY"),
    "MEXC_API_KEY": os.getenv("MEXC_API_KEY"),
    
    # Data Aggregators
    "COINGECKO_API_KEY": os.getenv("COINGECKO_API_KEY"),
    "COINMARKETCAP_API_KEY": os.getenv("COINMARKETCAP_API_KEY"),
    "CRYPTOCOMPARE_API_KEY": os.getenv("CRYPTOCOMPARE_API_KEY"),
    "NOMICS_API_KEY": os.getenv("NOMICS_API_KEY"),
    "COINAPI_KEY": os.getenv("COINAPI_KEY"),
    "COINCAP_API_KEY": os.getenv("COINCAP_API_KEY"),
    "COINRANKING_API_KEY": os.getenv("COINRANKING_API_KEY"),
    
    # Blockchain APIs
    "ETHERSCAN_API_KEY": os.getenv("ETHERSCAN_API_KEY"),
    "BSCSCAN_API_KEY": os.getenv("BSCSCAN_API_KEY"),
    "POLYGONSCAN_API_KEY": os.getenv("POLYGONSCAN_API_KEY"),
    "MORALIS_API_KEY": os.getenv("MORALIS_API_KEY"),
    "ALCHEMY_API_KEY": os.getenv("ALCHEMY_API_KEY"),
    "INFURA_API_KEY": os.getenv("INFURA_API_KEY"),
    
    # News & Sentiment
    "CRYPTOPANIC_API_KEY": os.getenv("CRYPTOPANIC_API_KEY"),
    "NEWSAPI_KEY": os.getenv("NEWSAPI_KEY"),
    "LUNARCRUSH_API_KEY": os.getenv("LUNARCRUSH_API_KEY"),
    "SANTIMENT_API_KEY": os.getenv("SANTIMENT_API_KEY"),
    
    # AI & Analytics
    "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")
}

# OpenRouter AI Configuration
OPENROUTER_CONFIG = {
    "api_key": os.getenv("OPENROUTER_API_KEY", ""),
    "base_url": "https://openrouter.ai/api/v1",
    "site_url": "https://financial-analytics-hub.com",
    "app_name": "Financial Analytics Hub",
    
    # Default models for different use cases
    "default_models": {
        "stock_analysis": "openai/gpt-4o-mini",  # Best overall free model
        "portfolio_optimization": "anthropic/claude-3-haiku",  # Fast reasoning
        "market_sentiment": "google/gemini-flash-1.5",  # Free multimodal
        "trading_signals": "qwen/qwen-2.5-72b-instruct",  # Data analysis
        "risk_analysis": "meta-llama/llama-3.1-405b-instruct",  # Powerful reasoning
        "quick_analysis": "mistralai/mistral-7b-instruct"  # Fast responses
    },
    
    # Model usage limits per day (free tier)
    "usage_limits": {
        "openai/gpt-4o-mini": 1000000,  # 1M tokens/day
        "anthropic/claude-3-haiku": 500000,  # 500K tokens/day
        "google/gemini-flash-1.5": -1,  # Unlimited free
        "qwen/qwen-2.5-72b-instruct": -1,  # Unlimited free
        "meta-llama/llama-3.1-405b-instruct": 100000,  # 100K tokens/day
        "mistralai/mistral-7b-instruct": -1  # Unlimited free
    },
    
    # Cost tracking (USD per 1M tokens)
    "token_costs": {
        "openai/gpt-4o-mini": 0.15,
        "anthropic/claude-3-haiku": 0.25,
        "google/gemini-flash-1.5": 0.0,
        "qwen/qwen-2.5-72b-instruct": 0.0,
        "meta-llama/llama-3.1-405b-instruct": 0.0,
        "mistralai/mistral-7b-instruct": 0.0
    }
}

# AI Feature Flags
AI_FEATURES = {
    "enable_ai_analysis": os.getenv("ENABLE_AI_ANALYSIS", "True").lower() == "true",
    "enable_ai_trading_signals": os.getenv("ENABLE_AI_TRADING_SIGNALS", "True").lower() == "true",
    "enable_ai_portfolio_optimization": os.getenv("ENABLE_AI_PORTFOLIO_OPTIMIZATION", "True").lower() == "true",
    "enable_ai_sentiment_analysis": os.getenv("ENABLE_AI_SENTIMENT_ANALYSIS", "True").lower() == "true",
    "enable_ai_risk_analysis": os.getenv("ENABLE_AI_RISK_ANALYSIS", "True").lower() == "true",
    "enable_ai_streaming": os.getenv("ENABLE_AI_STREAMING", "True").lower() == "true",
    "ai_mock_mode": os.getenv("AI_MOCK_MODE", "False").lower() == "true"
}

# Rate Limiting Configuration
RATE_LIMITS = {
    "default": "100/minute",
    "ai_endpoints": "20/minute",
    "data_endpoints": "50/minute",
    "auth_endpoints": "10/minute"
}

# Cache Configuration
CACHE_CONFIG = {
    "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
    "default_ttl": 300,  # 5 minutes
    "market_data_ttl": 60,  # 1 minute
    "ai_analysis_ttl": 1800,  # 30 minutes
    "news_ttl": 900  # 15 minutes
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": os.getenv("LOG_FILE", "logs/financial_analytics.log"),
    "max_size": "10MB",
    "backup_count": 5
}

# Security Configuration
SECURITY_CONFIG = {
    "secret_key": os.getenv("SECRET_KEY", "your-secret-key-change-in-production"),
    "algorithm": "HS256",
    "access_token_expire_minutes": 30,
    "allowed_origins": [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://financial-analytics-hub.com"
    ]
}

# Data Sources Priority (for fallback)
DATA_SOURCE_PRIORITY = [
    "yahoo_finance",
    "alpha_vantage", 
    "finnhub",
    "twelve_data",
    "polygon",
    "iex"
]

# Mock Data Configuration
MOCK_DATA_CONFIG = {
    "enable_mock": os.getenv("ENABLE_MOCK_DATA", "False").lower() == "true",
    "mock_delay": float(os.getenv("MOCK_DELAY", "0.1")),  # Simulate API delay
    "mock_error_rate": float(os.getenv("MOCK_ERROR_RATE", "0.0"))  # Error simulation
}

class APIConfig:
    """Enhanced API Configuration with crypto provider management."""
    
    def __init__(self):
        self.api_keys = API_KEYS
        self.rate_limits = self._load_rate_limits()
        self.crypto_providers = self._load_crypto_providers()
    
    def _load_crypto_providers(self):
        """Load crypto provider configurations."""
        return {
            "major_exchanges": ["COINBASE", "BINANCE", "KRAKEN", "BITFINEX", "HUOBI"],
            "data_aggregators": ["COINGECKO", "COINMARKETCAP", "CRYPTOCOMPARE", "NOMICS"],
            "blockchain_apis": ["ETHERSCAN", "BSCSCAN", "POLYGONSCAN", "MORALIS"],
            "news_sentiment": ["CRYPTOPANIC", "NEWSAPI", "LUNARCRUSH", "SANTIMENT"]
        }
    
    def check_crypto_provider_availability(self, provider_type: str = None) -> Dict[str, bool]:
        """Check availability of crypto providers by type."""
        availability = {}
        
        if provider_type:
            providers = self.crypto_providers.get(provider_type, [])
        else:
            providers = []
            for category in self.crypto_providers.values():
                providers.extend(category)
        
        for provider in providers:
            key_name = f"{provider}_API_KEY"
            availability[provider.lower()] = bool(self.api_keys.get(key_name))
        
        return availability
    
    def get_available_crypto_providers(self) -> List[str]:
        """Get list of all available crypto providers with valid API keys."""
        available = []
        for provider_category in self.crypto_providers.values():
            for provider in provider_category:
                key_name = f"{provider}_API_KEY"
                if self.api_keys.get(key_name):
                    available.append(provider.lower())
        return available
    
    def enable_provider(self, provider_id: str) -> bool:
        """Enable a crypto provider if API key is available."""
        key_name = f"{provider_id.upper()}_API_KEY"
        return bool(self.api_keys.get(key_name))
    
    def disable_provider(self, provider_id: str) -> bool:
        """Disable a crypto provider (implementation for future use)."""
        # This could be extended to maintain a disabled providers list
        return True
    
    def get_provider_key(self, provider_id: str) -> Optional[str]:
        """Get API key for a specific provider."""
        key_name = f"{provider_id.upper()}_API_KEY"
        return self.api_keys.get(key_name)

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
    'crypto_data': ['coingecko', 'coinmarketcap', 'twelve_data'],
    'market_indices': ['yahoo_finance', 'alpha_vantage', 'twelve_data'],
    'economic_data': ['fred', 'world_bank', 'alpha_vantage'],
    'historical_data': ['yahoo_finance', 'alpha_vantage', 'twelve_data', 'polygon']
} 