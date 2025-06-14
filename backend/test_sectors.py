#!/usr/bin/env python3
"""
Test script for Sector-Based Financial Analytics
Tests the new sector endpoints (healthcare, technology, financial, etc.)
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8001"

def test_endpoint(endpoint, timeout=30):
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
            
            # Analyze response based on endpoint type
            if 'sectors' in data:
                # Sectors listing endpoint
                sector_count = data.get('total_sectors', 0)
                stock_count = data.get('total_stocks', 0)
                print(f"✅ SUCCESS - {response.status_code}")
                print(f"⏱️ Response Time: {response_time:.2f}s")
                print(f"🏢 Sectors: {sector_count}")
                print(f"📊 Total Stocks: {stock_count}")
                
                return {
                    'endpoint': endpoint,
                    'status': 'SUCCESS',
                    'response_time': round(response_time, 2),
                    'sectors': sector_count,
                    'stocks': stock_count
                }
            elif 'sector' in data:
                # Individual sector endpoint
                sector_name = data.get('sector', 'Unknown')
                count = data.get('count', 0)
                source = data.get('source', 'unknown')
                sector_info = data.get('sector_info', {})
                
                print(f"✅ SUCCESS - {response.status_code}")
                print(f"⏱️ Response Time: {response_time:.2f}s")
                print(f"🏢 Sector: {sector_info.get('name', sector_name)} {sector_info.get('emoji', '')}")
                print(f"📊 Stock Count: {count}")
                print(f"🔄 Source: {source}")
                
                return {
                    'endpoint': endpoint,
                    'status': 'SUCCESS',
                    'response_time': round(response_time, 2),
                    'sector': sector_name,
                    'count': count,
                    'source': source
                }
            else:
                print(f"✅ SUCCESS - {response.status_code}")
                print(f"⏱️ Response Time: {response_time:.2f}s")
                return {
                    'endpoint': endpoint,
                    'status': 'SUCCESS',
                    'response_time': round(response_time, 2)
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
                'response_time': round(response_time, 2)
            }
            
    except requests.exceptions.Timeout:
        print(f"⏰ TIMEOUT - Request took longer than {timeout}s")
        return {'endpoint': endpoint, 'status': 'TIMEOUT', 'timeout': timeout}
    except Exception as e:
        print(f"💥 ERROR - {str(e)}")
        return {'endpoint': endpoint, 'status': 'ERROR', 'error': str(e)}

def main():
    print("🏥💻🏦 Financial Analytics Hub - Sector Analysis Test Suite")
    print("=" * 70)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {BASE_URL}")
    
    results = []
    total_start_time = time.time()
    
    # Test server health first
    print("\n🔍 Testing server health...")
    health_result = test_endpoint("/health", 5)
    if health_result['status'] != 'SUCCESS':
        print("❌ Server health check failed. Aborting tests.")
        return
    
    print("\n" + "="*70)
    print("🏢 TESTING SECTOR ENDPOINTS")
    print("="*70)
    
    # Test 1: Get available sectors
    print("\n📋 STEP 1: Testing sectors listing...")
    sectors_result = test_endpoint("/api/sectors", 10)
    results.append(sectors_result)
    
    if sectors_result['status'] != 'SUCCESS':
        print("❌ Cannot proceed without sectors data")
        return
    
    # Get actual sectors from the API
    try:
        response = requests.get(f"{BASE_URL}/api/sectors", timeout=10)
        sectors_data = response.json()
        available_sectors = list(sectors_data['sectors'].keys())
        print(f"📊 Found {len(available_sectors)} sectors: {', '.join(available_sectors)}")
    except Exception as e:
        print(f"❌ Error getting sectors: {e}")
        return
    
    # Test 2: Test each sector individually
    print(f"\n🧪 STEP 2: Testing individual sectors...")
    for i, sector in enumerate(available_sectors, 1):
        print(f"\n--- Sector {i}/{len(available_sectors)}: {sector} ---")
        sector_result = test_endpoint(f"/api/sectors/{sector}", 30)
        results.append(sector_result)
        
        # Brief pause between sector tests
        if i < len(available_sectors):
            print("⏸️ Waiting 2 seconds...")
            time.sleep(2)
    
    # Test 3: Test invalid sector
    print(f"\n❌ STEP 3: Testing invalid sector...")
    invalid_result = test_endpoint("/api/sectors/invalid_sector", 10)
    # Don't add invalid result to main results as it's expected to fail
    
    total_end_time = time.time()
    total_time = total_end_time - total_start_time
    
    # Generate summary report
    print("\n" + "="*70)
    print("📊 SECTOR ANALYSIS TEST REPORT")
    print("="*70)
    
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
    
    # Sector-specific analysis
    sector_tests = [r for r in results if 'sector' in r and r['status'] == 'SUCCESS']
    if sector_tests:
        total_stocks = sum(r.get('count', 0) for r in sector_tests)
        print(f"🏢 Total Stocks Across Sectors: {total_stocks}")
        
        # Show sector breakdown
        print(f"\n📋 SECTOR BREAKDOWN:")
        print("-" * 50)
        for result in sector_tests:
            if 'sector' in result:
                sector = result['sector']
                count = result.get('count', 0)
                response_time = result.get('response_time', 0)
                source = result.get('source', 'unknown')
                status_emoji = "✅" if result['status'] == 'SUCCESS' else "❌"
                print(f"{status_emoji} {sector.title()}: {count} stocks ({response_time:.1f}s, {source})")
    
    # Performance analysis
    print(f"\n⚡ PERFORMANCE ANALYSIS:")
    print("-" * 50)
    fast_tests = [r for r in successful_tests if r.get('response_time', 999) < 2]
    medium_tests = [r for r in successful_tests if 2 <= r.get('response_time', 0) < 10]
    slow_tests = [r for r in successful_tests if r.get('response_time', 0) >= 10]
    
    print(f"🚀 Fast (<2s): {len(fast_tests)} endpoints")
    print(f"🏃 Medium (2-10s): {len(medium_tests)} endpoints")
    print(f"🐌 Slow (>10s): {len(slow_tests)} endpoints")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    print("-" * 50)
    
    if len(successful_tests) == len(results):
        print("🎉 Perfect! All sector endpoints are working flawlessly.")
        print("🏥💻🏦 Your sector-based analytics are ready for production.")
    elif len(successful_tests) >= len(results) * 0.8:
        print("👍 Great! Most sector endpoints are working well.")
        print("🔧 Consider caching slow sectors for better performance.")
    else:
        print("⚠️ Several sector endpoints need attention.")
        print("🔧 Check API rate limits and server resources.")
    
    print(f"\n🔗 Quick Access URLs:")
    print(f"📋 All Sectors: {BASE_URL}/api/sectors")
    print(f"🏥 Healthcare: {BASE_URL}/api/sectors/healthcare")
    print(f"💻 Technology: {BASE_URL}/api/sectors/technology")
    print(f"🏦 Financial: {BASE_URL}/api/sectors/financial")
    print("📖 Full Documentation: /docs")

if __name__ == "__main__":
    main() 