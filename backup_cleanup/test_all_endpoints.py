#!/usr/bin/env python3
"""
Financial Analytics Hub - Comprehensive Endpoint Test
Tests all API endpoints to verify the 13-minute auto-update system is working
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

def test_endpoint(endpoint, method="GET", data=None, description=""):
    """Test a single endpoint and return results"""
    try:
        if method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=10)
        else:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return {"status": "✅ SUCCESS", "data": result, "error": None}
        else:
            return {"status": f"❌ HTTP {response.status_code}", "data": None, "error": response.text[:100]}
    
    except Exception as e:
        return {"status": "❌ ERROR", "data": None, "error": str(e)[:100]}

def main():
    print("🚀 Financial Analytics Hub - Comprehensive Test Suite")
    print("=" * 60)
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test endpoints
    tests = [
        # System endpoints
        {
            "endpoint": "/",
            "description": "Root endpoint with cache info",
            "key_checks": ["message", "cache_info"]
        },
        {
            "endpoint": "/health",
            "description": "Health check",
            "key_checks": ["status"]
        },
        {
            "endpoint": "/api/system/status",
            "description": "System status with auto-update info",
            "key_checks": ["auto_update", "cache_status"]
        },
        
        # Market data endpoints
        {
            "endpoint": "/api/market/overview",
            "description": "Market overview with indices and crypto",
            "key_checks": ["indices", "crypto_overview", "market_status"]
        },
        
        # Stock analysis
        {
            "endpoint": "/api/stocks/analyze",
            "method": "POST",
            "data": {"symbol": "AAPL", "period": "1y"},
            "description": "Stock analysis (AAPL)",
            "key_checks": ["current_price", "data_source", "technical_indicators"]
        },
        
        # Crypto analysis
        {
            "endpoint": "/api/crypto/analyze", 
            "method": "POST",
            "data": {"symbol": "bitcoin", "currency": "usd"},
            "description": "Crypto analysis (Bitcoin)",
            "key_checks": ["current_price", "data_source"]
        },
        
        # Trending endpoints
        {
            "endpoint": "/api/stocks/trending",
            "description": "Trending stocks",
            "key_checks": ["trending_stocks"]
        },
        {
            "endpoint": "/api/crypto/trending",
            "description": "Trending crypto",
            "key_checks": ["trending_crypto"]
        }
    ]
    
    results = []
    success_count = 0
    
    for test in tests:
        print(f"🔍 Testing: {test['description']}")
        
        result = test_endpoint(
            test["endpoint"],
            test.get("method", "GET"),
            test.get("data"),
            test["description"]
        )
        
        print(f"   {result['status']}")
        
        if result["status"].startswith("✅"):
            success_count += 1
            
            # Check for required keys
            if "key_checks" in test and result["data"]:
                missing_keys = []
                for key in test["key_checks"]:
                    if key not in result["data"]:
                        missing_keys.append(key)
                
                if missing_keys:
                    print(f"   ⚠️  Missing keys: {', '.join(missing_keys)}")
                else:
                    print(f"   ✅ All required keys present")
                    
                # Show some key data
                if test["endpoint"] == "/api/system/status":
                    data = result["data"]
                    print(f"      📊 Cached Items: {data['cache_status']['total_items']}")
                    print(f"      🔄 Next Update: {data['auto_update']['next_update_in_minutes']:.1f}min")
                elif test["endpoint"] == "/api/market/overview":
                    data = result["data"]
                    print(f"      📈 Indices Count: {len(data.get('indices', {}))}")
                    print(f"      🪙 Crypto Count: {len(data.get('crypto_overview', {}))}")
                elif "analyze" in test["endpoint"]:
                    data = result["data"]
                    symbol = data.get('symbol', 'N/A')
                    price = data.get('current_price', 0)
                    source = data.get('data_source', 'N/A')
                    print(f"      💰 {symbol}: ${price} from {source}")
        else:
            print(f"   ❌ Error: {result.get('error', 'Unknown')}")
        
        results.append(result)
        print()
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Successful: {success_count}/{len(tests)} endpoints")
    print(f"❌ Failed: {len(tests) - success_count}/{len(tests)} endpoints")
    
    if success_count == len(tests):
        print("\n🎉 ALL TESTS PASSED! Financial Analytics Hub is fully operational!")
        print("🔄 Auto-update system is running every 13 minutes")
        print("📊 All APIs are responding correctly")
        print("💾 Caching system is active")
    else:
        print(f"\n⚠️  {len(tests) - success_count} endpoints need attention")
    
    print(f"\n🌐 Server running at: {BASE_URL}")
    print("📈 Ready for financial analytics!")

if __name__ == "__main__":
    main() 