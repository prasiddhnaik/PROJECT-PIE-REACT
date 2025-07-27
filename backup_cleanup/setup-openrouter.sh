#!/bin/bash

# OpenRouter API Key Setup Script
# ===============================
# This script automatically configures your OpenRouter API key across the project

set -e

OPENROUTER_KEY="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"

echo "🚀 Setting up OpenRouter AI integration..."
echo "========================================="

# Setup Backend Environment
echo "📁 Configuring backend environment..."
cd services/backend

if [ ! -f .env ]; then
    cp env.example .env
    echo "✅ Created .env from template"
else
    echo "ℹ️  .env already exists"
fi

# Update the OpenRouter API key in .env
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/OPENROUTER_API_KEY=your_openrouter_api_key_here/OPENROUTER_API_KEY=$OPENROUTER_KEY/" .env
    sed -i '' "s/AI_MOCK_MODE=True/AI_MOCK_MODE=False/" .env
    sed -i '' "s/ENABLE_MOCK_DATA=True/ENABLE_MOCK_DATA=False/" .env
    sed -i '' "s/RATE_LIMIT_AI=20/RATE_LIMIT_AI=50/" .env
else
    # Linux
    sed -i "s/OPENROUTER_API_KEY=your_openrouter_api_key_here/OPENROUTER_API_KEY=$OPENROUTER_KEY/" .env
    sed -i "s/AI_MOCK_MODE=True/AI_MOCK_MODE=False/" .env
    sed -i "s/ENABLE_MOCK_DATA=True/ENABLE_MOCK_DATA=False/" .env
    sed -i "s/RATE_LIMIT_AI=20/RATE_LIMIT_AI=50/" .env
fi

echo "✅ Backend .env configured with OpenRouter API key"

# Setup Frontend Environment
echo "📁 Configuring frontend environment..."
cd ../../apps/web

if [ ! -f .env.local ]; then
    cp env.example .env.local
    echo "✅ Created .env.local from template"
else
    echo "ℹ️  .env.local already exists"
fi

echo "✅ Frontend .env.local configured"

# Setup Docker Environment
echo "📁 Configuring Docker environment..."
cd ../..

if [ ! -f .env ]; then
    echo "# Docker Compose Environment Variables" > .env
    echo "OPENROUTER_API_KEY=$OPENROUTER_KEY" >> .env
    echo "ALPHA_VANTAGE_API_KEY=22TNS9NWXVD5CPVF" >> .env
    echo "POLYGON_API_KEY=SavZMeuTDTxjWJuFzBO6zES7mBFK68RJ" >> .env
    echo "FINNHUB_API_KEY=d16k039r01qvtdbj2gtgd16k039r01qvtdbj2gu0" >> .env
    echo "GRAFANA_ADMIN_PASSWORD=admin123" >> .env
    echo "✅ Created Docker .env file"
else
    echo "ℹ️  Docker .env already exists"
fi

echo ""
echo "🎉 OpenRouter AI Setup Complete!"
echo "================================"
echo ""
echo "Your OpenRouter API key has been configured:"
echo "• Backend: services/backend/.env"
echo "• Frontend: apps/web/.env.local" 
echo "• Docker: .env"
echo ""
echo "🚀 Ready to start with AI features:"
echo ""
echo "1. Start the backend:"
echo "   cd services/backend"
echo "   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001"
echo ""
echo "2. Start the frontend:"
echo "   cd apps/web"
echo "   npm run dev"
echo ""
echo "3. Test AI endpoints:"
echo "   curl -X POST http://localhost:8001/api/ai/query \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"query\": \"What are the best crypto investments right now?\"}'"
echo ""
echo "📚 Available AI Models (Free):"
echo "• GPT-4o Mini - Best overall (\$0.15/1M tokens)"
echo "• Gemini Flash 1.5 - FREE multimodal"
echo "• Llama 3.1 405B - FREE most powerful"
echo "• Qwen 2.5 72B - FREE data analysis"
echo "• Mistral 7B - FREE & fast"
echo ""
echo "🌐 API Documentation: http://localhost:8001/docs"
echo ""
echo "Happy AI-powered trading! 📈🤖" 