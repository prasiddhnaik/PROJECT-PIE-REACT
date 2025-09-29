"""
Base Crypto Provider

Abstract base class that defines the standard interface for all crypto
data provider adapters. Provides common functionality for authentication,
rate limiting, error handling, and response normalization.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp
import os


class BaseCryptoProvider(ABC):
    """
    Abstract base class for all crypto data providers.
    
    Provides common functionality and defines the interface that all
    provider adapters must implement.
    """
    
    def __init__(self, provider_config: Dict[str, Any]):
        self.config = provider_config
        self.provider_id = provider_config.get('id')
        self.name = provider_config.get('name')
        self.base_url = provider_config.get('base_url')
        self.auth_type = provider_config.get('auth_type', 'none')
        self.rate_limits = provider_config.get('rate_limits', {})
        self.logger = logging.getLogger(f"{__name__}.{self.provider_id}")
        
        # Initialize authentication
        self.api_key = self._get_api_key()
        self.headers = self._build_headers()
        
        # Rate limiting tracking
        self.last_request_time = 0
        self.request_count = 0
        self.request_window_start = time.time()
        
        # Session management
        self.session = None

    @abstractmethod
    async def fetch_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch current price quote for a crypto symbol.
        
        Args:
            symbol: Crypto symbol (e.g., 'bitcoin', 'ethereum')
            
        Returns:
            Dictionary with price data or None if failed
        """
        pass

    @abstractmethod
    async def fetch_history(self, symbol: str, days: int) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch historical price data for a crypto symbol.
        
        Args:
            symbol: Crypto symbol
            days: Number of days of history to fetch
            
        Returns:
            List of historical data points or None if failed
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Perform health check for this provider.
        
        Returns:
            True if provider is healthy, False otherwise
        """
        pass

    async def fetch_batch_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Fetch quotes for multiple symbols (default implementation uses individual requests).
        
        Args:
            symbols: List of crypto symbols
            
        Returns:
            Dictionary mapping symbols to price data
        """
        results = {}
        
        for symbol in symbols:
            try:
                # Respect rate limits between requests
                await self._enforce_rate_limit()
                
                quote_data = await self.fetch_quote(symbol)
                if quote_data:
                    results[symbol] = quote_data
                    
            except Exception as e:
                self.logger.warning(f"Failed to fetch {symbol}: {str(e)}")
                continue
                
        return results

    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment variables."""
        if self.auth_type == 'none':
            return None
            
        # Get required environment key names from config
        required_keys = self.config.get('required_env_keys', [])
        if not required_keys:
            return None
            
        # Try to get the first available key
        for key_name in required_keys:
            api_key = os.getenv(key_name)
            if api_key:
                return api_key
                
        self.logger.warning(f"No API key found for {self.provider_id}. Required keys: {required_keys}")
        return None

    def _build_headers(self) -> Dict[str, str]:
        """Build HTTP headers for API requests."""
        headers = {
            'User-Agent': 'CryptoAnalytics/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Add authentication headers based on auth type
        if self.auth_type == 'api_key' and self.api_key:
            headers['X-API-Key'] = self.api_key
        elif self.auth_type == 'bearer' and self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
            
        return headers

    async def _make_request(self, 
                          endpoint: str, 
                          method: str = 'GET', 
                          params: Optional[Dict[str, Any]] = None,
                          data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Make HTTP request to provider API with error handling and rate limiting.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            params: Query parameters
            data: Request body data
            
        Returns:
            Response JSON or None if failed
        """
        await self._enforce_rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                )
            
            async with self.session.request(
                method=method,
                url=url,
                params=params,
                json=data
            ) as response:
                
                # Update rate limiting counters
                self._update_rate_limit_counters()
                
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    # Rate limit exceeded
                    self.logger.warning(f"Rate limit exceeded for {self.provider_id}")
                    retry_after = response.headers.get('Retry-After', '60')
                    await asyncio.sleep(int(retry_after))
                    return None
                else:
                    self.logger.error(f"HTTP {response.status} from {self.provider_id}: {await response.text()}")
                    return None
                    
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout error for {self.provider_id}")
            return None
        except Exception as e:
            self.logger.error(f"Request error for {self.provider_id}: {str(e)}")
            return None

    async def _enforce_rate_limit(self):
        """Enforce rate limits based on provider configuration."""
        current_time = time.time()
        
        # Reset window if needed
        if current_time - self.request_window_start >= 60:
            self.request_count = 0
            self.request_window_start = current_time
        
        # Check per-minute rate limit
        per_minute_limit = self.rate_limits.get('per_minute', 60)
        if self.request_count >= per_minute_limit:
            sleep_time = 60 - (current_time - self.request_window_start)
            if sleep_time > 0:
                self.logger.debug(f"Rate limit reached for {self.provider_id}, sleeping {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
                self.request_count = 0
                self.request_window_start = time.time()
        
        # Enforce minimum delay between requests
        min_delay = 60 / per_minute_limit if per_minute_limit > 0 else 1
        time_since_last = current_time - self.last_request_time
        if time_since_last < min_delay:
            await asyncio.sleep(min_delay - time_since_last)

    def _update_rate_limit_counters(self):
        """Update rate limiting counters after making a request."""
        self.last_request_time = time.time()
        self.request_count += 1

    def _normalize_symbol(self, symbol: str) -> str:
        """
        Normalize crypto symbol for this provider's API format.
        Default implementation - override in provider-specific adapters.
        """
        return symbol.lower()

    def _standardize_response(self, raw_data: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """
        Convert provider-specific response to standard format.
        Override this method in provider-specific adapters.
        """
        return {
            'symbol': symbol,
            'price': raw_data.get('price', 0),
            'volume_24h': raw_data.get('volume_24h', 0),
            'market_cap': raw_data.get('market_cap'),
            'price_change_24h': raw_data.get('price_change_24h'),
            'price_change_percentage_24h': raw_data.get('price_change_percentage_24h'),
            'last_updated': datetime.now().isoformat(),
            'provider_source': self.provider_id
        }

    def _validate_response(self, data: Dict[str, Any]) -> bool:
        """Validate response data quality."""
        if not data:
            return False
            
        # Check for required fields
        required_fields = ['price']
        for field in required_fields:
            if field not in data or data[field] is None:
                return False
        
        # Validate price is a positive number
        try:
            price = float(data['price'])
            if price <= 0:
                return False
        except (ValueError, TypeError):
            return False
            
        return True

    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None

    def __del__(self):
        """Cleanup when provider is destroyed."""
        if self.session and not self.session.closed:
            # Note: This is not ideal for async cleanup, but serves as a fallback
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
            except:
                pass 