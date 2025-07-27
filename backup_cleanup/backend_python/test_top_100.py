#!/usr/bin/env python3
"""
Test script for Top 100 Financial Assets API
Tests all new endpoints for stocks, crypto, and forex data
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8001"

def test_endpoint(endpoint, timeout=60):
    """Test a single endpoint and return results"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🧪 Testing: {endpoint}")
    print(f"📍 URL: {url}")
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            # Analyze response
            data_count = 0
            if 'data' in data:
                if isinstance(data['data'], list):
                    data_count = len(data['data'])
                elif isinstance(data['data'], dict):
                    # For comprehensive endpoint
                    stocks_count = len(data['data'].get('stocks', {}).get('data', []))
                    crypto_count = len(data['data'].get('crypto', {}).get('data', []))
                    forex_count = len(data['data'].get('forex', {}).get('data', []))
                    data_count = f"Stocks: {stocks_count}, Crypto: {crypto_count}, Forex: {forex_count}"
            elif 'count' in data:
                data_count = data['count']
                
            print(f"✅ SUCCESS - {response.status_code}")
            print(f"⏱️ Response Time: {response_time:.2f}s")
            print(f"📊 Data Count: {data_count}")
            print(f"🔄 Source: {data.get('source', 'unknown')}")
            
            return {
                'endpoint': endpoint,
                'status': 'SUCCESS',
                'status_code': response.status_code,
                'response_time': round(response_time, 2),
                'data_count': data_count,
                'source': data.get('source', 'unknown')
            }
            
        else:
            print(f"❌ FAILED - {response.status_code}")
            try:
                error_data = response.json()
                print(f"📝 Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"📝 Error: {response.text[:200]}...")
                
            return {
                'endpoint': endpoint,
                'status': 'FAILED',
                'status_code': response.status_code,
                'response_time': round(response_time, 2),
                'error': response.text[:100]
            }
            
    except requests.exceptions.Timeout:
        print(f"⏰ TIMEOUT - Request took longer than {timeout}s")
        return {
            'endpoint': endpoint,
            'status': 'TIMEOUT',
            'timeout': timeout
        }
    except Exception as e:
        print(f"💥 ERROR - {str(e)}")
        return {
            'endpoint': endpoint,
            'status': 'ERROR',
            'error': str(e)
        }

def main():
    print("🚀 Financial Analytics Hub - Top 100 API Test Suite")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {BASE_URL}")
    
    # Test endpoints in order of complexity
    endpoints = [
        # Quick tests first
        ("/api/top100/summary", 10),
        
        # Individual asset classes
        ("/api/top100/crypto", 30),    # Fastest API
        ("/api/top100/forex", 60),     # Medium speed
        ("/api/top100/stocks", 60),    # Slower due to rate limits
        
        # Comprehensive test last
        ("/api/top100/all", 120),      # Longest timeout for all data
    ]
    
    results = []
    total_start_time = time.time()
    
    # Test server health first
    print("\n🔍 Testing server health...")
    health_result = test_endpoint("/health", 5)
    if health_result['status'] != 'SUCCESS':
        print("❌ Server health check failed. Aborting tests.")
        return
    
    print("\n" + "="*60)
    print("🧪 TESTING TOP 100 ENDPOINTS")
    print("="*60)
    
    for endpoint, timeout in endpoints:
        result = test_endpoint(endpoint, timeout)
        results.append(result)
        
        # Brief pause between tests to avoid overwhelming the API
        if endpoint != endpoints[-1][0]:  # Don't sleep after last test
            print("⏸️ Waiting 3 seconds before next test...")
            time.sleep(3)
    
    total_end_time = time.time()
    total_time = total_end_time - total_start_time
    
    # Generate summary report
    print("\n" + "="*60)
    print("📊 TEST SUMMARY REPORT")
    print("="*60)
    
    successful_tests = [r for r in results if r['status'] == 'SUCCESS']
    failed_tests = [r for r in results if r['status'] in ['FAILED', 'TIMEOUT', 'ERROR']]
    
    print(f"📈 Total Tests: {len(results)}")
    print(f"✅ Successful: {len(successful_tests)}")
    print(f"❌ Failed: {len(failed_tests)}")
    print(f"📊 Success Rate: {len(successful_tests)/len(results)*100:.1f}%")
    print(f"⏱️ Total Test Time: {total_time:.2f}s")
    
    if successful_tests:
        avg_response_time = sum(r.get('response_time', 0) for r in successful_tests) / len(successful_tests)
        print(f"⚡ Average Response Time: {avg_response_time:.2f}s")
    
    # Detailed results
    print(f"\n📋 DETAILED RESULTS:")
    print("-" * 60)
    for result in results:
        status_emoji = "✅" if result['status'] == 'SUCCESS' else "❌"
        endpoint = result['endpoint']
        status = result['status']
        
        if result['status'] == 'SUCCESS':
            response_time = result.get('response_time', 0)
            data_count = result.get('data_count', 'N/A')
            source = result.get('source', 'unknown')
            print(f"{status_emoji} {endpoint}")
            print(f"    Status: {status} | Time: {response_time}s | Count: {data_count} | Source: {source}")
        else:
            error = result.get('error', result.get('timeout', 'Unknown'))
            print(f"{status_emoji} {endpoint}")
            print(f"    Status: {status} | Error: {error}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    print("-" * 60)
    
    if len(successful_tests) == len(results):
        print("🎉 Perfect! All endpoints are working flawlessly.")
        print("🚀 Your Financial Analytics Hub is ready for production.")
    elif len(successful_tests) >= len(results) * 0.8:
        print("👍 Great! Most endpoints are working well.")
        print("🔧 Consider investigating the failed endpoints for optimization.")
    else:
        print("⚠️ Several endpoints need attention.")
        print("🔧 Check server logs and API configurations.")
    
    # Performance insights
    fast_endpoints = [r for r in successful_tests if r.get('response_time', 999) < 5]
    slow_endpoints = [r for r in successful_tests if r.get('response_time', 0) > 30]
    
    if fast_endpoints:
        print(f"⚡ Fast endpoints ({len(fast_endpoints)}): Excellent performance")
    if slow_endpoints:
        print(f"🐌 Slow endpoints ({len(slow_endpoints)}): Consider caching or optimization")
    
    print(f"\n🔗 Access your Top 100 data at: {BASE_URL}/api/top100/summary")
    print("📖 Documentation: Check FastAPI docs at /docs")

if __name__ == "__main__":
    main() 