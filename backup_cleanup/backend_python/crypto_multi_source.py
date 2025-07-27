"""
Crypto Multi-Source Data Orchestrator

This module provides intelligent multi-provider data fetching for crypto data
with built-in failover, rate limiting, health monitoring, and caching.
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import aiohttp
import redis

# Local imports - using local files
from rate_limiter import APIRateLimiter as RateLimiter

# Dummy classes for missing imports
class ProviderFactory:
    def get_provider(self, provider_id):
        return None

class HealthCache:
    def get_provider_state(self, provider_id):
        return {'status': 'CLOSED', 'failures': 0, 'last_failure': 0}
    
    def set_provider_state(self, provider_id, status, failures):
        pass

# --- Data Classes ---

@dataclass
class CryptoHistoryPoint:
    """Standardized crypto history data structure."""
    timestamp: str
    price: float
    volume: Optional[float] = None

# --- Main Orchestrator Class ---

class CryptoMultiSource:
    """
    Intelligent crypto data orchestrator that manages multiple providers
    with failover, rate limiting, and health monitoring.
    """
    
    def __init__(self, provider_factory: ProviderFactory, health_cache: HealthCache, redis_client=None):
        self.provider_factory = provider_factory
        self.health_cache = health_cache
        self.redis_client = redis_client
        if not self.redis_client:
            try:
                # Use a socket timeout to prevent long waits on connection
                self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True, socket_connect_timeout=1)
                self.redis_client.ping()
                self.logger.info("Successfully connected to Redis.")
            except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
                self.logger.warning(f"Could not connect to Redis: {e}. Caching will be disabled.")
                self.redis_client = None
        
        self.rate_limiter = RateLimiter(redis_client=self.redis_client)
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.circuit_breaker_config = {'failure_threshold': 3, 'recovery_timeout': 60} # Fail faster, recover faster
        self.cache_ttl = {'history_data': 180} # 3 minutes

    # --- Public API Methods ---

    async def get_crypto_history(self, symbol: str, days: int = 7, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get historical crypto data with multi-provider fallback.
        Returns a dictionary containing the history and provider source, or None if all fail.
        """
        cache_key = f"crypto_history:{symbol}:{days}"
        
        if use_cache and self.redis_client:
            cached_data = self._get_cached_data(cache_key)
            if cached_data:
                self.logger.debug(f"CACHE HIT for {symbol} history")
                return cached_data
        
        providers = self._get_prioritized_providers('crypto_history')
        if not providers:
            self.logger.error("No healthy crypto history providers configured.")
            return None

        for provider in providers:
            provider_id = provider['id']
            if self._is_circuit_breaker_open(provider_id):
                self.logger.warning(f"Circuit breaker is OPEN for {provider_id}, skipping.")
                continue
            
            try:
                if not await self.rate_limiter.check_limit(provider_id):
                    self.logger.warning(f"RATE LIMIT for {provider_id}, skipping.")
                    continue
                
                history_data = await self._fetch_history_from_provider(provider, symbol, days)
                
                if history_data:
                    # Successfully fetched data
                    result = {"history": [asdict(p) for p in history_data], "provider_source": provider_id}
                    if self.redis_client:
                        self._cache_data(cache_key, result, self.cache_ttl['history_data'])
                    self._reset_circuit_breaker(provider_id)
                    self.logger.info(f"OK: Fetched {symbol} history from {provider_id}")
                    return result
                else:
                    # Provider returned no data, treat as a failure
                    raise ValueError("Provider returned no data")
                    
            except Exception as e:
                self.logger.warning(f"FAIL: Provider {provider_id} failed for {symbol} history. Error: {str(e)}")
                self._record_provider_failure(provider_id)
                continue
        
        self.logger.error(f"FAIL: All providers failed for {symbol} history.")
        return None

    # --- Internal Fetch & Normalization Logic ---

    async def _fetch_history_from_provider(self, provider: Dict[str, Any], symbol: str, days: int) -> Optional[List[CryptoHistoryPoint]]:
        """Fetch and normalize historical data from a single provider instance."""
        provider_id = provider['id']
        try:
            provider_instance = self.provider_factory.get_provider(provider_id)
            if not hasattr(provider_instance, 'get_historical_data'):
                self.logger.warning(f"Provider {provider_id} does not have 'get_historical_data' method.")
                return None
            
            raw_history = await provider_instance.get_historical_data(symbol.lower(), days)
            return self._normalize_history(raw_history, provider_id)
            
        except aiohttp.ClientResponseError as e:
            # Handle specific HTTP errors from the provider
            self.logger.error(f"HTTP Error {e.status} from {provider_id} for {symbol}: {e.message}")
            raise # Re-raise to trigger failure logic
        except Exception as e:
            self.logger.error(f"Unexpected error fetching from {provider_id}: {e}")
            raise # Re-raise to trigger failure logic

    def _normalize_history(self, raw_history: Any, provider_id: str) -> Optional[List[CryptoHistoryPoint]]:
        """Safely normalize historical data from various provider formats into a standard structure."""
        if not isinstance(raw_history, list):
            self.logger.warning(f"Provider {provider_id} returned non-list data for history: {type(raw_history)}")
            return None
            
        normalized = []
        for point in raw_history:
            if not isinstance(point, dict): continue
            try:
                ts_raw = point.get('timestamp') or point.get('time') or point.get('date')
                if ts_raw is None: continue

                if isinstance(ts_raw, (int, float)):
                    timestamp = datetime.fromtimestamp(ts_raw if ts_raw < 1e12 else ts_raw / 1000)
                elif isinstance(ts_raw, str):
                    timestamp = datetime.fromisoformat(ts_raw.replace('Z', '+00:00'))
                else:
                    continue
                
                price = float(point.get('priceUsd', point.get('price', 0)))
                if price <= 0: continue

                normalized.append(CryptoHistoryPoint(
                    timestamp=timestamp.isoformat(),
                    price=price,
                    volume=float(point.get('volumeUsd24Hr', point.get('volume', 0))),
                ))
            except (ValueError, TypeError, AttributeError) as e:
                self.logger.debug(f"Skipping invalid history point from {provider_id}: Point={point}, Error={e}")
                continue
                
        return sorted(normalized, key=lambda x: x.timestamp) if normalized else None

    # --- Health, Caching, and Provider Management ---

    def _get_prioritized_providers(self, category: str) -> List[Dict[str, Any]]:
        """Get a list of healthy, sorted providers."""
        # This should ideally come from a dynamic configuration or service discovery.
        if category == 'crypto_history':
            # Define providers and their priorities. Higher is better.
            return [{'id': 'coingecko', 'priority': 10}]
        return []

    def _get_cached_data(self, key: str) -> Optional[Any]:
        """Retrieve data from Redis cache, handling potential errors."""
        try:
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except (redis.exceptions.RedisError, TypeError, json.JSONDecodeError) as e:
            self.logger.error(f"Cache GET error for key '{key}': {e}")
            return None

    def _cache_data(self, key: str, data: Any, ttl: int):
        """Cache data in Redis, handling potential errors."""
        try:
            self.redis_client.setex(key, ttl, json.dumps(data))
        except (redis.exceptions.RedisError, TypeError) as e:
            self.logger.error(f"Cache SET error for key '{key}': {e}")
            pass

    def _is_circuit_breaker_open(self, provider_id: str) -> bool:
        """Check if the circuit breaker is open for a provider."""
        state = self.health_cache.get_provider_state(provider_id)
        if state['status'] == 'OPEN':
            if time.time() - state['last_failure'] > self.circuit_breaker_config['recovery_timeout']:
                self.health_cache.set_provider_state(provider_id, 'HALF_OPEN', 0)
                return False
            return True
        return False

    def _record_provider_failure(self, provider_id: str):
        """Record a failure and potentially open the circuit breaker."""
        state = self.health_cache.get_provider_state(provider_id)
        new_failures = state['failures'] + 1
        if new_failures >= self.circuit_breaker_config['failure_threshold']:
            self.health_cache.set_provider_state(provider_id, 'OPEN', new_failures)
            self.logger.warning(f"Circuit breaker OPENED for {provider_id}")
        else:
            self.health_cache.set_provider_state(provider_id, state['status'], new_failures)

    def _reset_circuit_breaker(self, provider_id: str):
        """Reset the circuit breaker for a provider on success."""
        state = self.health_cache.get_provider_state(provider_id)
        if state['failures'] > 0 or state['status'] != 'CLOSED':
             self.health_cache.set_provider_state(provider_id, 'CLOSED', 0)
             self.logger.info(f"Circuit breaker RESET for {provider_id}")

# Dummy implementation of other methods if they are not the focus
    async def get_crypto_data(self, symbol: str, use_cache: bool = True): return None
    async def get_batch_crypto_data(self, symbols: list, use_cache: bool = True): return {}
    def _validate_crypto_data(self, data): return True 