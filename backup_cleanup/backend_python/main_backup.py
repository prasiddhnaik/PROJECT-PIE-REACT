import os
import asyncio
import logging
import random
import aiohttp
import requests
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from twelvedata import TDClient
from polygon import RESTClient
from pycoingecko import CoinGeckoAPI
from iexfinance.stocks import Stock

# Import configuration
from config import APIConfig, DEFAULT_STOCK_SYMBOLS, DEFAULT_CRYPTO_SYMBOLS, MAJOR_INDICES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="Financial Analytics Hub API",
    description="Comprehensive financial data and analytics platform",
    version="2.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Keys Configuration
ALPHA_VANTAGE_KEY = APIConfig.ALPHA_VANTAGE_KEY
TWELVE_DATA_KEY = APIConfig.TWELVE_DATA_KEY
FINNHUB_KEY = APIConfig.FINNHUB_KEY
FRED_API_KEY = APIConfig.FRED_API_KEY

# Pydantic models
class PortfolioRequest(BaseModel):
    funds: List[Dict[str, Any]]
    start_date: str
    end_date: str
    allocation: Optional[Dict[str, float]] = None

class StockRequest(BaseModel):
    symbol: str
    period: Optional[str] = "1y"

class CryptoRequest(BaseModel):
    symbol: str
    currency: Optional[str] = "usd"

class RiskAnalysisRequest(BaseModel):
    symbols: Optional[List[str]] = None
    portfolio: Optional[List[Dict[str, Any]]] = None
    period: Optional[str] = "1y"
    confidence_level: Optional[float] = 0.95
    time_horizon: Optional[str] = "daily"

# Initialize API clients with error handling
td_client = None
polygon_client = None
coingecko_client = None
iex_client = None

try:
    # Twelve Data API
    if TWELVE_DATA_KEY:
        td_client = TDClient(apikey=TWELVE_DATA_KEY)
        logger.info("Twelve Data client initialized")
except Exception as e:
    logger.error(f"Error initializing Twelve Data: {str(e)}")

try:
    # Polygon API
    POLYGON_KEY = APIConfig.POLYGON_KEY
    if POLYGON_KEY:
        polygon_client = RESTClient(POLYGON_KEY)
        logger.info("Polygon client initialized")
except Exception as e:
    logger.error(f"Error initializing Polygon: {str(e)}")

try:
    # CoinGecko API (no key required for basic usage)
    coingecko_client = CoinGeckoAPI()
    logger.info("CoinGecko client initialized")
except Exception as e:
    logger.error(f"Error initializing CoinGecko: {str(e)}")

try:
    # IEX Cloud API
    IEX_CLOUD_KEY = APIConfig.IEX_CLOUD_KEY
    if IEX_CLOUD_KEY:
        iex_client = Stock(token=IEX_CLOUD_KEY)
        logger.info("IEX Cloud client initialized")
except Exception as e:
    logger.error(f"Error initializing IEX Cloud: {str(e)}")

# Global data cache with timestamps
cache = {}
last_update_time = {}

# Update interval in seconds (13 minutes = 780 seconds)
UPDATE_INTERVAL = 13 * 60

# Falling stocks check interval (2 minutes = 120 seconds)
FALLING_STOCKS_INTERVAL = 2 * 60

# Popular symbols to keep updated
TRACKED_SYMBOLS = [
    # Major stocks
    'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
    # Crypto
    'bitcoin', 'ethereum', 'cardano', 'polygon', 'solana'
]

# Additional stocks to monitor for falling trends
FALLING_STOCKS_WATCHLIST = [
    'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
    'AMD', 'INTC', 'CRM', 'ORCL', 'V', 'JPM', 'JNJ', 'PG', 'KO', 'WMT',
    'DIS', 'ADBE', 'PYPL', 'BABA', 'UBER', 'SHOP', 'ZM', 'ROKU', 'SQ', 'TWTR'
]

# Global cache for falling stocks data
falling_stocks_cache = {
    'stocks': [],
    'last_update': None,
    'notification_count': 0
}

