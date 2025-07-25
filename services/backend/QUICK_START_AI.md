# 🚀 Quick Start - OpenRouter AI Features

## Start in 30 Seconds

### 1. Start the Server (Demo Mode)
```bash
cd services/backend
source .venv/bin/activate
python main.py
```

### 2. Test AI Endpoints
Visit: http://localhost:8001/docs

### 3. Try Sample Requests

**Stock Analysis:**
```javascript
fetch('http://localhost:8001/api/ai/analyze/stock', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    symbol: 'AAPL',
    include_ai: true,
    ai_model: 'openai/gpt-4o-mini'
  })
})
```

**Natural Language Query:**
```javascript
fetch('http://localhost:8001/api/ai/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'Should I buy Tesla stock right now?',
    model: 'openai/gpt-4o-mini'
  })
})
```

## Enable Full AI (With Free API Key)

1. Get free key: https://openrouter.ai/keys
2. Add to `.env`:
   ```
   OPENROUTER_API_KEY=sk-or-v1-xxxxx
   ```
3. Restart server

## Available Models (Free)

- **GPT-4o Mini** - Best overall ($0.15/1M tokens)
- **Gemini Flash 1.5** - FREE multimodal  
- **Llama 3.1 405B** - FREE most powerful
- **Qwen 2.5 72B** - FREE data analysis
- **Mistral 7B** - FREE & fast

## React Integration

```jsx
const analyzeStock = async (symbol) => {
  const response = await fetch('/api/ai/analyze/stock', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol, include_ai: true })
  });
  return response.json();
};
```

---
**You're ready to build AI-powered financial apps!** 🎯 