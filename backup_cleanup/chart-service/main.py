"""
Chart Service - Microservice for chart generation and technical analysis.
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
from typing import Dict, Any, List, Optional
import sys
import os
import httpx
from datetime import datetime
import numpy as np

# Add parent directory to path for common imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import ChartServiceConfig, get_config, service_registry
from common.logging import setup_logging, log_request_middleware, get_logger, RequestIDMiddleware, log_structured_error
from common.cache import chart_cache, cache_manager
from common.rate_limiter import chart_service_rate_limit
from common.auth import get_optional_user
from common.http_client import get_service_client, create_service_client
from common.errors import (
    ServiceError, InvalidInputError, NotFoundError, ValidationError,
    ServiceUnavailableError, BadGatewayError, GatewayTimeoutError,
    InvalidDataError, InsufficientDataError, ComputationError
)
from technical_analysis import TechnicalAnalyzer

# Configuration
config: ChartServiceConfig = get_config("chart-service")
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Chart Service",
    description="Microservice for chart generation and technical analysis",
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
technical_analyzer = None

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup."""
    global data_service_client, technical_analyzer
    
    logger.info("🚀 Chart Service starting up...")
    
    # Setup logging
    setup_logging(config.service_name, config.log_level, config.log_format)
    
    # Initialize data service client
    data_service_client = get_service_client("data-service", config.data_service_url)
    
    # Initialize technical analyzer
    technical_analyzer = TechnicalAnalyzer()
    
    logger.info("✅ Chart Service initialized")
    logger.info("🌐 Chart Service ready for requests!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Chart Service shutting down...")

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

