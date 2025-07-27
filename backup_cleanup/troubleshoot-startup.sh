#!/bin/bash

# Financial Analytics Hub - Comprehensive Troubleshooting Script
# This script diagnoses and fixes common startup issues

# Colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8001
FRONTEND_PORT=3000
BACKEND_DIR="services/backend"
FRONTEND_DIR="apps/web"
VENV_DIR="venv"

print_header() {
    echo -e "${PURPLE}============================================${NC}"
    echo -e "${PURPLE}  Financial Analytics Hub Troubleshooter${NC}"
    echo -e "${PURPLE}============================================${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
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

print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

check_port_usage() {
    local port=$1
    local service_name=$2
    
    print_step "Checking if port $port is in use ($service_name)..."
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        local pid=$(lsof -Pi :$port -sTCP:LISTEN -t)
        local process_name=$(ps -p $pid -o comm= 2>/dev/null)
        print_warning "Port $port is in use by process: $process_name (PID: $pid)"
        
        read -p "Do you want to kill this process? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill -9 $pid 2>/dev/null
            sleep 2
            if ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
                print_success "Process killed successfully"
                return 0
            else
                print_error "Failed to kill process"
                return 1
            fi
        else
            print_warning "Process left running - this may cause conflicts"
            return 1
        fi
    else
        print_success "Port $port is available"
        return 0
    fi
}

verify_dependencies() {
    print_step "Verifying system dependencies..."
    
    # Check Node.js
    if command -v node >/dev/null 2>&1; then
        local node_version=$(node --version)
        print_success "Node.js found: $node_version"
    else
        print_error "Node.js not found. Please install Node.js 18 or higher"
        return 1
    fi
    
    # Check pnpm
    if command -v pnpm >/dev/null 2>&1; then
        local pnpm_version=$(pnpm --version)
        print_success "pnpm found: $pnpm_version"
    else
        print_warning "pnpm not found. Installing..."
        npm install -g pnpm
        if [ $? -eq 0 ]; then
            print_success "pnpm installed successfully"
        else
            print_error "Failed to install pnpm"
            return 1
        fi
    fi
    
    # Check Python
    if command -v python3 >/dev/null 2>&1; then
        local python_version=$(python3 --version)
        print_success "Python found: $python_version"
    else
        print_error "Python 3 not found. Please install Python 3.8 or higher"
        return 1
    fi
    
    # Check pip
    if command -v pip3 >/dev/null 2>&1; then
        print_success "pip3 found"
    else
        print_error "pip3 not found. Please install pip"
        return 1
    fi
    
    return 0
}

setup_python_environment() {
    print_step "Setting up Python virtual environment..."
    
    cd "$BACKEND_DIR" || {
        print_error "Backend directory not found: $BACKEND_DIR"
        return 1
    }
    
    if [ ! -d "$VENV_DIR" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv $VENV_DIR
        if [ $? -eq 0 ]; then
            print_success "Virtual environment created"
        else
            print_error "Failed to create virtual environment"
            cd - >/dev/null
            return 1
        fi
    else
        print_success "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source $VENV_DIR/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip >/dev/null 2>&1
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        print_info "Installing Python dependencies..."
        pip install -r requirements.txt
        if [ $? -eq 0 ]; then
            print_success "Python dependencies installed"
        else
            print_error "Failed to install Python dependencies"
            cd - >/dev/null
            return 1
        fi
    else
        print_warning "requirements.txt not found"
    fi
    
    cd - >/dev/null
    return 0
}

install_frontend_dependencies() {
    print_step "Installing frontend dependencies..."
    
    cd "$FRONTEND_DIR" || {
        print_error "Frontend directory not found: $FRONTEND_DIR"
        return 1
    }
    
    if [ -f "package.json" ]; then
        print_info "Installing Node.js dependencies..."
        pnpm install
        if [ $? -eq 0 ]; then
            print_success "Frontend dependencies installed"
        else
            print_error "Failed to install frontend dependencies"
            cd - >/dev/null
            return 1
        fi
    else
        print_error "package.json not found in frontend directory"
        cd - >/dev/null
        return 1
    fi
    
    cd - >/dev/null
    return 0
}

start_backend_service() {
    print_step "Starting backend service..."
    
    cd "$BACKEND_DIR" || {
        print_error "Backend directory not found"
        return 1
    }
    
    # Activate virtual environment
    source $VENV_DIR/bin/activate
    
    # Start FastAPI server in background
    print_info "Starting FastAPI server on port $BACKEND_PORT..."
    python3 main.py &
    BACKEND_PID=$!
    
    # Wait for service to start
    sleep 5
    
    # Check if service is running
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        print_success "Backend service started (PID: $BACKEND_PID)"
        echo $BACKEND_PID > backend.pid
        cd - >/dev/null
        return 0
    else
        print_error "Failed to start backend service"
        cd - >/dev/null
        return 1
    fi
}

test_backend_health() {
    print_step "Testing backend health..."
    
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        print_info "Health check attempt $attempt/$max_attempts..."
        
        if curl -s "http://localhost:$BACKEND_PORT/health" >/dev/null 2>&1; then
            print_success "Backend health check passed"
            return 0
        fi
        
        sleep 2
        ((attempt++))
    done
    
    print_error "Backend health check failed after $max_attempts attempts"
    return 1
}

start_frontend_service() {
    print_step "Starting frontend service..."
    
    cd "$FRONTEND_DIR" || {
        print_error "Frontend directory not found"
        return 1
    }
    
    # Start Next.js development server in background
    print_info "Starting Next.js server on port $FRONTEND_PORT..."
    pnpm dev &
    FRONTEND_PID=$!
    
    # Wait for service to start
    sleep 10
    
    # Check if service is running
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        print_success "Frontend service started (PID: $FRONTEND_PID)"
        echo $FRONTEND_PID > frontend.pid
        cd - >/dev/null
        return 0
    else
        print_error "Failed to start frontend service"
        cd - >/dev/null
        return 1
    fi
}

verify_services() {
    print_step "Verifying both services are accessible..."
    
    # Test backend
    if curl -s "http://localhost:$BACKEND_PORT/health" >/dev/null 2>&1; then
        print_success "Backend is accessible at http://localhost:$BACKEND_PORT"
    else
        print_error "Backend is not accessible"
        return 1
    fi
    
    # Test frontend (just check if port is listening)
    if nc -z localhost $FRONTEND_PORT 2>/dev/null; then
        print_success "Frontend is accessible at http://localhost:$FRONTEND_PORT"
    else
        print_error "Frontend is not accessible"
        return 1
    fi
    
    return 0
}

cleanup_on_exit() {
    print_info "Cleaning up..."
    
    if [ -n "$BACKEND_PID" ] && ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID
        print_info "Backend service stopped"
    fi
    
    if [ -n "$FRONTEND_PID" ] && ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID
        print_info "Frontend service stopped"
    fi
    
    # Clean up pid files
    rm -f "$BACKEND_DIR/backend.pid" "$FRONTEND_DIR/frontend.pid"
}

main() {
    # Set up cleanup on exit
    trap cleanup_on_exit EXIT INT TERM
    
    print_header
    
    # Step 1: Check port availability
    check_port_usage $BACKEND_PORT "Backend" || print_warning "Backend port may have conflicts"
    check_port_usage $FRONTEND_PORT "Frontend" || print_warning "Frontend port may have conflicts"
    
    # Step 2: Verify dependencies
    if ! verify_dependencies; then
        print_error "Dependency verification failed. Please install missing dependencies."
        exit 1
    fi
    
    # Step 3: Setup Python environment
    if ! setup_python_environment; then
        print_error "Python environment setup failed"
        exit 1
    fi
    
    # Step 4: Install frontend dependencies
    if ! install_frontend_dependencies; then
        print_error "Frontend dependency installation failed"
        exit 1
    fi
    
    # Step 5: Start backend service
    if ! start_backend_service; then
        print_error "Backend service startup failed"
        exit 1
    fi
    
    # Step 6: Test backend health
    if ! test_backend_health; then
        print_error "Backend health check failed"
        exit 1
    fi
    
    # Step 7: Start frontend service
    if ! start_frontend_service; then
        print_error "Frontend service startup failed"
        exit 1
    fi
    
    # Step 8: Verify both services
    if ! verify_services; then
        print_error "Service verification failed"
        exit 1
    fi
    
    # Success message
    echo ""
    print_success "All services are running successfully!"
    echo ""
    echo -e "${GREEN}🎉 Financial Analytics Hub is ready!${NC}"
    echo ""
    echo -e "${CYAN}Frontend:${NC} http://localhost:$FRONTEND_PORT"
    echo -e "${CYAN}Backend:${NC}  http://localhost:$BACKEND_PORT"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
    
    # Keep script running
    while true; do
        sleep 10
        
        # Check if services are still running
        if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
            print_error "Backend service has stopped unexpectedly"
            exit 1
        fi
        
        if ! ps -p $FRONTEND_PID > /dev/null 2>&1; then
            print_error "Frontend service has stopped unexpectedly"
            exit 1
        fi
    done
}

# Make sure we're in the project root
if [ ! -f "pnpm-workspace.yaml" ] && [ ! -f "package.json" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

main "$@" 