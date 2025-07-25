"""
CoinGecko Provider

Enhanced adapter for CoinGecko API (free and pro) that implements the standard
crypto provider interface. Provides comprehensive crypto data with market cap,
volume, and extensive coin coverage.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .base_crypto_provider import BaseCryptoProvider


class CoinGeckoProvider(BaseCryptoProvider):
    """Enhanced CoinGecko API provider adapter."""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.is_pro = 'pro-api' in self.base_url
        
        # CoinGecko uses coin IDs, not symbols
        self.symbol_to_id_mapping = {
            'bitcoin': 'bitcoin',
            'ethereum': 'ethereum',
            'litecoin': 'litecoin',
            'bitcoin-cash': 'bitcoin-cash',
            'chainlink': 'chainlink',
            'cardano': 'cardano',
            'polkadot': 'polkadot',
            'stellar': 'stellar',
            'dogecoin': 'dogecoin',
            'uniswap': 'uniswap',
            'ripple': 'ripple',
            'solana': 'solana',
            'avalanche-2': 'avalanche-2',
            'polygon': 'matic-network',
            'binancecoin': 'binancecoin',
            'cosmos': 'cosmos',
            'algorand': 'algorand',
            'vechain': 'vechain',
            'internet-computer': 'internet-computer',
            'filecoin': 'filecoin'
        }

    async def fetch_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch current price quote from CoinGecko."""
        try:
            coin_id = self._normalize_symbol(symbol)
            if not coin_id:
                return None
            
            # Use simple price endpoint for single coin
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true',
                'include_last_updated_at': 'true'
            }
            
            price_data = await self._make_request("/simple/price", params=params)
            if not price_data or coin_id not in price_data:
                return None
            
            coin_data = price_data[coin_id]
            standardized = self._standardize_response(coin_data, symbol)
            
            if self._validate_response(standardized):
                return standardized
                
        except Exception as e:
            self.logger.error(f"Error fetching quote for {symbol}: {str(e)}")
            
        return None

    async def fetch_history(self, symbol: str, days: int) -> Optional[List[Dict[str, Any]]]:
        """Fetch historical price data from CoinGecko."""
        try:
            coin_id = self._normalize_symbol(symbol)
            if not coin_id:
                return None
            
            # CoinGecko supports different intervals based on days
            if days <= 1:
                interval = 'minutely' if self.is_pro else 'hourly'
            elif days <= 90:
                interval = 'hourly'
            else:
                interval = 'daily'
            
            params = {
                'vs_currency': 'usd',
                'days': min(days, 365),  # CoinGecko limit
                'interval': interval
            }
            
            history_data = await self._make_request(f"/coins/{coin_id}/market_chart", params=params)
            if not history_data:
                return None
            
            # Convert to standard format
            history_points = []
            prices = history_data.get('prices', [])
            volumes = history_data.get('total_volumes', [])
            market_caps = history_data.get('market_caps', [])
            
            for i, price_point in enumerate(prices):
                if len(price_point) >= 2:
                    timestamp = price_point[0] / 1000  # Convert to seconds
                    price = price_point[1]
                    
                    # Get corresponding volume and market cap
                    volume = volumes[i][1] if i < len(volumes) and len(volumes[i]) >= 2 else None
                    market_cap = market_caps[i][1] if i < len(market_caps) and len(market_caps[i]) >= 2 else None
                    
                    history_points.append({
                        'timestamp': timestamp,
                        'price': price,
                        'volume': volume,
                        'market_cap': market_cap
                    })
            
            return history_points
            
        except Exception as e:
            self.logger.error(f"Error fetching history for {symbol}: {str(e)}")
            
        return None

    async def fetch_batch_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch quotes for multiple symbols using CoinGecko's batch endpoint."""
        try:
            # Convert symbols to coin IDs
            coin_ids = []
            id_to_symbol_map = {}
            
            for symbol in symbols:
                coin_id = self._normalize_symbol(symbol)
                if coin_id:
                    coin_ids.append(coin_id)
                    id_to_symbol_map[coin_id] = symbol
            
            if not coin_ids:
                return {}
            
            # Batch request (up to 250 coins for pro, 100 for free)
            batch_limit = 250 if self.is_pro else 100
            results = {}
            
            for i in range(0, len(coin_ids), batch_limit):
                batch_ids = coin_ids[i:i + batch_limit]
                
                params = {
                    'ids': ','.join(batch_ids),
                    'vs_currencies': 'usd',
                    'include_market_cap': 'true',
                    'include_24hr_vol': 'true',
                    'include_24hr_change': 'true',
                    'include_last_updated_at': 'true'
                }
                
                batch_data = await self._make_request("/simple/price", params=params)
                if batch_data:
                    for coin_id, coin_data in batch_data.items():
                        if coin_id in id_to_symbol_map:
                            original_symbol = id_to_symbol_map[coin_id]
                            standardized = self._standardize_response(coin_data, original_symbol)
                            if self._validate_response(standardized):
                                results[original_symbol] = standardized
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error fetching batch quotes: {str(e)}")
            return {}

    async def health_check(self) -> bool:
        """Perform health check for CoinGecko API."""
        try:
            # Use the ping endpoint for health check
            response = await self._make_request("/ping")
            return response is not None and response.get('gecko_says') == '(V3) To the Moon!'
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False

    def _normalize_symbol(self, symbol: str) -> Optional[str]:
        """Convert symbol to CoinGecko coin ID."""
        # Try direct mapping first
        if symbol.lower() in self.symbol_to_id_mapping:
            return self.symbol_to_id_mapping[symbol.lower()]
        
        # For CoinGecko, we need to use coin IDs, not symbols
        # This is a simplified mapping - in production, you'd want to
        # maintain a more comprehensive mapping or use CoinGecko's coins list API
        
        # Try some common transformations
        lower_symbol = symbol.lower()
        
        # Direct match for many coins
        common_ids = [
            'bitcoin', 'ethereum', 'litecoin', 'ripple', 'cardano',
            'polkadot', 'chainlink', 'stellar', 'dogecoin', 'uniswap',
            'solana', 'cosmos', 'algorand', 'vechain', 'filecoin'
        ]
        
        if lower_symbol in common_ids:
            return lower_symbol
        
        # Default fallback - use the symbol as-is (might not work for all coins)
        return lower_symbol

    def _standardize_response(self, raw_data: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """Convert CoinGecko response to standard format."""
        try:
            # CoinGecko simple/price response format
            price = raw_data.get('usd', 0)
            market_cap = raw_data.get('usd_market_cap')
            volume_24h = raw_data.get('usd_24h_vol', 0)
            price_change_24h = raw_data.get('usd_24h_change')
            last_updated = raw_data.get('last_updated_at')
            
            return {
                'symbol': symbol,
                'price': float(price) if price else 0,
                'volume_24h': float(volume_24h) if volume_24h else 0,
                'market_cap': float(market_cap) if market_cap else None,
                'price_change_24h': None,  # CoinGecko provides percentage, not absolute
                'price_change_percentage_24h': float(price_change_24h) if price_change_24h else None,
                'last_updated': datetime.fromtimestamp(last_updated).isoformat() if last_updated else datetime.now().isoformat(),
                'provider_source': self.provider_id
            }
        except (ValueError, TypeError) as e:
            self.logger.error(f"Error standardizing response: {str(e)}")
            return {}

    def _build_headers(self) -> Dict[str, str]:
        """Build headers specific to CoinGecko API."""
        headers = super()._build_headers()
        
        # CoinGecko Pro uses x-cg-pro-api-key
        if self.api_key and self.is_pro:
            headers['x-cg-pro-api-key'] = self.api_key
            
        return headers 