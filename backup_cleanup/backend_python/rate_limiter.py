"""
Rate Limiter with Exponential Backoff for Financial Analytics Hub
Addresses P0 Priority: API rate limiting issues
"""

import asyncio
import time
import logging
from typing import Dict, Optional, Callable, Any
from functools import wraps
import random

logger = logging.getLogger(__name__)

class APIRateLimiter:
    """Rate limiter with exponential backoff for API calls"""
    
    def __init__(self):
        self.api_call_history: Dict[str, list] = {}
        self.failure_counts: Dict[str, int] = {}
        self.circuit_breaker_state: Dict[str, dict] = {}
        
    def reset_failures(self, api_name: str):
        """Reset failure count for an API"""
        self.failure_counts[api_name] = 0
        
    def record_failure(self, api_name: str):
        """Record a failure for an API"""
        self.failure_counts[api_name] = self.failure_counts.get(api_name, 0) + 1
        
    def should_circuit_break(self, api_name: str, threshold: int = 5) -> bool:
        """Check if circuit breaker should activate"""
        return self.failure_counts.get(api_name, 0) >= threshold
        
    async def wait_with_backoff(self, api_name: str, attempt: int):
        """Exponential backoff wait"""
        base_delay = 1.0  # 1 second base delay
        max_delay = 30.0  # Maximum 30 seconds
        
        # Exponential backoff: 1s, 2s, 4s, 8s, 16s, 30s...
        delay = min(base_delay * (2 ** attempt), max_delay)
        
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0, 0.1 * delay)
        total_delay = delay + jitter
        
        logger.info(f"Rate limit backoff for {api_name}: waiting {total_delay:.2f}s (attempt {attempt + 1})")
        await asyncio.sleep(total_delay)