# Enhanced stock data fetching with multiple APIs
async def fetch_stock_data_multiple_sources(symbol: str, period: str = "1y"):
    """
    Fetch stock data from multiple sources with fallback support
    """
    errors = []
    
    # Method 1: Try Yahoo Finance first (fastest and always available)
    try:
        # Add small delay to avoid rate limits
        await asyncio.sleep(0.1)
        
        # Create ticker with session to avoid cache issues
        session = requests.Session()
        ticker = yf.Ticker(symbol, session=session)
        
        # Try to get data with error handling
        try:
            info = ticker.info
        except Exception:
            info = {}
            
        try:
            hist = ticker.history(period=period)
        except Exception:
            hist = pd.DataFrame()
        
        if hist is not None and not hist.empty and len(hist) > 0:
            current_price = float(hist['Close'].iloc[-1])
            previous_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'previous_close': previous_close,
                'history': hist,
                'info': info,
                'source': 'yahoo'
            }
        else:
            # Try alternative periods if the requested period fails
            for alt_period in ['5d', '1mo', '3mo', '1d']:
                try:
                    hist = ticker.history(period=alt_period)
                    if hist is not None and not hist.empty and len(hist) > 0:
                        current_price = float(hist['Close'].iloc[-1])
                        previous_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
                        
                        return {
                            'symbol': symbol,
                            'current_price': current_price,
                            'previous_close': previous_close,
                            'history': hist,
                            'info': info,
                            'source': 'yahoo'
                        }
                except Exception:
                    continue
            
    except Exception as e:
        errors.append(f"Yahoo Finance: {str(e)}")
    
    # Method 2: Try Twelve Data API (if available)
    if td_client:
        try:
            # Get current price using time_series with 1 day interval
            ts = td_client.time_series(symbol=symbol, interval="1day", outputsize=2)
            df = ts.as_pandas()
            
            if df is not None and not df.empty and 'close' in df.columns:
                current_price = float(df['close'].iloc[0])  # Most recent close
                previous_close = float(df['close'].iloc[1]) if len(df) > 1 else current_price
                
                return {
                    'symbol': symbol,
                    'current_price': current_price,
                    'previous_close': previous_close,
                    'history': df,
                    'info': {'close': current_price, 'previous_close': previous_close},
                    'source': 'twelvedata'
                }
        except Exception as e:
            errors.append(f"Twelve Data: {str(e)}")
    
    # Method 3: Try Alpha Vantage API
    try:
        alpha_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_KEY}"
        async with aiohttp.ClientSession() as session:
            async with session.get(alpha_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'Global Quote' in data and '05. price' in data['Global Quote']:
                        quote = data['Global Quote']
                        return {
                            'symbol': symbol,
                            'current_price': float(quote['05. price']),
                            'previous_close': float(quote['08. previous close']),
                            'history': None,
                            'info': quote,
                            'source': 'alphavantage'
                        }
    except Exception as e:
        errors.append(f"Alpha Vantage: {str(e)}")
    
    # Fallback to mock data with realistic values
    logger.warning(f"All APIs failed for {symbol}, using mock data. Errors: {'; '.join(errors)}")
    return generate_mock_stock_data(symbol)

def generate_mock_stock_data(symbol: str):
    """Generate realistic mock stock data"""
    base_prices = {
        'AAPL': 196.45, 'GOOGL': 174.67, 'MSFT': 474.96, 'AMZN': 212.1,
        'TSLA': 325.31, 'META': 682.87, 'NVDA': 141.97, 'NFLX': 1212.15,
        'AMD': 180.50, 'INTC': 20.14, 'CRM': 258.40, 'ORCL': 185.30,
        'V': 352.85, 'JPM': 245.60, 'JNJ': 155.20, 'PG': 165.80
    }
    
    base_price = base_prices.get(symbol, random.uniform(50, 500))
    current_price = base_price * (0.98 + random.random() * 0.04)
    previous_close = base_price * (0.97 + random.random() * 0.06)
    
    return {
        'symbol': symbol,
        'current_price': round(current_price, 2),
        'previous_close': round(previous_close, 2),
        'history': None,
        'info': {'longName': f'{symbol} Corporation', 'symbol': symbol},
        'source': 'mock'
    }

async def fetch_crypto_data_multiple_sources(symbol: str, currency: str = "usd"):
    """Fetch crypto data from multiple sources with fallback support"""
    errors = []
    
    # Method 1: Try CoinGecko API (primary)
    if coingecko_client:
        try:
            # Get current price
            price_data = coingecko_client.get_price(ids=symbol, vs_currencies=currency, include_24hr_change=True)
            
            if symbol in price_data:
                current_price = price_data[symbol][currency]
                change_24h = price_data[symbol].get(f'{currency}_24h_change', 0)
                previous_close = current_price / (1 + change_24h / 100) if change_24h != 0 else current_price
                
                return {
                    'symbol': symbol,
                    'current_price': current_price,
                    'previous_close': previous_close,
                    'change_24h': change_24h,
                    'currency': currency,
                    'source': 'coingecko'
                }
        except Exception as e:
            errors.append(f"CoinGecko: {str(e)}")
    
    # Fallback to mock data
    logger.warning(f"All APIs failed for {symbol}, using mock data. Errors: {'; '.join(errors)}")
    return generate_mock_crypto_data(symbol)

def generate_mock_crypto_data(symbol: str):
    """Generate realistic mock crypto data"""
    base_prices = {
        'bitcoin': 105000, 'ethereum': 2540, 'cardano': 0.637,
        'polygon': 0.85, 'solana': 145, 'binancecoin': 650
    }
    
    base_price = base_prices.get(symbol, random.uniform(0.1, 100))
    current_price = base_price * (0.95 + random.random() * 0.1)
    change_24h = random.uniform(-5, 5)
    previous_close = current_price / (1 + change_24h / 100)
    
    return {
        'symbol': symbol,
        'current_price': round(current_price, 6),
        'previous_close': round(previous_close, 6),
        'change_24h': round(change_24h, 2),
        'currency': 'usd',
        'source': 'mock'
    }

def get_cached_data(cache_key: str, max_age_minutes: int = 15):
    """Get cached data if it exists and is not expired"""
    if cache_key in cache and cache_key in last_update_time:
        age = (datetime.now(timezone.utc) - last_update_time[cache_key]).total_seconds() / 60
        if age < max_age_minutes:
            return cache[cache_key]
    return None

# Background data update functions
async def update_stock_cache():
    """Update cache for tracked stock symbols"""
    logger.info("Starting background stock data update...")
    
    for symbol in TRACKED_SYMBOLS[:8]:  # Only stock symbols
        try:
            data = await fetch_stock_data_multiple_sources(symbol)
            cache[f"stock_{symbol}"] = data
            last_update_time[f"stock_{symbol}"] = datetime.now(timezone.utc)
            logger.info(f"Updated stock data for {symbol}: ${data['current_price']}")
            
            # Small delay to respect rate limits
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"Failed to update {symbol}: {str(e)}")
    
    logger.info("Stock data update completed")

