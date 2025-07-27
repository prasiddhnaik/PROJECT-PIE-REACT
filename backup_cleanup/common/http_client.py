"""
Shared HTTP client utilities for microservices.
"""

import httpx
import asyncio
import time
import random
from typing import Dict, Any, Optional, Union, List, Callable, Awaitable
from functools import wraps
import logging
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime, timedelta
import hashlib
import pickle
from collections import defaultdict, deque
from .logging import log_structured_error, PerformanceLogger
from .errors import (
    ServiceError, BadGatewayError, ServiceUnavailableError, 
    GatewayTimeoutError, UnauthorizedError, ForbiddenError,
    InvalidInputError, NotFoundError, ValidationError, RateLimitError
)

logger = logging.getLogger(__name__)

class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: int = 60
    expected_exception: Exception = Exception

@dataclass
class CacheConfig:
    """Configuration for request caching"""
    enabled: bool = True
    ttl_seconds: int = 300  # 5 minutes default
    max_size: int = 1000
    include_headers: bool = False
    include_query_params: bool = True

@dataclass
class RequestMetrics:
    """Metrics for request tracking"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    error_counts: Dict[str, int] = field(default_factory=dict)
    
    @property
    def average_response_time(self) -> float:
        return self.total_response_time / self.total_requests if self.total_requests > 0 else 0.0
    
    @property
    def success_rate(self) -> float:
        return self.successful_requests / self.total_requests if self.total_requests > 0 else 0.0

class CircuitBreakerError(Exception):
    """Custom exception for circuit breaker open state"""
    pass

class GatewayError(Exception):
    """Custom exception for gateway errors"""
    pass

class CacheKey:
    """Cache key generator for HTTP requests"""
    
    @staticmethod
    def generate(method: str, url: str, headers: Dict = None, 
                 query_params: Dict = None, body: Any = None, 
                 config: CacheConfig = None) -> str:
        """Generate a cache key for the request"""
        if not config:
            config = CacheConfig()
        
        # Build key components
        key_parts = [method.upper(), url]
        
        if config.include_query_params and query_params:
            # Sort query params for consistent keys
            sorted_params = sorted(query_params.items())
            key_parts.append(json.dumps(sorted_params, sort_keys=True))
        
        if config.include_headers and headers:
            # Only include cache-relevant headers
            cache_headers = {k: v for k, v in headers.items() 
                           if k.lower() in ['accept', 'content-type', 'authorization']}
            if cache_headers:
                key_parts.append(json.dumps(cache_headers, sort_keys=True))
        
        if body:
            if isinstance(body, (dict, list)):
                key_parts.append(json.dumps(body, sort_keys=True))
            else:
                key_parts.append(str(body))
        
        # Create hash of the key
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

class RequestCache:
    """Simple in-memory request cache with TTL"""
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or CacheConfig()
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, datetime] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        
        if self.config.enabled:
            self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background cleanup task"""
        async def cleanup():
            while True:
                await asyncio.sleep(60)  # Clean up every minute
                self._cleanup_expired()
        
        self._cleanup_task = asyncio.create_task(cleanup())
    
    def _cleanup_expired(self):
        """Remove expired cache entries"""
        now = datetime.now()
        expired_keys = []
        
        for key, access_time in self._access_times.items():
            if (now - access_time).total_seconds() > self.config.ttl_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            self._cache.pop(key, None)
            self._access_times.pop(key, None)
        
        # Also remove oldest entries if cache is too large
        if len(self._cache) > self.config.max_size:
            sorted_keys = sorted(self._access_times.items(), key=lambda x: x[1])
            keys_to_remove = [k for k, _ in sorted_keys[:len(self._cache) - self.config.max_size]]
            
            for key in keys_to_remove:
                self._cache.pop(key, None)
                self._access_times.pop(key, None)
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached response"""
        if not self.config.enabled:
            return None
        
        if key in self._cache:
            entry = self._cache[key]
            access_time = self._access_times[key]
            
            # Check if entry is still valid
            if (datetime.now() - access_time).total_seconds() <= self.config.ttl_seconds:
                self._access_times[key] = datetime.now()  # Update access time
                return entry
        
        return None
    
    def set(self, key: str, response_data: Dict[str, Any]):
        """Cache response data"""
        if not self.config.enabled:
            return
        
        self._cache[key] = response_data
        self._access_times[key] = datetime.now()
    
    def invalidate(self, pattern: str = None):
        """Invalidate cache entries"""
        if pattern:
            keys_to_remove = [k for k in self._cache.keys() if pattern in k]
        else:
            keys_to_remove = list(self._cache.keys())
        
        for key in keys_to_remove:
            self._cache.pop(key, None)
            self._access_times.pop(key, None)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "enabled": self.config.enabled,
            "size": len(self._cache),
            "max_size": self.config.max_size,
            "ttl_seconds": self.config.ttl_seconds
        }
    
    async def close(self):
        """Stop cleanup task"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