def with_rate_limit_and_retry(api_name: str, max_retries: int = 3):
    """Decorator for API calls with rate limiting and retry logic"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Optional[Any]:
            rate_limiter = APIRateLimiter()
            
            for attempt in range(max_retries):
                try:
                    # Check circuit breaker
                    if rate_limiter.should_circuit_break(api_name):
                        logger.warning(f"Circuit breaker active for {api_name}, skipping call")
                        return None
                    
                    # Make the API call
                    result = await func(*args, **kwargs)
                    
                    if result is not None:
                        # Success - reset failure count
                        rate_limiter.reset_failures(api_name)
                        return result
                    else:
                        # No data received - treat as soft failure
                        rate_limiter.record_failure(api_name)
                        
                except Exception as e:
                    error_msg = str(e).lower()
                    
                    # Check for rate limiting errors
                    if any(term in error_msg for term in ['rate limit', '429', 'too many requests', 'quota']):
                        logger.warning(f"Rate limit detected for {api_name}: {str(e)}")
                        rate_limiter.record_failure(api_name)
                        
                        if attempt < max_retries - 1:
                            await rate_limiter.wait_with_backoff(api_name, attempt)
                            continue
                    
                    # Check for timeout errors
                    elif any(term in error_msg for term in ['timeout', 'connection', 'network']):
                        logger.warning(f"Network error for {api_name}: {str(e)}")
                        rate_limiter.record_failure(api_name)
                        
                        if attempt < max_retries - 1:
                            await rate_limiter.wait_with_backoff(api_name, attempt)
                            continue
                    
                    # Other errors
                    else:
                        logger.error(f"API error for {api_name}: {str(e)}")
                        rate_limiter.record_failure(api_name)
                        
                        if attempt < max_retries - 1:
                            await asyncio.sleep(1)  # Short delay for other errors
                            continue
                
                # If we get here, the attempt failed
                if attempt < max_retries - 1:
                    logger.info(f"Retrying {api_name} (attempt {attempt + 2}/{max_retries})")
            
            # All attempts failed
            logger.error(f"All {max_retries} attempts failed for {api_name}")
            return None
            
        return wrapper
    return decorator

class SmartAPIManager:
    """Smart API manager with load balancing and fallback logic"""
    
    def __init__(self):
        self.api_priorities = {
            'stock_data': ['yahoo_finance', 'alpha_vantage', 'twelve_data', 'mock'],
            'crypto_data': ['coingecko', 'twelve_data', 'mock'],
            'market_indices': ['yahoo_finance', 'alpha_vantage', 'mock']
        }
        self.api_health = {}
        self.last_health_check = {}
        
    def get_best_api(self, data_type: str) -> str:
        """Get the best available API for a data type"""
        priorities = self.api_priorities.get(data_type, [])
        
        for api in priorities:
            health = self.api_health.get(api, {'status': 'unknown', 'last_success': 0})
            
            # If API is healthy or we haven't checked recently, use it
            if health['status'] in ['healthy', 'unknown']:
                return api
        
        # Fallback to first available or mock
        return priorities[0] if priorities else 'mock'
    
    def mark_api_healthy(self, api_name: str):
        """Mark an API as healthy"""
        self.api_health[api_name] = {
            'status': 'healthy',
            'last_success': time.time(),
            'failure_count': 0
        }
    
    def mark_api_unhealthy(self, api_name: str):
        """Mark an API as unhealthy"""
        current_health = self.api_health.get(api_name, {'failure_count': 0})
        self.api_health[api_name] = {
            'status': 'unhealthy',
            'last_failure': time.time(),
            'failure_count': current_health['failure_count'] + 1
        }
    
    def get_api_health_summary(self) -> dict:
        """Get overall API health summary"""
        return {
            'apis': self.api_health,
            'total_apis': len(self.api_health),
            'healthy_apis': len([a for a in self.api_health.values() if a.get('status') == 'healthy']),
            'timestamp': time.time()
        }

# Global instance
smart_api_manager = SmartAPIManager()

# Utility functions for quick implementation
async def safe_api_call(api_func: Callable, api_name: str, *args, **kwargs) -> Optional[Any]:
    """Safely call an API function with error handling"""
    try:
        result = await api_func(*args, **kwargs)
        if result:
            smart_api_manager.mark_api_healthy(api_name)
        return result
    except Exception as e:
        smart_api_manager.mark_api_unhealthy(api_name)
        logger.error(f"Safe API call failed for {api_name}: {str(e)}")
        return None

def get_timeout_for_api(api_name: str) -> float:
    """Get appropriate timeout for different APIs"""
    timeouts = {
        'alpha_vantage': 5.0,
        'twelve_data': 4.0,
        'coingecko': 3.0,
        'yahoo_finance': 6.0,
        'world_bank': 8.0,
        'default': 5.0
    }
    return timeouts.get(api_name, timeouts['default'])

# Example usage decorators for immediate implementation
@with_rate_limit_and_retry('alpha_vantage', max_retries=3)
async def safe_alpha_vantage_call(url: str):
    """Example of protected Alpha Vantage call"""
    import aiohttp
    timeout = get_timeout_for_api('alpha_vantage')
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=timeout) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 429:
                raise Exception("Rate limit exceeded")
            else:
                raise Exception(f"HTTP {response.status}")

@with_rate_limit_and_retry('twelve_data', max_retries=2)
async def safe_twelve_data_call(url: str):
    """Example of protected Twelve Data call"""
    import aiohttp
    timeout = get_timeout_for_api('twelve_data')
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=timeout) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 429:
                raise Exception("Rate limit exceeded")
            else:
                raise Exception(f"HTTP {response.status}")

@with_rate_limit_and_retry('coingecko', max_retries=2)
async def safe_coingecko_call(url: str):
    """Example of protected CoinGecko call"""
    import aiohttp
    timeout = get_timeout_for_api('coingecko')
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=timeout) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 429:
                raise Exception("Rate limit exceeded")
            else:
                raise Exception(f"HTTP {response.status}") 