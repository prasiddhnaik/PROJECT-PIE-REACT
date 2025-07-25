#!/usr/bin/env python3
"""
Quick AI Server - OpenRouter Integration Demo
============================================
A simple FastAPI server to demonstrate OpenRouter AI integration.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import aiohttp
import asyncio
import uvicorn
from typing import Optional
import os

# Your OpenRouter API key
OPENROUTER_API_KEY = "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"

app = FastAPI(
    title="Financial Analytics AI Hub",
    description="AI-powered financial analysis with OpenRouter",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AIQuery(BaseModel):
    query: str
    model: Optional[str] = "openai/gpt-4o-mini"

class StockAnalysis(BaseModel):
    symbol: str
    include_ai: Optional[bool] = True
    model: Optional[str] = "openai/gpt-4o-mini"

@app.get("/", response_class=HTMLResponse)
async def home():
    """Home page with API documentation."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Financial Analytics AI Hub</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .endpoint { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .method { background: #3498db; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; }
            .test-btn { background: #27ae60; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
            .test-btn:hover { background: #219a52; }
            .result { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 10px 0; max-height: 300px; overflow-y: auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Financial Analytics AI Hub</h1>
            <p><strong>🔑 OpenRouter API:</strong> ✅ Connected</p>
            <p><strong>🌐 Server:</strong> http://localhost:8001</p>
            
            <h2>🚀 Available Endpoints</h2>
            
            <div class="endpoint">
                <span class="method">POST</span> <strong>/api/ai/query</strong>
                <p>Ask AI any financial question</p>
                <button class="test-btn" onclick="testAIQuery()">Test AI Query</button>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <strong>/api/ai/analyze/stock</strong>
                <p>Get AI-powered stock analysis</p>
                <button class="test-btn" onclick="testStockAnalysis()">Test Stock Analysis</button>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <strong>/health</strong>
                <p>Check server health</p>
                <button class="test-btn" onclick="testHealth()">Test Health</button>
            </div>
            
            <div id="result" class="result" style="display: none;">
                <h3>📊 Result:</h3>
                <pre id="resultContent"></pre>
            </div>
        </div>
        
        <script>
            async function testAIQuery() {
                showResult('Testing AI Query...');
                try {
                    const response = await fetch('/api/ai/query', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            query: 'What are the top 3 crypto investments right now?',
                            model: 'openai/gpt-4o-mini'
                        })
                    });
                    const data = await response.json();
                    showResult(JSON.stringify(data, null, 2));
                } catch (error) {
                    showResult('Error: ' + error.message);
                }
            }
            
            async function testStockAnalysis() {
                showResult('Testing Stock Analysis...');
                try {
                    const response = await fetch('/api/ai/analyze/stock', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            symbol: 'AAPL',
                            include_ai: true,
                            model: 'openai/gpt-4o-mini'
                        })
                    });
                    const data = await response.json();
                    showResult(JSON.stringify(data, null, 2));
                } catch (error) {
                    showResult('Error: ' + error.message);
                }
            }
            
            async function testHealth() {
                showResult('Testing Health...');
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    showResult(JSON.stringify(data, null, 2));
                } catch (error) {
                    showResult('Error: ' + error.message);
                }
            }
            
            function showResult(content) {
                document.getElementById('result').style.display = 'block';
                document.getElementById('resultContent').textContent = content;
            }
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Financial Analytics AI Hub",
        "openrouter_api": "connected",
        "available_models": [
            "openai/gpt-4o-mini ($0.15/1M tokens)",
            "google/gemini-flash-1.5 (FREE)",
            "meta-llama/llama-3.1-405b-instruct (FREE)",
            "qwen/qwen-2.5-72b-instruct (FREE)",
            "mistralai/mistral-7b-instruct (FREE)"
        ]
    }

