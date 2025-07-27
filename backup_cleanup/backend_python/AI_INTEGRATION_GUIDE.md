# OpenRouter AI Integration Guide
## Financial Analytics Hub - Best Free AI Models

### 🚀 Overview

The Financial Analytics Hub now includes **OpenRouter AI integration** with access to the **best free AI models** for financial analysis:

- **GPT-4o Mini** (OpenAI) - $0.15/1M tokens - Best overall free model
- **Claude 3 Haiku** (Anthropic) - $0.25/1M tokens - Fast reasoning  
- **Gemini Flash 1.5** (Google) - **FREE** - Latest multimodal model
- **Llama 3.1 405B** (Meta) - **FREE** - Most powerful open source
- **Qwen 2.5 72B** (Alibaba) - **FREE** - Excellent for data analysis
- **Mistral 7B** - **FREE** - Fast and efficient

### 🔑 Setup Instructions

1. **Get Your Free OpenRouter API Key**
   ```bash
   # Visit: https://openrouter.ai/keys
   # Sign up for free and generate your API key
   ```

2. **Configure Environment**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env and add your OpenRouter API key
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

3. **Start the Enhanced Backend**
   ```bash
   # From services/backend directory
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
   ```

### 🎯 AI-Powered Features

#### 1. **Stock Analysis** `/api/ai/analyze/stock`
```bash
curl -X POST "http://localhost:8001/api/ai/analyze/stock" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "include_ai": true,
    "ai_model": "openai/gpt-4o-mini"
  }'
```

**Provides:**
- Buy/Hold/Sell recommendations
- Price targets and support/resistance levels
- Risk assessment and confidence scores
- Technical analysis interpretation

#### 2. **Portfolio Optimization** `/api/ai/portfolio/optimize`
```bash
curl -X POST "http://localhost:8001/api/ai/portfolio/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "holdings": [
      {"symbol": "AAPL", "shares": 100, "value": 15000},
      {"symbol": "GOOGL", "shares": 50, "value": 12000}
    ],
    "risk_tolerance": "moderate"
  }'
```

**Provides:**
- Asset allocation optimization
- Rebalancing recommendations
- Risk-adjusted return analysis
- Tax efficiency suggestions

#### 3. **Market Sentiment Analysis** `/api/ai/sentiment/analyze`
```bash
curl -X POST "http://localhost:8001/api/ai/sentiment/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL", "TSLA"],
    "include_news": true,
    "timeframe": "1d"
  }'
```

**Provides:**
- Sentiment scores (-100 to +100)
- News impact analysis
- Contrarian opportunities
- Market psychology insights

#### 4. **Trading Signals** `/api/ai/trading/signals`
```bash
curl -X POST "http://localhost:8001/api/ai/trading/signals" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL", "MSFT", "TSLA"],
    "strategy": "technical",
    "risk_level": "medium"
  }'
```

**Provides:**
- Entry/exit signals
- Stop loss and target levels
- Position sizing recommendations
- Risk management strategies

#### 5. **Natural Language Queries** `/api/ai/query`
```bash
curl -X POST "http://localhost:8001/api/ai/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Should I buy Apple stock right now? What are the risks?",
    "model": "google/gemini-flash-1.5",
    "stream": false
  }'
```

**Supports:**
- Natural language questions about markets
- Stock-specific inquiries
- Investment strategy discussions
- Real-time streaming responses

### 🎨 Frontend Integration

Add AI-powered features to your React components:

```typescript
// In your React component
const { data: aiAnalysis } = useQuery({
  queryKey: ['ai-analysis', symbol],
  queryFn: () => fetch(`/api/ai/analyze/stock`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      symbol: symbol,
      include_ai: true,
      ai_model: 'openai/gpt-4o-mini'
    })
  }).then(res => res.json())
});
```

### 🔧 Model Selection Guide

| Use Case | Best Model | Why |
|----------|------------|-----|
| **General Stock Analysis** | GPT-4o Mini | Balanced performance and cost |
| **Quick Insights** | Gemini Flash 1.5 | Free and fast |
| **Data Analysis** | Qwen 2.5 72B | Excellent with numbers |
| **Portfolio Optimization** | Claude 3 Haiku | Strong reasoning |
| **Trading Signals** | Llama 3.1 405B | Most powerful free model |
| **High Volume** | Mistral 7B | Fast and unlimited |

