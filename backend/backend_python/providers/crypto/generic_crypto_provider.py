"""
Generic Crypto Provider

A flexible adapter that can handle any REST API crypto provider using
configurable field mappings and common API patterns. This allows the
system to support 100+ providers without requiring individual adapters.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .base_crypto_provider import BaseCryptoProvider


class GenericCryptoProvider(BaseCryptoProvider):
    """Generic adapter for REST API crypto providers."""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        
        # Default field mappings - can be overridden in provider config
        self.field_mappings = provider_config.get('field_mappings', {
            'price': ['price', 'last_price', 'current_price', 'quote.USD.price', 'result.price'],
            'volume_24h': ['volume_24h', 'total_volume', 'quote.USD.volume_24h', 'volume'],
            'market_cap': ['market_cap', 'quote.USD.market_cap', 'market_cap_usd'],
            'price_change_24h': ['price_change_24h', 'quote.USD.change_24h', 'change_24h'],
            'price_change_percentage_24h': ['price_change_percentage_24h', 'quote.USD.percent_change_24h', 'percent_change_24h'],
            'symbol': ['symbol', 'name', 'id'],
            'last_updated': ['last_updated', 'timestamp', 'updated_at', 'time']
        })
        
        # API endpoints configuration
        self.endpoints = provider_config.get('endpoints', {
            'quote': '/quote/{symbol}',
            'quotes': '/quotes',
            'history': '/history/{symbol}',
            'health': '/status'
        })
        
        # Symbol transformation rules
        self.symbol_transform = provider_config.get('symbol_transform', {
            'uppercase': True,
            'separator': '',
            'base_currency': 'USD'
        })
        
        # Response structure configuration
        self.response_structure = provider_config.get('response_structure', {
            'data_path': '',  # Path to data in response (e.g., 'data', 'result.data')
            'is_array': False,  # Whether the response is an array
            'symbol_key': 'symbol'  # Key to identify symbol in response
        })

    async def fetch_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch current price quote using generic patterns."""
        try:
            normalized_symbol = self._normalize_symbol(symbol)
            if not normalized_symbol:
                return None
            
            # Try different endpoint patterns
            endpoint_patterns = [
                self.endpoints.get('quote', '/quote/{symbol}').format(symbol=normalized_symbol),
                f"/price/{normalized_symbol}",
                f"/ticker/{normalized_symbol}",
                f"/v1/cryptocurrency/quotes/latest?symbol={normalized_symbol}",
                f"/simple/price?ids={normalized_symbol}&vs_currencies=usd"
            ]
            
            for endpoint in endpoint_patterns:
                try:
                    response_data = await self._make_request(endpoint)
                    if response_data:
                        extracted_data = self._extract_data_from_response(response_data, normalized_symbol)
                        if extracted_data:
                            standardized = self._standardize_response(extracted_data, symbol)
                            if self._validate_response(standardized):
                                return standardized
                except Exception as e:
                    self.logger.debug(f"Endpoint {endpoint} failed: {str(e)}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error fetching quote for {symbol}: {str(e)}")
            
        return None

    async def fetch_history(self, symbol: str, days: int) -> Optional[List[Dict[str, Any]]]:
        """Fetch historical price data using generic patterns."""
        try:
            normalized_symbol = self._normalize_symbol(symbol)
            if not normalized_symbol:
                return None
            
            # Try different history endpoint patterns
            endpoint_patterns = [
                self.endpoints.get('history', '/history/{symbol}').format(symbol=normalized_symbol),
                f"/history/{normalized_symbol}?days={days}",
                f"/chart/{normalized_symbol}?period={days}d",
                f"/klines/{normalized_symbol}?interval=1d&limit={days}",
                f"/ohlc/{normalized_symbol}?days={days}"
            ]
            
            for endpoint in endpoint_patterns:
                try:
                    response_data = await self._make_request(endpoint)
                    if response_data:
                        history_points = self._extract_history_from_response(response_data)
                        if history_points:
                            return history_points
                except Exception as e:
                    self.logger.debug(f"History endpoint {endpoint} failed: {str(e)}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error fetching history for {symbol}: {str(e)}")
            
        return None

    async def fetch_batch_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch quotes for multiple symbols using generic batch patterns."""
        try:
            normalized_symbols = [self._normalize_symbol(s) for s in symbols if self._normalize_symbol(s)]
            if not normalized_symbols:
                return {}
            
            # Try different batch endpoint patterns
            batch_endpoints = [
                (self.endpoints.get('quotes', '/quotes'), {'symbols': ','.join(normalized_symbols)}),
                ('/batch/quotes', {'symbols': normalized_symbols}),
                ('/quotes/batch', {'symbols': '|'.join(normalized_symbols)}),
                ('/v1/cryptocurrency/quotes/latest', {'symbol': ','.join(normalized_symbols)}),
                ('/simple/price', {'ids': ','.join(normalized_symbols), 'vs_currencies': 'usd'})
            ]
            
            for endpoint, params in batch_endpoints:
                try:
                    response_data = await self._make_request(endpoint, params=params)
                    if response_data:
                        results = self._extract_batch_data_from_response(response_data, symbols, normalized_symbols)
                        if results:
                            return results
                except Exception as e:
                    self.logger.debug(f"Batch endpoint {endpoint} failed: {str(e)}")
                    continue
            
            # Fallback to individual requests
            return await super().fetch_batch_quotes(symbols)
            
        except Exception as e:
            self.logger.error(f"Error fetching batch quotes: {str(e)}")
            return {}

    async def health_check(self) -> bool:
        """Perform health check using generic patterns."""
        try:
            # Try different health check endpoints
            health_endpoints = [
                self.endpoints.get('health', '/status'),
                '/health',
                '/ping',
                '/time',
                '/api/status',
                '/v1/status'
            ]
            
            for endpoint in health_endpoints:
                try:
                    response = await self._make_request(endpoint)
                    if response is not None:
                        return True
                except Exception:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False

    def _normalize_symbol(self, symbol: str) -> Optional[str]:
        """Apply symbol transformations based on provider configuration."""
        if not symbol:
            return None
        
        result = symbol
        
        # Apply case transformation
        if self.symbol_transform.get('uppercase', True):
            result = result.upper()
        else:
            result = result.lower()
        
        # Add base currency if needed
        base_currency = self.symbol_transform.get('base_currency')
        separator = self.symbol_transform.get('separator', '')
        
        if base_currency and not result.endswith(base_currency):
            result = f"{result}{separator}{base_currency}"
        
        return result

    def _extract_data_from_response(self, response_data: Dict[str, Any], symbol: str) -> Optional[Dict[str, Any]]:
        """Extract relevant data from API response using configured paths."""
        try:
            data = response_data
            
            # Navigate to data using configured path
            data_path = self.response_structure.get('data_path', '')
            if data_path:
                for path_segment in data_path.split('.'):
                    if path_segment and path_segment in data:
                        data = data[path_segment]
                    else:
                        return None
            
            # Handle array responses
            if self.response_structure.get('is_array', False):
                if isinstance(data, list) and len(data) > 0:
                    # Find the correct item by symbol
                    symbol_key = self.response_structure.get('symbol_key', 'symbol')
                    for item in data:
                        if isinstance(item, dict) and item.get(symbol_key, '').upper() == symbol.upper():
                            return item
                    # If no match found, use first item
                    return data[0] if data else None
                else:
                    return None
            
            # Handle object responses
            if isinstance(data, dict):
                # If data contains the symbol as a key, use that
                if symbol.upper() in data:
                    return data[symbol.upper()]
                elif symbol.lower() in data:
                    return data[symbol.lower()]
                else:
                    return data
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting data from response: {str(e)}")
            return None

    def _extract_history_from_response(self, response_data: Any) -> Optional[List[Dict[str, Any]]]:
        """Extract historical data from API response."""
        try:
            if isinstance(response_data, list):
                # Assume it's already in the right format
                history_points = []
                for item in response_data:
                    if isinstance(item, dict):
                        history_points.append({
                            'timestamp': self._extract_field_value(item, ['timestamp', 'time', 'date']),
                            'price': self._extract_field_value(item, ['price', 'close', 'value']),
                            'volume': self._extract_field_value(item, ['volume', 'vol']),
                            'high': self._extract_field_value(item, ['high', 'h']),
                            'low': self._extract_field_value(item, ['low', 'l']),
                            'open': self._extract_field_value(item, ['open', 'o'])
                        })
                    elif isinstance(item, list) and len(item) >= 2:
                        # Handle array format [timestamp, price, ...] or [timestamp, open, high, low, close, volume]
                        history_points.append({
                            'timestamp': item[0],
                            'price': item[4] if len(item) >= 5 else item[1],  # close or price
                            'volume': item[5] if len(item) >= 6 else None,
                            'high': item[2] if len(item) >= 5 else None,
                            'low': item[3] if len(item) >= 5 else None,
                            'open': item[1] if len(item) >= 5 else None
                        })
                return history_points
            
            elif isinstance(response_data, dict):
                # Try to find array data in the response
                for key in ['data', 'result', 'prices', 'history', 'chart']:
                    if key in response_data and isinstance(response_data[key], list):
                        return self._extract_history_from_response(response_data[key])
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting history from response: {str(e)}")
            return None

    def _extract_batch_data_from_response(self, response_data: Any, original_symbols: List[str], normalized_symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Extract batch data from API response."""
        try:
            results = {}
            data = response_data
            
            # Navigate to data using configured path
            data_path = self.response_structure.get('data_path', '')
            if data_path:
                for path_segment in data_path.split('.'):
                    if path_segment and isinstance(data, dict) and path_segment in data:
                        data = data[path_segment]
            
            if isinstance(data, dict):
                # Map normalized symbols back to original symbols
                symbol_map = dict(zip(normalized_symbols, original_symbols))
                
                for key, value in data.items():
                    if isinstance(value, dict):
                        # Find corresponding original symbol
                        original_symbol = None
                        for norm_sym, orig_sym in symbol_map.items():
                            if key.upper() == norm_sym.upper():
                                original_symbol = orig_sym
                                break
                        
                        if original_symbol:
                            standardized = self._standardize_response(value, original_symbol)
                            if self._validate_response(standardized):
                                results[original_symbol] = standardized
            
            elif isinstance(data, list):
                symbol_key = self.response_structure.get('symbol_key', 'symbol')
                symbol_map = dict(zip(normalized_symbols, original_symbols))
                
                for item in data:
                    if isinstance(item, dict) and symbol_key in item:
                        item_symbol = item[symbol_key].upper()
                        original_symbol = symbol_map.get(item_symbol)
                        if original_symbol:
                            standardized = self._standardize_response(item, original_symbol)
                            if self._validate_response(standardized):
                                results[original_symbol] = standardized
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error extracting batch data: {str(e)}")
            return {}

    def _extract_field_value(self, data: Dict[str, Any], field_paths: List[str]) -> Any:
        """Extract field value using multiple possible paths."""
        for path in field_paths:
            try:
                # Handle nested paths (e.g., 'quote.USD.price')
                value = data
                for segment in path.split('.'):
                    if isinstance(value, dict) and segment in value:
                        value = value[segment]
                    else:
                        value = None
                        break
                
                if value is not None:
                    return value
            except Exception:
                continue
        
        return None

    def _standardize_response(self, raw_data: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """Convert provider response to standard format using field mappings."""
        try:
            standardized = {
                'symbol': symbol,
                'provider_source': self.provider_id,
                'last_updated': datetime.now().isoformat()
            }
            
            # Map each field using configured mappings
            for standard_field, possible_paths in self.field_mappings.items():
                if standard_field not in ['symbol', 'provider_source', 'last_updated']:
                    value = self._extract_field_value(raw_data, possible_paths)
                    if value is not None:
                        # Try to convert to appropriate type
                        if standard_field in ['price', 'volume_24h', 'market_cap', 'price_change_24h', 'price_change_percentage_24h']:
                            try:
                                standardized[standard_field] = float(value)
                            except (ValueError, TypeError):
                                standardized[standard_field] = 0 if 'volume' in standard_field or 'price' in standard_field else None
                        else:
                            standardized[standard_field] = value
            
            return standardized
            
        except Exception as e:
            self.logger.error(f"Error standardizing response: {str(e)}")
            return {} 