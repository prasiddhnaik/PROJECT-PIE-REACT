"""
API Gateway - Central entry point for microservices.
"""

from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
import httpx
import asyncio
from typing import Dict, Any, List, Optional
import sys
import os
import logging
import json
from datetime import datetime

# Add parent directory to path for common imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import APIGatewayConfig, get_config, service_registry
from common.logging import setup_logging, log_request_middleware, get_logger, RequestIDMiddleware, log_structured_error
from common.rate_limiter import api_gateway_rate_limit
from common.auth import get_optional_user
from common.http_client import get_service_client, ServiceClient
from common.errors import (
    ServiceError,
    ValidationError,
    InvalidInputError,
    BadGatewayError,
    ServiceUnavailableError,
    GatewayTimeoutError,
    ExternalAPIError
)
from router import APIRouter

# Configuration
config: APIGatewayConfig = get_config("api-gateway")
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Financial Analytics API Gateway",
    description="Central API Gateway for microservices",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
app.middleware("http")(log_request_middleware)

# Add request ID middleware
app.add_middleware(RequestIDMiddleware)

# Global components
api_router: Optional[APIRouter] = None
service_clients: Dict[str, ServiceClient] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize gateway on startup."""
    global api_router, service_clients
    
    logger.info("🚀 API Gateway starting up...")
    
    # Setup logging
    setup_logging(config.service_name, config.log_level, config.log_format)
    
    # Initialize service clients
    service_clients = {
        "data-service": get_service_client("data-service", config.data_service_url),
        "chart-service": get_service_client("chart-service", config.chart_service_url),
        "graph-service": get_service_client("graph-service", config.graph_service_url),
        "ai-service": get_service_client("ai-service", config.ai_service_url),
    }
    
    # Initialize router
    api_router = APIRouter()
    
    # Register health checks if enabled
    if config.health_check_enabled:
        asyncio.create_task(start_health_checks())
    
    logger.info("🌐 API Gateway ready for requests!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("API Gateway shutting down...")
    for client in service_clients.values():
        await client.client.client.aclose()

async def start_health_checks():
    """Start periodic health checks for services."""
    while True:
        try:
            for service_name, client in service_clients.items():
                is_healthy = await client.health_check()
                service_registry.update_service_status(
                    service_name, 
                    "healthy" if is_healthy else "unhealthy"
                )
            
            await asyncio.sleep(30)  # Check every 30 seconds
        except Exception as e:
            logger.error(f"Health check error: {e}")
            await asyncio.sleep(60)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Gateway health check."""
    services_status = {}
    
    for service_name, client in service_clients.items():
        try:
            is_healthy = await client.health_check()
            services_status[service_name] = "healthy" if is_healthy else "unhealthy"
        except:
            services_status[service_name] = "error"
    
    all_healthy = all(status == "healthy" for status in services_status.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "service": config.service_name,
        "version": config.service_version,
        "services": services_status,
        "timestamp": datetime.utcnow().isoformat()
    }