class RequestInterceptor:
    """Request/response interceptor for logging, metrics, and transformations"""
    
    def __init__(self):
        self.request_hooks: List[Callable] = []
        self.response_hooks: List[Callable] = []
        self.error_hooks: List[Callable] = []
    
    def add_request_hook(self, hook: Callable[[Dict[str, Any]], Awaitable[None]]):
        """Add request hook"""
        self.request_hooks.append(hook)
    
    def add_response_hook(self, hook: Callable[[Dict[str, Any]], Awaitable[None]]):
        """Add response hook"""
        self.response_hooks.append(hook)
    
    def add_error_hook(self, hook: Callable[[Dict[str, Any]], Awaitable[None]]):
        """Add error hook"""
        self.error_hooks.append(hook)
    
    async def execute_request_hooks(self, request_data: Dict[str, Any]):
        """Execute request hooks"""
        for hook in self.request_hooks:
            try:
                await hook(request_data)
            except Exception as e:
                logger.error(f"Request hook failed: {e}")
    
    async def execute_response_hooks(self, response_data: Dict[str, Any]):
        """Execute response hooks"""
        for hook in self.response_hooks:
            try:
                await hook(response_data)
            except Exception as e:
                logger.error(f"Response hook failed: {e}")
    
    async def execute_error_hooks(self, error_data: Dict[str, Any]):
        """Execute error hooks"""
        for hook in self.error_hooks:
            try:
                await hook(error_data)
            except Exception as e:
                logger.error(f"Error hook failed: {e}")

class CircuitBreaker:
    """Enhanced circuit breaker implementation with configurable thresholds"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60, 
                 expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        
    def call(self, func, *args, **kwargs):
        if self.state == 'OPEN':
            if self._should_attempt_reset():
                self.state = 'HALF_OPEN'
            else:
                raise CircuitBreakerError(f"Circuit breaker is OPEN. Last failure: {self.last_failure_time}")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    async def call_async(self, func, *args, **kwargs):
        if self.state == 'OPEN':
            if self._should_attempt_reset():
                self.state = 'HALF_OPEN'
            else:
                raise CircuitBreakerError(f"Circuit breaker is OPEN. Last failure: {self.last_failure_time}")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self):
        return (datetime.now() - self.last_failure_time).seconds > self.recovery_timeout
    
    def _on_success(self):
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state for monitoring"""
        return {
            'state': self.state,
            'failure_count': self.failure_count,
            'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'failure_threshold': self.failure_threshold
        }

