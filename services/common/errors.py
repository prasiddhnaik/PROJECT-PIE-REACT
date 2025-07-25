"""
Unified Error Taxonomy for Financial Analytics Hub
Provides consistent HTTP status code mapping across all microservices.
"""

from typing import Optional, Dict, Any
import json


class ServiceError(Exception):
    """
    Base exception class for all service errors.
    Preserves HTTP status codes and provides context for debugging.
    """
    
    def __init__(
        self,
        message: str,
        http_status: int = 500,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        service_name: Optional[str] = None
    ):
        super().__init__(message)
        self.http_status = http_status
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.request_id = request_id
        self.service_name = service_name
        
    def to_dict(self) -> Dict[str, Any]:
        """Serialize error for API responses."""
        return {
            "error": self.error_code,
            "message": str(self),
            "status_code": self.http_status,
            "context": self.context,
            "request_id": self.request_id,
            "service": self.service_name
        }
    
    def to_json(self) -> str:
        """Serialize error to JSON string."""
        return json.dumps(self.to_dict())


# Client Error Classes (4xx)

class InvalidInputError(ServiceError):
    """400 Bad Request - Malformed requests and invalid parameters."""
    
    def __init__(self, message: str = "Invalid input provided", **kwargs):
        super().__init__(message, http_status=400, **kwargs)


class UnauthorizedError(ServiceError):
    """401 Unauthorized - Authentication failures."""
    
    def __init__(self, message: str = "Authentication required", **kwargs):
        super().__init__(message, http_status=401, **kwargs)


class ForbiddenError(ServiceError):
    """403 Forbidden - Authorization failures."""
    
    def __init__(self, message: str = "Access forbidden", **kwargs):
        super().__init__(message, http_status=403, **kwargs)


class NotFoundError(ServiceError):
    """404 Not Found - Missing resources or data."""
    
    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, http_status=404, **kwargs)


class ValidationError(ServiceError):
    """422 Unprocessable Entity - Data validation failures."""
    
    def __init__(self, message: str = "Validation failed", **kwargs):
        super().__init__(message, http_status=422, **kwargs)


class RateLimitError(ServiceError):
    """429 Too Many Requests - Rate limiting scenarios."""
    
    def __init__(
        self, 
        message: str = "Rate limit exceeded", 
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, http_status=429, **kwargs)
        if retry_after:
            self.context["retry_after"] = retry_after


# Gateway Error Classes (5xx)

class BadGatewayError(ServiceError):
    """502 Bad Gateway - Upstream service errors."""
    
    def __init__(self, message: str = "Bad gateway", **kwargs):
        super().__init__(message, http_status=502, **kwargs)


class ServiceUnavailableError(ServiceError):
    """503 Service Unavailable - Service unavailability and circuit breaker scenarios."""
    
    def __init__(
        self, 
        message: str = "Service temporarily unavailable", 
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, http_status=503, **kwargs)
        if retry_after:
            self.context["retry_after"] = retry_after


class GatewayTimeoutError(ServiceError):
    """504 Gateway Timeout - Timeout errors."""
    
    def __init__(self, message: str = "Gateway timeout", **kwargs):
        super().__init__(message, http_status=504, **kwargs)


# External API Error Classes

class ExternalAPIError(ServiceError):
    """External API errors with status code preservation."""
    
    def __init__(
        self, 
        message: str, 
        original_status: Optional[int] = None,
        api_provider: Optional[str] = None,
        **kwargs
    ):
        # Map external API status codes appropriately
        if original_status:
            if 400 <= original_status < 500:
                http_status = original_status
            else:
                http_status = 502  # Map 5xx to Bad Gateway
        else:
            http_status = 502
            
        super().__init__(message, http_status=http_status, **kwargs)
        self.context["original_status"] = original_status
        self.context["api_provider"] = api_provider


class ExternalAPITimeoutError(ServiceError):
    """504 Gateway Timeout - External API timeouts."""
    
    def __init__(
        self, 
        message: str = "External API timeout", 
        api_provider: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, http_status=504, **kwargs)
        self.context["api_provider"] = api_provider