async def update_crypto_cache():
    """Update cache for tracked crypto symbols"""
    logger.info("Starting background crypto data update...")
    
    for symbol in TRACKED_SYMBOLS[8:]:  # Only crypto symbols
        try:
            data = await fetch_crypto_data_multiple_sources(symbol)
            cache[f"crypto_{symbol}"] = data
            last_update_time[f"crypto_{symbol}"] = datetime.now(timezone.utc)
            logger.info(f"Updated crypto data for {symbol}: ${data['current_price']}")
            
            # Small delay to respect rate limits
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Failed to update {symbol}: {str(e)}")
    
    logger.info("Crypto data update completed")

async def update_market_overview_cache():
    """Update market overview data with real index values"""
    try:
        logger.info("Fetching fresh market overview data")
        market_overview_data = {}
        
        # Try to get real index data from Yahoo Finance
        index_symbols = {
            '^GSPC': 'S&P 500',
            '^DJI': 'Dow Jones', 
            '^IXIC': 'NASDAQ Composite',
            '^RUT': 'Russell 2000'
        }
        
        for symbol, name in index_symbols.items():
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="2d")
                if not data.empty and len(data) >= 2:
                    current_price = data['Close'].iloc[-1]
                    previous_price = data['Close'].iloc[-2]
                    change = current_price - previous_price
                    change_percent = (change / previous_price) * 100
                    
                    logger.info(f"Yahoo Finance {name} data: ${current_price:.2f}")
                    
                    market_overview_data[symbol] = {
                        'name': name,
                        'price': round(float(current_price), 2),
                        'change': round(float(change), 2),
                        'change_percent': round(float(change_percent), 2),
                        'source': 'yahoo_finance'
                    }
                else:
                    # Generate fallback data
                    base_prices = {'^GSPC': 5976.97, '^DJI': 42197.79, '^IXIC': 19406.83, '^RUT': 2100.51}
                    base_price = base_prices.get(symbol, 1000)
                    current_price = base_price * (0.99 + random.random() * 0.02)
                    change_percent = random.uniform(-2, 2)
                    change = current_price * (change_percent / 100)
                    
                    logger.info(f"Generated {name} data: ${current_price:.2f}")
                    
                    market_overview_data[symbol] = {
                        'name': name,
                        'price': round(current_price, 2),
                        'change': round(change, 2),
                        'change_percent': round(change_percent, 2),
                        'source': 'generated'
                    }
            except Exception as e:
                logger.warning(f"Failed to fetch {name} data: {str(e)}")
                # Generate fallback data
                base_prices = {'^GSPC': 5976.97, '^DJI': 42197.79, '^IXIC': 19406.83, '^RUT': 2100.51}
                base_price = base_prices.get(symbol, 1000)
                current_price = base_price * (0.99 + random.random() * 0.02)
                change_percent = random.uniform(-2, 2)
                change = current_price * (change_percent / 100)
                
                logger.info(f"Generated {name} data: ${current_price:.2f}")
                
                market_overview_data[symbol] = {
                    'name': name,
                    'price': round(current_price, 2),
                    'change': round(change, 2),
                    'change_percent': round(change_percent, 2),
                    'source': 'generated'
                }
        
        # Cache the market overview data
        cache['market_overview'] = market_overview_data
        last_update_time['market_overview'] = datetime.now(timezone.utc)
        logger.info("Market overview updated")
        
    except Exception as e:
        logger.error(f"Error updating market overview: {str(e)}")

