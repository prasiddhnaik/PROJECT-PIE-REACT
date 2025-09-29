#!/usr/bin/env python3
"""
Financial Analytics Hub - Backend Health Check Script
This script verifies the backend service health and diagnoses issues.
"""

import sys
import json
import time
import requests
import subprocess
import pkg_resources
from pathlib import Path
from typing import Dict, List, Tuple

# Configuration
BACKEND_PORT = 8001
BASE_URL = f"http://localhost:{BACKEND_PORT}"
REQUIRED_PACKAGES = [
    'fastapi', 'uvicorn', 'requests', 'python-dotenv',
    'pandas', 'numpy', 'yfinance', 'pydantic'
]

# ANSI Colors
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Print the script header."""
    print(f"{Colors.PURPLE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.PURPLE}{Colors.BOLD}  Financial Analytics Hub - Backend Health Check{Colors.ENDC}")
    print(f"{Colors.PURPLE}{'='*60}{Colors.ENDC}")
    print()

def print_success(message: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ [SUCCESS]{Colors.ENDC} {message}")

def print_error(message: str):
    """Print error message."""
    print(f"{Colors.RED}❌ [ERROR]{Colors.ENDC} {message}")

def print_warning(message: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  [WARNING]{Colors.ENDC} {message}")

def print_info(message: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  [INFO]{Colors.ENDC} {message}")

def print_step(message: str):
    """Print step message."""
    print(f"{Colors.CYAN}🔍 [STEP]{Colors.ENDC} {message}")

def check_python_packages() -> Tuple[bool, List[str]]:
    """Check if required Python packages are installed."""
    print_step("Checking Python package dependencies...")
    
    missing_packages = []
    installed_packages = []
    
    for package in REQUIRED_PACKAGES:
        try:
            pkg_resources.get_distribution(package)
            installed_packages.append(package)
        except pkg_resources.DistributionNotFound:
            missing_packages.append(package)
    
    if missing_packages:
        print_error(f"Missing packages: {', '.join(missing_packages)}")
        print_info("Install missing packages with: pip install " + " ".join(missing_packages))
        return False, missing_packages
    else:
        print_success(f"All required packages are installed: {', '.join(installed_packages)}")
        return True, []

def check_environment_variables() -> bool:
    """Check environment variables and configuration."""
    print_step("Checking environment configuration...")
    
    # Check if .env file exists
    env_file = Path('.env')
    if env_file.exists():
        print_success("Environment file (.env) found")
    else:
        print_warning("No .env file found - using default configuration")
    
    # Check if main.py exists
    main_file = Path('main.py')
    if main_file.exists():
        print_success("Main application file (main.py) found")
        return True
    else:
        print_error("Main application file (main.py) not found")
        return False

def check_service_status() -> bool:
    """Check if the backend service is running."""
    print_step(f"Checking if backend service is running on port {BACKEND_PORT}...")
    
    try:
        # Check if port is in use
        result = subprocess.run(['lsof', '-i', f':{BACKEND_PORT}'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success(f"Service is running on port {BACKEND_PORT}")
            return True
        else:
            print_error(f"No service running on port {BACKEND_PORT}")
            return False
    except FileNotFoundError:
        print_warning("lsof command not found, trying alternative method...")
        
        # Alternative method using netstat
        try:
            result = subprocess.run(['netstat', '-tuln'], 
                                  capture_output=True, text=True)
            if f":{BACKEND_PORT}" in result.stdout:
                print_success(f"Service is running on port {BACKEND_PORT}")
                return True
            else:
                print_error(f"No service running on port {BACKEND_PORT}")
                return False
        except FileNotFoundError:
            print_warning("netstat command not found, skipping port check")
            return False

def test_health_endpoint() -> bool:
    """Test the health endpoint."""
    print_step("Testing health endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("Health endpoint responding correctly")
            return True
        else:
            print_error(f"Health endpoint returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to health endpoint - service may not be running")
        return False
    except requests.exceptions.Timeout:
        print_error("Health endpoint request timed out")
        return False
    except Exception as e:
        print_error(f"Error testing health endpoint: {str(e)}")
        return False

def test_api_endpoints() -> Dict[str, bool]:
    """Test critical API endpoints."""
    print_step("Testing critical API endpoints...")
    
    endpoints = {
        '/api/status': 'Status endpoint',
        '/api/crypto/trending': 'Trending crypto endpoint',
        '/api/market/overview': 'Market overview endpoint',
        '/api/crypto/top100': 'Top 100 crypto endpoint'
    }
    
    results = {}
    
    for endpoint, description in endpoints.items():
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                print_success(f"{description}: OK")
                results[endpoint] = True
            else:
                print_warning(f"{description}: Status {response.status_code}")
                results[endpoint] = False
        except requests.exceptions.ConnectionError:
            print_error(f"{description}: Connection failed")
            results[endpoint] = False
        except requests.exceptions.Timeout:
            print_error(f"{description}: Request timeout")
            results[endpoint] = False
        except Exception as e:
            print_error(f"{description}: Error - {str(e)}")
            results[endpoint] = False
    
    return results

def measure_response_times() -> Dict[str, float]:
    """Measure API response times."""
    print_step("Measuring API response times...")
    
    endpoints = ['/health', '/api/status']
    response_times = {}
    
    for endpoint in endpoints:
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            response_times[endpoint] = response_time
            
            if response_time < 500:
                print_success(f"{endpoint}: {response_time:.2f}ms")
            elif response_time < 1000:
                print_warning(f"{endpoint}: {response_time:.2f}ms (slow)")
            else:
                print_error(f"{endpoint}: {response_time:.2f}ms (very slow)")
                
        except Exception as e:
            print_error(f"{endpoint}: Failed to measure response time - {str(e)}")
            response_times[endpoint] = -1
    
    return response_times

def check_external_dependencies() -> Dict[str, bool]:
    """Check external API dependencies."""
    print_step("Checking external API dependencies...")
    
    external_apis = {
        'CoinGecko': 'https://api.coingecko.com/api/v3/ping',
        'JSONBin': 'https://api.jsonbin.io/v3'
    }
    
    results = {}
    
    for api_name, url in external_apis.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code < 400:
                print_success(f"{api_name} API: Accessible")
                results[api_name] = True
            else:
                print_warning(f"{api_name} API: Status {response.status_code}")
                results[api_name] = False
        except Exception as e:
            print_warning(f"{api_name} API: {str(e)}")
            results[api_name] = False
    
    return results

def generate_report(packages_ok: bool, missing_packages: List[str], 
                   config_ok: bool, service_running: bool, 
                   health_ok: bool, endpoints: Dict[str, bool],
                   response_times: Dict[str, float], 
                   external_deps: Dict[str, bool]) -> None:
    """Generate a comprehensive health report."""
    print()
    print(f"{Colors.PURPLE}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.PURPLE}{Colors.BOLD}  BACKEND HEALTH REPORT{Colors.ENDC}")
    print(f"{Colors.PURPLE}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print()
    
    # Overall status
    overall_healthy = (packages_ok and config_ok and service_running and 
                      health_ok and all(endpoints.values()))
    
    if overall_healthy:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 OVERALL STATUS: HEALTHY{Colors.ENDC}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ OVERALL STATUS: ISSUES DETECTED{Colors.ENDC}")
    
    print()
    
    # Detailed status
    status_items = [
        ("Package Dependencies", "✅" if packages_ok else "❌"),
        ("Configuration", "✅" if config_ok else "❌"),
        ("Service Running", "✅" if service_running else "❌"),
        ("Health Endpoint", "✅" if health_ok else "❌"),
        ("API Endpoints", "✅" if all(endpoints.values()) else "⚠️"),
    ]
    
    for item, status in status_items:
        print(f"{item:<20} {status}")
    
    # Missing packages
    if missing_packages:
        print(f"\n{Colors.RED}Missing Packages:{Colors.ENDC}")
        for package in missing_packages:
            print(f"  - {package}")
    
    # Endpoint details
    if endpoints:
        print(f"\n{Colors.BLUE}Endpoint Status:{Colors.ENDC}")
        for endpoint, status in endpoints.items():
            status_icon = "✅" if status else "❌"
            print(f"  {endpoint:<25} {status_icon}")
    
    # Response times
    if response_times:
        print(f"\n{Colors.CYAN}Response Times:{Colors.ENDC}")
        for endpoint, time_ms in response_times.items():
            if time_ms > 0:
                print(f"  {endpoint:<25} {time_ms:.2f}ms")
    
    # External dependencies
    if external_deps:
        print(f"\n{Colors.YELLOW}External Dependencies:{Colors.ENDC}")
        for api, status in external_deps.items():
            status_icon = "✅" if status else "⚠️"
            print(f"  {api:<25} {status_icon}")
    
    # Recommendations
    print(f"\n{Colors.PURPLE}Recommendations:{Colors.ENDC}")
    
    if not packages_ok:
        print("  • Install missing Python packages")
    
    if not service_running:
        print("  • Start the backend service with: python main.py")
    
    if not health_ok:
        print("  • Check service logs for startup errors")
        print("  • Verify port 8001 is not blocked by firewall")
    
    if not all(endpoints.values()):
        print("  • Some API endpoints are not responding")
        print("  • Check external API configurations and keys")
    
    if any(time_ms > 1000 for time_ms in response_times.values() if time_ms > 0):
        print("  • Some endpoints have slow response times")
        print("  • Consider optimizing database queries or caching")

def main():
    """Main execution function."""
    print_header()
    
    # Step 1: Check Python packages
    packages_ok, missing_packages = check_python_packages()
    
    # Step 2: Check environment and configuration
    config_ok = check_environment_variables()
    
    # Step 3: Check if service is running
    service_running = check_service_status()
    
    # Step 4: Test health endpoint
    health_ok = test_health_endpoint() if service_running else False
    
    # Step 5: Test API endpoints
    endpoints = test_api_endpoints() if health_ok else {}
    
    # Step 6: Measure response times
    response_times = measure_response_times() if health_ok else {}
    
    # Step 7: Check external dependencies
    external_deps = check_external_dependencies()
    
    # Step 8: Generate comprehensive report
    generate_report(packages_ok, missing_packages, config_ok, 
                   service_running, health_ok, endpoints, 
                   response_times, external_deps)
    
    # Exit with appropriate code
    if packages_ok and config_ok and service_running and health_ok:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 