"""
Coinbase Pro Provider

Adapter for Coinbase Pro API that implements the standard crypto provider interface.
Provides real-time and historical crypto data with proper authentication and rate limiting.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .base_crypto_provider import BaseCryptoProvider


class CoinbaseProvider(BaseCryptoProvider):
    """Coinbase Pro API provider adapter."""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.symbol_mapping = {
            'bitcoin': 'BTC-USD',
            'ethereum': 'ETH-USD',
            'litecoin': 'LTC-USD',
            'bitcoin-cash': 'BCH-USD',
            'chainlink': 'LINK-USD',
            'cardano': 'ADA-USD',
            'polkadot': 'DOT-USD',
            'stellar': 'XLM-USD',
            'dogecoin': 'DOGE-USD',
            'uniswap': 'UNI-USD'
        }

    async def fetch_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch current price quote from Coinbase Pro."""
        try:
            coinbase_symbol = self._normalize_symbol(symbol)
            if not coinbase_symbol:
                return None
            
            # Fetch current price
            price_data = await self._make_request(f"/products/{coinbase_symbol}/ticker")
            if not price_data:
                return None
            
            # Fetch 24h stats
            stats_data = await self._make_request(f"/products/{coinbase_symbol}/stats")
            
            # Combine data and standardize
            combined_data = {
                'price': price_data.get('price'),
                'volume_24h': stats_data.get('volume') if stats_data else None,
                'high_24h': stats_data.get('high') if stats_data else None,
                'low_24h': stats_data.get('low') if stats_data else None,
                'last_updated': price_data.get('time')
            }
            
            # Calculate price changes if we have high/low data
            if stats_data and stats_data.get('open'):
                open_price = float(stats_data['open'])
                current_price = float(price_data['price'])
                combined_data['price_change_24h'] = current_price - open_price
                combined_data['price_change_percentage_24h'] = ((current_price - open_price) / open_price) * 100
            
            standardized = self._standardize_response(combined_data, symbol)
            
            if self._validate_response(standardized):
                return standardized
                
        except Exception as e:
            self.logger.error(f"Error fetching quote for {symbol}: {str(e)}")
            
        return None

    async def fetch_history(self, symbol: str, days: int) -> Optional[List[Dict[str, Any]]]:
        """Fetch historical price data from Coinbase Pro."""
        try:
            coinbase_symbol = self._normalize_symbol(symbol)
            if not coinbase_symbol:
                return None
            
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # Determine granularity based on time range
            if days <= 1:
                granularity = 300  # 5 minutes
            elif days <= 7:
                granularity = 3600  # 1 hour
            elif days <= 30:
                granularity = 21600  # 6 hours
            else:
                granularity = 86400  # 1 day
            
            params = {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'granularity': granularity
            }
            
            candles_data = await self._make_request(f"/products/{coinbase_symbol}/candles", params=params)
            if not candles_data:
                return None
            
            # Convert candles to standard format
            # Coinbase format: [timestamp, low, high, open, close, volume]
            history_points = []
            for candle in candles_data:
                if len(candle) >= 6:
                    history_points.append({
                        'timestamp': candle[0],
                        'price': candle[4],  # close price
                        'volume': candle[5],
                        'high': candle[2],
                        'low': candle[1],
                        'open': candle[3]
                    })
            
            # Sort by timestamp (oldest first)
            history_points.sort(key=lambda x: x['timestamp'])
            
            return history_points
            
        except Exception as e:
            self.logger.error(f"Error fetching history for {symbol}: {str(e)}")
            
        return None

    async def health_check(self) -> bool:
        """Perform health check for Coinbase Pro API."""
        try:
            # Use the time endpoint for health check
            response = await self._make_request("/time")
            return response is not None and 'iso' in response
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False

    def _normalize_symbol(self, symbol: str) -> Optional[str]:
        """Convert symbol to Coinbase Pro format."""
        # Try direct mapping first
        if symbol.lower() in self.symbol_mapping:
            return self.symbol_mapping[symbol.lower()]
        
        # Try adding -USD suffix for common symbols
        if symbol.upper() in ['BTC', 'ETH', 'LTC', 'BCH', 'LINK', 'ADA', 'DOT', 'XLM', 'DOGE', 'UNI']:
            return f"{symbol.upper()}-USD"
        
        # Default fallback
        return f"{symbol.upper()}-USD"

    def _standardize_response(self, raw_data: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """Convert Coinbase Pro response to standard format."""
        try:
            return {
                'symbol': symbol,
                'price': float(raw_data.get('price', 0)),
                'volume_24h': float(raw_data.get('volume_24h', 0)) if raw_data.get('volume_24h') else 0,
                'market_cap': None,  # Coinbase doesn't provide market cap
                'price_change_24h': float(raw_data.get('price_change_24h', 0)) if raw_data.get('price_change_24h') else None,
                'price_change_percentage_24h': float(raw_data.get('price_change_percentage_24h', 0)) if raw_data.get('price_change_percentage_24h') else None,
                'high_24h': float(raw_data.get('high_24h', 0)) if raw_data.get('high_24h') else None,
                'low_24h': float(raw_data.get('low_24h', 0)) if raw_data.get('low_24h') else None,
                'last_updated': raw_data.get('last_updated', datetime.now().isoformat()),
                'provider_source': self.provider_id
            }
        except (ValueError, TypeError) as e:
            self.logger.error(f"Error standardizing response: {str(e)}")
            return {}

    def _build_headers(self) -> Dict[str, str]:
        """Build headers specific to Coinbase Pro API."""
        headers = super()._build_headers()
        
        # Coinbase Pro uses standard API key in header
        if self.api_key:
            headers['CB-ACCESS-KEY'] = self.api_key
            
        return headers 