def background_data_updater():
    """Background task to update data every 13 minutes"""
    async def update_loop():
        while True:
            try:
                logger.info("🔄 Starting 13-minute data refresh cycle...")
                await update_stock_cache()
                await update_crypto_cache()
                await update_market_overview_cache()
                logger.info("✅ Data refresh completed. Next update in 13 minutes.")
                await asyncio.sleep(UPDATE_INTERVAL)
            except Exception as e:
                logger.error(f"Background update error: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    asyncio.create_task(update_loop())

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("🚀 Starting Financial Analytics Hub...")
    logger.info("📊 Initializing 13-minute auto-update system...")
    
    # Start background data updater
    background_data_updater()
    logger.info("✅ Background data updater started")
    
    # Initial data update
    logger.info("🔄 First data update will begin immediately")

@app.get("/")
async def root():
    """Root endpoint with system status"""
    return {
        "message": "Financial Analytics Hub API v2.1.0",
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "market_overview": "/api/market/overview",
            "trending_stocks": "/api/stocks/trending",
            "portfolio_analysis": "/api/portfolio/analyze",
            "risk_analysis": "/api/portfolio/risk-analysis"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.post("/api/portfolio/risk-analysis")
async def portfolio_risk_analysis(request: RiskAnalysisRequest):
    """Enhanced portfolio risk analysis with comprehensive metrics"""
    try:
        # Handle both legacy (symbols) and new (portfolio) request formats
        if request.portfolio:
            # New format: portfolio with holdings
            symbols = [holding['symbol'] for holding in request.portfolio]
            holdings = {holding['symbol']: holding for holding in request.portfolio}
        elif request.symbols:
            # Legacy format: just symbols
            symbols = request.symbols
            holdings = {}
        else:
            raise HTTPException(status_code=400, detail="Either 'symbols' or 'portfolio' must be provided")
        
        if not symbols:
            raise HTTPException(status_code=400, detail="No symbols provided")
        
        # Fetch stock data for all symbols
        portfolio_data = []
        portfolio_values = []
        
        for symbol in symbols:
            try:
                # Get stock data
                stock_data = await fetch_stock_data_multiple_sources(symbol, request.period or "1y")
                
                if stock_data and stock_data.get('history') is not None:
                    hist = stock_data['history']
                    if not hist.empty:
                        returns = hist['Close'].pct_change().dropna()
                        portfolio_data.append(returns)
                        current_price = stock_data['current_price']
                        
                        # Calculate position value if portfolio details provided
                        if symbol in holdings:
                            quantity = holdings[symbol].get('quantity', 0)
                            portfolio_values.append(current_price * quantity)
                        else:
                            portfolio_values.append(current_price)  # Assume 1 share
                            
            except Exception as e:
                logger.warning(f"Failed to fetch data for {symbol}: {str(e)}")
                continue
        
        if not portfolio_data:
            raise HTTPException(status_code=404, detail="No valid data found for symbols")
        
        # Combine returns into DataFrame
        valid_symbols = symbols[:len(portfolio_data)]
        returns_df = pd.concat(portfolio_data, axis=1, keys=valid_symbols)
        
        # Calculate portfolio weights
        total_value = sum(portfolio_values)
        weights = [value / total_value for value in portfolio_values] if total_value > 0 else [1/len(portfolio_values)] * len(portfolio_values)
        
        # Calculate weighted portfolio returns
        portfolio_returns = (returns_df * weights).sum(axis=1)
        
        # Calculate Value at Risk (VaR)
        confidence_level = request.confidence_level or 0.95
        var_percentile = (1 - confidence_level) * 100
        var_value = np.percentile(portfolio_returns, var_percentile)
        
        # Portfolio metrics
        annual_return = portfolio_returns.mean() * 252
        annual_volatility = portfolio_returns.std() * np.sqrt(252)
        
        # Maximum Drawdown
        cumulative_returns = (1 + portfolio_returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = drawdowns.min()
        
        # Sharpe Ratio (assuming 2% risk-free rate)
        risk_free_rate = 0.02
        sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility if annual_volatility > 0 else 0
        
        # Beta calculation (vs S&P 500)
        try:
            sp500 = yf.Ticker("^GSPC")
            sp500_hist = sp500.history(period=request.period or "1y")
            if not sp500_hist.empty:
                sp500_returns = sp500_hist['Close'].pct_change().dropna()
                aligned_data = portfolio_returns.align(sp500_returns, join='inner')
                if len(aligned_data[0]) > 10:
                    beta = np.cov(aligned_data[0], aligned_data[1])[0][1] / np.var(aligned_data[1])
                else:
                    beta = 1.0
            else:
                beta = 1.0
        except:
            beta = 1.0
        
        # Risk level assessment
        if annual_volatility > 0.25:
            risk_level = "HIGH"
        elif annual_volatility > 0.15:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Generate recommendations
        recommendations = []
        if annual_volatility > 0.3:
            recommendations.append("Consider reducing position sizes to lower portfolio volatility")
        if max_drawdown < -0.2:
            recommendations.append("Portfolio experienced significant drawdowns - consider diversification")
        if sharpe_ratio < 0.5:
            recommendations.append("Risk-adjusted returns are low - review asset allocation")
        if beta > 1.5:
            recommendations.append("Portfolio is highly sensitive to market movements")
        
        # Calculate portfolio value
        total_portfolio_value = sum(portfolio_values) if portfolio_values else 100000  # Default $100k
        
        # VaR in dollar terms
        var_dollar = var_value * total_portfolio_value
        
        return {
            "value_at_risk": {
                "daily_var_95": round(var_dollar, 2) if confidence_level == 0.95 else round(np.percentile(portfolio_returns, 5) * total_portfolio_value, 2),
                "daily_var_99": round(np.percentile(portfolio_returns, 1) * total_portfolio_value, 2),
                "monthly_var_95": round(var_dollar * np.sqrt(21), 2),
                "monthly_var_99": round(np.percentile(portfolio_returns, 1) * total_portfolio_value * np.sqrt(21), 2)
            },
            "portfolio_metrics": {
                "total_value": round(total_portfolio_value, 2),
                "volatility": round(annual_volatility, 4),
                "sharpe_ratio": round(sharpe_ratio, 3),
                "max_drawdown": round(max_drawdown, 4),
                "beta": round(beta, 3)
            },
            "risk_assessment": {
                "risk_level": risk_level,
                "recommendations": recommendations,
                "stress_test_results": {
                    "market_crash_scenario": round(var_dollar * 3, 2),  # 3x VaR for stress test
                    "interest_rate_shock": round(var_dollar * 1.5, 2),
                    "currency_crisis": round(var_dollar * 2, 2)
                }
            },
            "symbols": valid_symbols,
            "confidence_level": confidence_level,
            "period": request.period or "1y",
            "time_horizon": request.time_horizon or "daily",
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Risk analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}")

@app.get("/api/market/overview")
async def get_market_overview():
    """Get market overview with major indices"""
    try:
        # Check cache first
        cached_data = get_cached_data("market_overview", max_age_minutes=5)
        
        if cached_data:
            logger.info("Using cached market overview data")
            return {
                "status": "success",
                "source": "cache",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "indices": cached_data
            }
        
        # If no cached data, trigger update
        await update_market_overview_cache()
        
        # Get the updated data
        market_data = cache.get('market_overview', {})
        
        return {
            "status": "success",
            "source": "fresh",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "indices": market_data
        }
        
    except Exception as e:
        logger.error(f"Market overview error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch market overview: {str(e)}")

@app.get("/api/stocks/trending")
async def get_trending_stocks():
    """Get trending stocks with timeout protection"""
    try:
        # Try to get cached trending stocks first
        cached_trending = get_cached_data("trending_stocks", max_age_minutes=10)
        
        if cached_trending:
            logger.info("Using cached trending stocks data")
            return cached_trending
        
        logger.info("Fetching fresh trending stocks data")
        
        # Fallback method with timeout protection
        trending_symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX"]
        results = []
        
        try:
            # 2-second timeout for fallback method
            async def fetch_fallback_data():
                # Fetch stocks with limited parallelism to avoid timeouts
                batch_size = 4  # Process 4 at a time instead of all 8
                results = []
                for i in range(0, len(trending_symbols), batch_size):
                    batch = trending_symbols[i:i + batch_size]
                    tasks = [fetch_stock_data_multiple_sources(symbol, "1d") for symbol in batch]
                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for j, data in enumerate(batch_results):
                        if isinstance(data, Exception) or not data:
                            continue
                            
                        symbol = batch[j]
                        current_price = data['current_price']
                        prev_close = data['previous_close']
                        change_percent = ((current_price - prev_close) / prev_close) * 100
                        
                        info = data.get('info', {})
                        
                        results.append({
                            "symbol": symbol,
                            "name": info.get("shortName", info.get("longName", f"{symbol} Corporation")),
                            "price": round(current_price, 2),
                            "change_percent": round(change_percent, 2),
                            "volume": random.randint(1000000, 50000000),
                            "data_source": data['source']
                        })
                return results
            
            results = await asyncio.wait_for(fetch_fallback_data(), timeout=2.0)
        
        except asyncio.TimeoutError:
            logger.warning("Fallback method timeout, using cached/mock data")
            # Generate quick mock data as final fallback
            stock_names = {
                'AAPL': 'Apple Inc.', 'GOOGL': 'Alphabet Inc.', 'MSFT': 'Microsoft Corporation',
                'AMZN': 'Amazon.com Inc.', 'TSLA': 'Tesla Inc.', 'META': 'Meta Platforms Inc.',
                'NVDA': 'NVIDIA Corporation', 'NFLX': 'Netflix Inc.'
            }
            
            for symbol in trending_symbols:
                results.append({
                    "symbol": symbol,
                    "name": stock_names.get(symbol, f"{symbol} Corporation"),
                    "price": round(random.uniform(100, 500), 2),
                    "change_percent": round(random.uniform(-3, 3), 2),
                    "volume": random.randint(10000000, 100000000),
                    "data_source": "timeout_fallback"
                })
        
        result = {
            "trending_stocks": results,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        # Cache the result
        cache["trending_stocks"] = result
        last_update_time["trending_stocks"] = datetime.now(timezone.utc)
        
        return result
        
    except Exception as e:
        logger.error(f"Trending stocks error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch trending stocks: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)