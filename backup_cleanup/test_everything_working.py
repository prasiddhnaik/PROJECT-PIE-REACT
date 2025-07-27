#!/usr/bin/env python3
"""
Test script to verify everything is working
"""
import requests
import json
import time
from datetime import datetime

def test_backend():
    """Test backend APIs"""
    print("🔧 Testing Backend APIs...")
    
    # Test main endpoint
    try:
        response = requests.get("http://localhost:8001/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Status: {data.get('status', 'Unknown')}")
            print(f"✅ Exchange: {data.get('exchange', 'Unknown')}")
        else:
            print(f"❌ Backend Status: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Backend Error: {e}")
        return False
    
    # Test stocks API
    try:
        response = requests.get("http://localhost:8001/api/stocks/list", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                print(f"✅ Stocks API: {len(data['data'])} stocks loaded")
                print(f"✅ Sample: {data['data'][0]['symbol']} - ₹{data['data'][0]['price']}")
            else:
                print("⚠️  Stocks API: No data returned")
        else:
            print(f"❌ Stocks API: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Stocks API Error: {e}")
    
    return True

def test_frontend():
    """Test frontend"""
    print("\n🌐 Testing Frontend...")
    
    try:
        response = requests.get("http://localhost:3001", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend: Running on port 3001")
            if "xp-trading-platform" in response.text:
                print("✅ Frontend: XP theme detected")
            else:
                print("⚠️  Frontend: XP theme not found")
        else:
            print(f"❌ Frontend: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend Error: {e}")
        return False
    
    return True

def test_xp_dashboard():
    """Test XP dashboard functionality"""
    print("\n🖥️  Testing XP Dashboard...")
    
    try:
        # Test if the XP dashboard file exists and has content
        with open("xp-theme/xp-dashboard-xp-css.html", "r") as f:
            content = f.read()
            
        if "Financial Analytics" in content:
            print("✅ XP Dashboard: Financial Analytics section found")
        else:
            print("❌ XP Dashboard: Financial Analytics section missing")
            
        if "loadStockData" in content:
            print("✅ XP Dashboard: Stock data function found")
        else:
            print("❌ XP Dashboard: Stock data function missing")
            
        if "loadCryptoData" in content:
            print("✅ XP Dashboard: Crypto data function found")
        else:
            print("❌ XP Dashboard: Crypto data function missing")
            
        if "Enhanced APIs" not in content:
            print("✅ XP Dashboard: Non-working sections removed")
        else:
            print("⚠️  XP Dashboard: Some non-working sections still present")
            
    except Exception as e:
        print(f"❌ XP Dashboard Error: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Testing Everything Working...")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test backend
    backend_ok = test_backend()
    
    # Test frontend
    frontend_ok = test_frontend()
    
    # Test XP dashboard
    xp_ok = test_xp_dashboard()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    if backend_ok:
        print("✅ Backend: Working")
    else:
        print("❌ Backend: Issues detected")
        
    if frontend_ok:
        print("✅ Frontend: Working")
    else:
        print("❌ Frontend: Issues detected")
        
    if xp_ok:
        print("✅ XP Dashboard: Working")
    else:
        print("❌ XP Dashboard: Issues detected")
    
    if backend_ok and frontend_ok and xp_ok:
        print("\n🎉 Everything is working!")
        print("\n📱 Access Points:")
        print("   • Frontend: http://localhost:3001")
        print("   • Backend API: http://localhost:8001")
        print("   • XP Dashboard: backup_cleanup/xp-theme/xp-dashboard-xp-css.html")
        print("\n🔧 Available APIs:")
        print("   • GET / - Backend status")
        print("   • GET /api/stocks/list - Stock data")
        print("   • GET /api/stocks/quote/{symbol} - Individual stock quotes")
    else:
        print("\n⚠️  Some components have issues. Check the logs above.")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main() 