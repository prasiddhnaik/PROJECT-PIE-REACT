"""
Data Service - Microservice for data aggregation and external API integration.
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import uvicorn
from typing import Dict, Any, List, Optional
import sys
import os
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import httpx
import logging
import json
from datetime import datetime, timedelta

# Add parent directory to path for common imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import DataServiceConfig, get_config
from common.logging import setup_logging, log_request_middleware, get_logger, RequestIDMiddleware, log_structured_error
from common.cache import crypto_cache, market_cache, cache_manager
from common.rate_limiter import data_service_rate_limit
from common.auth import get_optional_user
from common.errors import (
    ServiceError, InvalidInputError, NotFoundError, ValidationError,
    ServiceUnavailableError, BadGatewayError, GatewayTimeoutError,
    ExternalAPIError, ExternalAPITimeoutError, ExternalAPIRateLimitError
)
from providers import DataProvider, CryptoDataProvider, StockDataProvider, ForexDataProvider

# Database imports for long-term storage
import sqlite3
import aiosqlite
from contextlib import asynccontextmanager

# Configuration
config: DataServiceConfig = get_config("data-service")
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Data Service",
    description="Microservice for financial data aggregation",
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

# Global data providers
crypto_provider: Optional[CryptoDataProvider] = None
stock_provider: Optional[StockDataProvider] = None
forex_provider: Optional[ForexDataProvider] = None

def get_crypto_provider():
    """Lazy initialization of crypto provider"""
    global crypto_provider
    if crypto_provider is None:
        try:
            crypto_provider = CryptoDataProvider()
            logger.info("Crypto provider initialized")
        except Exception as e:
            logger.error(f"Failed to initialize crypto provider: {e}")
            crypto_provider = None
    return crypto_provider

def get_stock_provider():
    """Lazy initialization of stock provider"""
    global stock_provider
    if stock_provider is None:
        try:
            stock_provider = StockDataProvider()
            logger.info("Stock provider initialized")
        except Exception as e:
            logger.error(f"Failed to initialize stock provider: {e}")
            stock_provider = None
    return stock_provider

def get_forex_provider():
    """Lazy initialization of forex provider"""
    global forex_provider
    if forex_provider is None:
        try:
            forex_provider = ForexDataProvider()
            logger.info("Forex provider initialized")
        except Exception as e:
            logger.error(f"Failed to initialize forex provider: {e}")
            forex_provider = None
    return forex_provider

class LongTermDataStorage:
    """Database manager for long-term API data storage (3-4 months)"""
    
    def __init__(self, db_path: str = "data/api_data.db"):
        self.db_path = db_path
        self.retention_days = 120  # 4 months
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    async def initialize_database(self):
        """Initialize database tables for long-term storage"""
        async with aiosqlite.connect(self.db_path) as db:
            # API Data table for storing all API responses
            await db.execute('''
                CREATE TABLE IF NOT EXISTS api_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    endpoint TEXT NOT NULL,
                    params TEXT,
                    data TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    source TEXT,
                    status_code INTEGER DEFAULT 200,
                    response_time REAL,
                    INDEX(endpoint),
                    INDEX(timestamp),
                    INDEX(source)
                )
            ''')
            
            # Crypto prices table for structured crypto data
            await db.execute('''
                CREATE TABLE IF NOT EXISTS crypto_prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    vs_currency TEXT DEFAULT 'usd',
                    market_cap REAL,
                    volume_24h REAL,
                    change_24h REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    source TEXT,
                    INDEX(symbol),
                    INDEX(timestamp),
                    INDEX(vs_currency)
                )
            ''')
            
            # Market data table for market overview data
            await db.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    market_type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    source TEXT,
                    INDEX(market_type),
                    INDEX(timestamp)
                )
            ''')
            
            await db.commit()
            logger.info(f"Database initialized at {self.db_path}")
    
    async def store_api_response(self, endpoint: str, params: Dict = None, 
                                data: Dict = None, source: str = None,
                                status_code: int = 200, response_time: float = None):
        """Store API response for long-term retention"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO api_data (endpoint, params, data, source, status_code, response_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    endpoint,
                    json.dumps(params) if params else None,
                    json.dumps(data) if data else None,
                    source,
                    status_code,
                    response_time
                ))
                await db.commit()
                
        except Exception as e:
            logger.error(f"Failed to store API response in database: {e}")
    
    async def store_crypto_price(self, symbol: str, price: float, vs_currency: str = 'usd',
                                market_cap: float = None, volume_24h: float = None,
                                change_24h: float = None, source: str = None):
        """Store structured crypto price data"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO crypto_prices (symbol, price, vs_currency, market_cap, volume_24h, change_24h, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (symbol, price, vs_currency, market_cap, volume_24h, change_24h, source))
                await db.commit()
                
        except Exception as e:
            logger.error(f"Failed to store crypto price in database: {e}")
    
    async def store_market_data(self, market_type: str, data: Dict, source: str = None):
        """Store market overview data"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO market_data (market_type, data, source)
                    VALUES (?, ?, ?)
                ''', (market_type, json.dumps(data), source))
                await db.commit()
                
        except Exception as e:
            logger.error(f"Failed to store market data in database: {e}")
    
    async def get_historical_data(self, endpoint: str, params: Dict = None, 
                                 days: int = 30) -> List[Dict]:
        """Retrieve historical data for analysis"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                query = '''
                    SELECT * FROM api_data 
                    WHERE endpoint = ? AND timestamp > datetime('now', '-{} days')
                    ORDER BY timestamp DESC
                '''.format(days)
                
                if params:
                    query = '''
                        SELECT * FROM api_data 
                        WHERE endpoint = ? AND params = ? AND timestamp > datetime('now', '-{} days')
                        ORDER BY timestamp DESC
                    '''.format(days)
                    
                    cursor = await db.execute(query, (endpoint, json.dumps(params)))
                else:
                    cursor = await db.execute(query, (endpoint,))
                
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to retrieve historical data: {e}")
            return []
    
    async def cleanup_old_data(self):
        """Remove data older than retention period"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cutoff_date = datetime.now() - timedelta(days=self.retention_days)
                
                # Clean up all tables
                tables = ['api_data', 'crypto_prices', 'market_data']
                total_deleted = 0
                
                for table in tables:
                    cursor = await db.execute(f'''
                        DELETE FROM {table} 
                        WHERE timestamp < ?
                    ''', (cutoff_date,))
                    
                    deleted = cursor.rowcount
                    total_deleted += deleted
                    logger.info(f"Cleaned up {deleted} old records from {table}")
                
                await db.commit()
                logger.info(f"Total cleanup: {total_deleted} records older than {self.retention_days} days")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
    
    async def get_storage_stats(self) -> Dict:
        """Get database storage statistics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                stats = {}
                
                # Count records in each table
                tables = ['api_data', 'crypto_prices', 'market_data']
                for table in tables:
                    cursor = await db.execute(f'SELECT COUNT(*) FROM {table}')
                    count = await cursor.fetchone()
                    stats[f"{table}_count"] = count[0]
                
                # Get database size
                try:
                    db_size = os.path.getsize(self.db_path)
                    stats['database_size_mb'] = round(db_size / (1024 * 1024), 2)
                except:
                    stats['database_size_mb'] = 0
                
                # Get date range
                cursor = await db.execute('''
                    SELECT MIN(timestamp) as oldest, MAX(timestamp) as newest 
                    FROM api_data
                ''')
                date_range = await cursor.fetchone()
                stats['oldest_record'] = date_range[0]
                stats['newest_record'] = date_range[1]
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {}

# Initialize long-term storage
long_term_storage = LongTermDataStorage()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting data service...")
    
    # Initialize long-term database storage
    await long_term_storage.initialize_database()
    
    logger.info("Database initialized successfully")
    logger.info("Data service startup complete - providers will be initialized on first request")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Data Service shutting down...")
    
    # Close providers
    try:
        if crypto_provider:
            await crypto_provider.close()
    except Exception as e:
        logger.error(f"Error closing crypto provider: {e}")
    
    try:
        if stock_provider:
            await stock_provider.close()
    except Exception as e:
        logger.error(f"Error closing stock provider: {e}")
    
    try:
        if forex_provider:
            await forex_provider.close()
    except Exception as e:
        logger.error(f"Error closing forex provider: {e}")
    
    logger.info("Data Service shutdown complete")

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

# Crypto endpoints
@app.get("/crypto/prices")
async def get_crypto_prices(
    symbols: str = Query(..., description="Comma-separated list of crypto symbols"),
    vs_currency: str = Query(default="usd", description="Currency to compare against"),
    _: bool = Depends(data_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get current prices for multiple cryptocurrencies."""
    try:
        symbol_list = [s.strip() for s in symbols.split(",")]
        
        if not symbol_list or not symbols.strip():
            raise InvalidInputError("Symbols parameter cannot be empty")
            
        try:
            prices = await crypto_provider.get_prices(symbol_list, vs_currency)
            
            # Store data before forwarding
            response_data = {"data": prices, "success": True}
            stored_data = await store_and_forward_data(
                response_data, 
                f"crypto/prices", 
                {"symbols": symbols, "vs_currency": vs_currency}
            )
            return stored_data
            
        except Exception as api_error:
            logger.error(f"API error fetching crypto prices: {api_error}")
            
            # Try to get fallback data
            fallback_data = await get_fallback_data(
                "crypto/prices",
                {"symbols": symbols, "vs_currency": vs_currency}
            )
            
            if fallback_data:
                logger.info(f"Returning fallback data for crypto prices: {symbols}")
                return fallback_data
            else:
                # No fallback available, return error with context
                raise HTTPException(
                    status_code=503,
                    detail=f"API temporarily unavailable and no cached data available for {symbols}"
                )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_crypto_prices: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/crypto/{symbol}")
@crypto_cache(ttl=config.cache_ttl_crypto)
async def get_crypto_details(
    symbol: str,
    _: bool = Depends(data_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get detailed information for a specific cryptocurrency."""
    try:
        if not symbol or not symbol.strip():
            raise InvalidInputError("Symbol parameter cannot be empty")
            
        provider = get_crypto_provider()
        if not provider:
            raise HTTPException(status_code=503, detail="Crypto provider not available")
        
        details = await provider.get_crypto_details(symbol.lower())
        
        # Store data before forwarding
        response_data = {"data": details, "success": True}
        stored_data = await store_and_forward_data(
            response_data,
            f"crypto/{symbol}",
            {"symbol": symbol}
        )
        return stored_data
        
    except Exception as e:
        logger.error(f"Error in get_crypto_details: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/crypto/{symbol}/history")
@crypto_cache(ttl=config.cache_ttl_crypto)
async def get_crypto_history(
    symbol: str,
    days: int = Query(7, description="Number of days", ge=1, le=365),
    interval: str = Query("daily", description="Data interval"),
    _: bool = Depends(data_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get crypto price history."""
    provider = get_crypto_provider()
    if not provider:
        raise HTTPException(status_code=503, detail="Crypto provider not available")
    
    try:
        if not symbol or not symbol.strip():
            raise InvalidInputError("Symbol parameter cannot be empty")
        if days < 1 or days > 365:
            raise ValidationError("Days parameter must be between 1 and 365")
            
        history = await provider.get_price_history(symbol.lower(), days, interval)
        
        # Ensure each record has the required keys
        if not isinstance(history, list):
            raise BadGatewayError("Malformed history data from provider")

        for record in history:
            if not all(key in record for key in ("timestamp", "price", "volume", "date")):
                raise BadGatewayError("Incomplete history record received from provider")

        response_payload = {
            "status": "success",
            "data": {
                "symbol": symbol.lower(),
                "history": history,
                "days": days,
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        return response_payload
        
    except ServiceError:
        # Re-raise service errors with preserved status codes
        raise
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise NotFoundError(f"Cryptocurrency '{symbol}' not found")
        elif 400 <= e.response.status_code < 500:
            raise
        else:
            raise BadGatewayError(f"External API error: {str(e)}")
    except httpx.TimeoutException as e:
        raise GatewayTimeoutError(f"External API timeout: {str(e)}")
    except httpx.ConnectError as e:
        raise ServiceUnavailableError(f"External API connection failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise BadGatewayError(f"Invalid JSON response from external API: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching crypto history for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/crypto/top100")
@crypto_cache(ttl=config.cache_ttl_crypto)
async def get_top_crypto(
    limit: int = Query(100, description="Number of cryptocurrencies", ge=1, le=250),
    vs_currency: str = Query("usd", description="Quote currency"),
    _: bool = Depends(data_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get top cryptocurrencies by market cap."""
    provider = get_crypto_provider()
    if not provider:
        raise HTTPException(status_code=503, detail="Crypto provider not available")
    
    try:
        if limit < 1 or limit > 250:
            raise ValidationError("Limit parameter must be between 1 and 250")
            
        top_crypto = await provider.get_top_cryptocurrencies(limit, vs_currency)
        return {"data": top_crypto, "success": True}
        
    except ServiceError:
        # Re-raise service errors with preserved status codes
        raise
    except httpx.HTTPStatusError as e:
        if 400 <= e.response.status_code < 500:
            raise
        else:
            raise BadGatewayError(f"External API error: {str(e)}")
    except httpx.TimeoutException as e:
        raise GatewayTimeoutError(f"External API timeout: {str(e)}")
    except httpx.ConnectError as e:
        raise ServiceUnavailableError(f"External API connection failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise BadGatewayError(f"Invalid JSON response from external API: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching top crypto: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/crypto/trending")
@crypto_cache(ttl=config.cache_ttl_crypto)
async def get_trending_crypto(
    _: bool = Depends(data_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get trending cryptocurrencies."""
    provider = get_crypto_provider()
    if not provider:
        raise HTTPException(status_code=503, detail="Crypto provider not available")
    
    try:
        trending = await provider.get_trending_crypto()
        return {"data": trending, "success": True}
        
    except ServiceError:
        # Re-raise service errors with preserved status codes
        raise
    except httpx.HTTPStatusError as e:
        if 400 <= e.response.status_code < 500:
            raise
        else:
            raise BadGatewayError(f"External API error: {str(e)}")
    except httpx.TimeoutException as e:
        raise GatewayTimeoutError(f"External API timeout: {str(e)}")
    except httpx.ConnectError as e:
        raise ServiceUnavailableError(f"External API connection failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise BadGatewayError(f"Invalid JSON response from external API: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching trending crypto: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Stock endpoints
@app.get("/api/stocks/{symbol}")
@market_cache(ttl=config.cache_ttl_market)
async def get_stock_data(
    symbol: str,
    _: bool = Depends(data_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get stock data."""
    provider = get_stock_provider()
    if not provider:
        raise HTTPException(status_code=503, detail="Stock provider not available")
    
    try:
        if not symbol or not symbol.strip():
            raise InvalidInputError("Symbol parameter cannot be empty")
            
        stock_data = await provider.get_stock_data(symbol.upper())
        return {"data": stock_data, "success": True}
        
    except ServiceError:
        # Re-raise service errors with preserved status codes
        raise
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise NotFoundError(f"Stock symbol '{symbol}' not found")
        elif 400 <= e.response.status_code < 500:
            raise
        else:
            raise BadGatewayError(f"External API error: {str(e)}")
    except httpx.TimeoutException as e:
        raise GatewayTimeoutError(f"External API timeout: {str(e)}")
    except httpx.ConnectError as e:
        raise ServiceUnavailableError(f"External API connection failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise BadGatewayError(f"Invalid JSON response from external API: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching stock data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/stocks/{symbol}/history")
@market_cache(ttl=config.cache_ttl_market)
async def get_stock_history(
    symbol: str,
    period: str = Query("1y", description="Time period"),
    interval: str = Query("1d", description="Data interval"),
    _: bool = Depends(data_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get stock price history."""
    provider = get_stock_provider()
    if not provider:
        raise HTTPException(status_code=503, detail="Stock provider not available")
    
    try:
        if not symbol or not symbol.strip():
            raise InvalidInputError("Symbol parameter cannot be empty")
        
        # Validate period and interval parameters
        valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
        valid_intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
        
        if period not in valid_periods:
            raise ValidationError(f"Invalid period '{period}'. Must be one of: {valid_periods}")
        if interval not in valid_intervals:
            raise ValidationError(f"Invalid interval '{interval}'. Must be one of: {valid_intervals}")
            
        history = await provider.get_stock_history(symbol.upper(), period, interval)
        return {"data": history, "success": True}
        
    except ServiceError:
        # Re-raise service errors with preserved status codes
        raise
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise NotFoundError(f"Stock symbol '{symbol}' not found")
        elif 400 <= e.response.status_code < 500:
            raise
        else:
            raise BadGatewayError(f"External API error: {str(e)}")
    except httpx.TimeoutException as e:
        raise GatewayTimeoutError(f"External API timeout: {str(e)}")
    except httpx.ConnectError as e:
        raise ServiceUnavailableError(f"External API connection failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise BadGatewayError(f"Invalid JSON response from external API: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching stock history for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Market data endpoints
@app.get("/market/overview")
async def get_market_overview(
    _: bool = Depends(data_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get comprehensive market overview."""
    try:
        # Fetch data from multiple sources concurrently
        results = await asyncio.gather(
            get_crypto_provider().get_market_overview() if get_crypto_provider() else asyncio.create_task(asyncio.sleep(0)),
            # Add more providers here as needed
            return_exceptions=True
        )
        
        # Combine results
        overview = {}
        
        # Process crypto data
        if len(results) > 0 and not isinstance(results[0], Exception):
            overview["crypto"] = results[0]
        
        # Add forex data if available
        if len(results) > 1 and not isinstance(results[1], Exception):
            overview["stocks"] = results[1]
        
        # Add stocks data if available
        if len(results) > 2 and not isinstance(results[2], Exception):
            overview["forex"] = results[2]
        
        # Store data before forwarding
        response_data = {"data": overview, "success": True}
        stored_data = await store_and_forward_data(
            response_data,
            "market/overview",
            {}
        )
        return stored_data
        
    except Exception as api_error:
        logger.error(f"API error fetching market overview: {api_error}")
        
        # Try to get fallback data
        fallback_data = await get_fallback_data(
            "market/overview",
            {}
        )
        
        if fallback_data:
            logger.info("Returning fallback data for market overview")
            return fallback_data
        else:
            # No fallback available, return error with context
            raise HTTPException(
                status_code=503,
                detail="Market overview API temporarily unavailable and no cached data available"
            )

@app.get("/api/market/sentiment")
@market_cache(ttl=config.cache_ttl_market)
async def get_market_sentiment(
    _: bool = Depends(data_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get market sentiment data."""
    provider = get_crypto_provider()
    if not provider:
        raise HTTPException(status_code=503, detail="Crypto provider not available")
    
    try:
        sentiment = await provider.get_fear_greed_index()
        return {"data": sentiment, "success": True}
        
    except ServiceError:
        # Re-raise service errors with preserved status codes
        raise
    except httpx.HTTPStatusError as e:
        if 400 <= e.response.status_code < 500:
            raise
        else:
            raise BadGatewayError(f"External API error: {str(e)}")
    except httpx.TimeoutException as e:
        raise GatewayTimeoutError(f"External API timeout: {str(e)}")
    except httpx.ConnectError as e:
        raise ServiceUnavailableError(f"External API connection failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise BadGatewayError(f"Invalid JSON response from external API: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching market sentiment: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Forex endpoints
@app.get("/api/forex/rates")
@market_cache(ttl=config.cache_ttl_market)
async def get_forex_rates(
    base: str = Query("USD", description="Base currency"),
    symbols: str = Query("EUR,GBP,JPY", description="Comma-separated currency symbols"),
    _: bool = Depends(data_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get forex exchange rates."""
    provider = get_forex_provider()
    if not provider:
        raise HTTPException(status_code=503, detail="Forex provider not available")
    
    try:
        if not symbols or not symbols.strip():
            raise InvalidInputError("Symbols parameter cannot be empty")
        if not base or not base.strip():
            raise InvalidInputError("Base currency parameter cannot be empty")
            
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        if not symbol_list:
            raise InvalidInputError("At least one target currency symbol is required")
            
        rates = await provider.get_exchange_rates(base.upper(), symbol_list)
        return {"data": rates, "success": True}
        
    except ServiceError:
        # Re-raise service errors with preserved status codes
        raise
    except httpx.HTTPStatusError as e:
        if 400 <= e.response.status_code < 500:
            raise
        else:
            raise BadGatewayError(f"External API error: {str(e)}")
    except httpx.TimeoutException as e:
        raise GatewayTimeoutError(f"External API timeout: {str(e)}")
    except httpx.ConnectError as e:
        raise ServiceUnavailableError(f"External API connection failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise BadGatewayError(f"Invalid JSON response from external API: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching forex rates: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Batch data endpoint
@app.post("/api/data/batch")
async def get_batch_data(
    requests: List[Dict[str, Any]],
    _: bool = Depends(data_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get multiple data points in parallel."""
    try:
        tasks = []
        
        for req in requests:
            data_type = req.get("type")
            params = req.get("params", {})
            
            if data_type == "crypto_price" and get_crypto_provider():
                symbol = params.get("symbol")
                tasks.append(get_crypto_provider().get_crypto_details(symbol))
            elif data_type == "stock_data" and get_stock_provider():
                symbol = params.get("symbol")
                tasks.append(get_stock_provider().get_stock_data(symbol))
            elif data_type == "forex_rate" and get_forex_provider():
                base = params.get("base", "USD")
                target = params.get("target", "EUR")
                tasks.append(get_forex_provider().get_exchange_rates(base, [target]))
        
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
        
        return {"data": processed_results, "success": True}
    except Exception as e:
        logger.error(f"Error processing batch data request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Global exception handlers
@app.exception_handler(ServiceError)
async def service_error_handler(request: Request, exc: ServiceError):
    """Handle ServiceError exceptions with preserved status codes"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    log_structured_error(
        logger=logger,
        message=f"Service error in data service: {str(exc)}",
        error_category=exc.error_code,
        request_id=request_id,
        service_name="data-service",
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
        message=f"Unhandled exception in data service: {str(exc)}",
        error_category="unhandled_exception",
        request_id=request_id,
        service_name="data-service",
        endpoint=str(request.url.path),
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while processing your request",
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

# Enhanced data storage before forwarding
async def store_and_forward_data(data: Dict[str, Any], endpoint: str, params: Dict = None) -> Dict[str, Any]:
    """Store API data persistently before forwarding to client"""
    try:
        # Generate storage key based on endpoint and params
        storage_key = f"api_data:{endpoint}"
        if params:
            param_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
            storage_key += f":{param_str}"
        
        # Store with extended TTL for data persistence
        await cache_manager.set(storage_key, data, ttl=86400, namespace="persistent_data")  # 24 hour storage
        
        # Also store in backup namespace for redundancy
        backup_key = f"backup:{storage_key}:{datetime.utcnow().strftime('%Y%m%d')}"
        await cache_manager.set(backup_key, data, ttl=604800, namespace="data_backup")  # 7 day backup
        
        # Store in long-term database (3-4 months retention)
        await long_term_storage.store_api_response(
            endpoint=endpoint,
            params=params,
            data=data,
            source="api_gateway"
        )
        
        # If it's crypto data, also store in structured format
        if endpoint.startswith("crypto/") and "data" in data:
            try:
                crypto_data = data["data"]
                if isinstance(crypto_data, dict):
                    for symbol, price_data in crypto_data.items():
                        if isinstance(price_data, dict) and "usd" in price_data:
                            await long_term_storage.store_crypto_price(
                                symbol=symbol,
                                price=price_data.get("usd", 0),
                                vs_currency="usd",
                                market_cap=price_data.get("usd_market_cap"),
                                change_24h=price_data.get("usd_24h_change"),
                                source="api_gateway"
                            )
            except Exception as e:
                logger.warning(f"Failed to store structured crypto data: {e}")
        
        # If it's market data, store in market table
        if endpoint.startswith("market/") and "data" in data:
            try:
                await long_term_storage.store_market_data(
                    market_type=endpoint.replace("market/", ""),
                    data=data["data"],
                    source="api_gateway"
                )
            except Exception as e:
                logger.warning(f"Failed to store market data: {e}")
        
        logger.info(f"Stored API data for {endpoint} with key {storage_key}")
        
        # Add metadata to response
        if isinstance(data, dict):
            data["_storage_info"] = {
                "stored_at": datetime.utcnow().isoformat(),
                "storage_key": storage_key,
                "backup_key": backup_key,
                "long_term_storage": True
            }
        
        return data
        
    except Exception as e:
        logger.error(f"Failed to store data for {endpoint}: {e}")
        # Return original data even if storage fails
        return data

@app.get("/api/data/storage/stats")
async def get_storage_stats(
    _: bool = Depends(data_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get statistics about stored API data."""
    try:
        # This would need Redis SCAN commands to count keys by namespace
        # For now, return basic info
        stats = {
            "persistent_data_namespace": "persistent_data",
            "backup_namespace": "data_backup",
            "storage_ttl_hours": 24,
            "backup_ttl_days": 7,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {"data": stats, "success": True}
        
    except Exception as e:
        logger.error(f"Error getting storage stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/data/storage/retrieve/{storage_key}")
async def retrieve_stored_data(
    storage_key: str,
    _: bool = Depends(data_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Retrieve previously stored API data by key."""
    try:
        # Try persistent data first
        data = await cache_manager.get(storage_key, namespace="persistent_data")
        
        if not data:
            # Try backup data
            data = await cache_manager.get(f"backup:{storage_key}", namespace="data_backup")
        
        if data:
            return {"data": data, "success": True, "retrieved_from": "storage"}
        else:
            raise HTTPException(status_code=404, detail="Stored data not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving stored data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_fallback_data(endpoint: str, params: Dict = None) -> Optional[Dict[str, Any]]:
    """Get cached data as fallback when API fails"""
    try:
        # Generate the same storage key
        storage_key = f"api_data:{endpoint}"
        if params:
            param_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
            storage_key += f":{param_str}"
        
        # Try persistent data first
        data = await cache_manager.get(storage_key, namespace="persistent_data")
        
        if data:
            logger.info(f"Using fallback data from persistent cache for {endpoint}")
            if isinstance(data, dict):
                data["_fallback_info"] = {
                    "used_cached_data": True,
                    "cache_source": "persistent_data",
                    "retrieved_at": datetime.utcnow().isoformat()
                }
            return data
        
        # Try backup data if persistent not available
        backup_keys = [
            f"backup:{storage_key}:{datetime.utcnow().strftime('%Y%m%d')}",  # Today
            f"backup:{storage_key}:{(datetime.utcnow() - timedelta(days=1)).strftime('%Y%m%d')}",  # Yesterday
            f"backup:{storage_key}:{(datetime.utcnow() - timedelta(days=2)).strftime('%Y%m%d')}"   # 2 days ago
        ]
        
        for backup_key in backup_keys:
            data = await cache_manager.get(backup_key, namespace="data_backup")
            if data:
                logger.info(f"Using fallback data from backup cache for {endpoint}")
                if isinstance(data, dict):
                    data["_fallback_info"] = {
                        "used_cached_data": True,
                        "cache_source": "data_backup",
                        "backup_key": backup_key,
                        "retrieved_at": datetime.utcnow().isoformat()
                    }
                return data
        
        logger.warning(f"No fallback data available for {endpoint}")
        return None
        
    except Exception as e:
        logger.error(f"Error retrieving fallback data for {endpoint}: {e}")
        return None

@app.get("/api/data/historical/{endpoint:path}")
async def get_historical_data(
    endpoint: str,
    days: int = Query(default=30, ge=1, le=120, description="Number of days to retrieve"),
    _: bool = Depends(data_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get historical data for analysis (up to 4 months)"""
    try:
        historical_data = await long_term_storage.get_historical_data(
            endpoint=endpoint,
            days=days
        )
        
        return {
            "data": historical_data,
            "endpoint": endpoint,
            "days_requested": days,
            "records_found": len(historical_data),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error retrieving historical data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/data/database/stats")
async def get_database_stats(
    _: bool = Depends(data_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get database storage statistics"""
    try:
        stats = await long_term_storage.get_storage_stats()
        
        return {
            "data": stats,
            "retention_days": long_term_storage.retention_days,
            "database_path": long_term_storage.db_path,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/data/database/cleanup")
async def cleanup_database(
    _: bool = Depends(data_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Manually trigger database cleanup (remove old data)"""
    try:
        await long_term_storage.cleanup_old_data()
        
        return {
            "message": "Database cleanup completed",
            "retention_days": long_term_storage.retention_days,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error during database cleanup: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/data/crypto/historical/{symbol}")
async def get_crypto_historical_prices(
    symbol: str,
    days: int = Query(default=30, ge=1, le=120, description="Number of days to retrieve"),
    vs_currency: str = Query(default="usd", description="Currency to compare against"),
    _: bool = Depends(data_service_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get historical crypto prices from database"""
    try:
        async with aiosqlite.connect(long_term_storage.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            cursor = await db.execute('''
                SELECT * FROM crypto_prices 
                WHERE symbol = ? AND vs_currency = ? 
                AND timestamp > datetime('now', '-{} days')
                ORDER BY timestamp DESC
            '''.format(days), (symbol.lower(), vs_currency))
            
            rows = await cursor.fetchall()
            historical_prices = [dict(row) for row in rows]
        
        return {
            "data": historical_prices,
            "symbol": symbol,
            "vs_currency": vs_currency,
            "days_requested": days,
            "records_found": len(historical_prices),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error retrieving crypto historical data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.host,
        port=config.port,
        reload=True if config.environment == "development" else False,
        workers=config.workers if config.environment == "production" else 1
    ) 