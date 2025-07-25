"""
Graph Service - Microservice for advanced graph generation and analytics.
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from typing import Dict, Any, List, Optional
import sys
import os
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import httpx
from datetime import datetime

# Add parent directory to path for common imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import GraphServiceConfig, get_config
from common.logging import setup_logging, log_request_middleware, get_logger, RequestIDMiddleware, log_structured_error
from common.cache import cached, cache_manager
from common.rate_limiter import graph_service_rate_limit
from common.auth import get_optional_user
from common.http_client import get_service_client, create_service_client
from common.errors import (
    ServiceError, InvalidInputError, NotFoundError, ValidationError,
    ServiceUnavailableError, BadGatewayError, GatewayTimeoutError
)

# Configuration
config: GraphServiceConfig = get_config("graph-service")
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Graph Service",
    description="Microservice for advanced graph generation and analytics",
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
data_service_client = None

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup."""
    global data_service_client
    
    logger.info("🚀 Graph Service starting up...")
    
    # Setup logging
    setup_logging(config.service_name, config.log_level, config.log_format)
    
    # Initialize data service client
    data_service_client = get_service_client("data-service", config.data_service_url)
    
    logger.info("✅ Graph Service initialized")
    logger.info("🌐 Graph Service ready for requests!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Graph Service shutting down...")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": config.service_name,
        "version": config.service_version,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/graphs/correlation")
