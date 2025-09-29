"""
Crypto Analytics Hub Backend with OpenRouter AI Integration
==========================================================

A comprehensive FastAPI backend focused on crypto analytics and market analysis
with OpenRouter AI for intelligent crypto insights.

Features:
- Crypto market data analysis
- AI-powered crypto recommendations
- Market sentiment analysis
- Real-time crypto signals
- Technical analysis for crypto
- Risk assessment for crypto portfolios
"""

from fastapi import FastAPI, HTTPException, Depends, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timedelta
import sys
import os
import asyncio

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import local modules
try:
    from config import (
        API_HOST, API_PORT, DEBUG, OPENROUTER_CONFIG,
        SECURITY_CONFIG
    )
except ImportError:
    # Fallback configuration if config module is not available
    API_HOST = "0.0.0.0"
    API_PORT = 8001
    DEBUG = True
    OPENROUTER_CONFIG = {"api_key": ""}
    SECURITY_CONFIG = {"allowed_origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}

# Import OpenRouter AI
try:
    from openrouter_ai import FinancialAI, AIModel
    AI_AVAILABLE = True
except ImportError as e:
    print(f"OpenRouter AI not available: {e}")
    AI_AVAILABLE = False

# Import crypto endpoints
try:
    from crypto_endpoints import crypto_provider
    CRYPTO_AVAILABLE = True
except ImportError as e:
    print(f"Crypto endpoints not available: {e}")
    CRYPTO_AVAILABLE = False

# Import stock data service
try:
    from stock_data_service import get_stock_quote, get_stock_list, screen_stocks_endpoint
    STOCK_AVAILABLE = True
except ImportError as e:
    print(f"Stock data service not available: {e}")
    STOCK_AVAILABLE = False

# Import NSE scraper
try:
    from nse_scraper import get_nse_stocks_data, get_nse_stock_quote
    NSE_AVAILABLE = True
except ImportError as e:
    print(f"NSE scraper not available: {e}")
    NSE_AVAILABLE = False

# Import multi-provider data service
try:
    from multi_data_provider import multi_provider
    MULTI_PROVIDER_AVAILABLE = True
except ImportError as e:
    print(f"Multi-provider data service not available: {e}")
    MULTI_PROVIDER_AVAILABLE = False

# Import helper for mock data when AI_AVAILABLE is enabled but real data unavailable
try:
    # The `create_mock_crypto_data` utility lives in the legacy `main_crypto` module.
    # Importing here ensures AI endpoints work even when running this standalone
    # `main.py` without circular import issues.
    from main_crypto import create_mock_crypto_data  # type: ignore
except ImportError:
    # Fallback stub (should rarely be used) – keeps runtime safe in edge builds
    def create_mock_crypto_data(data_type: str, symbol: str | None = None):  # type: ignore
        """Return minimal mock payload if main_crypto is unavailable."""
        return {
            "symbol": symbol or "bitcoin",
            "current_price": 0,
            "price_change_percentage_24h": 0,
        }

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global cache for Fear & Greed Index (valid for 50 minutes)
fear_greed_cache: Dict[str, Any] = {
    "data": None,
    "timestamp": None,
}

async def get_fear_greed_from_cache_or_fetch() -> Dict[str, Any]:
    """Return Fear & Greed Index, fetching only if cache is older than 50 minutes."""
    now = datetime.now()

    # If we have fresh cached data (≤ 50 minutes old) return it directly
    if fear_greed_cache["data"] and fear_greed_cache["timestamp"]:
        age = now - fear_greed_cache["timestamp"]
        if age < timedelta(minutes=50):
            return fear_greed_cache["data"]

    # Otherwise fetch fresh data
    try:
        import requests
        resp = requests.get("https://api.alternative.me/fng/", timeout=10)
        if resp.status_code == 200:
            payload = resp.json()
            if payload.get("data"):
                fg_raw = payload["data"][0]
                fear_greed_data = {
                    "value": int(fg_raw.get("value")),
                    "interpretation": fg_raw.get("value_classification"),
                    "last_updated": datetime.fromtimestamp(int(fg_raw.get("timestamp"))).isoformat(),
                }
                # Update cache
                fear_greed_cache["data"] = fear_greed_data
                fear_greed_cache["timestamp"] = now
                return fear_greed_data
    except Exception as e:
        logger.error(f"Error fetching Fear & Greed Index: {e}")

    # Fallback mock data when API call fails
    fallback_data = {
        "value": 72,
        "interpretation": "Greed",
        "last_updated": now.isoformat(),
    }
    fear_greed_cache["data"] = fallback_data
    fear_greed_cache["timestamp"] = now
    return fallback_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup services"""
    # Startup
    logger.info("🚀 Crypto Analytics Hub - Engine Starting...")
    logger.info(f"   🔧 Crypto Provider: {'✅ Operational' if CRYPTO_AVAILABLE else '❌ Offline'}")
    logger.info(f"   🤖 AI Services: {'✅ Operational' if AI_AVAILABLE else '❌ Offline'}")
    logger.info("🌟 Engine Running Like a Well-Oiled Machine! 🌟")
    
    yield
    
    # Shutdown
    logger.info("🛑 Crypto Analytics Hub shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Financial Analytics Hub with AI",
    description="Comprehensive financial analysis platform with crypto, stocks, and AI integration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware with expanded origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],
    expose_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Pydantic models
class CryptoSymbol(BaseModel):
    symbol: str = Field(..., description="Crypto symbol (e.g., bitcoin)")

class CryptoAnalysisRequest(BaseModel):
    symbol: str = Field(..., description="Crypto symbol to analyze")
    include_ai: bool = Field(True, description="Include AI analysis")
    ai_model: Optional[str] = Field(None, description="Specific AI model to use")

class MarketSentimentRequest(BaseModel):
    symbols: Optional[List[str]] = Field(None, description="Specific symbols to analyze")
    include_news: bool = Field(True, description="Include news sentiment")
    timeframe: str = Field("1d", description="Timeframe for analysis")

class AIQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query about crypto markets")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context data")
    model: Optional[str] = Field(None, description="Specific AI model to use")
    stream: bool = Field(False, description="Stream response")

class AIChatRequest(BaseModel):
    message: str = Field(..., description="User message for AI chat")

# Helper functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Simple token validation - replace with proper auth in production"""
    if not credentials:
        return None
    return {"user_id": "demo_user"}

# Mock data removed - using only real API data

# ======================
# BASIC ENDPOINTS
# ======================

@app.get("/")
async def root():
    """Root endpoint with crypto platform information"""
    return {
        "message": "🚀 Crypto Analytics Hub with AI",
        "description": "Advanced crypto analysis platform with OpenRouter AI integration",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Real-time crypto data",
            "AI-powered crypto analysis",
            "Market sentiment analysis",
            "Technical analysis for crypto",
            "OpenRouter AI integration"
        ],
        "endpoints": {
            "health": "/health",
            "crypto_data": "/api/crypto/{symbol}",
            "top_crypto": "/api/top100/crypto",
            "trending_crypto": "/api/crypto/trending",
            "fear_greed": "/api/market/fear-greed",
            "market_overview": "/api/market/overview",
            "ai_chat": "/api/ai/chat",
            "ai_analysis": "/api/ai/analyze/crypto"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "crypto_provider": CRYPTO_AVAILABLE,
            "ai_service": AI_AVAILABLE
        }
    }

