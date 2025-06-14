#!/usr/bin/env python3
"""
Quick API test script for Financial Analytics Hub
Tests all 8 APIs to ensure they're working correctly
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_api_endpoint(url, description):
    """Test a single API endpoint"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'endpoint': description,
                        'status': '✅ SUCCESS',
                        'response_code': response.status,
                        'data_available': bool(data)
                    }
                else:
                    return {
                        'endpoint': description,
                        'status': '❌ FAILED',
                        'response_code': response.status,
                        'error': f'HTTP {response.status}'
                    }
    except Exception as e:
        return {
            'endpoint': description,
            'status': '❌ ERROR',
            'error': str(e)
        }

async def main():
    """Test all API endpoints"""
    print("🚀 Financial Analytics Hub - API Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    base_url = "http://localhost:8001"
    
    # Test endpoints
    endpoints = [
        (f"{base_url}/api/system/status", "System Status"),
        (f"{base_url}/api/market/overview", "Market Overview"),
        (f"{base_url}/api/stocks/trending", "Trending Stocks"),
        (f"{base_url}/api/stocks/falling", "Falling Stocks"),
        (f"{base_url}/api/crypto/trending", "Trending Crypto"),
        (f"{base_url}/api/economic/indicators", "Economic Indicators (FRED)"),
        (f"{base_url}/api/news/market", "Market News (Finnhub)"),
        (f"{base_url}/api/market/status", "Market Status (Polygon)"),
        (f"{base_url}/api/company/profile/AAPL", "Company Profile (Finnhub)"),
        (f"{base_url}/api/stocks/historical/AAPL", "Historical Data (Polygon)")
    ]
    
    # Run all tests concurrently
    tasks = [test_api_endpoint(url, desc) for url, desc in endpoints]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Display results
    success_count = 0
    for result in results:
        if isinstance(result, dict):
            print(f"{result['status']} {result['endpoint']}")
            if 'error' in result:
                print(f"    Error: {result['error']}")
            elif 'response_code' in result:
                print(f"    Response: HTTP {result['response_code']}")
            
            if result['status'] == '✅ SUCCESS':
                success_count += 1
        else:
            print(f"❌ ERROR Exception: {str(result)}")
        print()
    
    # Summary
    total_tests = len(endpoints)
    success_rate = (success_count / total_tests) * 100
    
    print("=" * 60)
    print(f"📊 TEST SUMMARY")
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total_tests - success_count}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 EXCELLENT - System is working great!")
    elif success_rate >= 60:
        print("✅ GOOD - Most APIs are working")
    else:
        print("⚠️ NEEDS ATTENTION - Several APIs need fixing")

if __name__ == "__main__":
    asyncio.run(main()) 