# Service routing endpoints
@app.api_route("/api/data/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_to_data_service(
    request: Request,
    path: str,
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Route requests to data service."""
    return await api_router.route_request(
        method=request.method,
        path=f"/api/data/{path}",
        headers=dict(request.headers),
        query_params=dict(request.query_params),
        body=await request.json() if request.headers.get("content-type") == "application/json" else await request.body()
    )

@app.api_route("/api/charts/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_to_chart_service(
    request: Request,
    path: str,
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Route requests to chart service."""
    return await api_router.route_request(
        method=request.method,
        path=f"/api/charts/{path}",
        headers=dict(request.headers),
        query_params=dict(request.query_params),
        body=await request.json() if request.headers.get("content-type") == "application/json" else await request.body()
    )

@app.api_route("/api/graphs/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_to_graph_service(
    request: Request,
    path: str,
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Route requests to graph service."""
    return await api_router.route_request(
        method=request.method,
        path=f"/api/graphs/{path}",
        headers=dict(request.headers),
        query_params=dict(request.query_params),
        body=await request.json() if request.headers.get("content-type") == "application/json" else await request.body()
    )

@app.api_route("/api/ai/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_to_ai_service(
    request: Request,
    path: str,
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Route requests to AI service."""
    return await api_router.route_request(
        method=request.method,
        path=f"/api/ai/{path}",
        headers=dict(request.headers),
        query_params=dict(request.query_params),
        body=await request.json() if request.headers.get("content-type") == "application/json" else await request.body()
    )

# Legacy endpoint compatibility (for backward compatibility)
@app.api_route("/api/crypto/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_crypto_legacy(
    request: Request,
    path: str,
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Route legacy crypto endpoints to data service."""
    return await api_router.route_request(
        method=request.method,
        path=f"/api/crypto/{path}",
        headers=dict(request.headers),
        query_params=dict(request.query_params),
        body=await request.json() if request.headers.get("content-type") == "application/json" else await request.body()
    )

@app.api_route("/api/market/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_market_legacy(
    request: Request,
    path: str,
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Route legacy market endpoints to data service."""
    return await api_router.route_request(
        method=request.method,
        path=f"/api/market/{path}",
        headers=dict(request.headers),
        query_params=dict(request.query_params),
        body=await request.json() if request.headers.get("content-type") == "application/json" else await request.body()
    )

# Special handling for streaming endpoints
@app.post("/api/ai/chat/stream")
async def stream_chat(
    request: Request,
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Stream chat responses from AI service."""
    try:
        # Get request body
        body = await request.body()
        
        # Forward to AI service
        ai_client = service_clients["ai-service"]
        
        async with ai_client.client.client.stream(
            "POST",
            f"{config.ai_service_url}/api/ai/chat/stream",
            content=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": request.headers.get("Authorization", "")
            }
        ) as response:
            response.raise_for_status()
            
            return StreamingResponse(
                response.aiter_raw(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Service": "ai-service"
                }
            )
    except (ServiceError, ValidationError, InvalidInputError, BadGatewayError, 
            ServiceUnavailableError, GatewayTimeoutError, ExternalAPIError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error streaming chat: {e}")
        raise ServiceError(
            message=f"Unexpected error in streaming endpoint: {str(e)}",
            service_name="api-gateway",
            context={"endpoint": "/api/ai/chat/stream"}
        )

# Service discovery endpoint
@app.get("/api/gateway/services")
async def get_services():
    """Get available services and their status."""
    services = service_registry.get_all_services()
    
    # Add health status
    for service_name, service_info in services.items():
        if service_name in service_clients:
            try:
                is_healthy = await service_clients[service_name].health_check()
                service_info["health"] = "healthy" if is_healthy else "unhealthy"
            except:
                service_info["health"] = "error"
    
    return {
        "services": services,
        "gateway_config": {
            "timeout": config.timeout,
            "max_retries": config.max_retries,
            "load_balancing_enabled": config.enable_load_balancing
        }
    }

# Batch requests endpoint
@app.post("/api/gateway/batch")
async def batch_requests(
    requests: List[Dict[str, Any]],
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Execute multiple requests in parallel."""
    try:
        tasks = []
        
        for req in requests:
            service = req.get("service")
            path = req.get("path")
            method = req.get("method", "GET")
            
            if service in service_clients:
                task = service_clients[service].call_service(method, path, **req.get("params", {}))
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "error": str(result),
                    "request_index": i
                })
            else:
                processed_results.append({
                    "success": True,
                    "data": result,
                    "request_index": i
                })
        
        return {"results": processed_results, "success": True}
    except (ServiceError, ValidationError, InvalidInputError, BadGatewayError, 
            ServiceUnavailableError, GatewayTimeoutError, ExternalAPIError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing batch requests: {e}")
        raise ServiceError(
            message=f"Unexpected error processing batch requests: {str(e)}",
            service_name="api-gateway",
            context={"endpoint": "/api/gateway/batch", "request_count": len(requests) if 'requests' in locals() else 0}
        )

# ServiceError exception handler for preserving status codes
@app.exception_handler(ServiceError)
async def service_error_exception_handler(request: Request, exc: ServiceError):
    """Handle ServiceError exceptions to preserve status codes"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    return JSONResponse(
        status_code=exc.http_status,
        content={
            "error": exc.__class__.__name__,
            "message": str(exc),
            "service": exc.service_name,
            "details": exc.context,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# httpx.HTTPStatusError exception handler for downstream service errors
@app.exception_handler(httpx.HTTPStatusError)
async def httpx_exception_handler(request: Request, exc: httpx.HTTPStatusError):
    """Handle httpx.HTTPStatusError exceptions from downstream services"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    return JSONResponse(
        status_code=exc.response.status_code,
        content={
            "error": "DownstreamServiceError",
            "message": f"Downstream service error: {str(exc)}",
            "status_code": exc.response.status_code,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Global exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions with proper logging and response"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    log_structured_error(
        logger=logger,
        message=f"Unhandled exception in API Gateway: {str(exc)}",
        error_category="unhandled_exception",
        request_id=request_id,
        service_name="api-gateway",
        endpoint=str(request.url.path),
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTPExceptions with consistent formatting and request correlation"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "details": exc.errors(),
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.host,
        port=config.port,
        reload=True if config.environment == "development" else False,
        workers=config.workers if config.environment == "production" else 1
    ) 