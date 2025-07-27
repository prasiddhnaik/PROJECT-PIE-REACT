"""
Provider Factory - Dynamic provider instantiation and failover management
Creates provider instances based on registry configuration with health awareness
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Type, Union
import importlib
import inspect
import os
import logging

# YAML import with proper error handling
try:
    import yaml
except ImportError:
    yaml = None
from .http_client import HTTPClient
from .cache import get_health_cache

from health_cache import HealthCache

logger = logging.getLogger(__name__)

# Import crypto provider classes with absolute imports
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
    from providers.crypto.base_crypto_provider import BaseCryptoProvider
    from providers.crypto.coinbase_provider import CoinbaseProvider
    from providers.crypto.binance_provider import BinanceProvider
    from providers.crypto.kraken_provider import KrakenProvider
    from providers.crypto.coingecko_provider import CoinGeckoProvider
    from providers.crypto.generic_crypto_provider import GenericCryptoProvider
except ImportError as e:
    # Fallback if crypto providers are not available
    logger.warning(f"Crypto providers not available: {e}")
    BaseCryptoProvider = None
    CoinbaseProvider = None
    BinanceProvider = None
    KrakenProvider = None
    CoinGeckoProvider = None
    GenericCryptoProvider = None

class ProviderFactory:
    """
    Factory for creating and managing provider instances
    Integrates with health cache for intelligent provider selection
    """
    
    def __init__(self, config_path: str = "config/provider_registry.yaml"):
        self.config_path = config_path
        self.providers_config = self._load_providers_config()
        self.provider_classes = {}
        self._register_provider_classes()
        self.logger = logging.getLogger(__name__)
    
    def _register_provider_classes(self):
        """Register all available provider classes."""
        # Existing stock providers
        self.provider_classes.update({
            'alpha_vantage': AlphaVantageProvider,
            'finnhub': FinnhubProvider,
            'twelve_data': TwelveDataProvider,
            'generic_http': GenericHTTPProvider
        })
        
        # Register crypto provider classes
        if CoinbaseProvider:
            self.provider_classes.update({
                # Major Exchanges - Enhanced mappings
                'coinbase_pro': CoinbaseProvider,
                'coinbase': CoinbaseProvider,
                'binance': BinanceProvider,
                'binance_pro': BinanceProvider,
                'kraken_pro': KrakenProvider,
                'kraken': KrakenProvider,
                'coinmarketcap_pro': CoinMarketCapProvider,
                'coinmarketcap': CoinMarketCapProvider,
                'bitfinex': GenericCryptoProvider,
                'huobi': GenericCryptoProvider,
                'okx': GenericCryptoProvider,
                'kucoin': GenericCryptoProvider,
                'gate_io': GenericCryptoProvider,
                'bybit': GenericCryptoProvider,
                'bitget': GenericCryptoProvider,
                'mexc': GenericCryptoProvider,
                
                # Data Aggregators
                'coingecko_pro': CoinGeckoProvider,
                'coingecko': CoinGeckoProvider,
                'cryptocompare_pro': GenericCryptoProvider,
                'cryptocompare': GenericCryptoProvider,
                'nomics': GenericCryptoProvider,
                'coinapi': GenericCryptoProvider,
                'coincap': GenericCryptoProvider,
                'coinranking': GenericCryptoProvider,
                'coincodex': GenericCryptoProvider,
                'coinstats': GenericCryptoProvider,
                'coincheckup': GenericCryptoProvider,
                
                # DeFi Protocols
                'uniswap': GenericCryptoProvider,
                'pancakeswap': GenericCryptoProvider,
                'sushiswap': GenericCryptoProvider,
                '1inch': GenericCryptoProvider,
                'curve': GenericCryptoProvider,
                'balancer': GenericCryptoProvider,
                'compound': GenericCryptoProvider,
                'aave': GenericCryptoProvider,
                
                # Blockchain APIs
                'etherscan': GenericCryptoProvider,
                'bscscan': GenericCryptoProvider,
                'polygonscan': GenericCryptoProvider,
                'moralis': GenericCryptoProvider,
                'alchemy': GenericCryptoProvider,
                'infura': GenericCryptoProvider,
                'quicknode': GenericCryptoProvider,
                'ankr': GenericCryptoProvider,
                'getblock': GenericCryptoProvider,
                'nownodes': GenericCryptoProvider,
                
                # News & Sentiment
                'cryptopanic': GenericCryptoProvider,
                'cointelegraph': GenericCryptoProvider,
                'cryptonews': GenericCryptoProvider,
                'lunarcrush': GenericCryptoProvider,
                'santiment': GenericCryptoProvider,
                'messari': GenericCryptoProvider,
                
                # Technical Analysis
                'tradingview': GenericCryptoProvider,
                'coinigy': GenericCryptoProvider,
                'cryptowatch': GenericCryptoProvider,
                'bitcoinaverage': GenericCryptoProvider,
                'coinmetrics': GenericCryptoProvider,
                'glassnode': GenericCryptoProvider
            })
    
    def get_available_providers(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available providers, optionally filtered by category."""
        try:
            all_providers = []
            
            # Get providers from all categories
            for provider_category, providers in self.providers_config.get('providers', {}).items():
                if category and provider_category != f"{category}_providers":
                    continue
                    
                for provider_config in providers:
                    # Check if provider class is available
                    provider_id = provider_config.get('id')
                    if provider_id in self.provider_classes:
                        # Check if required environment keys are available
                        required_keys = provider_config.get('required_env_keys', [])
                        if self._check_api_keys_available(required_keys):
                            all_providers.append(provider_config)
                        else:
                            self.logger.debug(f"Provider {provider_id} disabled: missing API keys {required_keys}")
            
            # Sort by priority score and health status
            all_providers.sort(key=lambda p: (
                p.get('priority_score', 0),
                1 if self.get_provider_health_status(p.get('id', '')).get('status') == 'healthy' else 0
            ), reverse=True)
            
            return all_providers
            
        except Exception as e:
            self.logger.error(f"Error getting available providers: {str(e)}")
            return []
    
    def create_provider(self, provider_id: str) -> Optional[Any]:
        """Create and return a provider instance."""
        try:
            if provider_id not in self.provider_classes:
                self.logger.error(f"Unknown provider: {provider_id}")
                return None
            
            # Find provider config
            provider_config = self._find_provider_config(provider_id)
            if not provider_config:
                self.logger.error(f"No configuration found for provider: {provider_id}")
                return None
            
            # Check API key availability
            required_keys = provider_config.get('required_env_keys', [])
            if not self._check_api_keys_available(required_keys):
                self.logger.warning(f"Provider {provider_id} missing required API keys: {required_keys}")
                return None
            
            # Create provider instance
            provider_class = self.provider_classes[provider_id]
            provider_instance = provider_class(provider_config)
            
            self.logger.debug(f"Created provider instance: {provider_id}")
            return provider_instance
            
        except Exception as e:
            self.logger.error(f"Error creating provider {provider_id}: {str(e)}")
            return None
    
    def _find_provider_config(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """Find configuration for a specific provider."""
        try:
            for provider_category, providers in self.providers_config.get('providers', {}).items():
                for provider_config in providers:
                    if provider_config.get('id') == provider_id:
                        return provider_config
            return None
        except Exception as e:
            self.logger.error(f"Error finding provider config for {provider_id}: {str(e)}")
            return None
    
    def _check_api_keys_available(self, required_keys: List[str]) -> bool:
        """Check if all required API keys are available in environment."""
        if not required_keys:
            return True
        
        for key in required_keys:
            if not os.getenv(key):
                return False
        
        return True
    
    def get_provider_health_status(self, provider_id: str) -> Dict[str, Any]:
        """Get health status for a specific provider."""
        try:
            health_cache = get_health_cache()
            return health_cache.get_health_status(provider_id) or {
                'status': 'unknown',
                'last_check': None,
                'response_time': None,
                'error_message': None
            }
        except Exception as e:
            self.logger.error(f"Error getting health status for {provider_id}: {str(e)}")
            return {'status': 'error', 'error_message': str(e)}
    
    def get_crypto_providers_by_priority(self) -> List[Dict[str, Any]]:
        """Get crypto providers sorted by priority and health status."""
        try:
            crypto_providers = self.get_available_providers('crypto')
            
            # Add health status to each provider
            for provider in crypto_providers:
                provider_id = provider.get('id')
                health_status = self.get_provider_health_status(provider_id)
                provider['health_status'] = health_status
                
                # Adjust priority based on health
                if health_status.get('status') == 'healthy':
                    provider['effective_priority'] = provider.get('priority_score', 0)
                elif health_status.get('status') == 'degraded':
                    provider['effective_priority'] = provider.get('priority_score', 0) * 0.7
                else:
                    provider['effective_priority'] = 0
            
            # Sort by effective priority
            crypto_providers.sort(key=lambda p: p.get('effective_priority', 0), reverse=True)
            
            return crypto_providers
            
        except Exception as e:
            self.logger.error(f"Error getting crypto providers by priority: {str(e)}")
            return []

# Placeholder provider classes - These would be implemented based on actual APIs
class BaseProvider:
    """Base class for all providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_id = config['id']
        self.base_url = config['base_url']
        self.auth_type = config.get('auth_type', 'none')

class YahooFinanceProvider(BaseProvider):
    """Yahoo Finance provider implementation"""
    pass

class AlphaVantageProvider(BaseProvider):
    """Alpha Vantage provider implementation"""
    pass

class TwelveDataProvider(BaseProvider):
    """Twelve Data provider implementation"""
    pass

class FinnhubProvider(BaseProvider):
    """Finnhub provider implementation"""
    pass

class PolygonProvider(BaseProvider):
    """Polygon.io provider implementation"""
    pass

class IEXCloudProvider(BaseProvider):
    """IEX Cloud provider implementation"""
    pass

class CoinGeckoProvider(BaseProvider):
    """CoinGecko provider implementation"""
    pass

class CoinMarketCapProvider(BaseProvider):
    """CoinMarketCap provider implementation"""
    pass

class BinanceProvider(BaseProvider):
    """Binance provider implementation"""
    pass

class NewsAPIProvider(BaseProvider):
    """NewsAPI provider implementation"""
    pass

class GenericHTTPProvider:
    """Enhanced generic HTTP provider with crypto-specific improvements."""
    
    def __init__(self, provider_config: Dict[str, Any]):
        self.config = provider_config
        self.provider_id = provider_config.get('id')
        self.base_url = provider_config.get('base_url')
        self.auth_type = provider_config.get('auth_type', 'none')
        self.category = provider_config.get('category', 'unknown')
        self.client = HTTPClient()
        self.logger = logging.getLogger(f"{__name__}.{self.provider_id}")
        
        # Initialize crypto-specific features
        if self.category == 'crypto':
            self._setup_crypto_features()

    def _setup_crypto_features(self):
        """Setup crypto-specific features and field mappings."""
        # Common crypto field mappings
        self.crypto_field_mappings = {
            'coinbase': {
                'price': 'price',
                'volume_24h': 'volume',
                'price_change_24h': 'price_change',
                'time': 'time'
            },
            'binance': {
                'price': 'lastPrice',
                'volume_24h': 'volume',
                'price_change_24h': 'priceChange',
                'price_change_percentage_24h': 'priceChangePercent'
            },
            'coingecko': {
                'price': 'current_price',
                'volume_24h': 'total_volume',
                'market_cap': 'market_cap',
                'price_change_percentage_24h': 'price_change_percentage_24h'
            }
        }
        
        # Common crypto health check endpoints
        self.crypto_health_endpoints = {
            'coinbase': '/time',
            'binance': '/ping',
            'coingecko': '/ping',
            'kraken': '/0/public/SystemStatus',
            'default': '/status'
        }

    async def fetch_crypto_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch crypto data with provider-specific handling."""
        try:
            if self.category != 'crypto':
                return None
            
            # Use crypto-specific logic based on provider
            if 'coingecko' in self.provider_id:
                return await self._fetch_coingecko_data(symbol)
            elif 'coinmarketcap' in self.provider_id:
                return await self._fetch_coinmarketcap_data(symbol)
            elif 'binance' in self.provider_id:
                return await self._fetch_binance_data(symbol)
            else:
                return await self._fetch_generic_crypto_data(symbol)
                
        except Exception as e:
            self.logger.error(f"Error fetching crypto data for {symbol}: {str(e)}")
            return None

    async def _fetch_coingecko_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch data from CoinGecko API."""
        try:
            # Convert symbol to CoinGecko ID format
            coin_id = symbol.lower()
            endpoint = f"/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true&include_market_cap=true"
            
            response = await self.client.get(f"{self.base_url}{endpoint}")
            if response and coin_id in response:
                coin_data = response[coin_id]
                return {
                    'symbol': symbol,
                    'price': coin_data.get('usd', 0),
                    'volume_24h': coin_data.get('usd_24h_vol', 0),
                    'market_cap': coin_data.get('usd_market_cap'),
                    'price_change_percentage_24h': coin_data.get('usd_24h_change'),
                    'provider_source': self.provider_id
                }
            
        except Exception as e:
            self.logger.error(f"CoinGecko fetch error: {str(e)}")
        
        return None

    async def _fetch_coinmarketcap_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch data from CoinMarketCap API."""
        try:
            endpoint = f"/v1/cryptocurrency/quotes/latest?symbol={symbol.upper()}"
            headers = {}
            
            # Add API key if available
            api_key = os.getenv('COINMARKETCAP_API_KEY')
            if api_key:
                headers['X-CMC_PRO_API_KEY'] = api_key
            
            response = await self.client.get(f"{self.base_url}{endpoint}", headers=headers)
            if response and 'data' in response and symbol.upper() in response['data']:
                coin_data = response['data'][symbol.upper()]
                quote_data = coin_data.get('quote', {}).get('USD', {})
                
                return {
                    'symbol': symbol,
                    'price': quote_data.get('price', 0),
                    'volume_24h': quote_data.get('volume_24h', 0),
                    'market_cap': quote_data.get('market_cap'),
                    'price_change_percentage_24h': quote_data.get('percent_change_24h'),
                    'provider_source': self.provider_id
                }
            
        except Exception as e:
            self.logger.error(f"CoinMarketCap fetch error: {str(e)}")
        
        return None

    async def _fetch_binance_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch data from Binance API."""
        try:
            # Convert symbol to Binance format (e.g., BTCUSDT)
            binance_symbol = f"{symbol.upper()}USDT"
            endpoint = f"/api/v3/ticker/24hr?symbol={binance_symbol}"
            
            response = await self.client.get(f"{self.base_url}{endpoint}")
            if response:
                return {
                    'symbol': symbol,
                    'price': float(response.get('lastPrice', 0)),
                    'volume_24h': float(response.get('volume', 0)),
                    'market_cap': None,  # Binance doesn't provide market cap
                    'price_change_percentage_24h': float(response.get('priceChangePercent', 0)),
                    'provider_source': self.provider_id
                }
            
        except Exception as e:
            self.logger.error(f"Binance fetch error: {str(e)}")
        
        return None

    async def _fetch_generic_crypto_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch data using generic crypto patterns."""
        try:
            # Try common endpoint patterns
            endpoints = [
                f"/price/{symbol}",
                f"/ticker/{symbol}",
                f"/v1/crypto/{symbol}",
                f"/api/crypto/{symbol}",
                f"/quote/{symbol}"
            ]
            
            for endpoint in endpoints:
                try:
                    response = await self.client.get(f"{self.base_url}{endpoint}")
                    if response:
                        # Try to extract standard fields
                        return self._normalize_crypto_response(response, symbol)
                except Exception:
                    continue
            
        except Exception as e:
            self.logger.error(f"Generic crypto fetch error: {str(e)}")
        
        return None

    def _normalize_crypto_response(self, response: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """Normalize crypto response to standard format."""
        try:
            # Try different field names for price
            price = None
            for price_field in ['price', 'last_price', 'current_price', 'lastPrice', 'close']:
                if price_field in response:
                    price = float(response[price_field])
                    break
            
            # Try different field names for volume
            volume = None
            for volume_field in ['volume_24h', 'volume', 'total_volume', 'vol', '24h_volume']:
                if volume_field in response:
                    volume = float(response[volume_field])
                    break
            
            # Try different field names for market cap
            market_cap = None
            for cap_field in ['market_cap', 'marketCap', 'market_cap_usd', 'mcap']:
                if cap_field in response:
                    market_cap = float(response[cap_field])
                    break
            
            if price is not None:
                return {
                    'symbol': symbol,
                    'price': price,
                    'volume_24h': volume or 0,
                    'market_cap': market_cap,
                    'provider_source': self.provider_id
                }
            
        except Exception as e:
            self.logger.error(f"Error normalizing crypto response: {str(e)}")
        
        return None

    async def health_check(self) -> bool:
        """Perform health check with crypto-specific endpoints."""
        try:
            # Use crypto-specific health endpoint if available
            if self.category == 'crypto':
                health_endpoint = self.crypto_health_endpoints.get(
                    self.provider_id, 
                    self.crypto_health_endpoints.get('default', '/status')
                )
            else:
                health_endpoint = self.config.get('health_endpoint', '/status')
            
            response = await self.client.get(f"{self.base_url}{health_endpoint}")
            return response is not None
            
        except Exception as e:
            self.logger.error(f"Health check failed for {self.provider_id}: {str(e)}")
            return False

    async def refresh_provider_health(self, provider_id: str):
        """Refresh health status for a specific provider"""
        try:
            provider_config = self.providers_config.get('providers', {}).get(provider_id, {})
            if not provider_config:
                logger.warning(f"Provider config not found for {provider_id}")
                return
            
            # This would typically trigger a health check
            # For now, we'll just log
            logger.info(f"Refreshing health for provider {provider_id}")
            
        except Exception as e:
            logger.error(f"Failed to refresh health for {provider_id}: {e}")
    
    async def get_provider_statistics(self) -> Dict[str, Any]:
        """Get statistics about provider usage and health"""
        try:
            all_providers = self.providers_config.get('providers', {})
            
            stats = {
                'total_providers': len(all_providers),
                'healthy_providers': 0,
                'unhealthy_providers': 0,
                'categories': {},
                'top_providers': []
            }
            
            for provider_category, providers in all_providers.items():
                for provider_config in providers:
                    provider_id = provider_config.get('id')
                    category = provider_config.get('category', 'unknown')
                    
                    # Initialize category stats
                    if category not in stats['categories']:
                        stats['categories'][category] = {
                            'total': 0,
                            'healthy': 0,
                            'unhealthy': 0
                        }
                    
                    stats['categories'][category]['total'] += 1
                    
                    health_status = self.get_provider_health_status(provider_id)
                    if health_status.get('status') == 'healthy':
                        stats['healthy_providers'] += 1
                        stats['categories'][category]['healthy'] += 1
                    else:
                        stats['unhealthy_providers'] += 1
                        stats['categories'][category]['unhealthy'] += 1
            
            # Get top providers by health score
            for provider_category, providers in all_providers.items():
                for provider_config in providers[:10]:  # Top 10
                    provider_id = provider_config.get('id')
                    health_status = self.get_provider_health_status(provider_id)
                    
                    if health_status.get('status') == 'healthy':
                        stats['top_providers'].append({
                            'provider_id': provider_id,
                            'category': provider_config.get('category', 'unknown'),
                            'health_score': health_status.get('health_score', 0),
                            'uptime_percentage': health_status.get('uptime_percentage', 0)
                        })
            
            # Sort top providers by health score
            stats['top_providers'].sort(key=lambda p: p['health_score'], reverse=True)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get provider statistics: {e}")
            return {}
    
    async def cleanup_instances(self):
        """Clean up cached provider instances"""
        try:
            for provider_id, instance in self.provider_classes.items():
                if hasattr(instance, 'cleanup'):
                    try:
                        if inspect.iscoroutinefunction(instance.cleanup):
                            await instance.cleanup()
                        else:
                            instance.cleanup()
                    except Exception as e:
                        logger.warning(f"Failed to cleanup provider {provider_id}: {e}")
            
            self.provider_classes.clear()
            logger.info("Cleaned up all provider instances")
            
        except Exception as e:
            logger.error(f"Failed to cleanup provider instances: {e}")

    def _load_providers_config(self):
        """Load providers configuration from file"""
        try:
            if yaml is None:
                logger.warning("PyYAML not installed, using empty config")
                return {}
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading providers configuration: {str(e)}")
            return {} 