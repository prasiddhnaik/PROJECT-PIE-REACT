from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

# Import our optimal free APIs
from optimal_free_apis import optimal_apis

# Create router
router = APIRouter(prefix="/api", tags=["stock-data"])

class StockRequest(BaseModel):
    symbol: str
    
class BatchStockRequest(BaseModel):
    symbols: List[str]

@router.get("/quote/{symbol}")
async def get_quote(symbol: str):
    """
    Get real-time stock quote data from the optimal API source
    
    Uses a cascading fallback system:
    1. Yahoo Finance (unlimited)
    2. Finnhub (60/min)
    3. Twelve Data (8/min)
    4. Alpha Vantage (5/min)
    """
    try:
        data = await optimal_apis.get_stock_data(symbol)
        return data
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/quotes")
async def get_batch_quotes(request: BatchStockRequest):
    """
    Get real-time stock quotes for multiple symbols
    
    Intelligently distributes requests across available APIs to maximize throughput
    while respecting rate limits
    """
    try:
        data = await optimal_apis.get_batch_stock_data(request.symbols)
        return data
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/crypto/{crypto_id}")
async def get_crypto(crypto_id: str, vs_currency: str = "usd"):
    """
    Get cryptocurrency data from CoinGecko
    """
    try:
        data = await optimal_apis.get_crypto_coingecko(crypto_id, vs_currency)
        if not data:
            raise HTTPException(status_code=404, detail=f"Cryptocurrency {crypto_id} not found")
        return data
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/status")
async def get_api_status():
    """
    Get current API usage status and rate limits
    """
    return optimal_apis.get_api_status() 