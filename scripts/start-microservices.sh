#!/bin/bash

# Financial Analytics Hub - Microservices Startup Script
# This script starts all microservices in the correct order with health checks

set -e

echo "🚀 Starting Financial Analytics Hub Microservices v2.1.0"
echo "========================================================"

# Configuration
HEALTH_CHECK_TIMEOUT=30
HEALTH_CHECK_INTERVAL=2

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a service is healthy
check_health() {
    local service_name=$1
    local health_url=$2
    local timeout=$3
    
    print_status "Checking health of $service_name..."
    
    local count=0
    while [ $count -lt $((timeout / HEALTH_CHECK_INTERVAL)) ]; do
        if curl -s -f "$health_url" > /dev/null 2>&1; then
            print_success "$service_name is healthy"
            return 0
        fi
        
        echo -n "."
        sleep $HEALTH_CHECK_INTERVAL
        count=$((count + 1))
    done
    
    print_error "$service_name health check failed after ${timeout}s"
    return 1
}

# Function to wait for service to be ready
wait_for_service() {
    local service_name=$1
    local port=$2
    local timeout=${3:-30}
    
    print_status "Waiting for $service_name on port $port..."
    
    local count=0
    while [ $count -lt $((timeout / HEALTH_CHECK_INTERVAL)) ]; do
        if nc -z localhost $port > /dev/null 2>&1; then
            print_success "$service_name is ready on port $port"
            return 0
        fi
        
        echo -n "."
        sleep $HEALTH_CHECK_INTERVAL
        count=$((count + 1))
    done
    
    print_error "$service_name failed to start on port $port after ${timeout}s"
    return 1
}

# Function to start a service
start_service() {
    local service_name=$1
    local service_dir=$2
    local port=$3
    local log_file="logs/${service_name}.log"
    
    print_status "Starting $service_name..."
    
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    # Change to service directory and start the service
    cd "$service_dir"
    
    # Check if virtual environment exists, create if not
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment for $service_name..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    
    if [ -f "requirements.txt" ]; then
        print_status "Installing dependencies for $service_name..."
        pip install -q -r requirements.txt
    fi
    
    # Start the service in background
    nohup python -m uvicorn main:app --host 0.0.0.0 --port $port --reload > "../$log_file" 2>&1 &
    local pid=$!
    
    echo $pid > "../logs/${service_name}.pid"
    print_success "$service_name started with PID $pid"
    
    # Go back to root directory
    cd ..
    
    # Wait for service to be ready
    wait_for_service "$service_name" $port
}

# Function to cleanup on exit
cleanup() {
    print_warning "Shutting down services..."
    
    # Kill all services
    if [ -d "logs" ]; then
        for pid_file in logs/*.pid; do
            if [ -f "$pid_file" ]; then
                local pid=$(cat "$pid_file")
                if kill -0 "$pid" 2>/dev/null; then
                    print_status "Stopping PID $pid"
                    kill "$pid"
                fi
                rm -f "$pid_file"
            fi
        done
    fi
    
    print_success "All services stopped"
}

# Set up cleanup on script exit
trap cleanup EXIT INT TERM

# Check prerequisites
print_status "Checking prerequisites..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Check if Redis is running (for caching)
if ! command -v redis-cli &> /dev/null || ! redis-cli ping > /dev/null 2>&1; then
    print_warning "Redis is not running. Starting with Docker..."
    docker run -d --name financial-redis -p 6379:6379 redis:7-alpine || {
        print_error "Failed to start Redis. Please start Redis manually."
        exit 1
    }
    sleep 5
fi

print_success "Prerequisites check completed"

# Create logs directory
mkdir -p logs

# Start services in dependency order
print_status "Starting services in dependency order..."

# 1. Start Data Service (foundational service)
start_service "data-service" "services/data-service" 8002

# Check health before proceeding
check_health "data-service" "http://localhost:8002/health" $HEALTH_CHECK_TIMEOUT

# 2. Start Chart Service (depends on data service)
start_service "chart-service" "services/chart-service" 8003

# Check health
check_health "chart-service" "http://localhost:8003/health" $HEALTH_CHECK_TIMEOUT

# 3. Start Graph Service (depends on data service)
start_service "graph-service" "services/graph-service" 8004

# Check health
check_health "graph-service" "http://localhost:8004/health" $HEALTH_CHECK_TIMEOUT

# 4. Start AI Service (depends on data service)
start_service "ai-service" "services/ai-service" 8005

# Check health
check_health "ai-service" "http://localhost:8005/health" $HEALTH_CHECK_TIMEOUT

# 5. Start API Gateway (depends on all services)
start_service "api-gateway" "services/api-gateway" 8001

# Check health
check_health "api-gateway" "http://localhost:8001/health" $HEALTH_CHECK_TIMEOUT

print_success "All microservices started successfully!"

# Display service status
echo ""
echo "🌟 Service Status:"
echo "=================="
echo "📊 Data Service:    http://localhost:8002"
echo "📈 Chart Service:   http://localhost:8003"
echo "🔗 Graph Service:   http://localhost:8004"
echo "🤖 AI Service:      http://localhost:8005"
echo "🌐 API Gateway:     http://localhost:8001"
echo ""
echo "📚 Documentation:   http://localhost:8001/docs"
echo "📋 Service Health:  http://localhost:8001/api/gateway/services"
echo ""
echo "📝 Logs are available in the 'logs/' directory"
echo ""

# Start frontend if available
if [ -d "apps/web" ]; then
    print_status "Starting frontend..."
    cd apps/web
    
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    npm run dev > ../logs/frontend.log 2>&1 &
    echo $! > ../logs/frontend.pid
    
    print_success "Frontend started at http://localhost:3000"
    cd ../..
fi

print_success "Financial Analytics Hub is fully operational!"
print_status "Press Ctrl+C to stop all services"

# Keep script running
while true; do
    sleep 60
    
    # Periodic health checks
    services=("data-service:8002" "chart-service:8003" "graph-service:8004" "ai-service:8005" "api-gateway:8001")
    
    for service_port in "${services[@]}"; do
        IFS=':' read -r service port <<< "$service_port"
        if ! nc -z localhost "$port" > /dev/null 2>&1; then
            print_warning "$service on port $port appears to be down"
        fi
    done
done 