class ExternalAPIRateLimitError(ServiceError):
    """429 Too Many Requests - External API rate limits."""
    
    def __init__(
        self, 
        message: str = "External API rate limit exceeded", 
        api_provider: Optional[str] = None,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, http_status=429, **kwargs)
        self.context["api_provider"] = api_provider
        if retry_after:
            self.context["retry_after"] = retry_after


# Computation Error Classes

class InsufficientDataError(ServiceError):
    """422 Unprocessable Entity - Insufficient data for calculations."""
    
    def __init__(
        self, 
        message: str = "Insufficient data for calculation", 
        min_required: Optional[int] = None,
        actual_count: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, http_status=422, **kwargs)
        if min_required is not None:
            self.context["min_required"] = min_required
        if actual_count is not None:
            self.context["actual_count"] = actual_count


class InvalidDataError(ServiceError):
    """422 Unprocessable Entity - Invalid data format or content."""
    
    def __init__(
        self, 
        message: str = "Invalid data format", 
        expected_format: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, http_status=422, **kwargs)
        if expected_format:
            self.context["expected_format"] = expected_format


class ComputationError(ServiceError):
    """422 Unprocessable Entity - Mathematical and processing errors."""
    
    def __init__(
        self, 
        message: str = "Computation failed", 
        computation_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, http_status=422, **kwargs)
        if computation_type:
            self.context["computation_type"] = computation_type


# Utility Functions

def preserve_status_code(exception: Exception, default_status: int = 500) -> int:
    """Extract HTTP status code from exception, with fallback."""
    if isinstance(exception, ServiceError):
        return exception.http_status
    elif hasattr(exception, 'response') and hasattr(exception.response, 'status_code'):
        return exception.response.status_code
    else:
        return default_status


def create_error_context(
    request_id: Optional[str] = None,
    service_name: Optional[str] = None,
    endpoint: Optional[str] = None,
    **additional_context
) -> Dict[str, Any]:
    """Create standardized error context dictionary."""
    context = {
        "request_id": request_id,
        "service": service_name,
        "endpoint": endpoint,
        **additional_context
    }
    # Remove None values
    return {k: v for k, v in context.items() if v is not None}


def wrap_external_api_error(
    exception: Exception,
    api_provider: str,
    context: Optional[Dict[str, Any]] = None
) -> ServiceError:
    """Wrap external API exceptions with proper error taxonomy."""
    context = context or {}
    
    if hasattr(exception, 'response'):
        status_code = getattr(exception.response, 'status_code', None)
        response_text = getattr(exception.response, 'text', str(exception))
        
        if status_code == 401:
            return UnauthorizedError(
                f"{api_provider} API authentication failed: {response_text}",
                context={**context, "api_provider": api_provider}
            )
        elif status_code == 403:
            return ForbiddenError(
                f"{api_provider} API access forbidden: {response_text}",
                context={**context, "api_provider": api_provider}
            )
        elif status_code == 429:
            retry_after = None
            if hasattr(exception.response, 'headers'):
                retry_after = exception.response.headers.get('Retry-After')
                if retry_after:
                    try:
                        retry_after = int(retry_after)
                    except ValueError:
                        retry_after = None
            
            return ExternalAPIRateLimitError(
                f"{api_provider} API rate limit exceeded: {response_text}",
                api_provider=api_provider,
                retry_after=retry_after,
                context=context
            )
        elif 400 <= status_code < 500:
            return ExternalAPIError(
                f"{api_provider} API client error: {response_text}",
                original_status=status_code,
                api_provider=api_provider,
                context=context
            )
        elif 500 <= status_code < 600:
            return ExternalAPIError(
                f"{api_provider} API server error: {response_text}",
                original_status=status_code,
                api_provider=api_provider,
                context=context
            )
    
    # Handle connection/timeout errors
    if "timeout" in str(exception).lower():
        return ExternalAPITimeoutError(
            f"{api_provider} API timeout: {str(exception)}",
            api_provider=api_provider,
            context=context
        )
    elif "connection" in str(exception).lower():
        return ServiceUnavailableError(
            f"{api_provider} API connection failed: {str(exception)}",
            context={**context, "api_provider": api_provider}
        )
    
    # Generic external API error
    return ExternalAPIError(
        f"{api_provider} API error: {str(exception)}",
        api_provider=api_provider,
        context=context
    ) 