@cached(ttl=config.cache_ttl_graphs, namespace="graphs")
async def generate_correlation_graph(
    request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    _: bool = Depends(graph_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Generate correlation analysis graph."""
    try:
        # Input validation
        symbols = request.get("symbols", [])
        timeframe = request.get("timeframe", "30d")
        
        if not symbols:
            raise InvalidInputError("Symbols list cannot be empty")
        
        if not isinstance(symbols, list):
            raise InvalidInputError("Symbols must be provided as a list")
        
        if len(symbols) < 2:
            raise InvalidInputError("At least 2 symbols required for correlation analysis")
        
        if len(symbols) > 20:
            raise ValidationError("Maximum 20 symbols allowed for correlation analysis")
        
        # Validate timeframe
        valid_timeframes = ["7d", "30d", "90d", "1y"]
        if timeframe not in valid_timeframes:
            raise ValidationError(f"Invalid timeframe '{timeframe}'. Must be one of: {valid_timeframes}")
        
        # Clean and validate symbols
        symbol_list = []
        for symbol in symbols:
            if not symbol or not str(symbol).strip():
                continue
            symbol_list.append(str(symbol).strip().lower())
        
        if len(symbol_list) < 2:
            raise InvalidInputError("At least 2 valid symbols required after filtering")
        
        # Fetch data for all symbols in parallel
        tasks = []
        days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
        days = days_map.get(timeframe, 30)
        
        for symbol in symbol_list:
            tasks.append(
                data_service_client.call_service(
                    "GET",
                    f"/api/crypto/{symbol}/history",
                    params={"days": days}
                )
            )
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for data availability
        valid_responses = []
        failed_symbols = []
        
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                failed_symbols.append(symbol_list[i])
            elif response.get("data"):
                valid_responses.append(response)
            else:
                failed_symbols.append(symbol_list[i])
        
        if len(valid_responses) < 2:
            raise NotFoundError(f"Insufficient valid data for correlation analysis. Failed symbols: {failed_symbols}")
        
        # Process correlation data
        try:
            correlation_matrix = calculate_correlation_matrix(responses, symbol_list)
        except Exception as e:
            raise ValidationError(f"Correlation calculation failed: {str(e)}")
        
        result = {
            "data": {
                "correlation_matrix": correlation_matrix,
                "symbols": symbol_list,
                "timeframe": timeframe
            },
            "success": True
        }
        
        if failed_symbols:
            result["warnings"] = {
                "failed_symbols": failed_symbols,
                "message": f"Could not fetch data for symbols: {', '.join(failed_symbols)}"
            }
        
        return result
        
    except ServiceError:
        # Re-raise service errors with preserved status codes
        raise
    except httpx.HTTPStatusError as e:
        if 400 <= e.response.status_code < 500:
            raise
        else:
            raise BadGatewayError(f"Data service error: {str(e)}")
    except httpx.TimeoutException as e:
        raise GatewayTimeoutError(f"Data service timeout: {str(e)}")
    except httpx.ConnectError as e:
        raise ServiceUnavailableError(f"Data service connection failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error generating correlation graph: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/graphs/portfolio")
@cached(ttl=config.cache_ttl_graphs, namespace="graphs")
async def generate_portfolio_graph(
    request: Dict[str, Any],
    _: bool = Depends(graph_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Generate portfolio performance graph."""
    try:
        # Input validation
        holdings = request.get("holdings", [])
        timeframe = request.get("timeframe", "30d")
        
        if not holdings:
            raise InvalidInputError("Holdings list cannot be empty")
        
        if not isinstance(holdings, list):
            raise InvalidInputError("Holdings must be provided as a list")
        
        if len(holdings) > 50:
            raise ValidationError("Maximum 50 holdings allowed for portfolio analysis")
        
        # Validate timeframe
        valid_timeframes = ["7d", "30d", "90d", "1y"]
        if timeframe not in valid_timeframes:
            raise ValidationError(f"Invalid timeframe '{timeframe}'. Must be one of: {valid_timeframes}")
        
        # Validate holdings structure
        validated_holdings = []
        for i, holding in enumerate(holdings):
            if not isinstance(holding, dict):
                raise InvalidInputError(f"Holding at index {i} must be an object with 'symbol' and 'amount' fields")
            
            symbol = holding.get("symbol")
            amount = holding.get("amount", 0)
            
            if not symbol or not str(symbol).strip():
                raise InvalidInputError(f"Holding at index {i} must have a valid symbol")
            
            try:
                amount = float(amount)
                if amount < 0:
                    raise InvalidInputError(f"Holding amount for {symbol} cannot be negative")
            except (ValueError, TypeError):
                raise InvalidInputError(f"Holding amount for {symbol} must be a valid number")
            
            validated_holdings.append({
                "symbol": str(symbol).strip().lower(),
                "amount": amount
            })
        
        if not validated_holdings:
            raise InvalidInputError("No valid holdings found after validation")
        
        # Fetch data for portfolio assets
        days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
        days = days_map.get(timeframe, 30)
        
        portfolio_data = []
        failed_holdings = []
        
        for holding in validated_holdings:
            symbol = holding["symbol"]
            amount = holding["amount"]
            
            try:
                response = await data_service_client.call_service(
                    "GET",
                    f"/api/crypto/{symbol}/history",
                    params={"days": days}
                )
                
                if response.get("success") and response.get("data"):
                    portfolio_data.append({
                        "symbol": symbol,
                        "amount": amount,
                        "history": response.get("data", [])
                    })
                else:
                    failed_holdings.append(symbol)
                    
            except Exception as e:
                failed_holdings.append(symbol)
                logger.warning(f"Failed to fetch data for holding {symbol}: {e}")
        
        if not portfolio_data:
            raise NotFoundError("No valid data found for any portfolio holdings")
        
        # Calculate portfolio performance
        try:
            portfolio_performance = calculate_portfolio_performance(portfolio_data)
        except Exception as e:
            raise ValidationError(f"Portfolio performance calculation failed: {str(e)}")
        
        result = {
            "data": {
                "portfolio_performance": portfolio_performance,
                "holdings": validated_holdings,
                "timeframe": timeframe
            },
            "success": True
        }
        
        if failed_holdings:
            result["warnings"] = {
                "failed_holdings": failed_holdings,
                "message": f"Could not fetch data for holdings: {', '.join(failed_holdings)}"
            }
        
        return result
        
    except ServiceError:
        # Re-raise service errors with preserved status codes
        raise
    except httpx.HTTPStatusError as e:
        if 400 <= e.response.status_code < 500:
            raise
        else:
            raise BadGatewayError(f"Data service error: {str(e)}")
    except httpx.TimeoutException as e:
        raise GatewayTimeoutError(f"Data service timeout: {str(e)}")
    except httpx.ConnectError as e:
        raise ServiceUnavailableError(f"Data service connection failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error generating portfolio graph: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/graphs/heatmap")
@cached(ttl=config.cache_ttl_graphs, namespace="graphs")
async def generate_market_heatmap(
    category: str = Query("crypto", description="Market category"),
    limit: int = Query(50, description="Number of assets", le=100),
    _: bool = Depends(graph_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Generate market heatmap."""
    try:
        # Input validation
        valid_categories = ["crypto", "stocks", "forex"]
        if category not in valid_categories:
            raise InvalidInputError(f"Invalid category '{category}'. Must be one of: {valid_categories}")
        
        if limit <= 0 or limit > 100:
            raise ValidationError("Limit must be between 1 and 100")
        
        if category == "crypto":
            # Fetch top crypto data
            response = await data_service_client.call_service(
                "GET",
                "/api/crypto/top100",
                params={"limit": limit}
            )
            
            market_data = response.get("data", [])
            
            if not market_data:
                raise NotFoundError("No crypto market data available")
            
            # Format for heatmap
            heatmap_data = []
            for asset in market_data:
                try:
                    heatmap_data.append({
                        "symbol": asset.get("symbol", "").upper(),
                        "name": asset.get("name", ""),
                        "price_change_24h": float(asset.get("price_change_percentage_24h", 0)),
                        "market_cap": float(asset.get("market_cap", 0)),
                        "volume": float(asset.get("total_volume", 0))
                    })
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid data for asset {asset.get('symbol', 'unknown')}: {e}")
                    continue
            
            if not heatmap_data:
                raise ValidationError("No valid heatmap data could be generated from market data")
            
            return {
                "data": {
                    "heatmap": heatmap_data,
                    "category": category,
                    "count": len(heatmap_data)
                },
                "success": True
            }
        else:
            # TODO: Implement stocks and forex heatmaps
            raise NotFoundError(f"Heatmap for category '{category}' is not yet implemented")
            
    except ServiceError:
        # Re-raise service errors with preserved status codes
        raise
    except httpx.HTTPStatusError as e:
        if 400 <= e.response.status_code < 500:
            raise
        else:
            raise BadGatewayError(f"Data service error: {str(e)}")
    except httpx.TimeoutException as e:
        raise GatewayTimeoutError(f"Data service timeout: {str(e)}")
    except httpx.ConnectError as e:
        raise ServiceUnavailableError(f"Data service connection failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error generating heatmap: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def calculate_correlation_matrix(responses: List[Any], symbols: List[str]) -> List[List[float]]:
    """Calculate correlation matrix for price data."""
    import numpy as np
    
    # Extract price arrays
    price_arrays = []
    for i, response in enumerate(responses):
        if not isinstance(response, Exception) and response.get("success"):
            prices = [point[1] for point in response.get("data", []) if len(point) >= 2]
            price_arrays.append(prices)
        else:
            # Fill with zeros if data unavailable
            price_arrays.append([0] * 30)
    
    # Calculate correlation matrix
    if price_arrays:
        try:
            correlation_matrix = np.corrcoef(price_arrays).tolist()
            return correlation_matrix
        except:
            # Return identity matrix as fallback
            size = len(symbols)
            return [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]
    
    return []

def calculate_portfolio_performance(portfolio_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Calculate portfolio performance over time."""
    performance = []
    
    if not portfolio_data:
        return performance
    
    # Get time series length from first asset
    time_length = len(portfolio_data[0].get("history", []))
    
    for i in range(time_length):
        total_value = 0
        timestamp = None
        
        for asset in portfolio_data:
            history = asset.get("history", [])
            amount = asset.get("amount", 0)
            
            if i < len(history) and len(history[i]) >= 2:
                timestamp = history[i][0]
                price = history[i][1]
                total_value += price * amount
        
        if timestamp:
            performance.append({
                "timestamp": timestamp,
                "total_value": total_value
            })
    
    return performance

# Global exception handlers
@app.exception_handler(ServiceError)
async def service_error_handler(request: Request, exc: ServiceError):
    """Handle ServiceError exceptions with preserved status codes"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    log_structured_error(
        logger=logger,
        message=f"Service error in graph service: {str(exc)}",
        error_category=exc.error_code,
        request_id=request_id,
        service_name="graph-service",
        endpoint=str(request.url.path),
        error_context=exc.context,
        http_status=exc.http_status
    )
    
    return JSONResponse(
        status_code=exc.http_status,
        content={
            "error": exc.error_code,
            "message": str(exc),
            "status_code": exc.http_status,
            "context": exc.context,
            "request_id": request_id,
            "service": exc.service_name,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions with proper logging and response"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    log_structured_error(
        logger=logger,
        message=f"Unhandled exception in graph service: {str(exc)}",
        error_category="unhandled_exception",
        request_id=request_id,
        service_name="graph-service",
        endpoint=str(request.url.path),
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred during graph computation",
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