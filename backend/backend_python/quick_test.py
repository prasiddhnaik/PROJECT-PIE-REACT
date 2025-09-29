#!/usr/bin/env python3
"""
Quick Test Script for Financial APIs
===================================

Direct test without web server to verify everything works.
"""

import time
import sys
import os

# Add current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_import():
    """Test if we can import our modules"""
    try:
        import yfinance as yf
        print("✅ yfinance imported successfully")
        return True
    except ImportError as e:
        print(f"❌ yfinance import failed: {e}")
        return False

def test_yahoo_direct():
    """Test Yahoo Finance directly"""
    print("\n🧪 Testing Yahoo Finance directly...")
    try:
        import yfinance as yf
        start_time = time.time()
        
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="1d")
        
        if not hist.empty:
            price = float(hist['Close'].iloc[-1])
            elapsed = round((time.time() - start_time) * 1000, 2)
            
            print(f"✅ AAPL Price: ${price}")
            print(f"⚡ Response Time: {elapsed}ms")
            return True
        else:
            print("❌ No data returned")
            return False
            
    except Exception as e:
        elapsed = round((time.time() - start_time) * 1000, 2)
        print(f"❌ Error: {e}")
        print(f"⏱️  Time taken: {elapsed}ms")
        return False

def test_our_apis():
    """Test our enhanced API system"""
    print("\n🚀 Testing our enhanced API system...")
    try:
        from simplified_multi_source import get_stock_data
        
        start_time = time.time()
        data = get_stock_data("AAPL")
        elapsed = round((time.time() - start_time) * 1000, 2)
        
        if data and data.get('primary_data'):
            primary = data['primary_data']
            print(f"✅ Symbol: {primary.get('symbol')}")
            print(f"💰 Price: ${primary.get('current_price')}")
            print(f"📈 Change: {primary.get('change')} ({primary.get('change_percent')}%)")
            print(f"📊 Source: {primary.get('source')}")
            print(f"⚡ Response Time: {elapsed}ms")
            print(f"🔄 Sources Used: {', '.join(data.get('sources_used', []))}")
            print(f"⭐ Reliability Score: {data.get('reliability_score')}")
            return True
        else:
            print(f"❌ No data available")
            print(f"⏱️  Time taken: {elapsed}ms")
            return False
            
    except Exception as e:
        elapsed = round((time.time() - start_time) * 1000, 2)
        print(f"❌ Error: {e}")
        print(f"⏱️  Time taken: {elapsed}ms")
        return False

def test_multiple_symbols():
    """Test multiple symbols for performance"""
    print("\n📊 Testing multiple symbols...")
    symbols = ["AAPL", "GOOGL", "MSFT"]
    
    try:
        from simplified_multi_source import create_simple_provider
        provider = create_simple_provider()
        
        start_time = time.time()
        results = provider.get_multiple_stocks_data(symbols)
        elapsed = round((time.time() - start_time) * 1000, 2)
        
        success_count = 0
        for symbol, data in results.items():
            if data.get('primary_data'):
                price = data['primary_data'].get('current_price')
                print(f"✅ {symbol}: ${price}")
                success_count += 1
            else:
                print(f"❌ {symbol}: Failed")
        
        print(f"📈 Success Rate: {success_count}/{len(symbols)}")
        print(f"⚡ Total Time: {elapsed}ms")
        print(f"⚡ Avg Time per Symbol: {round(elapsed/len(symbols), 2)}ms")
        
        return success_count > 0
        
    except Exception as e:
        elapsed = round((time.time() - start_time) * 1000, 2)
        print(f"❌ Error: {e}")
        print(f"⏱️  Time taken: {elapsed}ms")
        return False

def main():
    """Run all tests"""
    print("🚀 Financial API Performance Test")
    print("=" * 40)
    
    tests = [
        ("Basic Import", test_basic_import),
        ("Yahoo Direct", test_yahoo_direct),
        ("Our Enhanced APIs", test_our_apis),
        ("Multiple Symbols", test_multiple_symbols)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n📋 Running: {name}")
        print("-" * 20)
        try:
            if test_func():
                passed += 1
                print(f"✅ {name}: PASSED")
            else:
                print(f"❌ {name}: FAILED")
        except Exception as e:
            print(f"💥 {name}: CRASHED - {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! APIs are working great!")
        print("\n🌐 To start the web server, run:")
        print("   python3 fast_api_server.py")
        print("\n🌐 Then visit:")
        print("   http://localhost:3000/fast/stock/AAPL")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        
        if passed > 0:
            print("✅ But some APIs are working, so you can still use the system!")

if __name__ == "__main__":
    main() 