class HTTPClient:
    """Enhanced HTTP client with improved retry logic and error handling"""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3, 
                 cache_config: CacheConfig = None, 
                 connection_pool_size: int = 100):
        self.timeout = timeout
        self.max_retries = max_retries
        self.cache = RequestCache(cache_config)
        self.interceptor = RequestInterceptor()
        self.metrics = RequestMetrics()
        
        # Enhanced connection pooling
        limits = httpx.Limits(
            max_keepalive_connections=connection_pool_size,
            max_connections=connection_pool_size * 2,
            keepalive_expiry=30
        )
        
        self.client = httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
            headers={
                'User-Agent': 'FinancialAnalytics-HTTPClient/1.0',
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip, deflate'
            }
        )
        self.logger = logging.getLogger(__name__)
        
        # Setup default hooks
        self._setup_default_hooks()
    
    def _setup_default_hooks(self):
        """Setup default request/response hooks"""
        
        async def metrics_hook(request_data: Dict[str, Any]):
            """Track request metrics"""
            self.metrics.total_requests += 1
            self.metrics.last_request_time = datetime.now()
        
        async def response_metrics_hook(response_data: Dict[str, Any]):
            """Track response metrics"""
            response_time = response_data.get('response_time', 0)
            status_code = response_data.get('status_code', 0)
            
            self.metrics.total_response_time += response_time
            self.metrics.min_response_time = min(self.metrics.min_response_time, response_time)
            self.metrics.max_response_time = max(self.metrics.max_response_time, response_time)
            
            if 200 <= status_code < 400:
                self.metrics.successful_requests += 1
            else:
                self.metrics.failed_requests += 1
                error_type = f"http_{status_code}"
                self.metrics.error_counts[error_type] = self.metrics.error_counts.get(error_type, 0) + 1
        
        async def error_metrics_hook(error_data: Dict[str, Any]):
            """Track error metrics"""
            self.metrics.failed_requests += 1
            error_type = error_data.get('error_type', 'unknown')
            self.metrics.error_counts[error_type] = self.metrics.error_counts.get(error_type, 0) + 1
        
        self.interceptor.add_request_hook(metrics_hook)
        self.interceptor.add_response_hook(response_metrics_hook)
        self.interceptor.add_error_hook(error_metrics_hook)
    
    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make HTTP request with enhanced retry logic and caching"""
        start_time = time.time()
        
        # Generate cache key for GET requests
        cache_key = None
        if method.upper() == 'GET':
            cache_key = CacheKey.generate(
                method=method,
                url=url,
                headers=kwargs.get('headers'),
                query_params=kwargs.get('params'),
                config=self.cache.config
            )
            
            # Check cache first
            cached_response = self.cache.get(cache_key)
            if cached_response:
                logger.debug(f"Cache hit for {url}")
                return self._create_cached_response(cached_response)
        
        # Execute request hooks
        request_data = {
            'method': method,
            'url': url,
            'headers': kwargs.get('headers', {}),
            'params': kwargs.get('params', {}),
            'timestamp': datetime.now()
        }
        await self.interceptor.execute_request_hooks(request_data)
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.request(method, url, **kwargs)
                response_time = time.time() - start_time
                
                # Execute response hooks
                response_data = {
                    'method': method,
                    'url': url,
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'headers': dict(response.headers),
                    'timestamp': datetime.now()
                }
                await self.interceptor.execute_response_hooks(response_data)
                
                # Cache successful GET responses
                if method.upper() == 'GET' and response.status_code == 200 and cache_key:
                    try:
                        response_text = response.text
                        cached_data = {
                            'status_code': response.status_code,
                            'headers': dict(response.headers),
                            'content': response_text,
                            'timestamp': datetime.now().isoformat()
                        }
                        self.cache.set(cache_key, cached_data)
                    except Exception as e:
                        logger.warning(f"Failed to cache response: {e}")
                
                # Don't retry on client errors (4xx) except specific cases
                if response.status_code < 500 and response.status_code != 429:
                    return response
                
                # Retry on server errors and rate limiting
                if attempt < self.max_retries:
                    # Respect rate limiting headers
                    if response.status_code == 429:
                        retry_after = int(response.headers.get('Retry-After', 1))
                        await asyncio.sleep(min(retry_after, 60))  # Cap at 60 seconds
                    else:
                        # Exponential backoff with jitter
                        delay = (2 ** attempt) + random.uniform(0, 1)
                        await asyncio.sleep(min(delay, 30))  # Cap at 30 seconds
                    continue
                
                return response
                
            except (httpx.TimeoutException, httpx.ConnectError, httpx.RequestError) as e:
                last_exception = e
                response_time = time.time() - start_time
                
                # Execute error hooks
                error_data = {
                    'method': method,
                    'url': url,
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'response_time': response_time,
                    'attempt': attempt + 1,
                    'timestamp': datetime.now()
                }
                await self.interceptor.execute_error_hooks(error_data)
                
                if attempt < self.max_retries:
                    # Exponential backoff with jitter for network errors
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    await asyncio.sleep(min(delay, 30))
                    continue
                break
        
        # If we get here, all retries failed
        if last_exception:
            raise last_exception
        
        # This shouldn't happen, but just in case
        raise httpx.RequestError("All retry attempts failed")
    
    def _create_cached_response(self, cached_data: Dict[str, Any]) -> httpx.Response:
        """Create a response object from cached data"""
        # This is a simplified version - in practice you'd want to create a proper mock response
        response = httpx.Response(
            status_code=cached_data['status_code'],
            headers=cached_data['headers'],
            content=cached_data['content'].encode() if isinstance(cached_data['content'], str) else cached_data['content']
        )
        return response
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get client metrics"""
        return {
            'total_requests': self.metrics.total_requests,
            'successful_requests': self.metrics.successful_requests,
            'failed_requests': self.metrics.failed_requests,
            'success_rate': self.metrics.success_rate,
            'average_response_time': self.metrics.average_response_time,
            'min_response_time': self.metrics.min_response_time if self.metrics.min_response_time != float('inf') else 0,
            'max_response_time': self.metrics.max_response_time,
            'error_counts': self.metrics.error_counts,
            'cache_stats': self.cache.get_stats(),
            'last_request_time': self.metrics.last_request_time.isoformat() if self.metrics.last_request_time else None
        }
    
    async def close(self):
        await self.client.aclose()
        await self.cache.close()

