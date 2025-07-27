#!/bin/bash

echo "🚀 Setting up Financial Analytics Hub"
echo "===================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Kill existing processes
echo "Cleaning up existing processes..."
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
lsof -ti:8002 | xargs kill -9 2>/dev/null || true
lsof -ti:3001 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Setup backend
echo -e "${PURPLE}Setting up backend...${NC}"
cd services/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${GREEN}Creating .env file with API keys...${NC}"
    echo "ALPHA_VANTAGE_API_KEY=3J52FQXN785RGJX0" > .env
    echo "TWELVE_DATA_API_KEY=2df82f24652f4fb08d90fcd537a97e9c" >> .env
fi

# Deactivate virtual environment
deactivate
cd ../..

# Setup frontend
echo -e "${BLUE}Setting up frontend...${NC}"
cd apps/web
npm install
cd ../..

echo -e "${GREEN}Setup complete! Run ./start.sh to launch the application.${NC}" 