#!/bin/bash

# Startup script for Render deployment
echo "🚀 Starting XP Trading Platform Backend..."

# Set default port if not provided
export PORT=${PORT:-10000}
export API_HOST=0.0.0.0

echo "📊 Environment Variables:"
echo "   PORT: $PORT"
echo "   API_HOST: $API_HOST"
echo "   DEBUG: $DEBUG"

# Change to backend directory
cd backend

# Test import first
echo "🧪 Testing app import..."
python -c "import main; print('✅ App imports successfully')" || {
    echo "❌ App import failed"
    exit 1
}

# Start the FastAPI application with explicit host and port
echo "🔧 Starting FastAPI server on 0.0.0.0:$PORT..."
exec python -u main.py 