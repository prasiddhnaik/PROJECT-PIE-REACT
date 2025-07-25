"""
Shared HTTP client utilities for microservices.
"""

import httpx
import asyncio
import time
import random
from typing import Dict, Any, Optional, Union, List
from functools import wraps
import logging
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime, timedelta
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

class CircuitBreakerError(Exception):
    """Custom exception for circuit breaker open state"""
    pass



class GatewayError(Exception):
    """Custom exception for gateway errors"""
    pass

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
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(timeout=timeout)
        self.logger = logging.getLogger(__name__)
    
    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make HTTP request with enhanced retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.request(method, url, **kwargs)
                
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
    
    async def close(self):
        await self.client.aclose()

class ServiceClient:
    """Enhanced service client with better error handling and status preservation"""
    
    def __init__(self, base_url: str, service_name: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.service_name = service_name
        self.http_client = HTTPClient(timeout=timeout)
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )
        self.logger = logging.getLogger(f"service_client.{service_name}")
        self.performance_logger = PerformanceLogger(self.logger)
    
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
                
                # Map status codes to appropriate exceptions with proper status preservation
                if 400 <= response.status_code < 500:
                    # Client errors - preserve original status code by re-raising HTTPStatusError
                    raise httpx.HTTPStatusError(error_msg, request=response.request, response=response)
                else:
                    # Server errors - preserve original status code instead of converting to generic error
                    raise httpx.HTTPStatusError(error_msg, request=response.request, response=response)
            
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
    
    async def close(self):
        """Close the HTTP client"""
        await self.http_client.close()

# Utility functions for common service clients
def create_service_client(service_name: str, base_url: str, timeout: int = 30) -> ServiceClient:
    """Factory function to create service clients"""
    return ServiceClient(base_url=base_url, service_name=service_name, timeout=timeout)

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