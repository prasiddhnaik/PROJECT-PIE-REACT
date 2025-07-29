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

# Start the FastAPI application
echo "🔧 Starting FastAPI server..."
python -u main.py 