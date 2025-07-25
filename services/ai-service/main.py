"""
AI Service - Microservice for AI chat and analysis.
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
import httpx
from typing import Dict, Any, List, Optional
import sys
import os
import json
import asyncio
from datetime import datetime

# Add parent directory to path for common imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import AIServiceConfig, get_config
from common.logging import setup_logging, log_request_middleware, get_logger, RequestIDMiddleware, log_structured_error
from common.cache import ai_cache, cache_manager
from common.rate_limiter import ai_service_rate_limit
from common.auth import get_optional_user
from common.http_client import get_service_client
from common.errors import (
    ServiceError,
    ValidationError,
    InvalidInputError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    BadGatewayError,
    ServiceUnavailableError,
    GatewayTimeoutError,
    ExternalAPIError,
    ExternalAPITimeoutError,
    ExternalAPIRateLimitError,
    InsufficientDataError
)
from openrouter_ai import OpenRouterClient
from chat_memory import ChatMemoryManager

# Configuration
config: AIServiceConfig = get_config("ai-service")
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Service",
    description="Microservice for AI chat and analysis",
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
openrouter_client: Optional[OpenRouterClient] = None
chat_memory: Optional[ChatMemoryManager] = None
data_service_client = None

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup."""
    global openrouter_client, chat_memory, data_service_client
    
    logger.info("🚀 AI Service starting up...")
    
    # Setup logging
    setup_logging(config.service_name, config.log_level, config.log_format)
    
    # Initialize OpenRouter client
    if config.openrouter_api_key:
        openrouter_client = OpenRouterClient(
            api_key=config.openrouter_api_key,
            base_url=config.openrouter_api_url,
            default_model=config.default_model,
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )
        logger.info("✅ OpenRouter client initialized")
    else:
        logger.warning("⚠️ OpenRouter API key not configured")
    
    # Initialize chat memory
    chat_memory = ChatMemoryManager(
        max_history=config.max_conversation_history,
        ttl=config.conversation_ttl
    )
    
    # Initialize data service client
    data_service_client = get_service_client("data-service", config.data_service_url)
    
    logger.info("🌐 AI Service ready for requests!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("AI Service shutting down...")
    if openrouter_client:
        await openrouter_client.close()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        ai_status = "available" if openrouter_client else "demo_mode"
        
        # Test AI service if available
        if openrouter_client:
            try:
                await openrouter_client.health_check()
                ai_status = "healthy"
            except Exception:
                ai_status = "degraded"
        
        return {
            "status": "healthy",
            "service": config.service_name,
            "ai_provider": ai_status,
            "timestamp": datetime.utcnow().isoformat(),
            "version": config.service_version
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@app.post("/api/ai/chat")
async def chat(
    request: Dict[str, Any],
    _: bool = Depends(ai_service_rate_limit("chat")),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Chat with AI assistant."""
    if not openrouter_client:
        raise ServiceUnavailableError(
            message="AI service not available - OpenRouter client not initialized",
            service_name="ai-service",
            context={"feature": "chat"}
        )
    
    try:
        # Input validation
        message = request.get("message", "").strip()
        if not message:
            raise InvalidInputError(
                message="Message cannot be empty",
                service_name="ai-service",
                context={"parameter": "message"}
            )
        
        if len(message) > 10000:
            raise InvalidInputError(
                message="Message too long (maximum 10,000 characters)",
                service_name="ai-service",
                context={"parameter": "message", "length": len(message), "max_length": 10000}
            )
        
        session_id = request.get("session_id", "default")
        if not session_id or not isinstance(session_id, str) or len(session_id) > 100:
            raise InvalidInputError(
                message="Invalid session_id (must be non-empty string, max 100 characters)",
                service_name="ai-service",
                context={"parameter": "session_id"}
            )
        
        model = request.get("model", config.default_model)
        if not isinstance(model, str) or len(model) > 100:
            raise InvalidInputError(
                message="Invalid model name",
                service_name="ai-service",
                context={"parameter": "model"}
            )
        
        # Get conversation history
        history = await chat_memory.get_conversation(session_id)
        
        # Add current message to history
        history.append({"role": "user", "content": message})
        
        # Get AI response
        response = await openrouter_client.chat_completion(
            messages=history,
            model=model
        )
        
        ai_message = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not ai_message:
            raise InsufficientDataError(
                message="No response generated from AI model",
                service_name="ai-service",
                context={"model": model, "session_id": session_id}
            )
        
        # Save AI response to history
        history.append({"role": "assistant", "content": ai_message})
        await chat_memory.save_conversation(session_id, history)
        
        return {
            "response": ai_message,
            "session_id": session_id,
            "model": model,
            "success": True
        }
    except (ServiceError, ValidationError, InvalidInputError, UnauthorizedError, 
            ForbiddenError, RateLimitError, ExternalAPIError, ExternalAPITimeoutError, 
            ExternalAPIRateLimitError, InsufficientDataError):
        raise
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise ServiceError(
            message=f"Chat error: {str(e)}",
            service_name="ai-service",
            context={"model": model, "session_id": session_id}
        )

@app.post("/api/ai/chat/stream")
async def chat_stream(
    request: Dict[str, Any],
    _: bool = Depends(ai_service_rate_limit("chat")),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Stream chat with AI assistant."""
    if not openrouter_client:
        raise ServiceUnavailableError(
            message="AI service not available - OpenRouter client not initialized",
            service_name="ai-service",
            context={"feature": "chat_stream"}
        )
    
    try:
        # Input validation
        message = request.get("message", "").strip()
        if not message:
            raise InvalidInputError(
                message="Message cannot be empty",
                service_name="ai-service",
                context={"parameter": "message"}
            )
        
        if len(message) > 10000:
            raise InvalidInputError(
                message="Message too long (maximum 10,000 characters)",
                service_name="ai-service",
                context={"parameter": "message", "length": len(message), "max_length": 10000}
            )
        
        session_id = request.get("session_id", "default")
        if not session_id or not isinstance(session_id, str) or len(session_id) > 100:
            raise InvalidInputError(
                message="Invalid session_id (must be non-empty string, max 100 characters)",
                service_name="ai-service",
                context={"parameter": "session_id"}
            )
        
        model = request.get("model", config.default_model)
        if not isinstance(model, str) or len(model) > 100:
            raise InvalidInputError(
                message="Invalid model name",
                service_name="ai-service",
                context={"parameter": "model"}
            )
        
        # Get conversation history
        history = await chat_memory.get_conversation(session_id)
        history.append({"role": "user", "content": message})
        
        async def generate_response():
            full_response = ""
            try:
                async for chunk in openrouter_client.chat_completion_stream(
                    messages=history,
                    model=model
                ):
                    chunk_content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if chunk_content:
                        full_response += chunk_content
                        yield f"data: {json.dumps({'content': chunk_content})}\n\n"
                
                # Save complete response to history
                if full_response:
                    history.append({"role": "assistant", "content": full_response})
                    await chat_memory.save_conversation(session_id, history)
                
                yield f"data: {json.dumps({'done': True})}\n\n"
                
            except (ServiceError, ValidationError, InvalidInputError, UnauthorizedError, 
                    ForbiddenError, RateLimitError, ExternalAPIError, ExternalAPITimeoutError, 
                    ExternalAPIRateLimitError) as e:
                yield f"data: {json.dumps({'error': str(e), 'error_type': type(e).__name__})}\n\n"
            except Exception as e:
                logger.error(f"Unexpected error in streaming generation: {e}")
                yield f"data: {json.dumps({'error': 'Internal server error', 'error_type': 'ServerError'})}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    except (ServiceError, ValidationError, InvalidInputError, UnauthorizedError, 
            ForbiddenError, RateLimitError, ExternalAPIError, ExternalAPITimeoutError, 
            ExternalAPIRateLimitError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error in streaming chat endpoint: {e}")
        raise ServiceError(
            message=f"Unexpected error processing streaming request: {str(e)}",
            service_name="ai-service",
            context={"endpoint": "/api/ai/chat/stream", "session_id": request.get("session_id", "unknown")}
        )

@app.post("/api/ai/analyze")
@ai_cache(ttl=config.cache_ttl_ai)
async def analyze_data(
    request: Dict[str, Any],
    _: bool = Depends(ai_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Analyze financial data with AI."""
    if not openrouter_client:
        raise ServiceUnavailableError(
            message="AI service not available - OpenRouter client not initialized",
            service_name="ai-service",
            context={"feature": "data_analysis"}
        )
    
    try:
        # Input validation
        symbol = request.get("symbol", "").strip().upper()
        if not symbol:
            raise InvalidInputError(
                message="Symbol is required for analysis",
                service_name="ai-service",
                context={"parameter": "symbol"}
            )
        
        if not symbol.replace('-', '').replace('_', '').isalnum() or len(symbol) > 20:
            raise InvalidInputError(
                message="Invalid symbol format (must be non-empty string, max 20 characters)",
                service_name="ai-service",
                context={"parameter": "symbol", "value": symbol}
            )
        
        analysis_type = request.get("type", "general").strip().lower()
        valid_types = ["general", "technical", "fundamental", "sentiment", "risk"]
        if analysis_type not in valid_types:
            raise InvalidInputError(
                message=f"Invalid analysis type. Must be one of: {', '.join(valid_types)}",
                service_name="ai-service",
                context={"parameter": "type", "value": analysis_type, "valid_options": valid_types}
            )
        
        # Fetch data from data service
        try:
            data_response = await data_service_client.call_service(
                "GET",
                f"/api/crypto/{symbol}",
            )
        except ServiceError as e:
            if e.status_code == 404:
                raise NotFoundError(
                    message=f"No data available for cryptocurrency: {symbol}",
                    service_name="ai-service",
                    context={"symbol": symbol}
                )
            else:
                raise BadGatewayError(
                    message=f"Failed to fetch data for {symbol}: {str(e)}",
                    service_name="ai-service",
                    context={"symbol": symbol, "downstream_error": str(e)}
                )
        
        crypto_data = data_response.get("data", {})
        if not crypto_data:
            raise InsufficientDataError(
                message=f"No market data available for symbol: {symbol}",
                service_name="ai-service",
                context={"symbol": symbol}
            )
        
        # Create analysis prompt
        market_data = crypto_data.get('market_data', {})
        current_price = market_data.get('current_price', {}).get('usd', 'N/A')
        market_cap = market_data.get('market_cap', {}).get('usd', 'N/A')
        price_change_24h = market_data.get('price_change_percentage_24h', 'N/A')
        
        prompt = f"""
        Analyze the following cryptocurrency data for {symbol}:
        
        Current Price: ${current_price}
        Market Cap: ${market_cap}
        24h Change: {price_change_24h}%
        
        Please provide a {analysis_type} analysis including:
        1. Current market position
        2. Key factors affecting price
        3. Technical outlook
        4. Risk assessment
        
        Keep the analysis concise and actionable.
        """
        
        messages = [{"role": "user", "content": prompt}]
        
        response = await openrouter_client.chat_completion(
            messages=messages,
            model=config.default_model
        )
        
        analysis = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not analysis:
            raise InsufficientDataError(
                message="No analysis generated from AI model",
                service_name="ai-service",
                context={"symbol": symbol, "analysis_type": analysis_type}
            )
        
        return {
            "analysis": analysis,
            "symbol": symbol,
            "type": analysis_type,
            "data_timestamp": crypto_data.get("last_updated", ""),
            "success": True
        }
    except (ServiceError, ValidationError, InvalidInputError, NotFoundError, 
            BadGatewayError, InsufficientDataError, UnauthorizedError, 
            ForbiddenError, RateLimitError, ExternalAPIError, ExternalAPITimeoutError, 
            ExternalAPIRateLimitError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error in data analysis endpoint: {e}")
        raise ServiceError(
            message=f"Unexpected error processing analysis request: {str(e)}",
            service_name="ai-service",
            context={"endpoint": "/api/ai/analyze", "symbol": request.get("symbol", "unknown")}
        )

@app.get("/api/ai/models")
async def get_available_models(
    _: bool = Depends(ai_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get available AI models."""
    if not openrouter_client:
        raise ServiceUnavailableError(
            message="AI service not available - OpenRouter client not initialized",
            service_name="ai-service",
            context={"feature": "models"}
        )
    
    try:
        models = await openrouter_client.get_models()
        return {
            "models": models,
            "default_model": config.default_model,
            "success": True
        }
    except (ServiceError, ValidationError, UnauthorizedError, ForbiddenError, 
            RateLimitError, ExternalAPIError, ExternalAPITimeoutError, 
            ExternalAPIRateLimitError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching models: {e}")
        raise ServiceError(
            message=f"Unexpected error retrieving available models: {str(e)}",
            service_name="ai-service",
            context={"endpoint": "/api/ai/models"}
        )

@app.delete("/api/ai/chat/{session_id}")
async def clear_conversation(
    session_id: str,
    _: bool = Depends(ai_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Clear conversation history."""
    # Input validation
    if not session_id or not isinstance(session_id, str) or len(session_id) > 100:
        raise InvalidInputError(
            message="Invalid session_id (must be non-empty string, max 100 characters)",
            service_name="ai-service",
            context={"parameter": "session_id", "value": session_id}
        )
    
    try:
        await chat_memory.clear_conversation(session_id)
        return {
            "message": f"Conversation {session_id} cleared",
            "success": True
        }
    except Exception as e:
        logger.error(f"Unexpected error clearing conversation: {e}")
        raise ServiceError(
            message=f"Unexpected error clearing conversation: {str(e)}",
            service_name="ai-service",
            context={"endpoint": "/api/ai/chat/{session_id}", "session_id": session_id}
        )

@app.get("/api/ai/chat/{session_id}/history")
async def get_conversation_history(
    session_id: str,
    _: bool = Depends(ai_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get conversation history."""
    # Input validation
    if not session_id or not isinstance(session_id, str) or len(session_id) > 100:
        raise InvalidInputError(
            message="Invalid session_id (must be non-empty string, max 100 characters)",
            service_name="ai-service",
            context={"parameter": "session_id", "value": session_id}
        )
    
    try:
        history = await chat_memory.get_conversation(session_id)
        return {
            "history": history,
            "session_id": session_id,
            "success": True
        }
    except Exception as e:
        logger.error(f"Unexpected error fetching conversation history: {e}")
        raise ServiceError(
            message=f"Unexpected error retrieving conversation history: {str(e)}",
            service_name="ai-service",
            context={"endpoint": "/api/ai/chat/{session_id}/history", "session_id": session_id}
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
        message=f"Unhandled exception in AI service: {str(exc)}",
        error_category="unhandled_exception",
        request_id=request_id,
        service_name="ai-service",
        endpoint=str(request.url.path),
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while processing your AI request",
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTPExceptions with consistent formatting"""
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