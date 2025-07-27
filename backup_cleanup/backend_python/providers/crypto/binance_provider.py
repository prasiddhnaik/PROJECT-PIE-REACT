"""
Binance Provider

Adapter for Binance API that implements the standard crypto provider interface.
Provides real-time and historical crypto data with high rate limits.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .base_crypto_provider import BaseCryptoProvider


class BinanceProvider(BaseCryptoProvider):
    """Binance API provider adapter."""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.symbol_mapping = {
            'bitcoin': 'BTCUSDT',
            'ethereum': 'ETHUSDT', 
            'litecoin': 'LTCUSDT',
            'bitcoin-cash': 'BCHUSDT',
            'chainlink': 'LINKUSDT',
            'cardano': 'ADAUSDT',
            'polkadot': 'DOTUSDT',
            'stellar': 'XLMUSDT',
            'dogecoin': 'DOGEUSDT',
            'uniswap': 'UNIUSDT',
            'ripple': 'XRPUSDT',
            'solana': 'SOLUSDT',
            'avalanche-2': 'AVAXUSDT',
            'polygon': 'MATICUSDT'
        }

    async def fetch_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch current price quote from Binance."""
        try:
            binance_symbol = self._normalize_symbol(symbol)
            if not binance_symbol:
                return None
            
            # Fetch 24hr ticker statistics
            ticker_data = await self._make_request("/ticker/24hr", params={'symbol': binance_symbol})
            if not ticker_data:
                return None
            
            standardized = self._standardize_response(ticker_data, symbol)
            
            if self._validate_response(standardized):
                return standardized
                
        except Exception as e:
            self.logger.error(f"Error fetching quote for {symbol}: {str(e)}")
            
        return None

    async def fetch_history(self, symbol: str, days: int) -> Optional[List[Dict[str, Any]]]:
        """Fetch historical price data from Binance."""
        try:
            binance_symbol = self._normalize_symbol(symbol)
            if not binance_symbol:
                return None
            
            # Determine interval based on days
            if days <= 1:
                interval = '5m'
                limit = min(288, days * 288)  # 5min intervals
            elif days <= 7:
                interval = '1h'
                limit = min(168, days * 24)  # hourly
            elif days <= 30:
                interval = '4h'
                limit = min(180, days * 6)  # 4hour
            else:
                interval = '1d'
                limit = min(1000, days)  # daily
            
            params = {
                'symbol': binance_symbol,
                'interval': interval,
                'limit': limit
            }
            
            klines_data = await self._make_request("/klines", params=params)
            if not klines_data:
                return None
            
            # Convert klines to standard format
            # Binance format: [open_time, open, high, low, close, volume, close_time, ...]
            history_points = []
            for kline in klines_data:
                if len(kline) >= 7:
                    history_points.append({
                        'timestamp': int(kline[0]) / 1000,  # Convert to seconds
                        'price': float(kline[4]),  # close price
                        'volume': float(kline[5]),
                        'high': float(kline[2]),
                        'low': float(kline[3]),
                        'open': float(kline[1])
                    })
            
            return history_points
            
        except Exception as e:
            self.logger.error(f"Error fetching history for {symbol}: {str(e)}")
            
        return None

    async def fetch_batch_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch quotes for multiple symbols using Binance's batch endpoint."""
        try:
            # Convert symbols to Binance format
            binance_symbols = []
            symbol_map = {}
            
            for symbol in symbols:
                binance_symbol = self._normalize_symbol(symbol)
                if binance_symbol:
                    binance_symbols.append(binance_symbol)
                    symbol_map[binance_symbol] = symbol
            
            if not binance_symbols:
                return {}
            
            # Fetch all tickers at once
            all_tickers = await self._make_request("/ticker/24hr")
            if not all_tickers:
                return {}
            
            # Filter for requested symbols
            results = {}
            for ticker in all_tickers:
                binance_symbol = ticker.get('symbol')
                if binance_symbol in symbol_map:
                    original_symbol = symbol_map[binance_symbol]
                    standardized = self._standardize_response(ticker, original_symbol)
                    if self._validate_response(standardized):
                        results[original_symbol] = standardized
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error fetching batch quotes: {str(e)}")
            return {}

    async def health_check(self) -> bool:
        """Perform health check for Binance API."""
        try:
            # Use the ping endpoint for health check
            response = await self._make_request("/ping")
            return response is not None
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False

    def _normalize_symbol(self, symbol: str) -> Optional[str]:
        """Convert symbol to Binance format."""
        # Try direct mapping first
        if symbol.lower() in self.symbol_mapping:
            return self.symbol_mapping[symbol.lower()]
        
        # Try common transformations
        upper_symbol = symbol.upper()
        
        # Common Binance pairs with USDT
        common_symbols = ['BTC', 'ETH', 'BNB', 'ADA', 'DOT', 'LINK', 'LTC', 'BCH', 
                         'XRP', 'SOL', 'AVAX', 'MATIC', 'UNI', 'DOGE', 'ATOM', 'VET']
        
        if upper_symbol in common_symbols:
            return f"{upper_symbol}USDT"
        
        # Default fallback
        return f"{upper_symbol}USDT"

    def _standardize_response(self, raw_data: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """Convert Binance response to standard format."""
        try:
            return {
                'symbol': symbol,
                'price': float(raw_data.get('lastPrice', 0)),
                'volume_24h': float(raw_data.get('volume', 0)),
                'market_cap': None,  # Binance doesn't provide market cap in ticker
                'price_change_24h': float(raw_data.get('priceChange', 0)),
                'price_change_percentage_24h': float(raw_data.get('priceChangePercent', 0)),
                'high_24h': float(raw_data.get('highPrice', 0)),
                'low_24h': float(raw_data.get('lowPrice', 0)),
                'last_updated': datetime.now().isoformat(),
                'provider_source': self.provider_id
            }
        except (ValueError, TypeError) as e:
            self.logger.error(f"Error standardizing response: {str(e)}")
            return {}

    def _build_headers(self) -> Dict[str, str]:
        """Build headers specific to Binance API."""
        headers = super()._build_headers()
        
        # Binance uses X-MBX-APIKEY for authentication
        if self.api_key:
            headers['X-MBX-APIKEY'] = self.api_key
            
        return headers 