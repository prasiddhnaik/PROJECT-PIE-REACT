"""
Shared logging utilities for microservices.
"""

import logging
import logging.config
import json
import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from contextvars import ContextVar
import sys
import os
from functools import wraps
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Context variables for request tracking
request_id_ctx: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_ctx: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
service_name_ctx: ContextVar[Optional[str]] = ContextVar('service_name', default=None)

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add request context if available
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'service_name'):
            log_entry['service_name'] = record.service_name
        if hasattr(record, 'http_method'):
            log_entry['http_method'] = record.http_method
        if hasattr(record, 'http_path'):
            log_entry['http_path'] = record.http_path
        if hasattr(record, 'user_agent'):
            log_entry['user_agent'] = record.user_agent
        if hasattr(record, 'client_ip'):
            log_entry['client_ip'] = record.client_ip
        if hasattr(record, 'downstream_service'):
            log_entry['downstream_service'] = record.downstream_service
        if hasattr(record, 'error_category'):
            log_entry['error_category'] = record.error_category
        if hasattr(record, 'error_severity'):
            log_entry['error_severity'] = record.error_severity
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add any extra fields
        if hasattr(record, 'extra'):
            log_entry.update(record.extra)
        
        # Add performance metrics if present
        if hasattr(record, 'duration'):
            log_entry["duration_ms"] = record.duration
        
        if hasattr(record, 'status_code'):
            log_entry["status_code"] = record.status_code
        
        return json.dumps(log_entry)

class PerformanceLogger:
    """Logger for performance metrics and error tracking."""
    
    def __init__(self, logger_name: str = "performance"):
        self.logger = logging.getLogger(logger_name)
        self.error_counts = {}
        self.response_times = {}
    
    def log_request(self, method: str, path: str, status_code: int, duration: float, **kwargs):
        """Log HTTP request performance."""
        extra = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2),
            **kwargs
        }
        
        self.logger.info(
            f"{method} {path} - {status_code} ({duration:.3f}s)",
            extra={"extra": extra}
        )
    
    def log_operation(self, operation: str, duration: float, success: bool = True, **kwargs):
        """Log operation performance."""
        extra = {
            "operation": operation,
            "duration_ms": round(duration * 1000, 2),
            "success": success,
            **kwargs
        }
        
        level = logging.INFO if success else logging.WARNING
        self.logger.log(
            level,
            f"Operation {operation} completed in {duration:.3f}s (success: {success})",
            extra={"extra": extra}
        )

    def log_error(self, error_type: str, service_name: str, endpoint: str, 
                  error_message: str, request_id: str = None, 
                  downstream_service: str = None):
        """Log categorized errors with detailed context"""
        
        error_key = f"{service_name}:{endpoint}:{error_type}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        extra = {
            'error_category': error_type,
            'service_name': service_name,
            'endpoint': endpoint,
            'error_count': self.error_counts[error_key]
        }
        
        if request_id:
            extra['request_id'] = request_id
        if downstream_service:
            extra['downstream_service'] = downstream_service
            
        # Categorize error severity
        if error_type in ['network_error', 'timeout', 'external_api_error']:
            extra['error_severity'] = 'medium'
        elif error_type in ['computation_error', 'data_validation_error']:
            extra['error_severity'] = 'low'
        else:
            extra['error_severity'] = 'high'
        
        self.logger.error(f"Categorized error: {error_message}", extra=extra)
    
    def log_performance(self, service_name: str, endpoint: str, 
                       response_time: float, status_code: int, 
                       request_id: str = None):
        """Log performance metrics"""
        
        perf_key = f"{service_name}:{endpoint}"
        if perf_key not in self.response_times:
            self.response_times[perf_key] = []
        
        self.response_times[perf_key].append(response_time)
        
        # Calculate percentiles for last 100 requests
        recent_times = self.response_times[perf_key][-100:]
        recent_times.sort()
        
        p50 = recent_times[len(recent_times) // 2] if recent_times else 0
        p95 = recent_times[int(len(recent_times) * 0.95)] if recent_times else 0
        
        extra = {
            'service_name': service_name,
            'endpoint': endpoint,
            'response_time': response_time,
            'status_code': status_code,
            'p50_response_time': p50,
            'p95_response_time': p95
        }
        
        if request_id:
            extra['request_id'] = request_id
        
        self.logger.info(f"Performance metrics: {endpoint}", extra=extra)

def setup_logging(
    service_name: str,
    log_level: str = "INFO",
    log_format: str = "json",
    enable_performance_logging: bool = True
):
    """Setup logging configuration for a service."""
    
    # Set service context
    service_name_ctx.set(service_name)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    if log_format.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    loggers_config = {
        "uvicorn": {"level": "INFO"},
        "uvicorn.access": {"level": "INFO"},
        "fastapi": {"level": "INFO"},
        "httpx": {"level": "WARNING"},
        "redis": {"level": "WARNING"},
    }
    
    for logger_name, config in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, config["level"]))
    
    # Setup performance logger if enabled
    if enable_performance_logging:
        perf_logger = logging.getLogger("performance")
        perf_logger.setLevel(logging.INFO)
    
    logging.info(f"Logging configured for {service_name} (level: {log_level}, format: {log_format})")

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)

