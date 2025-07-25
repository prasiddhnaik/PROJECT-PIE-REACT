#!/bin/bash

# Financial Analytics Hub - Quick Start Script
# Get the application running fast with minimal configuration

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
BACKEND_PORT=8001
FRONTEND_PORT=3000
BACKEND_DIR="services/backend"
FRONTEND_DIR="apps/web"

echo -e "${PURPLE}🚀 Financial Analytics Hub - Quick Start${NC}"
echo -e "${PURPLE}=======================================${NC}"
echo ""

# Function to handle cleanup
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${BLUE}Backend stopped${NC}"
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${BLUE}Frontend stopped${NC}"
    fi
    exit 0
}

# Set up cleanup on exit
trap cleanup INT TERM

# Kill any existing processes on our ports
echo -e "${BLUE}🧹 Cleaning up existing processes...${NC}"
lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
sleep 1

# Auto-install pnpm if needed
if ! command -v pnpm >/dev/null 2>&1; then
    echo -e "${YELLOW}📦 Installing pnpm...${NC}"
    npm install -g pnpm
fi

# Backend setup and start
echo -e "${BLUE}🐍 Setting up backend...${NC}"
cd $BACKEND_DIR

# Create and activate virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install --upgrade pip >/dev/null 2>&1
pip install -r requirements.txt >/dev/null 2>&1

# Start backend
echo -e "${GREEN}🚀 Starting backend on port $BACKEND_PORT...${NC}"
python3 main.py &
BACKEND_PID=$!

# Wait for backend to be ready
echo -e "${YELLOW}⏳ Waiting for backend to start...${NC}"
for i in {1..15}; do
    if curl -s "http://localhost:$BACKEND_PORT/health" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is ready!${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 15 ]; then
        echo -e "${RED}❌ Backend failed to start${NC}"
        exit 1
    fi
done

# Go back to project root then navigate to frontend
cd ../..
cd $FRONTEND_DIR
echo -e "${BLUE}⚛️  Setting up frontend...${NC}"

# Install dependencies
echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
pnpm install >/dev/null 2>&1

# Start frontend
echo -e "${GREEN}🚀 Starting frontend on port $FRONTEND_PORT...${NC}"
pnpm dev &
FRONTEND_PID=$!

# Wait for frontend to be ready
echo -e "${YELLOW}⏳ Waiting for frontend to start...${NC}"
for i in {1..20}; do
    if nc -z localhost $FRONTEND_PORT 2>/dev/null; then
        echo -e "${GREEN}✅ Frontend is ready!${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 20 ]; then
        echo -e "${RED}❌ Frontend failed to start${NC}"
        exit 1
    fi
done

# Success message
echo ""
echo -e "${GREEN}🎉 Financial Analytics Hub is running!${NC}"
echo ""
echo -e "${PURPLE}📱 Frontend: ${BLUE}http://localhost:$FRONTEND_PORT${NC}"
echo -e "${PURPLE}🔧 Backend:  ${BLUE}http://localhost:$BACKEND_PORT${NC}"
echo ""
echo -e "${YELLOW}📊 Open http://localhost:$FRONTEND_PORT in your browser${NC}"
echo -e "${YELLOW}🛑 Press Ctrl+C to stop all services${NC}"

# Monitor services
while true; do
    sleep 5
    
    # Check if backend is still running
    if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "${RED}❌ Backend service has stopped${NC}"
        cleanup
    fi
    
    # Check if frontend is still running
    if ! ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "${RED}❌ Frontend service has stopped${NC}"
        cleanup
    fi
    
    # Check if services are responding
    if ! curl -s "http://localhost:$BACKEND_PORT/health" >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Backend health check failed${NC}"
    fi
    
    if ! nc -z localhost $FRONTEND_PORT 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Frontend connection check failed${NC}"
    fi
done 