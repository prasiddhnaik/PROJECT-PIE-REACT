#!/bin/bash

# Financial Analytics Hub - Port Conflict Resolution Script
# This script handles port conflicts for the application

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_PORT=3000
BACKEND_PORT=8001
ALTERNATIVE_FRONTEND_PORTS=(3001 3002 3003 3004 3005)
ALTERNATIVE_BACKEND_PORTS=(8002 8003 8004 8005 8006)

print_header() {
    echo -e "${PURPLE}============================================${NC}"
    echo -e "${PURPLE}  Financial Analytics Hub - Port Manager${NC}"
    echo -e "${PURPLE}============================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

check_port_usage() {
    local port=$1
    local service_name=$2
    
    print_step "Checking port $port usage ($service_name)..."
    
    # Check if port is in use using lsof
    if command -v lsof >/dev/null 2>&1; then
        local processes=$(lsof -Pi :$port -sTCP:LISTEN -t 2>/dev/null)
        if [ -n "$processes" ]; then
            echo "$processes"
            return 0
        fi
    fi
    
    # Fallback to netstat if lsof is not available
    if command -v netstat >/dev/null 2>&1; then
        local netstat_result=$(netstat -tuln 2>/dev/null | grep ":$port ")
        if [ -n "$netstat_result" ]; then
            # Extract PID if possible (this varies by system)
            echo "unknown"
            return 0
        fi
    fi
    
    # Fallback to ss command (modern Linux)
    if command -v ss >/dev/null 2>&1; then
        local ss_result=$(ss -tuln 2>/dev/null | grep ":$port ")
        if [ -n "$ss_result" ]; then
            echo "unknown"
            return 0
        fi
    fi
    
    return 1
}

get_process_info() {
    local pid=$1
    
    if [ "$pid" = "unknown" ]; then
        echo "Unknown process"
        return
    fi
    
    if command -v ps >/dev/null 2>&1; then
        local process_info=$(ps -p $pid -o pid,ppid,comm,args 2>/dev/null | tail -n +2)
        if [ -n "$process_info" ]; then
            echo "$process_info"
        else
            echo "Process not found (PID: $pid)"
        fi
    else
        echo "Process info unavailable (PID: $pid)"
    fi
}

kill_process_on_port() {
    local port=$1
    local service_name=$2
    local force=$3
    
    print_step "Attempting to free port $port ($service_name)..."
    
    local pids=$(check_port_usage $port "$service_name")
    if [ $? -eq 0 ]; then
        if [ "$pids" = "unknown" ]; then
            print_warning "Port $port is in use but cannot identify the process"
            print_info "You may need to manually find and kill the process"
            return 1
        fi
        
        for pid in $pids; do
            local process_info=$(get_process_info $pid)
            print_warning "Port $port is used by process:"
            echo "  PID: $pid"
            echo "  Info: $process_info"
            
            if [ "$force" = "true" ]; then
                print_info "Force killing process $pid..."
                kill -9 $pid 2>/dev/null
                sleep 1
            else
                echo -n "Kill this process? (y/n): "
                read -r response
                if [[ $response =~ ^[Yy]$ ]]; then
                    print_info "Terminating process $pid..."
                    
                    # Try graceful termination first
                    kill -TERM $pid 2>/dev/null
                    sleep 2
                    
                    # Check if process is still running
                    if ps -p $pid > /dev/null 2>&1; then
                        print_warning "Process still running, force killing..."
                        kill -9 $pid 2>/dev/null
                        sleep 1
                    fi
                else
                    print_info "Process left running"
                    return 1
                fi
            fi
            
            # Verify process is killed
            if ps -p $pid > /dev/null 2>&1; then
                print_error "Failed to kill process $pid"
                return 1
            else
                print_success "Process $pid terminated"
            fi
        done
        
        # Verify port is now free
        sleep 1
        if check_port_usage $port "$service_name" >/dev/null 2>&1; then
            print_error "Port $port is still in use after killing processes"
            return 1
        else
            print_success "Port $port is now available"
            return 0
        fi
    else
        print_success "Port $port is already available"
        return 0
    fi
}

find_alternative_port() {
    local base_port=$1
    local alternatives=("${@:2}")
    
    print_step "Looking for alternative ports..."
    
    for alt_port in "${alternatives[@]}"; do
        if ! check_port_usage $alt_port "alternative" >/dev/null 2>&1; then
            print_success "Alternative port found: $alt_port"
            echo "$alt_port"
            return 0
        fi
    done
    
    print_error "No alternative ports available"
    return 1
}

check_firewall() {
    local port=$1
    local service_name=$2
    
    print_step "Checking firewall configuration for port $port..."
    
    # macOS firewall check
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v pfctl >/dev/null 2>&1; then
            local pf_rules=$(sudo pfctl -sr 2>/dev/null | grep -E ":$port|$port:")
            if [ -n "$pf_rules" ]; then
                print_warning "Firewall rules found for port $port:"
                echo "$pf_rules"
            else
                print_success "No blocking firewall rules found for port $port"
            fi
        else
            print_info "Cannot check pfctl firewall rules"
        fi
    fi
    
    # Linux firewall check
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Check ufw
        if command -v ufw >/dev/null 2>&1; then
            local ufw_status=$(sudo ufw status 2>/dev/null | grep $port)
            if [ -n "$ufw_status" ]; then
                print_info "UFW firewall rules for port $port:"
                echo "$ufw_status"
            else
                print_success "No UFW rules blocking port $port"
            fi
        fi
        
        # Check iptables
        if command -v iptables >/dev/null 2>&1; then
            local iptables_rules=$(sudo iptables -L -n 2>/dev/null | grep $port)
            if [ -n "$iptables_rules" ]; then
                print_info "iptables rules for port $port:"
                echo "$iptables_rules"
            fi
        fi
    fi
}

test_port_binding() {
    local port=$1
    local service_name=$2
    
    print_step "Testing port $port binding capability..."
    
    # Try to bind to the port briefly
    if command -v nc >/dev/null 2>&1; then
        # Use netcat to test port binding
        nc -l $port </dev/null &
        local nc_pid=$!
        sleep 1
        
        if ps -p $nc_pid > /dev/null 2>&1; then
            kill $nc_pid 2>/dev/null
            print_success "Port $port can be bound successfully"
            return 0
        else
            print_error "Cannot bind to port $port"
            return 1
        fi
    else
        print_warning "netcat not available, cannot test port binding"
        return 0
    fi
}

suggest_port_configuration() {
    local frontend_port=$1
    local backend_port=$2
    
    print_step "Generating port configuration suggestions..."
    
    echo ""
    echo -e "${PURPLE}Port Configuration Suggestions:${NC}"
    echo ""
    
    if [ "$frontend_port" != "$FRONTEND_PORT" ]; then
        echo -e "${YELLOW}Frontend Port Changed:${NC}"
        echo "  • Update apps/web/.env.local:"
        echo "    NEXT_PUBLIC_BACKEND_URL=http://localhost:$backend_port"
        echo "  • Start frontend with: PORT=$frontend_port pnpm dev"
        echo ""
    fi
    
    if [ "$backend_port" != "$BACKEND_PORT" ]; then
        echo -e "${YELLOW}Backend Port Changed:${NC}"
        echo "  • Update services/backend/.env:"
        echo "    PORT=$backend_port"
        echo "  • Start backend with: uvicorn main:app --port $backend_port"
        echo ""
    fi
    
    echo -e "${CYAN}Updated URLs:${NC}"
    echo "  • Frontend: http://localhost:$frontend_port"
    echo "  • Backend:  http://localhost:$backend_port"
    echo ""
}

main() {
    print_header
    
    local force_mode=false
    local check_only=false
    
    # Parse command line arguments
    for arg in "$@"; do
        case $arg in
            -f|--force)
                force_mode=true
                shift
                ;;
            -c|--check)
                check_only=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  -f, --force    Force kill processes without confirmation"
                echo "  -c, --check    Only check port status, don't modify anything"
                echo "  -h, --help     Show this help message"
                echo ""
                exit 0
                ;;
        esac
    done
    
    if [ "$check_only" = true ]; then
        print_info "Running in check-only mode..."
        check_port_usage $FRONTEND_PORT "Frontend" >/dev/null
        if [ $? -eq 0 ]; then
            print_warning "Frontend port $FRONTEND_PORT is in use"
        else
            print_success "Frontend port $FRONTEND_PORT is available"
        fi
        
        check_port_usage $BACKEND_PORT "Backend" >/dev/null
        if [ $? -eq 0 ]; then
            print_warning "Backend port $BACKEND_PORT is in use"
        else
            print_success "Backend port $BACKEND_PORT is available"
        fi
        
        exit 0
    fi
    
    local frontend_port=$FRONTEND_PORT
    local backend_port=$BACKEND_PORT
    
    # Handle frontend port
    if ! kill_process_on_port $FRONTEND_PORT "Frontend" $force_mode; then
        print_warning "Could not free frontend port $FRONTEND_PORT"
        alt_port=$(find_alternative_port $FRONTEND_PORT "${ALTERNATIVE_FRONTEND_PORTS[@]}")
        if [ $? -eq 0 ]; then
            frontend_port=$alt_port
            print_info "Will use alternative frontend port: $frontend_port"
        else
            print_error "No alternative frontend ports available"
        fi
    fi
    
    # Handle backend port
    if ! kill_process_on_port $BACKEND_PORT "Backend" $force_mode; then
        print_warning "Could not free backend port $BACKEND_PORT"
        alt_port=$(find_alternative_port $BACKEND_PORT "${ALTERNATIVE_BACKEND_PORTS[@]}")
        if [ $? -eq 0 ]; then
            backend_port=$alt_port
            print_info "Will use alternative backend port: $backend_port"
        else
            print_error "No alternative backend ports available"
        fi
    fi
    
    # Check firewall configuration
    check_firewall $frontend_port "Frontend"
    check_firewall $backend_port "Backend"
    
    # Test port binding
    test_port_binding $frontend_port "Frontend"
    test_port_binding $backend_port "Backend"
    
    # Provide configuration suggestions if ports changed
    if [ "$frontend_port" != "$FRONTEND_PORT" ] || [ "$backend_port" != "$BACKEND_PORT" ]; then
        suggest_port_configuration $frontend_port $backend_port
    fi
    
    echo ""
    print_success "Port management complete!"
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Start backend: cd services/backend && python main.py"
    echo "2. Start frontend: cd apps/web && pnpm dev"
    echo "3. Access application: http://localhost:$frontend_port"
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}Operation cancelled by user${NC}"; exit 1' INT

# Ensure we're in the project root
if [ ! -f "pnpm-workspace.yaml" ] && [ ! -f "package.json" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Run main function
main "$@" 