"""
Kraken Crypto Provider - Professional exchange integration
Priority Score: 92 (Third-highest in failover chain)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os

from .base_crypto_provider import BaseCryptoProvider, CryptoDataPoint
from services.common.http_client import HTTPClient


class KrakenProvider(BaseCryptoProvider):
    """
    Kraken exchange provider for crypto data
    Supports spot trading, professional-grade API
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://api.kraken.com"
        self.api_key = os.getenv("KRAKEN_API_KEY")
        self.client = HTTPClient()
        self.logger = logging.getLogger(__name__)
        
        # Kraken symbol mappings
        self.symbol_mappings = {
            'BTC': 'XBTUSD',
            'ETH': 'ETHUSD',
            'LTC': 'LTCUSD',
            'XRP': 'XRPUSD',
            'BCH': 'BCHUSD',
            'ADA': 'ADAUSD',
            'DOT': 'DOTUSD',
            'LINK': 'LINKUSD',
            'XLM': 'XLMUSD',
            'ATOM': 'ATOMUSD'
        }
    
    def _get_kraken_symbol(self, symbol: str) -> str:
        """Convert standard symbol to Kraken format."""
        symbol_upper = symbol.upper()
        return self.symbol_mappings.get(symbol_upper, f"{symbol_upper}USD")
    
    async def fetch_quote(self, symbol: str) -> Optional[CryptoDataPoint]:
        """Fetch current quote from Kraken ticker endpoint."""
        try:
            kraken_symbol = self._get_kraken_symbol(symbol)
            endpoint = f"/0/public/Ticker?pair={kraken_symbol}"
            
            response = await self.client.get(f"{self.base_url}{endpoint}")
            
            if not response or 'error' in response and response['error']:
                self.logger.error(f"Kraken API error: {response.get('error', 'Unknown error')}")
                return None
            
            if 'result' not in response or kraken_symbol not in response['result']:
                self.logger.warning(f"No data for symbol {kraken_symbol} in Kraken response")
                return None
            
            ticker_data = response['result'][kraken_symbol]
            
            # Extract data from Kraken format
            current_price = float(ticker_data.get('c', [0, 0])[0])  # Last trade price
            volume_24h = float(ticker_data.get('v', [0, 0])[1])  # 24h volume
            high_24h = float(ticker_data.get('h', [0, 0])[1])  # 24h high
            low_24h = float(ticker_data.get('l', [0, 0])[1])  # 24h low
            
            # Calculate 24h change percentage
            opening_price = float(ticker_data.get('o', current_price))
            price_change_24h = ((current_price - opening_price) / opening_price * 100) if opening_price > 0 else 0
            
            return CryptoDataPoint(
                symbol=symbol,
                price=current_price,
                volume_24h=volume_24h,
                price_change_24h=price_change_24h,
                market_cap=None,  # Kraken doesn't provide market cap
                high_24h=high_24h,
                low_24h=low_24h,
                timestamp=datetime.utcnow(),
                provider_source="kraken"
            )
            
        except Exception as e:
            self.logger.error(f"Error fetching Kraken quote for {symbol}: {str(e)}")
            return None
    
    async def fetch_history(self, symbol: str, days: int = 30) -> List[CryptoDataPoint]:
        """Fetch historical data from Kraken OHLC endpoint."""
        try:
            kraken_symbol = self._get_kraken_symbol(symbol)
            
            # Kraken intervals: 1, 5, 15, 30, 60, 240, 1440, 10080, 21600 (in minutes)
            interval = 1440 if days > 7 else 240 if days > 1 else 60  # Daily, 4h, or hourly
            
            # Calculate since timestamp (Kraken uses seconds)
            since_timestamp = int((datetime.utcnow() - timedelta(days=days)).timestamp())
            
            endpoint = f"/0/public/OHLC?pair={kraken_symbol}&interval={interval}&since={since_timestamp}"
            
            response = await self.client.get(f"{self.base_url}{endpoint}")
            
            if not response or 'error' in response and response['error']:
                self.logger.error(f"Kraken OHLC API error: {response.get('error', 'Unknown error')}")
                return []
            
            if 'result' not in response or kraken_symbol not in response['result']:
                self.logger.warning(f"No OHLC data for symbol {kraken_symbol}")
                return []
            
            ohlc_data = response['result'][kraken_symbol]
            history_points = []
            
            for candle in ohlc_data:
                timestamp = datetime.fromtimestamp(candle[0])
                open_price = float(candle[1])
                high_price = float(candle[2])
                low_price = float(candle[3])
                close_price = float(candle[4])
                volume = float(candle[6])
                
                history_points.append(CryptoDataPoint(
                    symbol=symbol,
                    price=close_price,
                    volume_24h=volume,
                    price_change_24h=0,  # Would need previous day's data to calculate
                    market_cap=None,
                    high_24h=high_price,
                    low_24h=low_price,
                    timestamp=timestamp,
                    provider_source="kraken"
                ))
            
            return history_points
            
        except Exception as e:
            self.logger.error(f"Error fetching Kraken history for {symbol}: {str(e)}")
            return []
    
    async def health_check(self) -> bool:
        """Check Kraken API health using system status endpoint."""
        try:
            endpoint = "/0/public/SystemStatus"
            response = await self.client.get(f"{self.base_url}{endpoint}")
            
            if response and 'result' in response:
                status = response['result'].get('status', 'unknown')
                return status.lower() in ['online', 'operational']
            
            return False
            
        except Exception as e:
            self.logger.error(f"Kraken health check failed: {str(e)}")
            return False
    
    async def get_supported_symbols(self) -> List[str]:
        """Get list of supported trading pairs from Kraken."""
        try:
            endpoint = "/0/public/AssetPairs"
            response = await self.client.get(f"{self.base_url}{endpoint}")
            
            if response and 'result' in response:
                pairs = response['result']
                supported = []
                
                for pair_name, pair_info in pairs.items():
                    # Extract base symbol from pair info
                    base = pair_info.get('base', '')
                    if base and base not in supported:
                        # Convert Kraken symbols back to standard format
                        if base == 'XXBT':
                            supported.append('BTC')
                        elif base.startswith('X') and len(base) == 4:
                            supported.append(base[1:])
                        else:
                            supported.append(base)
                
                return supported
            
            return list(self.symbol_mappings.keys())
            
        except Exception as e:
            self.logger.error(f"Error getting Kraken supported symbols: {str(e)}")
            return list(self.symbol_mappings.keys()) 