@app.get("/api/charts/{symbol}/ohlc")
@chart_cache(ttl=config.cache_ttl_charts)
async def get_ohlc_data(
    symbol: str,
    timeframe: str = Query(config.default_timeframe, description="Chart timeframe"),
    limit: int = Query(100, description="Number of data points", le=config.max_data_points),
    _: bool = Depends(chart_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get OHLC chart data."""
    try:
        # Input validation
        if not symbol or not symbol.strip():
            raise InvalidInputError("Symbol parameter cannot be empty")
        
        valid_timeframes = ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"]
        if timeframe not in valid_timeframes:
            raise ValidationError(f"Invalid timeframe '{timeframe}'. Must be one of: {valid_timeframes}")
        
        if limit <= 0:
            raise ValidationError("Limit must be greater than 0")
        
        # Fetch data from data service
        response = await data_service_client.call_service(
            "GET", 
            f"/api/crypto/{symbol}/history",
            params={"days": 30 if timeframe == "1d" else 7}
        )
        
        raw_data = response.get("data", [])
        
        if not raw_data:
            raise NotFoundError(f"No price data available for symbol '{symbol}'")
        
        # Convert to OHLC format
        ohlc_data = technical_analyzer.convert_to_ohlc(raw_data, timeframe)
        
        return {
            "data": ohlc_data[-limit:] if limit else ohlc_data,
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "success": True
        }
        
    except ServiceError:
        # Re-raise service errors with preserved status codes
        raise
    except (InvalidDataError, InsufficientDataError, ComputationError):
        # Re-raise technical analysis errors
        raise
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise NotFoundError(f"Symbol '{symbol}' not found")
        elif 400 <= e.response.status_code < 500:
            raise
        else:
            raise BadGatewayError(f"Data service error: {str(e)}")
    except httpx.TimeoutException as e:
        raise GatewayTimeoutError(f"Data service timeout: {str(e)}")
    except httpx.ConnectError as e:
        raise ServiceUnavailableError(f"Data service connection failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching OHLC data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/charts/{symbol}/indicators")
@chart_cache(ttl=config.cache_ttl_indicators)
async def get_technical_indicators(
    symbol: str,
    indicators: str = Query("sma,rsi,macd", description="Comma-separated indicators"),
    period: int = Query(14, description="Indicator period"),
    _: bool = Depends(chart_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get technical indicators."""
    try:
        # Input validation
        if not symbol or not symbol.strip():
            raise InvalidInputError("Symbol parameter cannot be empty")
        
        if not indicators or not indicators.strip():
            raise InvalidInputError("Indicators parameter cannot be empty")
        
        if period <= 0 or period > 200:
            raise ValidationError("Period must be between 1 and 200")
        
        indicator_list = [i.strip().lower() for i in indicators.split(",")]
        valid_indicators = ["sma", "ema", "rsi", "macd", "bollinger"]
        
        invalid_indicators = [ind for ind in indicator_list if ind not in valid_indicators]
        if invalid_indicators:
            raise ValidationError(f"Invalid indicators: {invalid_indicators}. Valid indicators: {valid_indicators}")
        
        # Fetch price data
        response = await data_service_client.call_service(
            "GET",
            f"/api/crypto/{symbol}/history",
            params={"days": 100}  # Get more data for indicators
        )
        
        price_data = response.get("data", [])
        
        if not price_data:
            raise NotFoundError(f"No price data available for symbol '{symbol}'")
        
        # Extract price values for calculations
        prices = technical_analyzer.extract_prices(price_data)
        
        if len(prices) < period:
            raise InsufficientDataError(
                f"Insufficient data for calculations. Need at least {period} data points, got {len(prices)}",
                min_required=period,
                actual_count=len(prices)
            )
        
        # Calculate indicators
        results = {}
        for indicator in indicator_list:
            try:
                if indicator == "sma":
                    results["sma"] = technical_analyzer.calculate_sma(prices, period)
                elif indicator == "ema":
                    results["ema"] = technical_analyzer.calculate_ema(prices, period)
                elif indicator == "rsi":
                    results["rsi"] = technical_analyzer.calculate_rsi(prices, period)
                elif indicator == "macd":
                    results["macd"] = technical_analyzer.calculate_macd(prices)
                elif indicator == "bollinger":
                    results["bollinger"] = technical_analyzer.calculate_bollinger_bands(prices, period)
            except (InvalidDataError, InsufficientDataError, ComputationError) as e:
                # Include indicator name in error context
                e.context = e.context or {}
                e.context["indicator"] = indicator
                e.context["symbol"] = symbol
                raise
        
        return {
            "data": results,
            "symbol": symbol.upper(),
            "period": period,
            "indicators": indicator_list,
            "success": True
        }
        
    except ServiceError:
        # Re-raise service errors with preserved status codes
        raise
    except (InvalidDataError, InsufficientDataError, ComputationError):
        # Re-raise technical analysis errors
        raise
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise NotFoundError(f"Symbol '{symbol}' not found")
        elif 400 <= e.response.status_code < 500:
            raise
        else:
            raise BadGatewayError(f"Data service error: {str(e)}")
    except httpx.TimeoutException as e:
        raise GatewayTimeoutError(f"Data service timeout: {str(e)}")
    except httpx.ConnectError as e:
        raise ServiceUnavailableError(f"Data service connection failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error calculating indicators for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/charts/{symbol}/volume")
@chart_cache(ttl=config.cache_ttl_charts)
async def get_volume_data(
    symbol: str,
    days: int = Query(30, description="Number of days", ge=1, le=365),
    _: bool = Depends(chart_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get volume chart data."""
    try:
        # Input validation
        if not symbol or not symbol.strip():
            raise InvalidInputError("Symbol parameter cannot be empty")
        
        if days < 1 or days > 365:
            raise ValidationError("Days parameter must be between 1 and 365")
        
        # Fetch data from data service
        response = await data_service_client.call_service(
            "GET",
            f"/api/crypto/{symbol}/history",
            params={"days": days}
        )
        
        raw_data = response.get("data", [])
        
        if not raw_data:
            raise NotFoundError(f"No price data available for symbol '{symbol}'")
        
        volume_data = technical_analyzer.extract_volume_data(raw_data)
        
        return {
            "data": volume_data,
            "symbol": symbol.upper(),
            "days": days,
            "success": True
        }
        
    except ServiceError:
        # Re-raise service errors with preserved status codes
        raise
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise NotFoundError(f"Symbol '{symbol}' not found")
        elif 400 <= e.response.status_code < 500:
            raise
        else:
            raise BadGatewayError(f"Data service error: {str(e)}")
    except httpx.TimeoutException as e:
        raise GatewayTimeoutError(f"Data service timeout: {str(e)}")
    except httpx.ConnectError as e:
        raise ServiceUnavailableError(f"Data service connection failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching volume data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/charts/compare")
@chart_cache(ttl=config.cache_ttl_charts)
async def compare_symbols(
    symbols: str = Query(..., description="Comma-separated symbols to compare"),
    days: int = Query(30, description="Number of days"),
    normalize: bool = Query(True, description="Normalize prices to percentage"),
    _: bool = Depends(chart_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Compare multiple symbols on the same chart."""
    try:
        # Input validation
        if not symbols or not symbols.strip():
            raise InvalidInputError("Symbols parameter cannot be empty")
        
        if days < 1 or days > 365:
            raise ValidationError("Days parameter must be between 1 and 365")
        
        symbol_list = [s.strip().lower() for s in symbols.split(",")]
        
        if not symbol_list:
            raise InvalidInputError("At least one symbol is required")
        
        if len(symbol_list) > 10:
            raise ValidationError("Maximum 10 symbols allowed for comparison")
        
        # Remove duplicates
        symbol_list = list(dict.fromkeys(symbol_list))
        
        # Fetch data for all symbols in parallel
        tasks = []
        for symbol in symbol_list:
            tasks.append(
                data_service_client.call_service(
                    "GET",
                    f"/api/crypto/{symbol}/history",
                    params={"days": days}
                )
            )
        
        import asyncio
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process comparison data
        comparison_data = {}
        successful_symbols = []
        failed_symbols = []
        
        for i, response in enumerate(responses):
            symbol = symbol_list[i]
            if isinstance(response, Exception):
                failed_symbols.append(symbol)
                logger.warning(f"Failed to fetch data for symbol {symbol}: {response}")
            else:
                raw_data = response.get("data", [])
                if raw_data:
                    try:
                        if normalize:
                            comparison_data[symbol] = technical_analyzer.normalize_prices(raw_data)
                        else:
                            comparison_data[symbol] = raw_data
                        successful_symbols.append(symbol)
                    except Exception as e:
                        failed_symbols.append(symbol)
                        logger.warning(f"Failed to process data for symbol {symbol}: {e}")
                else:
                    failed_symbols.append(symbol)
        
        if not comparison_data:
            raise NotFoundError("No valid data found for any of the requested symbols")
        
        result = {
            "data": comparison_data,
            "symbols": successful_symbols,
            "normalized": normalize,
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
    except (InvalidDataError, InsufficientDataError, ComputationError):
        # Re-raise technical analysis errors
        raise
    except Exception as e:
        logger.error(f"Unexpected error comparing symbols: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Global exception handlers
@app.exception_handler(ServiceError)
async def service_error_handler(request: Request, exc: ServiceError):
    """Handle ServiceError exceptions with preserved status codes"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    log_structured_error(
        logger=logger,
        message=f"Service error in chart service: {str(exc)}",
        error_category=exc.error_code,
        request_id=request_id,
        service_name="chart-service",
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
        message=f"Unhandled exception in chart service: {str(exc)}",
        error_category="unhandled_exception",
        request_id=request_id,
        service_name="chart-service",
        endpoint=str(request.url.path),
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred during chart analysis",
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

@app.exception_handler(InvalidDataError)
async def invalid_data_exception_handler(request: Request, exc: InvalidDataError):
    """Handle invalid data errors from technical analysis"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Invalid Data",
            "message": str(exc),
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(InsufficientDataError)
async def insufficient_data_exception_handler(request: Request, exc: InsufficientDataError):
    """Handle insufficient data errors from technical analysis"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Insufficient Data",
            "message": str(exc),
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