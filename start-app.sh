#!/bin/bash

# Financial Analytics Hub - App Startup Script
echo "🚀 Starting Financial Analytics Hub..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    lsof -ti:$1 > /dev/null 2>&1
}

# Kill existing processes
echo -e "${BLUE}🔄 Cleaning up existing processes...${NC}"
pkill -f "uvicorn main:app" 2>/dev/null || true
pkill -f "npm start" 2>/dev/null || true
sleep 2

# Start Backend API
echo -e "${BLUE}🔧 Starting Backend API (Port 8001)...${NC}"
cd backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo -e "${BLUE}⏳ Waiting for backend to initialize...${NC}"
sleep 5

# Check if backend is running
if check_port 8001; then
    echo -e "${GREEN}✅ Backend API running on http://localhost:8001${NC}"
else
    echo -e "${RED}❌ Backend failed to start${NC}"
    exit 1
fi

# Start Frontend
echo -e "${BLUE}🎨 Starting Frontend (Port 3000)...${NC}"
npm start &
FRONTEND_PID=$!

# Wait for frontend to start
echo -e "${BLUE}⏳ Waiting for frontend to initialize...${NC}"
sleep 10

# Check if frontend is running
if check_port 3000; then
    echo -e "${GREEN}✅ Frontend running on http://localhost:3000${NC}"
else
    echo -e "${RED}❌ Frontend failed to start${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}"
echo "🎉 Financial Analytics Hub is now running!"
echo "📊 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8001"
echo "📱 The app is ready to use!"
echo -e "${NC}"

# Keep script running
echo "Press Ctrl+C to stop all services..."
wait 