class ServiceClient:
    """Enhanced service client with better error handling and status preservation"""
    
    def __init__(self, base_url: str, service_name: str, timeout: int = 30,
                 cache_config: CacheConfig = None):
        self.base_url = base_url.rstrip('/')
        self.service_name = service_name
        self.http_client = HTTPClient(timeout=timeout, cache_config=cache_config)
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )
        self.logger = logging.getLogger(f"service_client.{service_name}")
        self.performance_logger = PerformanceLogger(self.logger)
        
        # Service-specific metrics
        self.service_metrics = RequestMetrics()
    
    async def call_service(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Enhanced service call with proper error handling and status preservation"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        request_id = kwargs.get('headers', {}).get('X-Request-ID')
        
        try:
            response = await self.circuit_breaker.call_async(
                self.http_client.request, method, url, **kwargs
            )
            
            response_time = time.time() - start_time
            
            # Log performance metrics
            self.performance_logger.log_performance(
                service_name=self.service_name,
                endpoint=endpoint,
                response_time=response_time,
                status_code=response.status_code,
                request_id=request_id
            )
            
            # Update service metrics
            self.service_metrics.total_requests += 1
            self.service_metrics.total_response_time += response_time
            self.service_metrics.min_response_time = min(self.service_metrics.min_response_time, response_time)
            self.service_metrics.max_response_time = max(self.service_metrics.max_response_time, response_time)
            self.service_metrics.last_request_time = datetime.now()
            
            # Handle different response types
            if response.status_code >= 400:
                # Preserve the original status code and create appropriate exception
                error_msg = f"Service {self.service_name} returned {response.status_code}"
                
                try:
                    error_detail = response.json()
                    if 'detail' in error_detail:
                        error_msg = f"{error_msg}: {error_detail['detail']}"
                except:
                    error_msg = f"{error_msg}: {response.text[:200]}"
                
                # Update error metrics
                self.service_metrics.failed_requests += 1
                error_type = f"http_{response.status_code}"
                self.service_metrics.error_counts[error_type] = self.service_metrics.error_counts.get(error_type, 0) + 1
                
                # Map status codes to appropriate exceptions with proper status preservation
                if 400 <= response.status_code < 500:
                    # Client errors - preserve original status code by re-raising HTTPStatusError
                    raise httpx.HTTPStatusError(error_msg, request=response.request, response=response)
                else:
                    # Server errors - preserve original status code instead of converting to generic error
                    raise httpx.HTTPStatusError(error_msg, request=response.request, response=response)
            
            # Update success metrics
            self.service_metrics.successful_requests += 1
            
            # Return successful response data
            try:
                return response.json()
            except:
                return {"data": response.text, "status_code": response.status_code}
                
        except CircuitBreakerError as e:
            self.performance_logger.log_error(
                error_type="circuit_breaker_open",
                service_name=self.service_name,
                endpoint=endpoint,
                error_message=str(e),
                request_id=request_id
            )
            raise ServiceUnavailableError(
                message=f"Service {self.service_name} is currently unavailable: {str(e)}",
                http_status=503,
                context={"service": self.service_name, "endpoint": endpoint},
                request_id=request_id,
                service_name=self.service_name
            )
            
        except httpx.TimeoutException as e:
            response_time = time.time() - start_time
            self.performance_logger.log_error(
                error_type="timeout",
                service_name=self.service_name,
                endpoint=endpoint,
                error_message=f"Request timeout after {response_time:.2f}s",
                request_id=request_id
            )
            raise GatewayTimeoutError(
                message=f"Service {self.service_name} timeout after {response_time:.2f}s",
                http_status=504,
                context={"service": self.service_name, "endpoint": endpoint, "response_time": response_time},
                request_id=request_id,
                service_name=self.service_name
            )
            
        except httpx.ConnectError as e:
            self.performance_logger.log_error(
                error_type="connection_error",
                service_name=self.service_name,
                endpoint=endpoint,
                error_message=str(e),
                request_id=request_id
            )
            raise BadGatewayError(
                message=f"Cannot connect to service {self.service_name}: {str(e)}",
                http_status=502,
                context={"service": self.service_name, "endpoint": endpoint},
                request_id=request_id,
                service_name=self.service_name
            )
            
        except httpx.RequestError as e:
            self.performance_logger.log_error(
                error_type="request_error",
                service_name=self.service_name,
                endpoint=endpoint,
                error_message=str(e),
                request_id=request_id
            )
            raise BadGatewayError(
                message=f"Request error to service {self.service_name}: {str(e)}",
                http_status=502,
                context={"service": self.service_name, "endpoint": endpoint},
                request_id=request_id,
                service_name=self.service_name
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            self.performance_logger.log_error(
                error_type="unknown_error",
                service_name=self.service_name,
                endpoint=endpoint,
                error_message=str(e),
                request_id=request_id
            )
            log_structured_error(
                logger=self.logger,
                message=f"Unexpected error calling {self.service_name}: {str(e)}",
                error_category="service_communication_error",
                request_id=request_id,
                service_name=self.service_name,
                endpoint=endpoint,
                downstream_service=self.service_name,
                exc_info=True
            )
            raise
    
    def get_circuit_breaker_state(self) -> Dict[str, Any]:
        """Get circuit breaker state for monitoring"""
        return {
            'service': self.service_name,
            **self.circuit_breaker.get_state()
        }
    
    def get_service_metrics(self) -> Dict[str, Any]:
        """Get service-specific metrics"""
        return {
            'service': self.service_name,
            'total_requests': self.service_metrics.total_requests,
            'successful_requests': self.service_metrics.successful_requests,
            'failed_requests': self.service_metrics.failed_requests,
            'success_rate': self.service_metrics.success_rate,
            'average_response_time': self.service_metrics.average_response_time,
            'min_response_time': self.service_metrics.min_response_time if self.service_metrics.min_response_time != float('inf') else 0,
            'max_response_time': self.service_metrics.max_response_time,
            'error_counts': self.service_metrics.error_counts,
            'last_request_time': self.service_metrics.last_request_time.isoformat() if self.service_metrics.last_request_time else None,
            'http_client_metrics': self.http_client.get_metrics()
        }
    
    async def close(self):
        """Close the HTTP client"""
        await self.http_client.close()

class RequestBatcher:
    """Batch multiple requests for efficiency"""
    
    def __init__(self, max_batch_size: int = 10, max_wait_time: float = 0.1):
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time
        self.pending_requests: deque = deque()
        self.processing = False
        self._batch_task: Optional[asyncio.Task] = None
    
    async def add_request(self, request_func: Callable, *args, **kwargs) -> asyncio.Future:
        """Add a request to the batch"""
        future = asyncio.Future()
        self.pending_requests.append((future, request_func, args, kwargs))
        
        if not self.processing:
            self._batch_task = asyncio.create_task(self._process_batch())
        
        return future
    
    async def _process_batch(self):
        """Process batched requests"""
        self.processing = True
        
        while self.pending_requests:
            batch = []
            
            # Collect requests for current batch
            while self.pending_requests and len(batch) < self.max_batch_size:
                batch.append(self.pending_requests.popleft())
            
            if batch:
                # Process batch in parallel
                tasks = []
                for future, request_func, args, kwargs in batch:
                    task = asyncio.create_task(self._execute_request(future, request_func, args, kwargs))
                    tasks.append(task)
                
                # Wait for all requests in batch to complete
                await asyncio.gather(*tasks, return_exceptions=True)
            
            # Small delay before next batch
            if self.pending_requests:
                await asyncio.sleep(self.max_wait_time)
        
        self.processing = False
    
    async def _execute_request(self, future: asyncio.Future, request_func: Callable, args, kwargs):
        """Execute a single request"""
        try:
            result = await request_func(*args, **kwargs)
            if not future.done():
                future.set_result(result)
        except Exception as e:
            if not future.done():
                future.set_exception(e)

# Utility functions for common service clients
def create_service_client(service_name: str, base_url: str, timeout: int = 30,
                         cache_config: CacheConfig = None) -> ServiceClient:
    """Factory function to create service clients"""
    return ServiceClient(base_url=base_url, service_name=service_name, timeout=timeout, cache_config=cache_config)

async def propagate_request_id(headers: Dict[str, str], request_id: str = None) -> Dict[str, str]:
    """Ensure request ID is propagated in headers"""
    if not headers:
        headers = {}
    
    if request_id and 'X-Request-ID' not in headers:
        headers['X-Request-ID'] = request_id
    
    return headers

# Service client factory
_service_clients: Dict[str, ServiceClient] = {}

def get_service_client(service_name: str, base_url: str) -> ServiceClient:
    """Get or create service client."""
    if service_name not in _service_clients:
        _service_clients[service_name] = ServiceClient(base_url=base_url, service_name=service_name)
    return _service_clients[service_name]

async def close_all_service_clients():
    """Close all service clients."""
    for client in _service_clients.values():
        await client.close()
    _service_clients.clear()

# Utility functions for common HTTP operations
async def parallel_requests(requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Execute multiple HTTP requests in parallel."""
    
    async def make_request(req_config):
        client = HTTPClient()
        try:
            response = await client.request(**req_config)
            return response.json()
        finally:
            await client.close()
    
    tasks = [make_request(req) for req in requests]
    return await asyncio.gather(*tasks, return_exceptions=True)

def with_retry(max_retries: int = 3, delay: float = 1.0):
    """Decorator to add retry logic to functions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {e}, retrying...")
                    await asyncio.sleep(delay * (2 ** attempt))
        return wrapper
    return decorator

# Health monitoring utilities
class HealthMonitor:
    """Monitor health of HTTP clients and services"""
    
    def __init__(self):
        self.monitors: Dict[str, Callable] = {}
        self.health_status: Dict[str, Dict[str, Any]] = {}
    
    def add_monitor(self, name: str, check_func: Callable[[], Awaitable[bool]]):
        """Add a health check monitor"""
        self.monitors[name] = check_func
    
    async def check_health(self) -> Dict[str, Dict[str, Any]]:
        """Run all health checks"""
        results = {}
        
        for name, check_func in self.monitors.items():
            try:
                start_time = time.time()
                is_healthy = await check_func()
                check_time = time.time() - start_time
                
                results[name] = {
                    'healthy': is_healthy,
                    'check_time': check_time,
                    'last_check': datetime.now().isoformat()
                }
            except Exception as e:
                results[name] = {
                    'healthy': False,
                    'error': str(e),
                    'last_check': datetime.now().isoformat()
                }
        
        self.health_status = results
        return results
    
    def get_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Get last health check results"""
        return self.health_status

# Global health monitor instance
health_monitor = HealthMonitor()

# Monitoring utilities
def get_all_metrics() -> Dict[str, Any]:
    """Get metrics from all service clients"""
    metrics = {
        'service_clients': {},
        'global_health': health_monitor.get_health_status()
    }
    
    for service_name, client in _service_clients.items():
        metrics['service_clients'][service_name] = client.get_service_metrics()
    
    return metrics

async def health_check_all_services() -> Dict[str, Any]:
    """Perform health checks on all services"""
    return await health_monitor.check_health() 