@app.get("/api/status")
async def api_status():
    """Detailed API status"""
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "services": {
            "crypto_data": "available" if CRYPTO_AVAILABLE else "unavailable",
            "ai_analysis": "available" if AI_AVAILABLE else "unavailable"
        },
        "features": ["crypto_analysis", "ai_chat", "market_sentiment"],
        "environment": "development" if DEBUG else "production"
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint for crypto server compatibility"""
    if CRYPTO_AVAILABLE:
        return await crypto_provider.get_server_status()
    else:
        return {
            "status": "success",
            "message": "Crypto analytics server is running!",
            "timestamp": datetime.now().isoformat(),
            "available_apis": ["mock_data"]
        }

# ======================
# CRYPTO ENDPOINTS
# ======================

@app.get("/api/crypto/trending")
async def get_trending_crypto():
    """Get trending cryptocurrencies using top 7 from top100 data."""
    try:
        logger.info("Fetching trending crypto data")
        
        if not CRYPTO_AVAILABLE:
            raise HTTPException(status_code=503, detail="Crypto providers not available")
        
        # Direct approach - get top100 and return first 7 for trending
        import requests
        import json
        from datetime import datetime
        
        # Try to get fresh data from CoinGecko top100
        try:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': '7',  # Only get 7 for trending
                'page': '1',
                'sparkline': 'false',
                'price_change_percentage': '24h'
            }
            
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                coingecko_data = resp.json()
                
                # Transform to expected format
                trending_list = []
                for crypto in coingecko_data:
                    trending_crypto = {
                        "id": crypto.get("id"),
                        "symbol": crypto.get("symbol"),
                        "name": crypto.get("name"),
                        "current_price": crypto.get("current_price"),
                        "market_cap": crypto.get("market_cap"),
                        "market_cap_rank": crypto.get("market_cap_rank"),
                        "volume_24h": crypto.get("total_volume", 0),
                        "price_change_percent_24h": crypto.get("price_change_percentage_24h", 0),
                        "price_change_percent_1h": crypto.get("price_change_percentage_1h"),
                        "price_change_percent_7d": crypto.get("price_change_percentage_7d"),
                        "asset_type": "cryptocurrency"
                    }
                    trending_list.append(trending_crypto)
                
                logger.info(f"✅ Retrieved {len(trending_list)} trending cryptos directly from CoinGecko")
                return {
                    "data": trending_list,
                    "count": len(trending_list),
                    "timestamp": datetime.now().isoformat(),
                    "provider_sources": ["coingecko_direct"]
                }
            else:
                logger.warning(f"CoinGecko trending failed: {resp.status_code}")
        except Exception as e:
            logger.warning(f"Direct CoinGecko call failed: {e}")
        
        # Fallback: Try to get from existing top100 endpoint
        try:
            top100_resp = await crypto_provider.get_top100_crypto()
            
            if top100_resp and "data" in top100_resp and len(top100_resp["data"]) >= 7:
                trending_list = top100_resp["data"][:7]
                
                logger.info(f"📊 Using top 7 from cached top100 data for trending")
                return {
                    "data": trending_list,
                    "count": len(trending_list),
                    "timestamp": top100_resp.get("timestamp", datetime.now().isoformat()),
                    "provider_sources": ["top100_fallback"]
                }
        except Exception as e:
            logger.warning(f"Top100 fallback failed: {e}")
        
        # No static fallback - fail with proper error message
        raise HTTPException(status_code=503, detail="Trending data temporarily unavailable - all providers are rate limited")
    
    except Exception as e:
        logger.error(f"Error fetching trending crypto: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching trending crypto: {str(e)}")

@app.get("/api/crypto/{symbol}")
async def get_crypto_data(symbol: str):
    """Get real-time crypto data with multi-provider failover."""
    try:
        logger.info(f"Fetching crypto data for symbol: {symbol}")
        
        if not CRYPTO_AVAILABLE:
            raise HTTPException(status_code=503, detail="Crypto providers not available")
        
        # Use orchestrator for real data - no mock fallback
        provider_response = await crypto_provider.get_crypto_data(symbol)
        
        if not provider_response:
            raise HTTPException(status_code=404, detail=f"No data available for symbol: {symbol}")
        
        # The upstream provider returns a wrapper with its own `status` and `data` keys.
        # We expose the inner `data` object directly under `data` so that the
        # frontend hooks (useCryptoData) receive the exact shape they expect
        # (id, symbol, current_price, price_change_percentage_24h, etc.).
        crypto_payload = provider_response.get("data", provider_response)

        return {
            "data": crypto_payload,
            "timestamp": provider_response.get("timestamp", datetime.now().isoformat()),
            "source": crypto_payload.get("source"),
        }
    
    except Exception as e:
        logger.error(f"Error fetching crypto data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching crypto data: {str(e)}")

@app.get("/api/crypto/{symbol}/history")
async def get_crypto_history(symbol: str, days: int = 30):
    """Get historical crypto data with multi-provider failover."""
    try:
        logger.info(f"Fetching crypto history for symbol: {symbol}, days: {days}")
        
        if not CRYPTO_AVAILABLE:
            raise HTTPException(status_code=503, detail="Crypto providers not available")
        
        # Use orchestrator for real historical data
        history_data = await crypto_provider.get_crypto_history(symbol, days)
        
        # Check if we have valid history data
        if not history_data:
            raise HTTPException(status_code=404, detail=f"No historical data available for symbol: {symbol}")
        
        # Handle both possible response formats
        history_list = None
        if isinstance(history_data.get("data"), dict) and "history" in history_data["data"]:
            # Format: {"data": {"history": [...], ...}, ...}
            history_list = history_data["data"]["history"]
        elif isinstance(history_data.get("history"), list):
            # Format: {"history": [...], ...}
            history_list = history_data["history"]
        
        if not history_list or not isinstance(history_list, list) or len(history_list) == 0:
            raise HTTPException(status_code=404, detail=f"No historical data available for symbol: {symbol}")

        # Return the provider's response directly, ensuring it has the history key at top level
        if "history" not in history_data:
            # If history is nested under data, move it to top level for frontend compatibility
            return {
                "history": history_list,
                "symbol": symbol.upper(),
                "days": days,
                "data_points": len(history_list),
                "timestamp": history_data.get("timestamp", datetime.now().isoformat()),
                "status": "success"
            }
        else:
            return history_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching crypto history for {symbol}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching crypto history: {str(e)}")

@app.get("/api/top100/crypto")
async def get_top100_crypto():
    """Get top 100 cryptocurrencies with real aggregated data."""
    try:
        logger.info("Fetching top 100 crypto data")
        
        if not CRYPTO_AVAILABLE:
            raise HTTPException(status_code=503, detail="Crypto providers not available")
        
        # Use orchestrator for real aggregated data
        top100_resp = await crypto_provider.get_top100_crypto()
        
        if not top100_resp:
            raise HTTPException(status_code=404, detail="No top 100 data available")
        
        # The crypto provider now returns the correct structure with "data" key
        return top100_resp
    
    except Exception as e:
        logger.error(f"Error fetching top 100 crypto: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching top 100 crypto: {str(e)}")

@app.get("/api/crypto/providers/status")
async def get_crypto_providers_status():
    """Get health status of all crypto providers."""
    try:
        logger.info("Fetching crypto providers status")
        
        provider_status = await crypto_provider.get_provider_status()
        
        return {
            "status": "success",
            "data": provider_status,
            "total_providers": len(provider_status.get("providers", [])),
            "healthy_providers": provider_status.get("healthy_count", 0),
            "last_updated": provider_status.get("timestamp")
        }
    
    except Exception as e:
        logger.error(f"Error fetching provider status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching provider status: {str(e)}")

@app.get("/api/crypto/providers/usage")
async def get_crypto_providers_usage():
    """Get API usage statistics and rate limit status."""
    try:
        logger.info("Fetching crypto providers usage")
        
        usage_stats = await crypto_provider.get_provider_usage()
        
        return {
            "status": "success",
            "data": usage_stats,
            "rate_limits": usage_stats.get("rate_limits", {}),
            "usage_summary": usage_stats.get("summary", {})
        }
    
    except Exception as e:
        logger.error(f"Error fetching provider usage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching provider usage: {str(e)}")

@app.post("/api/crypto/batch")
async def get_crypto_batch(request: Request):
    """Efficient bulk crypto data fetching."""
    try:
        body = await request.json()
        symbols = body.get("symbols", [])
        
        if not symbols:
            raise HTTPException(status_code=400, detail="No symbols provided")
        
        if len(symbols) > 50:  # Batch size limit
            raise HTTPException(status_code=400, detail="Too many symbols requested (max 50)")
        
        logger.info(f"Fetching batch crypto data for {len(symbols)} symbols")
        
        batch_data = await crypto_provider.get_crypto_batch(symbols)
        
        return {
            "status": "success",
            "data": batch_data,
            "requested_symbols": len(symbols),
            "successful_fetches": len([d for d in batch_data.values() if d is not None])
        }
    
    except Exception as e:
        logger.error(f"Error fetching batch crypto data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching batch crypto data: {str(e)}")

# ======================
# MARKET SENTIMENT ENDPOINTS
# ======================

@app.get("/api/market/fear-greed")
async def get_fear_greed_index():
    """Get Fear & Greed Index for crypto market sentiment (cached for 50 minutes).

    Response schema:
    {
        "value": int,                 # Index value (0-100)
        "interpretation": str,        # Text interpretation ("Fear", "Greed", etc.)
        "last_updated": ISO8601 str   # Timestamp of the underlying data
    }
    """
    try:
        return await get_fear_greed_from_cache_or_fetch()
    except Exception as e:
        logger.error(f"Error fetching fear & greed index: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching fear & greed index: {str(e)}")

@app.get("/api/market/overview")
async def get_market_overview():
    """Get comprehensive market overview with key metrics"""
    try:
        logger.info("Fetching global market stats from CoinGecko")

        import requests
        resp = requests.get("https://api.coingecko.com/api/v3/global", timeout=10)
        if resp.status_code == 200:
            g = resp.json().get("data", {})
            total_mc_usd = g.get("total_market_cap", {}).get("usd", 0)
            total_vol_usd = g.get("total_volume", {}).get("usd", 0)
            btc_dom = g.get("market_cap_percentage", {}).get("btc", 0)
            eth_dom = g.get("market_cap_percentage", {}).get("eth", 0)
            active_coins = g.get("active_cryptocurrencies", 0)
            market_cap_change_24h = g.get("market_cap_change_percentage_24h_usd", 0)
            # Calculate volume change as not provided; set None

            market_overview = {
                "total_market_cap": total_mc_usd,
                "total_volume_24h": total_vol_usd,
                "bitcoin_dominance": btc_dom,
                "ethereum_dominance": eth_dom,
                "active_cryptocurrencies": active_coins,
                "market_cap_change_24h": market_cap_change_24h,
                "volume_change_24h": None,
                "timestamp": datetime.now().isoformat()
            }
            return {
                "status": "success",
                "data": market_overview,
                "timestamp": datetime.now().isoformat()
            }

        logger.warning("CoinGecko global API failed – returning fallback demo values")
        return {
            "status": "fallback",
            "data": {
                "total_market_cap": 2100000000000,
                "total_volume_24h": 89200000000,
                "bitcoin_dominance": 52.3,
                "ethereum_dominance": 17.8,
                "active_cryptocurrencies": 12847,
                "market_cap_change_24h": 3.45,
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching market overview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching market overview: {str(e)}")

# ======================
# AI ENDPOINTS
# ======================

@app.post("/api/ai/analyze/crypto")
async def ai_analyze_crypto(request: CryptoAnalysisRequest):
    """AI-powered comprehensive crypto analysis"""
    if not AI_AVAILABLE:
        return {
            "symbol": request.symbol,
            "ai_analysis": {
                "content": f"Mock AI Analysis for {request.symbol}: This cryptocurrency shows strong technical indicators with RSI at 58.2 indicating healthy momentum. Market sentiment is bullish with increasing adoption metrics. Consider dollar-cost averaging for long-term positions. Confidence: 82%",
                "model_used": "mock_model",
                "confidence": 82.0,
                "tokens_used": 120,
                "cost_estimate": 0.0
            },
            "message": "AI service in demo mode. Configure OpenRouter API key to enable real AI analysis.",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        # Get crypto data
        crypto_data = create_mock_crypto_data("quote", request.symbol)
        
        if request.include_ai:
            # Use OpenRouter AI for analysis
            ai_model = AIModel(request.ai_model) if request.ai_model else AIModel.GPT_4O_MINI
            
            async with FinancialAI(OPENROUTER_CONFIG["api_key"]) as ai:
                # Adapt the stock analysis for crypto
                ai_response = await ai.analyze_stock(request.symbol, crypto_data, {}, ai_model)
                
                return {
                    "symbol": request.symbol,
                    "crypto_data": crypto_data,
                    "ai_analysis": {
                        "content": ai_response.content.replace("stock", "cryptocurrency").replace("Stock", "Crypto"),
                        "model_used": ai_response.model,
                        "confidence": ai_response.confidence,
                        "tokens_used": ai_response.tokens_used,
                        "cost_estimate": ai_response.cost_estimate
                    },
                    "timestamp": datetime.now().isoformat()
                }
        else:
            return {
                "symbol": request.symbol,
                "crypto_data": crypto_data,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error in AI crypto analysis: {e}")
        raise HTTPException(status_code=500, detail=f"AI analysis error: {str(e)}")

@app.post("/api/ai/chat")
async def ai_chat(request: AIChatRequest):
    """AI chat endpoint for crypto-focused conversations"""
    if not AI_AVAILABLE:
        # Enhanced fallback responses for crypto
        crypto_responses = [
            "I'm currently in demo mode! For real crypto insights, configure your OpenRouter API key. Meanwhile, Bitcoin is showing interesting patterns in the current market cycle.",
            "Demo mode active! I'd love to analyze crypto markets for you with real AI. Consider the volatility patterns in altcoins during this market phase.",
            "Running in demo mode! With proper AI integration, I can provide detailed crypto analysis including technical indicators and market sentiment.",
            "Demo response: The crypto market is showing mixed signals. Enable AI features for deeper analysis of specific cryptocurrencies and market trends."
        ]
        
        response_text = f"🤖 **Demo Mode Active**\n\n{crypto_responses[hash(request.message) % len(crypto_responses)]}\n\n💡 **Quick Crypto Insight**: {request.message.upper()} - The current market conditions suggest careful analysis of support and resistance levels before making investment decisions."
        
        return {
            "response": response_text,
            "model_used": "demo_mode",
            "tokens_used": len(response_text.split()),
            "timestamp": datetime.now().isoformat(),
            "is_demo": True
        }
    
    try:
        # Use OpenRouter AI for crypto-focused chat
        async with FinancialAI(OPENROUTER_CONFIG["api_key"]) as ai:
            # Create crypto-focused context
            crypto_context = "You are a crypto market analyst. Focus on cryptocurrency analysis, blockchain technology, and digital asset markets."
            enhanced_message = f"{crypto_context}\n\nUser question: {request.message}"
            
            ai_response = await ai.chat(enhanced_message, AIModel.GPT_4O_MINI)
            
            return {
                "response": ai_response.content,
                "model_used": ai_response.model,
                "confidence": ai_response.confidence,
                "tokens_used": ai_response.tokens_used,
                "cost_estimate": ai_response.cost_estimate,
                "timestamp": datetime.now().isoformat(),
                "is_demo": False
            }
            
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        return {
            "response": f"I encountered an error while processing your crypto question. Please try again. Error: {str(e)[:100]}",
            "model_used": "error_fallback",
            "timestamp": datetime.now().isoformat(),
            "is_demo": True
        }

@app.get("/api/ai/models")
async def get_available_ai_models():
    """Get available AI models for crypto analysis"""
    if not AI_AVAILABLE:
        return {
            "models": [],
            "message": "AI service unavailable - Configure OpenRouter API key",
            "demo_models": ["gpt-4o-mini", "claude-3-haiku", "gemini-flash"]
        }
    
    try:
        models = [
            {"id": "gpt-4o-mini", "name": "GPT-4O Mini", "provider": "OpenAI", "optimized_for": "crypto_analysis"},
            {"id": "claude-3-haiku", "name": "Claude 3 Haiku", "provider": "Anthropic", "optimized_for": "technical_analysis"},
            {"id": "gemini-flash", "name": "Gemini Flash", "provider": "Google", "optimized_for": "market_sentiment"}
        ]
        
        return {
            "models": models,
            "count": len(models),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching AI models: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching models: {str(e)}")

# ======================
# STOCK ENDPOINTS
# ======================

@app.get("/api/stock/{symbol}")
async def get_stock_data(symbol: str):
    """Get real-time stock data"""
    if not STOCK_AVAILABLE:
        raise HTTPException(status_code=503, detail="Stock data service not available")
    
    try:
        result = await get_stock_quote(symbol.upper())
        return result
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stocks/list")
async def get_stocks_list():
    """Get list of NSE stocks with real-time data"""
    if not STOCK_AVAILABLE:
        raise HTTPException(status_code=503, detail="Stock data service not available")
    
    try:
        result = await get_stock_list()
        return result
    except Exception as e:
        logger.error(f"Error fetching stocks list: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stocks/screen/{criteria}")
async def screen_stocks(criteria: str):
    """Screen stocks by criteria (breakouts, high_volume, rsi_oversold, rsi_overbought, gainers, losers, low_pe, momentum)"""
    if not STOCK_AVAILABLE:
        raise HTTPException(status_code=503, detail="Stock data service not available")
    
    try:
        result = await screen_stocks_endpoint(criteria)
        return result
    except Exception as e:
        logger.error(f"Error screening stocks with criteria {criteria}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ======================
# NSE SCRAPER ENDPOINTS
# ======================

@app.get("/api/nse/stocks")
async def get_nse_stocks():
    """Get NSE stock data using fake browser scraper"""
    try:
        if not NSE_AVAILABLE:
            raise HTTPException(status_code=503, detail="NSE scraper not available")
        
        result = get_nse_stocks_data()
        return result
        
    except Exception as e:
        logger.error(f"Error fetching NSE stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/nse/quote/{symbol}")
async def get_nse_stock_quote_endpoint(symbol: str):
    """Get NSE stock quote using fake browser scraper"""
    try:
        if not NSE_AVAILABLE:
            raise HTTPException(status_code=503, detail="NSE scraper not available")
        
        result = get_nse_stock_quote(symbol.upper())
        return result
        
    except Exception as e:
        logger.error(f"Error fetching NSE quote for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/nse/nifty50")
async def get_nifty50_stocks():
    """Get NIFTY 50 stocks from NSE"""
    try:
        if not NSE_AVAILABLE:
            raise HTTPException(status_code=503, detail="NSE scraper not available")
        
        result = get_nse_stocks_data()
        if result['success'] and 'data' in result and 'nifty50' in result['data']:
            return {
                "success": True,
                "data": result['data']['nifty50'],
                "count": len(result['data']['nifty50']),
                "timestamp": result['data']['timestamp']
            }
        else:
            return result
        
    except Exception as e:
        logger.error(f"Error fetching NIFTY 50 stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/nse/top-gainers")
async def get_nse_top_gainers():
    """Get top gaining stocks from NSE"""
    try:
        if not NSE_AVAILABLE:
            raise HTTPException(status_code=503, detail="NSE scraper not available")
        
        result = get_nse_stocks_data()
        if result['success'] and 'data' in result and 'top_gainers' in result['data']:
            return {
                "success": True,
                "data": result['data']['top_gainers'],
                "count": len(result['data']['top_gainers']),
                "timestamp": result['data']['timestamp']
            }
        else:
            return result
        
    except Exception as e:
        logger.error(f"Error fetching NSE top gainers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/nse/top-losers")
async def get_nse_top_losers():
    """Get top losing stocks from NSE"""
    try:
        if not NSE_AVAILABLE:
            raise HTTPException(status_code=503, detail="NSE scraper not available")
        
        result = get_nse_stocks_data()
        if result['success'] and 'data' in result and 'top_losers' in result['data']:
            return {
                "success": True,
                "data": result['data']['top_losers'],
                "count": len(result['data']['top_losers']),
                "timestamp": result['data']['timestamp']
            }
        else:
            return result
        
    except Exception as e:
        logger.error(f"Error fetching NSE top losers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/nse/indices")
async def get_nse_indices():
    """Get NSE market indices"""
    try:
        if not NSE_AVAILABLE:
            raise HTTPException(status_code=503, detail="NSE scraper not available")
        
        result = get_nse_stocks_data()
        if result['success'] and 'data' in result and 'indices' in result['data']:
            return {
                "success": True,
                "data": result['data']['indices'],
                "count": len(result['data']['indices']),
                "timestamp": result['data']['timestamp']
            }
        else:
            return result
        
    except Exception as e:
        logger.error(f"Error fetching NSE indices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ======================
# COMPREHENSIVE DATA ENDPOINTS
# ======================

@app.get("/api/data/stock/{symbol}")
async def get_comprehensive_stock_data(symbol: str):
    """Get comprehensive stock data from multiple providers"""
    try:
        if not MULTI_PROVIDER_AVAILABLE:
            raise HTTPException(status_code=503, detail="Multi-provider service not available")
        
        result = await multi_provider.get_stock_data(symbol)
        return result
        
    except Exception as e:
        logger.error(f"Error fetching comprehensive stock data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/stocks/top")
async def get_top_stocks_comprehensive(limit: int = Query(default=100, ge=1, le=500)):
    """Get top stocks from multiple providers"""
    try:
        if not MULTI_PROVIDER_AVAILABLE:
            raise HTTPException(status_code=503, detail="Multi-provider service not available")
        
        result = await multi_provider.get_top_stocks(limit)
        return result
        
    except Exception as e:
        logger.error(f"Error fetching top stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/crypto/top")
async def get_top_crypto_comprehensive(limit: int = Query(default=100, ge=1, le=500)):
    """Get top cryptocurrencies from multiple providers"""
    try:
        if not MULTI_PROVIDER_AVAILABLE:
            raise HTTPException(status_code=503, detail="Multi-provider service not available")
        
        result = await multi_provider.get_top_crypto(limit)
        return result
        
    except Exception as e:
        logger.error(f"Error fetching top crypto: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/crypto/{symbol}")
async def get_comprehensive_crypto_data(symbol: str):
    """Get comprehensive crypto data from multiple providers"""
    try:
        if not MULTI_PROVIDER_AVAILABLE:
            raise HTTPException(status_code=503, detail="Multi-provider service not available")
        
        result = await multi_provider.get_crypto_data(symbol)
        return result
        
    except Exception as e:
        logger.error(f"Error fetching comprehensive crypto data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/search")
async def search_all_symbols(
    q: str = Query(..., description="Search query"),
    limit: int = Query(default=20, ge=1, le=100, description="Number of results")
):
    """Search for stocks and crypto symbols across all providers"""
    try:
        if not MULTI_PROVIDER_AVAILABLE:
            raise HTTPException(status_code=503, detail="Multi-provider service not available")
        
        result = await multi_provider.search_symbols(q, limit)
        return result
        
    except Exception as e:
        logger.error(f"Error searching symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/market/overview")
async def get_comprehensive_market_overview():
    """Get comprehensive market overview with stocks and crypto"""
    try:
        if not MULTI_PROVIDER_AVAILABLE:
            raise HTTPException(status_code=503, detail="Multi-provider service not available")
        
        # Get top stocks and crypto
        stocks_task = multi_provider.get_top_stocks(10)
        crypto_task = multi_provider.get_top_crypto(10)
        
        stocks_result, crypto_result = await asyncio.gather(
            stocks_task, crypto_task, return_exceptions=True
        )
        
        # Handle exceptions
        stocks_data = stocks_result.get('data', []) if isinstance(stocks_result, dict) else []
        crypto_data = crypto_result.get('data', []) if isinstance(crypto_result, dict) else []
        
        return {
            "success": True,
            "data": {
                "stocks": stocks_data,
                "crypto": crypto_data,
                "summary": {
                    "total_stocks": len(stocks_data),
                    "total_crypto": len(crypto_data),
                    "top_stock": stocks_data[0] if stocks_data else None,
                    "top_crypto": crypto_data[0] if crypto_data else None
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching market overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ======================
# ERROR HANDLERS
# ======================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "timestamp": datetime.now().isoformat()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "timestamp": datetime.now().isoformat()}
    )

@app.get("/api/crypto/search")
async def search_cryptocurrencies(
    q: str = Query(..., description="Search query"),
    limit: int = Query(default=10, ge=1, le=50, description="Number of results")
):
    """Search cryptocurrencies by name or symbol."""
    try:
        if not q or not q.strip():
            raise HTTPException(status_code=400, detail="Search query cannot be empty")
            
        if not CRYPTO_AVAILABLE:
            raise HTTPException(status_code=503, detail="Crypto provider not available")
        
        # Simple search implementation using popular cryptos
        popular_cryptos = [
            {"id": "bitcoin", "symbol": "BTC", "name": "Bitcoin"},
            {"id": "ethereum", "symbol": "ETH", "name": "Ethereum"},
            {"id": "binancecoin", "symbol": "BNB", "name": "BNB"},
            {"id": "solana", "symbol": "SOL", "name": "Solana"},
            {"id": "ripple", "symbol": "XRP", "name": "XRP"},
            {"id": "dogecoin", "symbol": "DOGE", "name": "Dogecoin"},
            {"id": "cardano", "symbol": "ADA", "name": "Cardano"},
            {"id": "chainlink", "symbol": "LINK", "name": "Chainlink"},
            {"id": "polygon", "symbol": "MATIC", "name": "Polygon"},
            {"id": "avalanche-2", "symbol": "AVAX", "name": "Avalanche"}
        ]
        
        query_lower = q.lower().strip()
        results = []
        
        for crypto in popular_cryptos:
            if (query_lower in crypto["name"].lower() or 
                query_lower in crypto["symbol"].lower() or 
                query_lower in crypto["id"].lower()):
                results.append(crypto)
                if len(results) >= limit:
                    break
        
        return {
            "data": results,
            "query": q,
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in search_cryptocurrencies: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/crypto/symbol-map/{symbol}")
async def get_crypto_symbol_mapping(
    symbol: str
):
    """Get the correct crypto ID for a given symbol."""
    try:
        if not symbol or not symbol.strip():
            raise HTTPException(status_code=400, detail="Symbol parameter cannot be empty")
            
        if not CRYPTO_AVAILABLE:
            raise HTTPException(status_code=503, detail="Crypto provider not available")
        
        # Simple symbol mapping
        symbol_map = {
            "btc": "bitcoin",
            "eth": "ethereum", 
            "bnb": "binancecoin",
            "sol": "solana",
            "xrp": "ripple",
            "doge": "dogecoin",
            "ada": "cardano",
            "link": "chainlink",
            "matic": "polygon",
            "avax": "avalanche-2",
            "dot": "polkadot",
            "usdt": "tether",
            "usdc": "usd-coin"
        }
        
        coin_id = symbol_map.get(symbol.lower())
        
        if coin_id:
            return {
                "symbol": symbol.upper(),
                "coin_id": coin_id,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=404, 
                detail=f"No mapping found for symbol: {symbol.upper()}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_crypto_symbol_mapping: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Use Render's PORT environment variable, fallback to API_PORT
    port = int(os.getenv("PORT", API_PORT))
    host = "0.0.0.0"  # Always bind to 0.0.0.0 for Render
    
    print(f"🚀 Starting FastAPI server on {host}:{port}")
    print(f"📊 Environment: {'DEBUG' if DEBUG else 'PRODUCTION'}")
    print(f"🔧 Crypto Provider: {'✅ Available' if CRYPTO_AVAILABLE else '❌ Unavailable'}")
    print(f"🤖 AI Services: {'✅ Available' if AI_AVAILABLE else '❌ Unavailable'}")
    
    try:
        if DEBUG:
            uvicorn.run("main:app", host=host, port=port, reload=True, log_level="info")
        else:
            uvicorn.run(app, host=host, port=port, log_level="info")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1) 