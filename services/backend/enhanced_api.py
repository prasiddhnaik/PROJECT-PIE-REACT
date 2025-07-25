import time
import logging
import aiohttp
import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple
from fastapi import HTTPException

# Configure logging
logger = logging.getLogger(__name__)

# Import API keys from config
from config import APIConfig

ALPHA_VANTAGE_KEY = APIConfig.ALPHA_VANTAGE_KEY
TWELVE_DATA_KEY = APIConfig.TWELVE_DATA_KEY

async def get_stock_data_with_retry(symbol: str, max_retries: int = 3) -> Dict[str, Any]:
    """
    Get stock data with retry logic and fallback to other APIs
    
    Args:
        symbol: Stock ticker symbol
        max_retries: Maximum number of retry attempts
        
    Returns:
        Dictionary with stock data and source information
    """
    # Try yfinance first with retries
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to fetch {symbol} from yfinance (attempt {attempt + 1})...")
            data = yf.download(symbol, period="1d", progress=False)
            
            if not data.empty:
                logger.info(f"Successfully fetched {symbol} from yfinance")
                # Convert to dictionary format
                return {
                    "source": "yfinance",
                    "symbol": symbol,
                    "price": float(data['Close'].iloc[-1]),
                    "change": float(data['Close'].iloc[-1] - data['Open'].iloc[0]),
                    "change_percent": float((data['Close'].iloc[-1] - data['Open'].iloc[0]) / data['Open'].iloc[0] * 100),
                    "volume": int(data['Volume'].iloc[-1]) if 'Volume' in data else 0,
                    "timestamp": data.index[-1].isoformat()
                }
        except Exception as e:
            logger.warning(f"yfinance attempt {attempt + 1} failed for {symbol}: {e}")
            
        # Exponential backoff
        if attempt < max_retries - 1:
            sleep_time = 2 ** attempt
            logger.info(f"Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)
    
    # Fallback to Alpha Vantage
    try:
        logger.info(f"Falling back to Alpha Vantage for {symbol}...")
        av_data = await get_alpha_vantage_data(symbol)
        if av_data:
            logger.info(f"Successfully fetched {symbol} from Alpha Vantage")
            return av_data
    except Exception as e:
        logger.error(f"Alpha Vantage fallback failed for {symbol}: {e}")
        
    # Final fallback to Twelve Data
    try:
        logger.info(f"Falling back to Twelve Data for {symbol}...")
        td_data = await get_twelve_data(symbol)
        if td_data:
            logger.info(f"Successfully fetched {symbol} from Twelve Data")
            return td_data
    except Exception as e:
        logger.error(f"Twelve Data fallback failed for {symbol}: {e}")
    
    # If all APIs fail, raise an exception
    logger.error(f"All API sources failed for {symbol}")
    raise HTTPException(status_code=503, detail=f"Unable to fetch stock data for {symbol}")

async def get_alpha_vantage_data(symbol: str) -> Dict[str, Any]:
    """Fetch stock data from Alpha Vantage API"""
    # Remove ^ character for indices if present
    clean_symbol = symbol.replace('^', '')
    
    # Construct API URL with proper string formatting
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={clean_symbol}&apikey={ALPHA_VANTAGE_KEY}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=5) as response:
            if response.status == 200:
                data = await response.json()
                
                if 'Global Quote' in data and data['Global Quote']:
                    quote = data['Global Quote']
                    return {
                        "source": "alpha_vantage",
                        "symbol": symbol,
                        "price": float(quote.get('05. price', 0)),
                        "change": float(quote.get('09. change', 0)),
                        "change_percent": float(quote.get('10. change percent', '0%').replace('%', '')),
                        "volume": int(quote.get('06. volume', 0)),
                        "timestamp": quote.get('07. latest trading day', '')
                    }
    
    return None

async def get_twelve_data(symbol: str) -> Dict[str, Any]:
    """Fetch stock data from Twelve Data API"""
    # Remove ^ character for indices if present
    clean_symbol = symbol.replace('^', '')
    
    # Construct API URL with proper string formatting
    url = f"https://api.twelvedata.com/quote?symbol={clean_symbol}&apikey={TWELVE_DATA_KEY}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=5) as response:
            if response.status == 200:
                data = await response.json()
                
                if 'close' in data and 'symbol' in data:
                    return {
                        "source": "twelve_data",
                        "symbol": symbol,
                        "price": float(data.get('close', 0)),
                        "change": float(data.get('change', 0)),
                        "change_percent": float(data.get('percent_change', 0)),
                        "volume": int(data.get('volume', 0)),
                        "timestamp": data.get('datetime', '')
                    }
    
    return None

async def get_batch_stock_data(symbols: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Fetch data for multiple stock symbols with fallback mechanisms
    
    Args:
        symbols: List of stock ticker symbols
        
    Returns:
        Dictionary mapping symbols to their data
    """
    results = {}
    
    # Process symbols in batches to avoid rate limits
    batch_size = 5
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i+batch_size]
        
        # Process each symbol in the batch
        for symbol in batch:
            try:
                data = await get_stock_data_with_retry(symbol)
                results[symbol] = data
            except Exception as e:
                logger.error(f"Failed to fetch data for {symbol}: {e}")
                # Add minimal placeholder data
                results[symbol] = {
                    "source": "error",
                    "symbol": symbol,
                    "price": 0,
                    "change": 0,
                    "change_percent": 0,
                    "error": str(e)
                }
        
        # Add a small delay between batches to avoid rate limits
        if i + batch_size < len(symbols):
            time.sleep(1)
    
    return results 