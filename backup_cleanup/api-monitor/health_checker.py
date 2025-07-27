"""
Health Checker - Core health checking logic for API providers
Implements circuit breakers, retry logic, and Redis health ledger
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin

import aiohttp
import redis
from aiohttp import ClientSession, ClientTimeout, ClientError

logger = logging.getLogger(__name__)

class HealthChecker:
    """
    Core health checking logic for API providers
    Supports different authentication types, circuit breakers, and Redis health storage
    """
    
    def __init__(self, provider_registry, redis_client: redis.Redis):
        self.provider_registry = provider_registry
        self.redis_client = redis_client
        self.session: Optional[ClientSession] = None
        
        # Health check configuration
        self.timeout_seconds = int(os.getenv("HEALTH_CHECK_TIMEOUT", "10"))
        self.retry_attempts = int(os.getenv("HEALTH_CHECK_RETRIES", "3"))
        self.circuit_breaker_threshold = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5"))
        self.circuit_breaker_timeout = int(os.getenv("CIRCUIT_BREAKER_TIMEOUT", "300"))
        
        # Initialize HTTP session
        self._init_session()
    
    def _init_session(self):
        """Initialize HTTP session with proper timeout and headers"""
        timeout = ClientTimeout(total=self.timeout_seconds)
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=10,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        self.session = ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                'User-Agent': 'FinancialAnalytics-HealthChecker/1.0',
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip, deflate'
            }
        )
    
    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
    
    async def check_provider_health(self, provider_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check health of a single provider
        Returns health status with timing and error information
        """
        provider_id = provider_config['id']
        
        # Check circuit breaker status
        if await self._is_circuit_breaker_open(provider_id):
            logger.debug(f"Circuit breaker open for {provider_id}, skipping health check")
            return {
                'provider_id': provider_id,
                'status': 'circuit_breaker_open',
                'timestamp': time.time(),
                'error': 'Circuit breaker is open'
            }
        
        start_time = time.time()
        
        try:
            # Perform the actual health check
            result = await self._perform_health_check(provider_config)
            
            # Update circuit breaker on success
            await self._record_health_check_success(provider_id)
            
            # Store result in Redis
            await self._store_health_result(provider_id, result)
            
            return result
            
        except Exception as e:
            error_result = {
                'provider_id': provider_id,
                'status': 'unhealthy',
                'timestamp': time.time(),
                'response_time': time.time() - start_time,
                'error': str(e)
            }
            
            # Update circuit breaker on failure
            await self._record_health_check_failure(provider_id)
            
            # Store error result in Redis
            await self._store_health_result(provider_id, error_result)
            
            logger.warning(f"Health check failed for {provider_id}: {e}")
            return error_result
    
    async def _perform_health_check(self, provider_config: Dict[str, Any]) -> Dict[str, Any]:
        """Perform the actual HTTP health check"""
        provider_id = provider_config['id']
        base_url = provider_config['base_url']
        health_endpoint = provider_config['health_endpoint']
        auth_type = provider_config.get('auth_type', 'none')
        
        # Build health check URL
        if health_endpoint.startswith('http'):
            url = health_endpoint
        else:
            url = urljoin(base_url, health_endpoint)
        
        # Handle API key substitution
        if '{api_key}' in url:
            api_key = await self._get_api_key(provider_config)
            if not api_key:
                raise Exception(f"API key not found for provider {provider_id}")
            url = url.replace('{api_key}', api_key)
        
        # Prepare headers for authentication
        headers = {}
        if auth_type == 'bearer':
            token = await self._get_api_key(provider_config)
            if token:
                headers['Authorization'] = f'Bearer {token}'
        elif auth_type == 'api_key' and '{api_key}' not in url:
            # API key in header
            api_key = await self._get_api_key(provider_config)
            if api_key:
                headers['X-API-Key'] = api_key
        
        start_time = time.time()
        
        # Perform health check with retries
        last_exception = None
        
        for attempt in range(self.retry_attempts):
            try:
                async with self.session.get(url, headers=headers) as response:
                    response_time = time.time() - start_time
                    
                    # Check response status
                    if response.status == 200:
                        # Try to parse JSON response for validation
                        try:
                            response_data = await response.json()
                            # Additional validation based on provider type
                            if await self._validate_response_data(provider_config, response_data):
                                return {
                                    'provider_id': provider_id,
                                    'status': 'healthy',
                                    'timestamp': time.time(),
                                    'response_time': response_time,
                                    'http_status': response.status
                                }
                            else:
                                raise Exception("Response validation failed")
                        except json.JSONDecodeError:
                            # Some endpoints may not return JSON
                            if response.status == 200:
                                return {
                                    'provider_id': provider_id,
                                    'status': 'healthy',
                                    'timestamp': time.time(),
                                    'response_time': response_time,
                                    'http_status': response.status
                                }
                    
                    # Handle rate limiting
                    elif response.status == 429:
                        raise Exception(f"Rate limited (HTTP {response.status})")
                    
                    # Handle other HTTP errors
                    else:
                        raise Exception(f"HTTP {response.status}: {response.reason}")
                        
            except (ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    raise last_exception
        
        # If we get here, all retries failed
        raise last_exception or Exception("All retry attempts failed")
    
    async def _validate_response_data(self, provider_config: Dict[str, Any], data: Any) -> bool:
        """Validate response data based on provider type"""
        category = provider_config.get('category', '')
        
        try:
            if category == 'stock':
                # Stock data should have price-related fields
                if isinstance(data, dict):
                    return any(key in data for key in ['price', 'close', 'last', 'quote', 'regularMarketPrice'])
                elif isinstance(data, list) and data:
                    return any(key in data[0] for key in ['price', 'close', 'last', 'quote'] if isinstance(data[0], dict))
            
            elif category == 'crypto':
                # Crypto data validation
                if isinstance(data, dict):
                    return any(key in data for key in ['price', 'rate', 'last', 'ticker', 'result'])
            
            elif category == 'forex':
                # Forex data validation
                if isinstance(data, dict):
                    return any(key in data for key in ['rates', 'quotes', 'conversion_rates', 'result'])
            
            elif category == 'news':
                # News data validation
                if isinstance(data, dict):
                    return any(key in data for key in ['articles', 'feed', 'news', 'stories'])
            
            # Default validation - just check if we got some data
            return data is not None
            
        except Exception as e:
            logger.warning(f"Response validation error for {provider_config['id']}: {e}")
            return True  # Don't fail on validation errors
    
    async def _get_api_key(self, provider_config: Dict[str, Any]) -> Optional[str]:
        """Get API key for provider from environment variables"""
        required_keys = provider_config.get('required_env_keys', [])
        
        if not required_keys:
            return None
        
        # Try to get the first available key
        for key_name in required_keys:
            api_key = os.getenv(key_name)
            if api_key:
                return api_key
        
        return None
    
    async def _is_circuit_breaker_open(self, provider_id: str) -> bool:
        """Check if circuit breaker is open for provider"""
        try:
            circuit_key = f"circuit_breaker:{provider_id}"
            failure_count = self.redis_client.get(circuit_key)
            
            if failure_count and int(failure_count) >= self.circuit_breaker_threshold:
                # Check if timeout has passed
                circuit_time_key = f"circuit_breaker_time:{provider_id}"
                circuit_time = self.redis_client.get(circuit_time_key)
                
                if circuit_time:
                    time_since_opened = time.time() - float(circuit_time)
                    if time_since_opened > self.circuit_breaker_timeout:
                        # Reset circuit breaker
                        await self._reset_circuit_breaker(provider_id)
                        return False
                    return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking circuit breaker for {provider_id}: {e}")
            return False
    
    async def _record_health_check_success(self, provider_id: str):
        """Record successful health check"""
        try:
            circuit_key = f"circuit_breaker:{provider_id}"
            self.redis_client.delete(circuit_key)
            
            circuit_time_key = f"circuit_breaker_time:{provider_id}"
            self.redis_client.delete(circuit_time_key)
            
        except Exception as e:
            logger.error(f"Error recording success for {provider_id}: {e}")
    
    async def _record_health_check_failure(self, provider_id: str):
        """Record failed health check and update circuit breaker"""
        try:
            circuit_key = f"circuit_breaker:{provider_id}"
            current_failures = self.redis_client.get(circuit_key)
            
            if current_failures:
                failures = int(current_failures) + 1
            else:
                failures = 1
            
            self.redis_client.set(circuit_key, failures, ex=self.circuit_breaker_timeout)
            
            # If threshold reached, record the time
            if failures >= self.circuit_breaker_threshold:
                circuit_time_key = f"circuit_breaker_time:{provider_id}"
                self.redis_client.set(circuit_time_key, time.time(), ex=self.circuit_breaker_timeout)
                logger.warning(f"Circuit breaker opened for {provider_id} after {failures} failures")
            
        except Exception as e:
            logger.error(f"Error recording failure for {provider_id}: {e}")
    
    async def _reset_circuit_breaker(self, provider_id: str):
        """Reset circuit breaker for provider"""
        try:
            circuit_key = f"circuit_breaker:{provider_id}"
            circuit_time_key = f"circuit_breaker_time:{provider_id}"
            
            self.redis_client.delete(circuit_key)
            self.redis_client.delete(circuit_time_key)
            
            logger.info(f"Circuit breaker reset for {provider_id}")
            
        except Exception as e:
            logger.error(f"Error resetting circuit breaker for {provider_id}: {e}")
    
    async def _store_health_result(self, provider_id: str, result: Dict[str, Any]):
        """Store health check result in Redis"""
        try:
            # Store current health status
            health_key = f"api_health:{provider_id}"
            health_data = {
                'status': result['status'],
                'last_check': result['timestamp'],
                'response_time': result.get('response_time', 0),
                'error': result.get('error', ''),
                'http_status': result.get('http_status', 0)
            }
            
            # Store as hash with TTL
            self.redis_client.hset(health_key, mapping=health_data)
            self.redis_client.expire(health_key, 3600)  # 1 hour TTL
            
            # Maintain uptime history (last 100 checks)
            uptime_key = f"api_uptime:{provider_id}"
            self.redis_client.lpush(uptime_key, result['status'])
            self.redis_client.ltrim(uptime_key, 0, 99)  # Keep last 100 checks
            self.redis_client.expire(uptime_key, 86400)  # 24 hour TTL
            
            # Store detailed history for analysis
            history_key = f"api_history:{provider_id}"
            history_data = json.dumps(result)
            self.redis_client.lpush(history_key, history_data)
            self.redis_client.ltrim(history_key, 0, 999)  # Keep last 1000 checks
            self.redis_client.expire(history_key, 604800)  # 7 day TTL
            
        except Exception as e:
            logger.error(f"Error storing health result for {provider_id}: {e}")
    
    async def batch_health_check(self, provider_configs: List[Dict[str, Any]], max_concurrent: int = 10) -> List[Dict[str, Any]]:
        """Perform health checks on multiple providers concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def check_with_semaphore(provider_config):
            async with semaphore:
                return await self.check_provider_health(provider_config)
        
        tasks = [check_with_semaphore(config) for config in provider_configs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                provider_id = provider_configs[i]['id']
                processed_results.append({
                    'provider_id': provider_id,
                    'status': 'error',
                    'timestamp': time.time(),
                    'error': str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def get_provider_health_summary(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive health summary for a provider"""
        try:
            # Get current health
            health_key = f"api_health:{provider_id}"
            current_health = self.redis_client.hgetall(health_key)
            
            if not current_health:
                return None
            
            # Get uptime history
            uptime_key = f"api_uptime:{provider_id}"
            uptime_history = self.redis_client.lrange(uptime_key, 0, -1)
            
            # Calculate uptime percentage
            if uptime_history:
                healthy_count = sum(1 for status in uptime_history if status == 'healthy')
                uptime_percentage = (healthy_count / len(uptime_history)) * 100
            else:
                uptime_percentage = 0.0
            
            # Get circuit breaker status
            circuit_key = f"circuit_breaker:{provider_id}"
            circuit_failures = self.redis_client.get(circuit_key)
            is_circuit_open = await self._is_circuit_breaker_open(provider_id)
            
            return {
                'provider_id': provider_id,
                'current_status': current_health.get('status'),
                'last_check': float(current_health.get('last_check', 0)),
                'response_time': float(current_health.get('response_time', 0)),
                'uptime_percentage': uptime_percentage,
                'total_checks': len(uptime_history),
                'circuit_breaker_open': is_circuit_open,
                'circuit_failures': int(circuit_failures) if circuit_failures else 0,
                'error_message': current_health.get('error')
            }
            
        except Exception as e:
            logger.error(f"Error getting health summary for {provider_id}: {e}")
            return None 