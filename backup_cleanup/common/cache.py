f"""
Shared caching utilities for microservices.
"""

import json
import redis
import asyncio
from typing import Any, Optional, Union, Dict, List
from datetime import timedelta
import hashlib
import logging
from functools import wraps
import pickle
import os

logger = logging.getLogger(__name__)

class CacheManager:
    """Redis-based cache manager with fallback to in-memory cache."""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = None
        self.memory_cache = {}  # Fallback in-memory cache
        self.default_ttl = 300  # 5 minutes default TTL
        
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed, using memory cache: {e}")
            self.redis_client = None
    
    def _generate_key(self, key: str, namespace: str = "default") -> str:
        """Generate a namespaced cache key."""
        return f"{namespace}:{key}"
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize value for caching."""
        try:
            return json.dumps(value, default=str)
        except (TypeError, ValueError):
            # Fallback to pickle for complex objects
            return pickle.dumps(value).decode('latin-1')
    
    def _deserialize_value(self, value: str) -> Any:
        """Deserialize cached value."""
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            # Try pickle fallback
            try:
                return pickle.loads(value.encode('latin-1'))
            except:
                return value
    
    async def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get value from cache."""
        cache_key = self._generate_key(key, namespace)
        
        if self.redis_client:
            try:
                value = self.redis_client.get(cache_key)
                if value is not None:
                    return self._deserialize_value(value)
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        
        # Fallback to memory cache
        return self.memory_cache.get(cache_key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, namespace: str = "default") -> bool:
        """Set value in cache with TTL."""
        cache_key = self._generate_key(key, namespace)
        ttl = ttl or self.default_ttl
        serialized_value = self._serialize_value(value)
        
        if self.redis_client:
            try:
                result = self.redis_client.setex(cache_key, ttl, serialized_value)
                return bool(result)
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        
        # Fallback to memory cache
        self.memory_cache[cache_key] = value
        # Simple TTL simulation for memory cache
        asyncio.create_task(self._expire_memory_key(cache_key, ttl))
        return True
    
    async def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete key from cache."""
        cache_key = self._generate_key(key, namespace)
        
        if self.redis_client:
            try:
                result = self.redis_client.delete(cache_key)
                return bool(result)
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
        
        # Fallback to memory cache
        self.memory_cache.pop(cache_key, None)
        return True
    
    async def exists(self, key: str, namespace: str = "default") -> bool:
        """Check if key exists in cache."""
        cache_key = self._generate_key(key, namespace)
        
        if self.redis_client:
            try:
                return bool(self.redis_client.exists(cache_key))
            except Exception as e:
                logger.error(f"Redis exists error: {e}")
        
        return cache_key in self.memory_cache
    
    async def clear_namespace(self, namespace: str) -> bool:
        """Clear all keys in a namespace."""
        pattern = f"{namespace}:*"
        
        if self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                return True
            except Exception as e:
                logger.error(f"Redis clear namespace error: {e}")
        
        # Clear from memory cache
        keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith(f"{namespace}:")]
        for key in keys_to_delete:
            del self.memory_cache[key]
        return True
    
    async def _expire_memory_key(self, key: str, ttl: int):
        """Expire key from memory cache after TTL."""
        await asyncio.sleep(ttl)
        self.memory_cache.pop(key, None)

# Global cache manager instance
cache_manager = CacheManager()

def cache_key_from_args(*args, **kwargs) -> str:
    """Generate cache key from function arguments."""
    key_parts = []
    for arg in args:
        key_parts.append(str(arg))
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")
    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()

def cached(ttl: int = 300, namespace: str = "default", key_func=None):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{cache_key_from_args(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key, namespace)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            await cache_manager.set(cache_key, result, ttl, namespace)
            return result
        
        # Add cache management methods to the wrapped function
        wrapper.cache_clear = lambda: asyncio.create_task(
            cache_manager.clear_namespace(namespace)
        )
        
        return wrapper
    return decorator

# Specialized cache decorators
def crypto_cache(ttl: int = 60):
    """Cache decorator for crypto data."""
    return cached(ttl=ttl, namespace="crypto")

def market_cache(ttl: int = 300):
    """Cache decorator for market data."""
    return cached(ttl=ttl, namespace="market")

def chart_cache(ttl: int = 600):
    """Cache decorator for chart data."""
    return cached(ttl=ttl, namespace="charts")

def ai_cache(ttl: int = 1800):
    """Cache decorator for AI responses."""
    return cached(ttl=ttl, namespace="ai") 