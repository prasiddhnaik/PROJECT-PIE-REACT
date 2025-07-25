"""
Enhanced OpenRouter AI client with streaming and memory management.
"""

import httpx
import asyncio
import json
import logging
import time
import random
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
import sys
import os

# Add parent directory to path for common imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.errors import (
    ServiceError, 
    UnauthorizedError, 
    ForbiddenError, 
    ValidationError, 
    RateLimitError,
    BadGatewayError, 
    ServiceUnavailableError, 
    GatewayTimeoutError,
    ExternalAPIError,
    ExternalAPITimeoutError,
    ExternalAPIRateLimitError
)

logger = logging.getLogger(__name__)

class OpenRouterClient:
    """Enhanced OpenRouter API client."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://openrouter.ai/api/v1",
        default_model: str = "anthropic/claude-3-sonnet",
        max_tokens: int = 4000,
        temperature: float = 0.7
    ):
        if not api_key or not api_key.strip():
            raise ValidationError("OpenRouter API key is required")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.default_model = default_model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # HTTP client with connection pooling
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=50),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://financial-analytics-hub.com",
                "X-Title": "Financial Analytics Hub"
            }
        )
        
        # Request stats
        self.request_count = 0
        self.total_tokens = 0
        self.error_count = 0
        
        # Rate limiting and retry configuration
        self.max_retries = 3
        self.base_delay = 1.0
        self.max_delay = 60.0
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with retry logic and proper error handling"""
        url = f"{self.base_url}{endpoint}"
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Add request ID for tracing
                if "headers" not in kwargs:
                    kwargs["headers"] = {}
                kwargs["headers"]["X-Request-ID"] = str(int(time.time() * 1000))
                
                logger.debug(f"Making {method} request to {endpoint} (attempt {attempt + 1})")
                
                response = await self.client.request(method, url, **kwargs)
                
                # Handle successful responses
                if response.status_code < 400:
                    return self._parse_response(response)
                
                # Handle client and server errors
                await self._handle_error_response(response)
                
            except httpx.TimeoutException as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = min(self.base_delay * (2 ** attempt) + random.uniform(0, 1), self.max_delay)
                    logger.warning(f"Request timeout, retrying in {delay:.2f}s (attempt {attempt + 1})")
                    await asyncio.sleep(delay)
                    continue
                break
                
            except httpx.ConnectError as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = min(self.base_delay * (2 ** attempt) + random.uniform(0, 1), self.max_delay)
                    logger.warning(f"Connection error, retrying in {delay:.2f}s (attempt {attempt + 1})")
                    await asyncio.sleep(delay)
                    continue
                break
                
            except ExternalAPIRateLimitError as e:
                # Handle rate limiting with exponential backoff
                if attempt < self.max_retries:
                    retry_after = getattr(e, 'retry_after', None) or (2 ** attempt)
                    delay = min(retry_after + random.uniform(0, 1), self.max_delay)
                    logger.warning(f"Rate limited, retrying in {delay:.2f}s (attempt {attempt + 1})")
                    await asyncio.sleep(delay)
                    continue
                raise e
                
            except (UnauthorizedError, ForbiddenError, ValidationError):
                # Don't retry auth and validation errors
                raise
                
            except (BadGatewayError, ServiceUnavailableError) as e:
                # Retry service errors
                if attempt < self.max_retries:
                    delay = min(self.base_delay * (2 ** attempt) + random.uniform(0, 1), self.max_delay)
                    logger.warning(f"Service error, retrying in {delay:.2f}s (attempt {attempt + 1})")
                    await asyncio.sleep(delay)
                    continue
                raise e
        
        # If we get here, all retries failed
        if last_exception:
            if isinstance(last_exception, httpx.TimeoutException):
                raise ExternalAPITimeoutError(
                    message="OpenRouter API timeout after all retries",
                    service_name="openrouter-api",
                    api_provider="OpenRouter"
                )
            elif isinstance(last_exception, httpx.ConnectError):
                raise ServiceUnavailableError(
                    message="OpenRouter API connection failed after all retries",
                    service_name="ai-service",
                    details={"api_provider": "OpenRouter"}
                )
            else:
                raise ExternalAPIError(
                    message=f"OpenRouter API request failed after all retries: {str(last_exception)}",
                    status_code=502,
                    service_name="openrouter-api",
                    api_provider="OpenRouter"
                )
        
        raise ServiceError("Unknown error occurred in OpenRouter API client")
    
    def _parse_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Parse and validate response JSON"""
        try:
            data = response.json()
            
            # Log successful request
            logger.debug(f"Successful response: {response.status_code}")
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {response.text[:200]}")
            raise ExternalAPIError(
                message="Invalid JSON response from OpenRouter API",
                status_code=502,
                service_name="openrouter-api",
                api_provider="OpenRouter",
                details={"response_preview": response.text[:200]}
            )
    
    async def _handle_error_response(self, response: httpx.Response):
        """Handle error responses with proper status code mapping"""
        status_code = response.status_code
        
        try:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", response.text[:200])
        except:
            error_message = response.text[:200] if response.text else f"HTTP {status_code} error"
        
        logger.error(f"OpenRouter API error {status_code}: {error_message}")
        
        # Map status codes to appropriate exceptions with context
        if status_code == 401:
            raise UnauthorizedError(
                message=f"OpenRouter authentication failed: {error_message}",
                service_name="ai-service",
                details={"api_provider": "OpenRouter"}
            )
        elif status_code == 403:
            raise ForbiddenError(
                message=f"OpenRouter access forbidden: {error_message}",
                service_name="ai-service",
                details={"api_provider": "OpenRouter"}
            )
        elif status_code == 400:
            raise ValidationError(
                message=f"OpenRouter invalid request: {error_message}",
                service_name="ai-service",
                details={"api_provider": "OpenRouter"}
            )
        elif status_code == 422:
            raise ValidationError(
                message=f"OpenRouter validation failed: {error_message}",
                service_name="ai-service",
                details={"api_provider": "OpenRouter"}
            )
        elif status_code == 429:
            retry_after = None
            try:
                retry_after = int(response.headers.get('Retry-After', 60))
            except:
                pass
            raise ExternalAPIRateLimitError(
                message=f"OpenRouter rate limit exceeded: {error_message}",
                service_name="openrouter-api",
                api_provider="OpenRouter",
                retry_after=retry_after
            )
        elif status_code >= 500:
            raise ExternalAPIError(
                message=f"OpenRouter service error: {error_message}",
                status_code=status_code,
                service_name="openrouter-api",
                api_provider="OpenRouter"
            )
        else:
            raise ExternalAPIError(
                message=f"OpenRouter error ({status_code}): {error_message}",
                status_code=status_code,
                service_name="openrouter-api",
                api_provider="OpenRouter"
            )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Get chat completion from OpenRouter."""
        
        # Input validation
        if not messages or not isinstance(messages, list):
            raise ValidationError(
                message="Messages must be a non-empty list",
                service_name="ai-service",
                details={"parameter": "messages"}
            )
        
        if max_tokens is not None and (max_tokens <= 0 or max_tokens > 32000):
            raise ValidationError(
                message="max_tokens must be between 1 and 32000",
                service_name="ai-service",
                details={"parameter": "max_tokens", "value": max_tokens}
            )
        
        if temperature is not None and (temperature < 0 or temperature > 2):
            raise ValidationError(
                message="temperature must be between 0 and 2",
                service_name="ai-service",
                details={"parameter": "temperature", "value": temperature}
            )
        
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature if temperature is not None else self.temperature,
            "stream": stream
        }
        
        try:
            self.request_count += 1
            start_time = time.time()
            
            response = await self._make_request("POST", "/chat/completions", json=payload)
            
            duration = time.time() - start_time
            
            # Track token usage
            usage = response.get("usage", {})
            if usage:
                self.total_tokens += usage.get("total_tokens", 0)
            
            logger.info(f"Chat completion successful ({duration:.2f}s, {usage.get('total_tokens', 0)} tokens)")
            return response
            
        except (ServiceError, ValidationError, UnauthorizedError, ForbiddenError, 
                RateLimitError, ExternalAPIError, ExternalAPITimeoutError, 
                ExternalAPIRateLimitError):
            self.error_count += 1
            raise
        except Exception as e:
            self.error_count += 1
            logger.error(f"Unexpected error in chat completion: {e}")
            raise ServiceError(
                message=f"Unexpected error in OpenRouter chat completion: {str(e)}",
                service_name="ai-service",
                details={"operation": "chat_completion"}
            )
    
    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream chat completion from OpenRouter."""
        
        # Input validation
        if not messages or not isinstance(messages, list):
            raise ValidationError(
                message="Messages must be a non-empty list",
                service_name="ai-service",
                details={"parameter": "messages"}
            )
        
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature if temperature is not None else self.temperature,
            "stream": True
        }
        
        try:
            self.request_count += 1
            start_time = time.time()
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload
            ) as response:
                if response.status_code >= 400:
                    await self._handle_error_response(response)
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        
                        if data.strip() == "[DONE]":
                            break
                        
                        try:
                            chunk = json.loads(data)
                            yield chunk
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            logger.warning(f"Error processing stream chunk: {e}")
                            continue
            
            duration = time.time() - start_time
            logger.info(f"Streaming completion successful ({duration:.2f}s)")
            
        except (ServiceError, ValidationError, UnauthorizedError, ForbiddenError, 
                RateLimitError, ExternalAPIError, ExternalAPITimeoutError, 
                ExternalAPIRateLimitError):
            self.error_count += 1
            raise
        except Exception as e:
            self.error_count += 1
            logger.error(f"Unexpected error in streaming: {e}")
            raise ServiceError(
                message=f"Unexpected error in OpenRouter streaming: {str(e)}",
                service_name="ai-service",
                details={"operation": "chat_completion_stream"}
            )
    
    async def get_models(self) -> List[Dict[str, Any]]:
        """Get available models from OpenRouter."""
        try:
            response = await self._make_request("GET", "/models")
            
            if "data" not in response:
                logger.warning("Models response missing 'data' field")
                return []
            
            models = response["data"]
            if not isinstance(models, list):
                logger.warning("Models data is not a list")
                return []
            
            logger.info(f"Retrieved {len(models)} available models")
            
            # Filter and format models
            formatted_models = []
            for model in models:
                try:
                    formatted_models.append({
                        "id": model.get("id"),
                        "name": model.get("name", model.get("id")),
                        "description": model.get("description", ""),
                        "pricing": model.get("pricing", {}),
                        "context_length": model.get("context_length", 4096)
                    })
                except Exception as e:
                    logger.warning(f"Error formatting model data: {e}")
                    continue
            
            return formatted_models
            
        except (ServiceError, ValidationError, UnauthorizedError, ForbiddenError, 
                RateLimitError, ExternalAPIError, ExternalAPITimeoutError, 
                ExternalAPIRateLimitError):
            logger.error("Failed to get models due to API error, returning empty list")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting models: {str(e)}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if OpenRouter API is healthy."""
        try:
            # Test with a minimal request
            test_messages = [{"role": "user", "content": "Hello"}]
            
            start_time = time.time()
            response = await self.chat_completion(
                messages=test_messages,
                model="meta-llama/llama-3.1-8b-instruct:free",
                max_tokens=10
            )
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": round(response_time, 3),
                "model_tested": response.get("model"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except UnauthorizedError:
            return {
                "status": "auth_error",
                "error": "Authentication failed",
                "timestamp": datetime.utcnow().isoformat()
            }
        except (RateLimitError, ExternalAPIRateLimitError):
            return {
                "status": "rate_limited",
                "error": "Rate limit exceeded",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics."""
        return {
            "request_count": self.request_count,
            "total_tokens": self.total_tokens,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(self.request_count, 1),
            "default_model": self.default_model
        }

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
        logger.debug("OpenRouter client closed") 