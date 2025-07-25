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

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import asyncio
import logging
from datetime import datetime
import json
import traceback
import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import local modules
try:
    from config import (
        API_HOST, API_PORT, DEBUG, OPENROUTER_CONFIG, AI_FEATURES,
        SECURITY_CONFIG, RATE_LIMITS, CACHE_CONFIG
    )
except ImportError:
    # Fallback configuration if config module is not available
    API_HOST = "0.0.0.0"
    API_PORT = 8001
    DEBUG = True
    OPENROUTER_CONFIG = {"api_key": ""}
    AI_FEATURES = {"enable_ai_analysis": False}
    SECURITY_CONFIG = {"allowed_origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}
    RATE_LIMITS = {}
    CACHE_CONFIG = {}

# Import OpenRouter AI
try:
    from openrouter_ai import FinancialAI, AIModel, AIResponse
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Crypto Analytics Hub with AI",
    description="Comprehensive crypto analysis platform with OpenRouter AI integration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=SECURITY_CONFIG["allowed_origins"] if 'SECURITY_CONFIG' in globals() else ["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

def create_mock_crypto_data(data_type: str, symbol: str = None) -> Dict[str, Any]:
    """Create mock crypto data when real services are unavailable"""
    if data_type == "quote":
        return {
            "symbol": symbol or "bitcoin",
            "current_price": 45000.25 + hash(symbol or "bitcoin") % 10000,
            "change": 1250.50,
            "change_percent": 2.85,
            "volume": 28543100000,
            "high_24h": 47000.00,
            "low_24h": 44000.00,
            "market_cap": 850000000000,
            "timestamp": datetime.now().isoformat()
        }
    elif data_type == "trending":
        return {
            "trending_crypto": [
                {"symbol": "BTC", "name": "Bitcoin", "current_price": 45000.25, "change": 1250.50, "change_percent": 2.85, "volume": 28543100000, "market_cap": 850000000000},
                {"symbol": "ETH", "name": "Ethereum", "current_price": 2800.75, "change": 125.30, "change_percent": 4.68, "volume": 15432800000, "market_cap": 340000000000},
                {"symbol": "BNB", "name": "Binance Coin", "current_price": 315.50, "change": 8.75, "change_percent": 2.85, "volume": 1854300000, "market_cap": 47000000000},
                {"symbol": "ADA", "name": "Cardano", "current_price": 0.52, "change": 0.025, "change_percent": 5.08, "volume": 854300000, "market_cap": 17500000000},
                {"symbol": "SOL", "name": "Solana", "current_price": 95.25, "change": 4.50, "change_percent": 4.96, "volume": 2154300000, "market_cap": 38000000000},
            ],
            "timestamp": datetime.now().isoformat()
        }

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

@app.get("/api/crypto/{symbol}")
async def get_crypto_data(symbol: str):
    """Get crypto data for a specific symbol"""
    try:
        if CRYPTO_AVAILABLE:
            return await crypto_provider.get_crypto_data(symbol)
        else:
            # Return mock data
            return {
                "status": "success",
                "data": create_mock_crypto_data("quote", symbol),
                "timestamp": datetime.now().isoformat()
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching crypto data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching crypto data: {str(e)}")

@app.get("/api/top100/crypto")
async def get_top_100_crypto():
    """Get top 100 cryptocurrencies data"""
    try:
        # Mock crypto data for top 100
        crypto_names = [
            'Bitcoin', 'Ethereum', 'Binance Coin', 'Cardano', 'Solana', 'XRP', 'Polkadot', 'Dogecoin',
            'Avalanche', 'Shiba Inu', 'Polygon', 'Chainlink', 'Litecoin', 'Bitcoin Cash', 'Algorand',
            'VeChain', 'Stellar', 'Filecoin', 'TRON', 'Monero', 'EOS', 'Aave', 'Theta', 'Cosmos',
            'Maker', 'Compound', 'Uniswap', 'Sushiswap', 'Yearn Finance', 'The Graph'
        ]
        
        mock_crypto = []
        for i, name in enumerate(crypto_names):
            symbol = name.upper().replace(' ', '')[:6]
            base_price = 50000 if name == 'Bitcoin' else (3000 if name == 'Ethereum' else (hash(name) % 100) + 1)
            price = base_price * (0.9 + (hash(name) % 20) / 100)
            mock_crypto.append({
                'id': name.lower().replace(' ', '-'),
                'symbol': symbol,
                'name': name,
                'current_price': round(price, 6),
                'market_cap': int(price * (1000000 + hash(name) % 10000000)),
                'market_cap_rank': i + 1,
                'volume_24h': int(price * (100000 + hash(name) % 1000000)),
                'price_change_percent_24h': (hash(name) % 20) - 10,
                'price_change_percent_1h': (hash(name) % 6) - 3,
                'price_change_percent_7d': (hash(name) % 30) - 15,
                'asset_type': 'crypto'
            })
        
        return {
            "data": mock_crypto,
            "count": len(mock_crypto),
            "total_market_cap": sum(coin.get('market_cap', 0) for coin in mock_crypto),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching top 100 crypto: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching crypto data: {str(e)}")

@app.get("/api/crypto/trending")
async def get_trending_crypto():
    """Get trending cryptocurrencies"""
    try:
        crypto_data = await get_top_100_crypto()
        # Return top 20 for trending
        trending = crypto_data["data"][:20]
        return {
            "data": trending,
            "count": len(trending),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching trending crypto: {e}")
        return create_mock_crypto_data("trending")

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

# ======================
# STARTUP EVENT
# ======================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Crypto Analytics Hub starting up...")
    logger.info(f"   - Crypto data provider: {'✅' if CRYPTO_AVAILABLE else '❌'}")
    logger.info(f"   - OpenRouter AI: {'✅' if AI_AVAILABLE else '❌'}")
    logger.info("🌐 Server ready for crypto analytics and AI insights!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT, debug=DEBUG) 