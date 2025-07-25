"""
API Gateway routing logic.
"""

import asyncio
import httpx
import json
import logging
from typing import Dict, Any, Optional, List
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from urllib.parse import urljoin
import time
import sys
import os

# Add parent directory to path for common imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.http_client import ServiceClient, create_service_client, propagate_request_id
from common.logging import log_structured_error, PerformanceLogger
from common.config import get_config
from common.errors import (
    ServiceError,
    ValidationError,
    InvalidInputError,
    BadGatewayError,
    ServiceUnavailableError,
    GatewayTimeoutError,
    ExternalAPIError
)

logger = logging.getLogger(__name__)

class APIRouter:
    """Enhanced API Router with better error handling and status code preservation"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger("api-gateway.router")
        self.performance_logger = PerformanceLogger(self.logger)
        
        # Service clients with circuit breakers
        self.service_clients: Dict[str, ServiceClient] = {}
        self._initialize_service_clients()
    
    def _initialize_service_clients(self):
        """Initialize service clients with proper configuration"""
        service_configs = {
            "data-service": {"url": "http://data-service:8002", "timeout": 30},
            "chart-service": {"url": "http://chart-service:8003", "timeout": 45},
            "graph-service": {"url": "http://graph-service:8004", "timeout": 60},
            "ai-service": {"url": "http://ai-service:8005", "timeout": 120}
        }
        
        for service_name, config in service_configs.items():
            try:
                self.service_clients[service_name] = create_service_client(
                    service_name=service_name,
                    base_url=config["url"],
                    timeout=config["timeout"]
                )
                self.logger.info(f"Initialized service client for {service_name}")
            except Exception as e:
                self.logger.error(f"Failed to initialize service client for {service_name}: {str(e)}")
    
    def _get_service_for_path(self, path: str) -> Optional[str]:
        """Determine which service should handle the request based on path"""
        path = path.strip('/')
        
        # Service routing logic
        if path.startswith('data/') or path.startswith('api/data/'):
            return "data-service"
        elif path.startswith('charts/') or path.startswith('api/charts/'):
            return "chart-service"
        elif path.startswith('graphs/') or path.startswith('api/graphs/'):
            return "graph-service"
        elif path.startswith('ai/') or path.startswith('api/ai/'):
            return "ai-service"
        
        # Default routing for common endpoints
        if any(keyword in path for keyword in ['crypto', 'market', 'stock', 'forex']):
            return "data-service"
        elif any(keyword in path for keyword in ['chart', 'technical', 'indicators']):
            return "chart-service"
        elif any(keyword in path for keyword in ['correlation', 'portfolio', 'heatmap']):
            return "graph-service"
        elif any(keyword in path for keyword in ['chat', 'predict', 'insights']):
            return "ai-service"
        
        return None
    
    def _clean_path_for_service(self, path: str, service_name: str) -> str:
        """Clean the path for forwarding to the service"""
        path = path.strip('/')
        
        # Remove api prefix if present
        if path.startswith('api/'):
            path = path[4:]
        
        # Remove service-specific prefixes
        service_prefixes = {
            "data-service": ["data/"],
            "chart-service": ["charts/"],
            "graph-service": ["graphs/"],
            "ai-service": ["ai/"]
        }
        
        if service_name in service_prefixes:
            for prefix in service_prefixes[service_name]:
                if path.startswith(prefix):
                    path = path[len(prefix):]
                    break
        
        return f"/{path}" if path else "/"
    
    async def route_request(self, method: str, path: str, headers: Dict[str, str] = None,
                           query_params: Dict[str, Any] = None, body: Any = None) -> Dict[str, Any]:
        """Route request to appropriate service with enhanced error handling"""
        start_time = time.time()
        request_id = headers.get('X-Request-ID') if headers else None
        
        # Input validation
        if not path or not isinstance(path, str):
            raise InvalidInputError(
                message="Invalid request path",
                service_name="api-gateway",
                details={"parameter": "path", "value": path}
            )
        
        # Determine target service
        service_name = self._get_service_for_path(path)
        if not service_name:
            raise ValidationError(
                message=f"No service found for path: {path}",
                service_name="api-gateway",
                details={"path": path, "available_services": list(self.service_clients.keys())}
            )
        
        # Check if service client exists
        if service_name not in self.service_clients:
            self.logger.error(f"Service client not found: {service_name}")
            raise ServiceUnavailableError(
                message=f"Service {service_name} is not available",
                service_name="api-gateway",
                details={"target_service": service_name, "path": path}
            )
        
        service_client = self.service_clients[service_name]
        
        # Prepare request
        clean_path = self._clean_path_for_service(path, service_name)
        headers = await propagate_request_id(headers or {}, request_id)
        
        try:
            # Build request parameters
            request_params = {
                "headers": headers,
                "params": query_params
            }
            
            # Add body for POST/PUT requests
            if method in ["POST", "PUT", "PATCH"] and body is not None:
                if isinstance(body, (dict, list)):
                    request_params["json"] = body
                else:
                    request_params["data"] = body
            
            # Make service call
            response_data = await service_client.call_service(
                method=method,
                endpoint=clean_path,
                **request_params
            )
            
            # Log successful routing
            response_time = time.time() - start_time
            self.performance_logger.log_performance(
                service_name="api-gateway",
                endpoint=path,
                response_time=response_time,
                status_code=200,
                request_id=request_id
            )
            
            return response_data
            
        except httpx.HTTPStatusError as e:
            # Preserve the original status code from downstream service
            response_time = time.time() - start_time
            
            # Log the error with proper categorization
            error_category = "downstream_http_error"
            if e.response and e.response.status_code >= 500:
                error_category = "downstream_server_error"
            elif e.response and e.response.status_code >= 400:
                error_category = "downstream_client_error"
            
            self.performance_logger.log_error(
                error_type=error_category,
                service_name="api-gateway",
                endpoint=path,
                error_message=f"Downstream service error: {str(e)}",
                request_id=request_id,
                downstream_service=service_name
            )
            
            # Re-raise to preserve status code
            raise e
            
        except httpx.TimeoutException as e:
            response_time = time.time() - start_time
            
            self.performance_logger.log_error(
                error_type="timeout",
                service_name="api-gateway",
                endpoint=path,
                error_message=f"Request timeout after {response_time:.2f}s",
                request_id=request_id,
                downstream_service=service_name
            )
            
            # Map to 504 Gateway Timeout
            raise GatewayTimeoutError(
                message=f"Gateway timeout while calling {service_name}",
                service_name="api-gateway",
                details={"target_service": service_name, "path": path, "timeout": f"{response_time:.2f}s"}
            )
            
        except httpx.ConnectError as e:
            self.performance_logger.log_error(
                error_type="connection_error",
                service_name="api-gateway",
                endpoint=path,
                error_message=f"Connection error to {service_name}: {str(e)}",
                request_id=request_id,
                downstream_service=service_name
            )
            
            # Map to 502 Bad Gateway
            raise BadGatewayError(
                message=f"Bad gateway - unable to connect to {service_name}",
                service_name="api-gateway",
                details={"target_service": service_name, "path": path, "error": str(e)}
            )
            
        except httpx.RequestError as e:
            self.performance_logger.log_error(
                error_type="request_error",
                service_name="api-gateway",
                endpoint=path,
                error_message=f"Request error to {service_name}: {str(e)}",
                request_id=request_id,
                downstream_service=service_name
            )
            
            # Map to 502 Bad Gateway
            raise BadGatewayError(
                message=f"Bad gateway - request error to {service_name}",
                service_name="api-gateway",
                details={"target_service": service_name, "path": path, "error": str(e)}
            )
            
        except (ServiceError, ValidationError, InvalidInputError, BadGatewayError, 
                ServiceUnavailableError, GatewayTimeoutError, ExternalAPIError):
            # Re-raise our custom errors to preserve status codes
            raise
        except Exception as e:
            response_time = time.time() - start_time
            
            log_structured_error(
                logger=self.logger,
                message=f"Unexpected error routing to {service_name}: {str(e)}",
                error_category="routing_error",
                request_id=request_id,
                service_name="api-gateway",
                endpoint=path,
                downstream_service=service_name,
                exc_info=True
            )
            
            # Wrap unexpected errors in ServiceError
            raise ServiceError(
                message=f"Unexpected error routing request to {service_name}: {str(e)}",
                service_name="api-gateway",
                details={"target_service": service_name, "path": path, "request_id": request_id}
            )
    
    def get_circuit_breaker_states(self) -> Dict[str, Any]:
        """Get circuit breaker states for all services"""
        states = {}
        for service_name, client in self.service_clients.items():
            try:
                states[service_name] = client.get_circuit_breaker_state()
            except Exception as e:
                states[service_name] = {
                    "service": service_name,
                    "state": "ERROR",
                    "error": str(e)
                }
        return states
    
    async def health_check_services(self) -> Dict[str, Any]:
        """Perform health checks on all services"""
        health_results = {}
        
        for service_name, client in self.service_clients.items():
            try:
                # Try to call health endpoint
                response = await client.call_service("GET", "/health")
                health_results[service_name] = {
                    "status": "healthy",
                    "response": response
                }
            except httpx.HTTPStatusError as e:
                health_results[service_name] = {
                    "status": "unhealthy",
                    "error": f"HTTP {e.response.status_code}" if e.response else "HTTP error",
                    "message": str(e)
                }
            except httpx.TimeoutException:
                health_results[service_name] = {
                    "status": "timeout",
                    "error": "Health check timeout"
                }
            except httpx.ConnectError:
                health_results[service_name] = {
                    "status": "unreachable",
                    "error": "Connection failed"
                }
            except Exception as e:
                health_results[service_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return health_results
    
    async def close(self):
        """Close all service clients"""
        for client in self.service_clients.values():
            try:
                await client.close()
            except Exception as e:
                self.logger.error(f"Error closing service client: {str(e)}") 