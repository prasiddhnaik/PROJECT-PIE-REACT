"""
Shared rate limiting utilities for microservices.
"""

import time
import redis
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Request
import logging
import os
import json

logger = logging.getLogger(__name__)

class RateLimiter:
    """Redis-based distributed rate limiter."""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = None
        self.memory_store = {}  # Fallback in-memory store
        
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("Rate limiter Redis connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed for rate limiter, using memory store: {e}")
            self.redis_client = None
    
    def _get_key(self, identifier: str, window: str) -> str:
        """Generate rate limit key."""
        return f"rate_limit:{identifier}:{window}"
    
    async def is_allowed(self, identifier: str, limit: int, window_seconds: int, provider_id: Optional[str] = None) -> tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed based on rate limit.
        Returns (is_allowed, info_dict)
        """
        now = int(time.time())
        window_start = now - window_seconds
        
        # Include provider_id in key if provided for per-provider tracking
        if provider_id:
            key = self._get_key(f"{identifier}:{provider_id}", f"{window_seconds}s")
        else:
            key = self._get_key(identifier, f"{window_seconds}s")
        
        if self.redis_client:
            try:
                # Use Redis sorted set for sliding window
                pipe = self.redis_client.pipeline()
                
                # Remove old entries
                pipe.zremrangebyscore(key, 0, window_start)
                
                # Count current requests
                pipe.zcard(key)
                
                # Add current request
                pipe.zadd(key, {str(now): now})
                
                # Set expiry
                pipe.expire(key, window_seconds)
                
                results = pipe.execute()
                current_requests = results[1]
                
                is_allowed = current_requests < limit
                
                return is_allowed, {
                    "limit": limit,
                    "remaining": max(0, limit - current_requests - 1) if is_allowed else 0,
                    "reset_time": now + window_seconds,
                    "window_seconds": window_seconds,
                    "provider_id": provider_id
                }
                
            except Exception as e:
                logger.error(f"Redis rate limit error: {e}")
                # Fall through to memory store
        
        # Fallback to memory store
        if key not in self.memory_store:
            self.memory_store[key] = []
        
        # Clean old requests
        self.memory_store[key] = [
            req_time for req_time in self.memory_store[key] 
            if req_time > window_start
        ]
        
        current_requests = len(self.memory_store[key])
        is_allowed = current_requests < limit
        
        if is_allowed:
            self.memory_store[key].append(now)
        
        return is_allowed, {
            "limit": limit,
            "remaining": max(0, limit - current_requests - 1) if is_allowed else 0,
            "reset_time": now + window_seconds,
            "window_seconds": window_seconds,
            "provider_id": provider_id
        }
    
    async def check_rate_limit(self, identifier: str, limit: int, window_seconds: int, provider_id: Optional[str] = None):
        """Check rate limit and raise HTTPException if exceeded."""
        is_allowed, info = await self.is_allowed(identifier, limit, window_seconds, provider_id)
        
        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": info["limit"],
                    "window_seconds": info["window_seconds"],
                    "reset_time": info["reset_time"],
                    "provider_id": provider_id
                },
                headers={
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": str(info["remaining"]),
                    "X-RateLimit-Reset": str(info["reset_time"]),
                    "Retry-After": str(info["window_seconds"])
                }
            )
        
        return info
    
    async def check_provider_quota(self, provider_id: str, limit_per_minute: int, limit_per_day: int) -> Dict[str, Any]:
        """Check provider-specific rate limits"""
        identifier = f"provider:{provider_id}"
        
        # Check minute limit
        minute_allowed, minute_info = await self.is_allowed(identifier, limit_per_minute, 60)
        
        # Check daily limit
        day_allowed, day_info = await self.is_allowed(identifier, limit_per_day, 86400)
        
        # Return combined status
        is_allowed = minute_allowed and day_allowed
        
        return {
            "allowed": is_allowed,
            "provider_id": provider_id,
            "minute_limit": minute_info,
            "day_limit": day_info,
            "blocked_by": "minute" if not minute_allowed else "day" if not day_allowed else None
        }
    
    async def record_provider_call(self, provider_id: str):
        """Record API call for provider quota tracking"""
        identifier = f"provider:{provider_id}"
        now = int(time.time())
        
        if self.redis_client:
            try:
                # Record call for minute window
                minute_key = self._get_key(identifier, "60s")
                self.redis_client.zadd(minute_key, {str(now): now})
                self.redis_client.expire(minute_key, 60)
                
                # Record call for day window
                day_key = self._get_key(identifier, "86400s")
                self.redis_client.zadd(day_key, {str(now): now})
                self.redis_client.expire(day_key, 86400)
                
            except Exception as e:
                logger.error(f"Failed to record provider call for {provider_id}: {e}")
    
    async def get_provider_usage(self, provider_id: str) -> Dict[str, int]:
        """Get current usage statistics for a provider"""
        identifier = f"provider:{provider_id}"
        now = int(time.time())
        
        usage = {
            "minute_count": 0,
            "hour_count": 0,
            "day_count": 0
        }
        
        if self.redis_client:
            try:
                # Get minute usage
                minute_key = self._get_key(identifier, "60s")
                minute_count = self.redis_client.zcount(minute_key, now - 60, now)
                usage["minute_count"] = minute_count
                
                # Get hour usage  
                hour_key = self._get_key(identifier, "3600s")
                hour_count = self.redis_client.zcount(hour_key, now - 3600, now)
                usage["hour_count"] = hour_count
                
                # Get day usage
                day_key = self._get_key(identifier, "86400s")
                day_count = self.redis_client.zcount(day_key, now - 86400, now)
                usage["day_count"] = day_count
                
            except Exception as e:
                logger.error(f"Failed to get provider usage for {provider_id}: {e}")
        
        return usage

# Global rate limiter instance
rate_limiter = RateLimiter()

# Service-specific rate limit configurations
RATE_LIMITS = {
    "data_service": {
        "requests_per_minute": 300,
        "requests_per_hour": 2000
    },
    "chart_service": {
        "requests_per_minute": 100,
        "requests_per_hour": 800
    },
    "graph_service": {
        "requests_per_minute": 50,
        "requests_per_hour": 400
    },
    "ai_service": {
        "requests_per_minute": 30,
        "requests_per_hour": 200,
        "chat_per_minute": 10,
        "chat_per_hour": 50
    },
    "api_gateway": {
        "requests_per_minute": 500,
        "requests_per_hour": 5000
    }
}

def get_client_identifier(request: Request) -> str:
    """Get client identifier for rate limiting."""
    # Try to get user ID from auth
    user_id = getattr(request.state, 'user_id', None)
    if user_id:
        return f"user:{user_id}"
    
    # Fallback to IP address
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return f"ip:{forwarded_for.split(',')[0].strip()}"
    
    client_host = request.client.host if request.client else "unknown"
    return f"ip:{client_host}"

async def apply_rate_limit(request: Request, service: str, limit_type: str = "requests"):
    """Apply rate limit for a service."""
    client_id = get_client_identifier(request)
    service_limits = RATE_LIMITS.get(service, RATE_LIMITS["api_gateway"])
    
    # Apply per-minute limit
    minute_limit_key = f"{limit_type}_per_minute"
    if minute_limit_key in service_limits:
        await rate_limiter.check_rate_limit(
            f"{client_id}:{service}:{limit_type}:minute",
            service_limits[minute_limit_key],
            60
        )
    
    # Apply per-hour limit
    hour_limit_key = f"{limit_type}_per_hour"
    if hour_limit_key in service_limits:
        await rate_limiter.check_rate_limit(
            f"{client_id}:{service}:{limit_type}:hour",
            service_limits[hour_limit_key],
            3600
        )

# Rate limit decorators for different services
def data_service_rate_limit():
    """Rate limit decorator for data service."""
    async def dependency(request: Request):
        await apply_rate_limit(request, "data_service")
        return True
    return dependency

def chart_service_rate_limit():
    """Rate limit decorator for chart service."""
    async def dependency(request: Request):
        await apply_rate_limit(request, "chart_service")
        return True
    return dependency

def graph_service_rate_limit():
    """Rate limit decorator for graph service."""
    async def dependency(request: Request):
        await apply_rate_limit(request, "graph_service")
        return True
    return dependency

def ai_service_rate_limit(limit_type: str = "requests"):
    """Rate limit decorator for AI service."""
    async def dependency(request: Request):
        await apply_rate_limit(request, "ai_service", limit_type)
        return True
    return dependency

def api_gateway_rate_limit():
    """Rate limit decorator for API gateway."""
    async def dependency(request: Request):
        await apply_rate_limit(request, "api_gateway")
        return True
    return dependency 