#!/bin/bash

echo "🚀 Starting Financial Analytics Hub v2.1.0"
echo "==========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo -e "${BLUE}📦 Installing dependencies...${NC}"

# Install React dependencies
if [ ! -d "node_modules" ]; then
    echo -e "${GREEN}Installing React dependencies...${NC}"
    npm install
else
    echo -e "${GREEN}React dependencies already installed ✓${NC}"
fi

# Install Python dependencies
if [ ! -d "services/backend/.venv" ]; then
    echo -e "${PURPLE}Creating Python virtual environment...${NC}"
    cd services/backend
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    cd ../..
else
    echo -e "${PURPLE}Python virtual environment already exists ✓${NC}"
fi

echo -e "${GREEN}🌟 Starting services...${NC}"

# Kill existing processes
echo "Cleaning up existing processes..."
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
lsof -ti:8002 | xargs kill -9 2>/dev/null || true
lsof -ti:3001 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Start backend
echo "Starting backend on port 8001..."
cd services/backend
source .venv/bin/activate
uvicorn main:app --reload --port 8001 --log-level info &
BACKEND_PID=$!

# Wait for backend to start
sleep 5
echo "Backend started with PID: $BACKEND_PID"

# Start frontend
echo "Starting frontend on port 3000..."
cd ../../apps/web
npm run dev &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

echo "Financial Analytics Hub is running!"
echo "- Backend: http://localhost:8001"
echo "- Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Handle shutdown
function cleanup {
  echo "Shutting down services..."
  kill $BACKEND_PID 2>/dev/null
  kill $FRONTEND_PID 2>/dev/null
  exit 0
}

trap cleanup INT TERM

# Keep script running
wait 