"""
CoinMarketCap Provider - Professional crypto data aggregator
Priority Score: 87 (High-priority data aggregator in failover chain)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os

from .base_crypto_provider import BaseCryptoProvider, CryptoDataPoint
from services.common.http_client import HTTPClient


class CoinMarketCapProvider(BaseCryptoProvider):
    """
    CoinMarketCap provider for comprehensive crypto market data
    Supports quotes, historical data, and market cap rankings
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://pro-api.coinmarketcap.com"
        self.api_key = os.getenv("COINMARKETCAP_API_KEY")
        self.client = HTTPClient()
        self.logger = logging.getLogger(__name__)
        
        # CoinMarketCap symbol mappings (CMC uses symbol lookup)
        self.symbol_to_id = {
            'BTC': 1,
            'ETH': 1027,
            'BNB': 1839,
            'XRP': 52,
            'ADA': 2010,
            'SOL': 5426,
            'DOGE': 74,
            'DOT': 6636,
            'MATIC': 3890,
            'LTC': 2,
            'AVAX': 5805,
            'LINK': 1975,
            'UNI': 7083,
            'ATOM': 3794,
            'XLM': 512
        }
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with API key for CoinMarketCap requests."""
        headers = {
            'Accepts': 'application/json',
            'Accept-Encoding': 'deflate, gzip'
        }
        
        if self.api_key:
            headers['X-CMC_PRO_API_KEY'] = self.api_key
        
        return headers
    
    def _get_cmc_id(self, symbol: str) -> Optional[int]:
        """Get CoinMarketCap ID for symbol."""
        return self.symbol_to_id.get(symbol.upper())
    
    async def fetch_quote(self, symbol: str) -> Optional[CryptoDataPoint]:
        """Fetch current quote from CoinMarketCap quotes endpoint."""
        try:
            cmc_id = self._get_cmc_id(symbol)
            
            if cmc_id:
                # Use ID-based endpoint for better reliability
                endpoint = f"/v2/cryptocurrency/quotes/latest?id={cmc_id}"
            else:
                # Fallback to symbol-based endpoint
                endpoint = f"/v2/cryptocurrency/quotes/latest?symbol={symbol.upper()}"
            
            headers = self._get_headers()
            response = await self.client.get(f"{self.base_url}{endpoint}", headers=headers)
            
            if not response or 'status' not in response:
                self.logger.error("Invalid CoinMarketCap API response")
                return None
            
            if response['status']['error_code'] != 0:
                self.logger.error(f"CoinMarketCap API error: {response['status']['error_message']}")
                return None
            
            # Extract cryptocurrency data
            data = response.get('data', {})
            
            # Handle both ID and symbol response formats
            crypto_data = None
            if cmc_id and str(cmc_id) in data:
                crypto_data = data[str(cmc_id)][0] if isinstance(data[str(cmc_id)], list) else data[str(cmc_id)]
            elif symbol.upper() in data:
                crypto_data = data[symbol.upper()][0] if isinstance(data[symbol.upper()], list) else data[symbol.upper()]
            
            if not crypto_data:
                self.logger.warning(f"No data found for symbol {symbol} in CoinMarketCap response")
                return None
            
            # Extract USD quote data
            quote_data = crypto_data.get('quote', {}).get('USD', {})
            
            if not quote_data:
                self.logger.warning(f"No USD quote data for symbol {symbol}")
                return None
            
            return CryptoDataPoint(
                symbol=symbol,
                price=float(quote_data.get('price', 0)),
                volume_24h=float(quote_data.get('volume_24h', 0)),
                price_change_24h=float(quote_data.get('percent_change_24h', 0)),
                market_cap=float(quote_data.get('market_cap', 0)),
                high_24h=None,  # CoinMarketCap doesn't provide 24h high/low in this endpoint
                low_24h=None,
                timestamp=datetime.utcnow(),
                provider_source="coinmarketcap"
            )
            
        except Exception as e:
            self.logger.error(f"Error fetching CoinMarketCap quote for {symbol}: {str(e)}")
            return None
    
    async def fetch_history(self, symbol: str, days: int = 30) -> List[CryptoDataPoint]:
        """Fetch historical data from CoinMarketCap historical endpoint."""
        try:
            cmc_id = self._get_cmc_id(symbol)
            
            if not cmc_id:
                self.logger.warning(f"No CoinMarketCap ID found for symbol {symbol}")
                return []
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # CoinMarketCap historical endpoint
            endpoint = f"/v2/cryptocurrency/quotes/historical"
            params = {
                'id': cmc_id,
                'time_start': start_date.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                'time_end': end_date.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                'interval': 'daily' if days > 7 else 'hourly',
                'count': min(days * 24 if days <= 7 else days, 365)  # Respect API limits
            }
            
            headers = self._get_headers()
            
            # Build URL with parameters
            param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{self.base_url}{endpoint}?{param_string}"
            
            response = await self.client.get(full_url, headers=headers)
            
            if not response or 'status' not in response:
                self.logger.error("Invalid CoinMarketCap historical API response")
                return []
            
            if response['status']['error_code'] != 0:
                self.logger.error(f"CoinMarketCap historical API error: {response['status']['error_message']}")
                return []
            
            data = response.get('data', {})
            quotes = data.get('quotes', [])
            
            history_points = []
            
            for quote in quotes:
                timestamp = datetime.fromisoformat(quote['timestamp'].replace('Z', '+00:00'))
                quote_data = quote.get('quote', {}).get('USD', {})
                
                if quote_data:
                    history_points.append(CryptoDataPoint(
                        symbol=symbol,
                        price=float(quote_data.get('price', 0)),
                        volume_24h=float(quote_data.get('volume_24h', 0)),
                        price_change_24h=float(quote_data.get('percent_change_24h', 0)),
                        market_cap=float(quote_data.get('market_cap', 0)),
                        high_24h=None,
                        low_24h=None,
                        timestamp=timestamp,
                        provider_source="coinmarketcap"
                    ))
            
            return history_points
            
        except Exception as e:
            self.logger.error(f"Error fetching CoinMarketCap history for {symbol}: {str(e)}")
            return []
    
    async def health_check(self) -> bool:
        """Check CoinMarketCap API health using key info endpoint."""
        try:
            endpoint = "/v1/key/info"
            headers = self._get_headers()
            
            response = await self.client.get(f"{self.base_url}{endpoint}", headers=headers)
            
            if response and 'status' in response:
                return response['status']['error_code'] == 0
            
            return False
            
        except Exception as e:
            self.logger.error(f"CoinMarketCap health check failed: {str(e)}")
            return False
    
    async def get_top_cryptocurrencies(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get top cryptocurrencies by market cap from CoinMarketCap."""
        try:
            endpoint = f"/v1/cryptocurrency/listings/latest?limit={min(limit, 5000)}"
            headers = self._get_headers()
            
            response = await self.client.get(f"{self.base_url}{endpoint}", headers=headers)
            
            if not response or 'status' not in response:
                self.logger.error("Invalid CoinMarketCap listings API response")
                return []
            
            if response['status']['error_code'] != 0:
                self.logger.error(f"CoinMarketCap listings API error: {response['status']['error_message']}")
                return []
            
            data = response.get('data', [])
            cryptocurrencies = []
            
            for crypto in data:
                quote_data = crypto.get('quote', {}).get('USD', {})
                
                cryptocurrencies.append({
                    'id': crypto.get('id'),
                    'symbol': crypto.get('symbol'),
                    'name': crypto.get('name'),
                    'current_price': float(quote_data.get('price', 0)),
                    'market_cap': float(quote_data.get('market_cap', 0)),
                    'market_cap_rank': crypto.get('cmc_rank'),
                    'volume_24h': float(quote_data.get('volume_24h', 0)),
                    'price_change_percent_24h': float(quote_data.get('percent_change_24h', 0)),
                    'price_change_percent_1h': float(quote_data.get('percent_change_1h', 0)),
                    'price_change_percent_7d': float(quote_data.get('percent_change_7d', 0)),
                    'circulating_supply': float(crypto.get('circulating_supply', 0)),
                    'total_supply': float(crypto.get('total_supply', 0)),
                    'max_supply': float(crypto.get('max_supply', 0)) if crypto.get('max_supply') else None,
                    'last_updated': crypto.get('last_updated'),
                    'provider_source': 'coinmarketcap'
                })
            
            return cryptocurrencies
            
        except Exception as e:
            self.logger.error(f"Error fetching CoinMarketCap top cryptocurrencies: {str(e)}")
            return []
    
    async def get_supported_symbols(self) -> List[str]:
        """Get list of supported symbols from CoinMarketCap."""
        try:
            # Return known symbols, or fetch from map endpoint for comprehensive list
            return list(self.symbol_to_id.keys())
            
        except Exception as e:
            self.logger.error(f"Error getting CoinMarketCap supported symbols: {str(e)}")
            return list(self.symbol_to_id.keys()) 