def set_request_context(request_id: str = None, user_id: str = None):
    """Set request context for logging."""
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    request_id_ctx.set(request_id)
    if user_id:
        user_id_ctx.set(user_id)
    
    return request_id

def clear_request_context():
    """Clear request context."""
    request_id_ctx.set(None)
    user_id_ctx.set(None)

def log_performance(operation_name: str = None):
    """Decorator to log function performance."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            logger = get_logger("performance")
            
            try:
                if hasattr(func, '__call__') and hasattr(func.__call__, '__code__'):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                logger.info(
                    f"Operation {operation} completed successfully",
                    extra={
                        "extra": {
                            "operation": operation,
                            "duration_ms": round(duration * 1000, 2),
                            "success": True
                        }
                    }
                )
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Operation {operation} failed: {str(e)}",
                    extra={
                        "extra": {
                            "operation": operation,
                            "duration_ms": round(duration * 1000, 2),
                            "success": False,
                            "error": str(e)
                        }
                    },
                    exc_info=True
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            logger = get_logger("performance")
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(
                    f"Operation {operation} completed successfully",
                    extra={
                        "extra": {
                            "operation": operation,
                            "duration_ms": round(duration * 1000, 2),
                            "success": True
                        }
                    }
                )
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Operation {operation} failed: {str(e)}",
                    extra={
                        "extra": {
                            "operation": operation,
                            "duration_ms": round(duration * 1000, 2),
                            "success": False,
                            "error": str(e)
                        }
                    },
                    exc_info=True
                )
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Global performance logger instance
performance_logger = PerformanceLogger()

# Middleware for request logging
async def log_request_middleware(request, call_next):
    """Middleware to log HTTP requests."""
    start_time = time.time()
    request_id = set_request_context()
    
    # Add request ID to request state
    request.state.request_id = request_id
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    performance_logger.log_request(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration=duration,
        query_params=str(request.query_params) if request.query_params else None,
        user_agent=request.headers.get("user-agent"),
        request_id=request_id
    )
    
    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id
    
    clear_request_context()
    return response

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to all requests"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate or extract request ID
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        
        # Store in request state
        request.state.request_id = request_id
        
        # Call next middleware/endpoint
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers['X-Request-ID'] = request_id
        
        return response

def log_structured_error(logger: logging.Logger, message: str, 
                        error_category: str, request_id: str = None,
                        service_name: str = None, endpoint: str = None,
                        downstream_service: str = None, exc_info: bool = False):
    """Log structured error with consistent format"""
    extra = create_error_context(
        request_id=request_id,
        service_name=service_name,
        endpoint=endpoint,
        error_category=error_category,
        downstream_service=downstream_service
    )
    
    logger.error(message, extra=extra, exc_info=exc_info)

def create_error_context(request_id: str = None, service_name: str = None, 
                        endpoint: str = None, error_category: str = None,
                        downstream_service: str = None) -> Dict[str, Any]:
    """Create structured error context for logging"""
    context = {}
    
    if request_id:
        context['request_id'] = request_id
    if service_name:
        context['service_name'] = service_name
    if endpoint:
        context['endpoint'] = endpoint
    if error_category:
        context['error_category'] = error_category
    if downstream_service:
        context['downstream_service'] = downstream_service
    
    return context

def setup_service_error_handler(app, service_name: str):
    """Setup ServiceError exception handler for consistent status code preservation"""
    from fastapi import Request
    from fastapi.responses import JSONResponse
    from datetime import datetime
    
    # Import ServiceError here to avoid circular imports
    try:
        from .errors import ServiceError
    except ImportError:
        # If errors module not available, create a minimal version
        class ServiceError(Exception):
            def __init__(self, message: str, http_status: int = 500, service_name: str = None, context: dict = None, request_id: str = None):
                super().__init__(message)
                self.http_status = http_status
                self.service_name = service_name
                self.context = context or {}
                self.request_id = request_id
    
    @app.exception_handler(ServiceError)
    async def service_error_exception_handler(request: Request, exc: ServiceError):
        """Handle ServiceError exceptions to preserve status codes"""
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # Log the error with structured context
        log_structured_error(
            logger=get_logger(service_name),
            message=f"ServiceError in {service_name}: {str(exc)}",
            error_category="service_error",
            request_id=request_id,
            service_name=service_name,
            endpoint=str(request.url.path),
            exc_info=False
        )
        
        return JSONResponse(
            status_code=exc.http_status,
            content={
                "error": exc.__class__.__name__,
                "message": str(exc),
                "service": exc.service_name or service_name,
                "details": exc.context,
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        ) 