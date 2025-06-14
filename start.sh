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
if [ ! -d "backend/venv" ]; then
    echo -e "${PURPLE}Creating Python virtual environment...${NC}"
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
else
    echo -e "${PURPLE}Python virtual environment already exists ✓${NC}"
fi

echo -e "${GREEN}🌟 Starting services...${NC}"

# Function to cleanup background processes
cleanup() {
    echo -e "\n${GREEN}🛑 Shutting down services...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start Python FastAPI backend
echo -e "${PURPLE}🐍 Starting Python FastAPI backend on http://localhost:8000${NC}"
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start React frontend
echo -e "${BLUE}⚛️  Starting React frontend on http://localhost:3000${NC}"
npm start &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}✅ Services started successfully!${NC}"
echo -e "${GREEN}🌐 Frontend: http://localhost:3000${NC}"
echo -e "${PURPLE}🔗 Backend API: http://localhost:8000${NC}"
echo -e "${BLUE}📚 API Docs: http://localhost:8000/docs${NC}"
echo ""
echo -e "${GREEN}💡 Features Available:${NC}"
echo "   • Portfolio Analysis with AI insights"
echo "   • Real-time Stock & Crypto tracking"
echo "   • Risk Assessment & Value at Risk"
echo "   • Educational modules (3-16)"
echo "   • Professional-grade visualizations"
echo ""
echo -e "${GREEN}🎨 Theme: Emerald-Purple Gradient${NC}"
echo -e "${GREEN}🚫 Zero Demo Data - Real APIs Only${NC}"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID 