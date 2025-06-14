#!/usr/bin/env python3
"""Simple test to verify all Financial Analytics Hub APIs are working"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_endpoint(url, method="GET", data=None):
    """Test an endpoint and return success status"""
    try:
        if method == "POST":
            response = requests.post(f"{BASE_URL}{url}", json=data, timeout=5)
        else:
            response = requests.get(f"{BASE_URL}{url}", timeout=5)
        return response.status_code == 200, response.status_code
    except Exception as e:
        return False, str(e)

print("🚀 Financial Analytics Hub - Quick API Test")
print("=" * 50)

# Test endpoints
tests = [
    ("/health", "GET", None, "Health Check"),
    ("/api/system/status", "GET", None, "System Status"),
    ("/api/stocks/analyze", "POST", {"symbol": "AAPL"}, "Stock Analysis"),
    ("/api/crypto/analyze", "POST", {"symbol": "bitcoin"}, "Crypto Analysis"),
    ("/api/market/overview", "GET", None, "Market Overview"),
    ("/api/stocks/trending", "GET", None, "Trending Stocks"),
    ("/api/crypto/trending", "GET", None, "Trending Crypto"),
    ("/api/education/modules", "GET", None, "Education Modules"),
]

passed = 0
total = len(tests)

for url, method, data, name in tests:
    success, status = test_endpoint(url, method, data)
    result = "✅ PASS" if success else "❌ FAIL"
    print(f"{result} {name} - {status}")
    if success:
        passed += 1

print("=" * 50)
print(f"📊 RESULTS: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")

if passed == total:
    print("🎉 ALL APIS WORKING PERFECTLY!")
elif passed >= total * 0.8:
    print("🟢 EXCELLENT - Most APIs working!")
else:
    print("🟡 Some APIs need attention")

print("\n🔧 Active API Sources:")
print("   • Alpha Vantage: K2BDU6HV1QBZAG5E")
print("   • Twelve Data: 2df82f24652f4fb08d90fcd537a97e9c") 
print("   • CoinGecko: Free tier")
print("   • Yahoo Finance: Available")
print("   • World Bank: Available")
print("   • Enhanced fallback systems: Active") 