### 💰 Cost Optimization

**Free Models (Unlimited):**
- Gemini Flash 1.5 - Google
- Llama 3.1 405B - Meta  
- Qwen 2.5 72B - Alibaba
- Mistral 7B - Mistral AI

**Low-Cost Premium Models:**
- GPT-4o Mini: $0.15/1M tokens (~$0.02 per analysis)
- Claude 3 Haiku: $0.25/1M tokens (~$0.03 per analysis)

### 🔍 Example API Responses

#### Stock Analysis Response
```json
{
  "symbol": "AAPL",
  "market_data": {
    "current_price": 150.25,
    "change_percent": 1.69,
    "volume": 65432100
  },
  "ai_analysis": {
    "content": "**APPLE INC (AAPL) - COMPREHENSIVE ANALYSIS**\n\n**OVERALL ASSESSMENT: BUY**\n\nBased on the current technical indicators, AAPL shows strong bullish momentum...",
    "model_used": "openai/gpt-4o-mini",
    "confidence": 85.2,
    "tokens_used": 1250,
    "cost_estimate": 0.0002
  }
}
```

#### Trading Signals Response
```json
{
  "trading_signals": {
    "symbols": ["AAPL", "MSFT"],
    "strategy": "technical"
  },
  "ai_signals": {
    "content": "**TRADING SIGNALS - TECHNICAL ANALYSIS**\n\n**AAPL:**\n- Signal: BUY\n- Entry: $148-150\n- Stop Loss: $142\n- Target: $165\n- Confidence: 8/10",
    "confidence": 82.1,
    "cost_estimate": 0.0003
  }
}
```

### 🚀 Advanced Features

#### Streaming Responses
```javascript
// Real-time AI analysis streaming
const eventSource = new EventSource('/api/ai/query');
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.content); // Real-time AI response chunks
};
```

#### Custom Prompts
```python
# Python backend - custom AI analysis
async def custom_analysis(symbol, custom_prompt):
    async with FinancialAI() as ai:
        response = await ai._make_request(
            f"Analyze {symbol}: {custom_prompt}",
            AIModel.GPT_4O_MINI
        )
        return response.content
```

### 📊 Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ai/analyze/stock` | POST | AI stock analysis |
| `/api/ai/portfolio/optimize` | POST | Portfolio optimization |
| `/api/ai/sentiment/analyze` | POST | Market sentiment |
| `/api/ai/trading/signals` | POST | Trading signals |
| `/api/ai/query` | POST | Natural language queries |
| `/api/ai/models` | GET | Available AI models |

### 🔒 Security & Rate Limits

- **API Key Protection**: Store in environment variables only
- **Rate Limits**: 20 AI requests per minute
- **Cost Monitoring**: Track token usage and costs
- **Error Handling**: Graceful fallbacks to mock data

### 🛠️ Troubleshooting

**Common Issues:**

1. **"AI service not available"**
   ```bash
   # Check if OpenRouter API key is set
   echo $OPENROUTER_API_KEY
   ```

2. **"Module not found"**
   ```bash
   # Reinstall AI dependencies
   pip install openai anthropic google-generativeai tiktoken sse-starlette
   ```

3. **"Rate limit exceeded"**
   ```bash
   # Switch to free models in .env
   AI_MOCK_MODE=True
   ```

### 📈 Performance Tips

1. **Use Free Models for High Volume**
   - Gemini Flash 1.5 for general queries
   - Qwen 2.5 72B for data analysis

2. **Cache AI Responses**
   - 30-minute TTL for analysis results
   - Redis caching for production

3. **Optimize Prompts**
   - Shorter prompts = lower costs
   - Specific questions = better results

### 🚀 Production Deployment

```bash
# Environment variables for production
OPENROUTER_API_KEY=your_production_key
AI_MOCK_MODE=False
ENABLE_AI_ANALYSIS=True
RATE_LIMIT_AI=50  # Increase for production
```

---

## 🎉 Ready to Use!

Your Financial Analytics Hub now has **world-class AI capabilities** with the best free models available. Start with the free models (Gemini Flash, Llama 3.1, Qwen 2.5) and upgrade to premium models as needed.

**Next Steps:**
1. Get your free OpenRouter API key
2. Configure environment variables  
3. Test the AI endpoints
4. Integrate with your React frontend
5. Deploy to production

**Happy AI-powered trading! 📈🤖** 