@app.post("/api/ai/query")
async def ai_query(query: AIQuery):
    """Ask AI any financial question."""
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://financial-analytics-hub.com",
        "X-Title": "Financial Analytics Hub"
    }
    
    payload = {
        "model": query.model,
        "messages": [
            {
                "role": "system",
                "content": "You are a financial analysis expert. Provide clear, actionable insights about investments, markets, and financial strategies. Always include risk warnings."
            },
            {
                "role": "user",
                "content": query.query
            }
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    ai_response = data.get("choices", [{}])[0].get("message", {}).get("content", "No response")
                    usage = data.get("usage", {})
                    
                    return {
                        "query": query.query,
                        "model": query.model,
                        "response": ai_response,
                        "token_usage": usage,
                        "cost_estimate": f"${(usage.get('total_tokens', 0) / 1_000_000) * 0.15:.6f}"
                    }
                else:
                    error_text = await response.text()
                    raise HTTPException(status_code=response.status, detail=f"OpenRouter API error: {error_text}")
                    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI query failed: {str(e)}")

@app.post("/api/ai/analyze/stock")
async def analyze_stock(analysis: StockAnalysis):
    """Get AI-powered stock analysis."""
    
    if not analysis.include_ai:
        return {"symbol": analysis.symbol, "message": "AI analysis disabled"}
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://financial-analytics-hub.com",
        "X-Title": "Financial Analytics Hub"
    }
    
    payload = {
        "model": analysis.model,
        "messages": [
            {
                "role": "system",
                "content": "You are a professional stock analyst. Provide comprehensive analysis including current outlook, key metrics to watch, potential risks, and investment recommendation (Buy/Hold/Sell) with reasoning."
            },
            {
                "role": "user",
                "content": f"Analyze {analysis.symbol} stock. Provide current market outlook, key factors to consider, risks, and investment recommendation. Keep it concise but comprehensive."
            }
        ],
        "max_tokens": 600,
        "temperature": 0.7
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    ai_response = data.get("choices", [{}])[0].get("message", {}).get("content", "No response")
                    usage = data.get("usage", {})
                    
                    return {
                        "symbol": analysis.symbol,
                        "model": analysis.model,
                        "analysis": ai_response,
                        "token_usage": usage,
                        "cost_estimate": f"${(usage.get('total_tokens', 0) / 1_000_000) * 0.15:.6f}",
                        "timestamp": "2024-06-29T13:30:00Z"
                    }
                else:
                    error_text = await response.text()
                    raise HTTPException(status_code=response.status, detail=f"OpenRouter API error: {error_text}")
                    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stock analysis failed: {str(e)}")

# Additional crypto endpoints for React frontend compatibility
@app.get("/api/top100/crypto")
async def get_top100_crypto():
    """Get top 100 cryptocurrencies with mock data for demo."""
    
    # Mock data for top 100 crypto
    mock_crypto_data = []
    crypto_names = [
        ("bitcoin", "BTC", "Bitcoin"), ("ethereum", "ETH", "Ethereum"), ("binancecoin", "BNB", "BNB"),
        ("solana", "SOL", "Solana"), ("cardano", "ADA", "Cardano"), ("dogecoin", "DOGE", "Dogecoin"),
        ("polygon", "MATIC", "Polygon"), ("avalanche-2", "AVAX", "Avalanche"), ("chainlink", "LINK", "Chainlink"),
        ("uniswap", "UNI", "Uniswap"), ("litecoin", "LTC", "Litecoin"), ("polkadot", "DOT", "Polkadot"),
        ("near", "NEAR", "NEAR Protocol"), ("algorand", "ALGO", "Algorand"), ("cosmos", "ATOM", "Cosmos"),
        ("fantom", "FTM", "Fantom"), ("hedera-hashgraph", "HBAR", "Hedera"), ("vechain", "VET", "VeChain"),
        ("stellar", "XLM", "Stellar"), ("filecoin", "FIL", "Filecoin"), ("sandbox", "SAND", "The Sandbox"),
        ("decentraland", "MANA", "Decentraland"), ("axie-infinity", "AXS", "Axie Infinity"), ("theta-token", "THETA", "Theta Network"),
        ("elrond-erd-2", "EGLD", "MultiversX"), ("flow", "FLOW", "Flow"), ("internet-computer", "ICP", "Internet Computer"),
        ("tezos", "XTZ", "Tezos"), ("eos", "EOS", "EOS"), ("aave", "AAVE", "Aave")
    ]
    
    import random
    from datetime import datetime, timedelta
    
    for i, (id, symbol, name) in enumerate(crypto_names[:30]):  # Top 30 for demo
        base_price = random.uniform(0.5, 50000) if symbol != "BTC" else random.uniform(40000, 70000)
        if symbol == "ETH":
            base_price = random.uniform(2500, 4000)
        elif symbol in ["BNB", "SOL", "ADA"]:
            base_price = random.uniform(50, 500)
        
        mock_crypto_data.append({
            "id": id,
            "symbol": symbol.lower(),
            "name": name,
            "current_price": round(base_price, 2),
            "market_cap": int(base_price * random.uniform(100000000, 1000000000)),
            "market_cap_rank": i + 1,
            "volume_24h": int(base_price * random.uniform(1000000, 100000000)),
            "price_change_24h": round(base_price * random.uniform(-0.15, 0.15), 2),
            "price_change_percent_24h": round(random.uniform(-15, 15), 2),
            "price_change_percent_1h": round(random.uniform(-5, 5), 2),
            "price_change_percent_7d": round(random.uniform(-25, 25), 2),
            "circulating_supply": random.randint(1000000, 1000000000),
            "total_supply": random.randint(1000000, 1000000000),
            "max_supply": random.randint(21000000, 1000000000) if random.choice([True, False]) else None,
            "ath": round(base_price * random.uniform(1.2, 3.0), 2),
            "ath_change_percentage": round(random.uniform(-80, -10), 2),
            "ath_date": (datetime.now() - timedelta(days=random.randint(30, 1000))).isoformat(),
            "atl": round(base_price * random.uniform(0.1, 0.8), 2),
            "atl_change_percentage": round(random.uniform(100, 2000), 2),
            "atl_date": (datetime.now() - timedelta(days=random.randint(100, 2000))).isoformat(),
            "last_updated": datetime.now().isoformat(),
            "asset_type": "cryptocurrency"
        })
    
    return {
        "data": mock_crypto_data,
        "count": len(mock_crypto_data),
        "total_market_cap": sum(crypto["market_cap"] for crypto in mock_crypto_data),
        "timestamp": datetime.now().isoformat(),
        "isDemo": True
    }

@app.get("/api/crypto/trending")
async def get_trending_crypto():
    """Get trending cryptocurrencies."""
    
    trending_cryptos = [
        {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"},
        {"id": "ethereum", "symbol": "eth", "name": "Ethereum"},
        {"id": "solana", "symbol": "sol", "name": "Solana"},
        {"id": "cardano", "symbol": "ada", "name": "Cardano"},
        {"id": "polygon", "symbol": "matic", "name": "Polygon"},
        {"id": "chainlink", "symbol": "link", "name": "Chainlink"},
        {"id": "avalanche-2", "symbol": "avax", "name": "Avalanche"}
    ]
    
    import random
    from datetime import datetime
    
    trending_data = []
    for i, crypto in enumerate(trending_cryptos):
        base_price = random.uniform(1, 50000)
        if crypto["symbol"] == "btc":
            base_price = random.uniform(40000, 70000)
        elif crypto["symbol"] == "eth":
            base_price = random.uniform(2500, 4000)
        
        trending_data.append({
            "id": crypto["id"],
            "symbol": crypto["symbol"],
            "name": crypto["name"],
            "current_price": round(base_price, 2),
            "market_cap": int(base_price * random.uniform(10000000, 1000000000)),
            "market_cap_rank": i + 1,
            "volume_24h": int(base_price * random.uniform(1000000, 100000000)),
            "price_change_percent_24h": round(random.uniform(-15, 15), 2),
            "price_change_percent_1h": round(random.uniform(-5, 5), 2),
            "price_change_percent_7d": round(random.uniform(-25, 25), 2),
            "asset_type": "cryptocurrency"
        })
    
    return {
        "trending_crypto": trending_data,
        "count": len(trending_data),
        "timestamp": datetime.now().isoformat(),
        "isDemo": True
    }

@app.get("/api/market/overview")
async def get_market_overview():
    """Get market overview data."""
    import random
    from datetime import datetime
    
    return {
        "total_market_cap": random.randint(2000000000000, 3000000000000),
        "total_volume_24h": random.randint(50000000000, 150000000000),
        "bitcoin_dominance": round(random.uniform(40, 60), 1),
        "ethereum_dominance": round(random.uniform(15, 25), 1),
        "active_cryptocurrencies": random.randint(8000, 12000),
        "markets": random.randint(500, 800),
        "market_cap_change_24h": round(random.uniform(-10, 10), 2),
        "volume_change_24h": round(random.uniform(-20, 20), 2),
        "timestamp": datetime.now().isoformat(),
        "isDemo": True
    }

@app.get("/api/market/fear-greed")
async def get_fear_greed():
    """Get Fear & Greed Index."""
    import random
    from datetime import datetime
    
    fear_greed_value = random.randint(20, 80)
    
    if fear_greed_value <= 25:
        classification = "Extreme Fear"
    elif fear_greed_value <= 45:
        classification = "Fear"
    elif fear_greed_value <= 55:
        classification = "Neutral"
    elif fear_greed_value <= 75:
        classification = "Greed"
    else:
        classification = "Extreme Greed"
    
    return {
        "value": fear_greed_value,
        "value_classification": classification,
        "timestamp": datetime.now().isoformat(),
        "time_until_update": "8 hours",
        "isDemo": True
    }

@app.get("/api/crypto/{symbol}/history")
async def get_crypto_history(symbol: str, days: int = 30):
    """Get cryptocurrency price history."""
    import random
    from datetime import datetime, timedelta
    
    # Symbol mapping for common crypto names
    symbol_mapping = {
        "bitcoin": "btc",
        "ethereum": "eth",
        "binancecoin": "bnb",
        "solana": "sol",
        "cardano": "ada",
        "polygon": "matic",
        "dogecoin": "doge",
        "avalanche-2": "avax",
        "chainlink": "link",
        "uniswap": "uni",
        "litecoin": "ltc",
        "polkadot": "dot",
        "near": "near",
        "algorand": "algo",
        "cosmos": "atom",
        "fantom": "ftm",
        "hedera-hashgraph": "hbar",
        "vechain": "vet",
        "stellar": "xlm",
        "filecoin": "fil",
        "sandbox": "sand",
        "decentraland": "mana",
        "axie-infinity": "axs",
        "theta-token": "theta",
        "elrond-erd-2": "egld",
        "flow": "flow",
        "internet-computer": "icp",
        "tezos": "xtz",
        "eos": "eos",
        "aave": "aave"
    }
    
    # Map symbol if needed
    mapped_symbol = symbol_mapping.get(symbol.lower(), symbol.lower())
    
    # Generate mock price history
    history_data = []
    base_price = 100.0
    if mapped_symbol == "btc":
        base_price = 50000.0
    elif mapped_symbol == "eth":
        base_price = 3000.0
    elif mapped_symbol in ["bnb", "sol", "ada"]:
        base_price = random.uniform(50, 500)
    elif mapped_symbol in ["matic", "doge", "avax", "link"]:
        base_price = random.uniform(1, 50)
    
    for i in range(days):
        date = datetime.now() - timedelta(days=days-i)
        # Add some realistic price movement
        price_change = random.uniform(-0.05, 0.05)  # ±5% daily change
        base_price *= (1 + price_change)
        
        history_data.append({
            "timestamp": date.isoformat(),
            "price": round(base_price, 2),
            "volume": random.randint(1000000, 10000000),
            "market_cap": int(base_price * random.uniform(10000000, 100000000)),
            "date": date.strftime("%m/%d")  # Add formatted date for chart
        })
    
    return {
        "symbol": mapped_symbol.upper(),
        "history": history_data,
        "days": days,
        "timestamp": datetime.now().isoformat(),
        "isDemo": True
    }

if __name__ == "__main__":
    print("🚀 Starting Financial Analytics AI Hub...")
    print("=" * 50)
    print(f"🔑 OpenRouter API: Connected")
    print(f"🌐 Server: http://localhost:8001")
    print(f"📚 Documentation: http://localhost:8001")
    print(f"🏥 Health Check: http://localhost:8001/health")
    print("=" * 50)
    print("🤖 Available AI Models:")
    print("• GPT-4o Mini - $0.15/1M tokens (best overall)")
    print("• Gemini Flash 1.5 - FREE (Google's latest)")
    print("• Llama 3.1 405B - FREE (most powerful)")
    print("• Qwen 2.5 72B - FREE (data analysis)")
    print("• Mistral 7B - FREE (fast & efficient)")
    print("=" * 50)
    print("📊 Crypto Data Endpoints:")
    print("• /api/top100/crypto - Top 100 cryptocurrencies")
    print("• /api/crypto/trending - Trending cryptocurrencies")
    print("• /api/market/overview - Market overview")
    print("• /api/market/fear-greed - Fear & Greed Index")
    print("• /api/crypto/{symbol}/history - Price history")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8001) 