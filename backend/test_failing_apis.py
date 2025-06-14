#!/usr/bin/env python3
"""
Test script for debugging failing API endpoints
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_trending_stocks():
    """Test trending stocks endpoint"""
    print("🔍 Testing Trending Stocks API...")
    
    try:
        # Import here to avoid circular imports
        from main import get_trending_stocks
        
        result = await get_trending_stocks()
        
        if result and 'data' in result:
            print(f"✅ Trending stocks: {len(result['data'])} items")
            print(f"   Source: {result.get('source', 'unknown')}")
            print(f"   Status: {result.get('status', 'unknown')}")
            
            # Show sample data
            if result['data']:
                sample = result['data'][0]
                print(f"   Sample: {sample.get('symbol', 'N/A')} - ${sample.get('current_price', 'N/A')}")
        else:
            print("❌ No trending stocks data returned")
            print(f"   Result: {result}")
            
    except Exception as e:
        print(f"❌ Trending stocks error: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_market_overview():
    """Test market overview endpoint"""
    print("\n🔍 Testing Market Overview API...")
    
    try:
        from main import get_market_overview
        
        result = await get_market_overview()
        
        if result and 'data' in result:
            print(f"✅ Market overview: {len(result['data'])} items")
            print(f"   Source: {result.get('source', 'unknown')}")
            print(f"   Status: {result.get('status', 'unknown')}")
            
            # Show sample data
            if result['data']:
                sample = result['data'][0]
                print(f"   Sample: {sample.get('symbol', 'N/A')} - ${sample.get('current_price', 'N/A')}")
        else:
            print("❌ No market overview data returned")
            print(f"   Result: {result}")
            
    except Exception as e:
        print(f"❌ Market overview error: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_individual_apis():
    """Test individual API sources"""
    print("\n🔍 Testing Individual API Sources...")
    
    try:
        from main import fetch_stock_data_multiple_sources
        
        test_symbols = ['AAPL', 'GOOGL', 'MSFT']
        
        for symbol in test_symbols:
            print(f"\n📊 Testing {symbol}:")
            try:
                data = await fetch_stock_data_multiple_sources(symbol)
                if data:
                    print(f"   ✅ {symbol}: ${data.get('current_price', 'N/A')} (source: {data.get('source', 'unknown')})")
                else:
                    print(f"   ❌ {symbol}: No data")
            except Exception as e:
                print(f"   ❌ {symbol}: {str(e)}")
                
    except Exception as e:
        print(f"❌ Individual API test error: {str(e)}")

async def test_api_status():
    """Test API status"""
    print("\n🔍 Testing API Status...")
    
    try:
        from config import APIConfig
        
        available_apis = APIConfig.get_available_apis()
        print("📊 API Status:")
        
        for api_name, is_available in available_apis.items():
            status = "✅" if is_available else "❌"
            print(f"   {status} {api_name}: {'Available' if is_available else 'Not Available'}")
            
    except Exception as e:
        print(f"❌ API status error: {str(e)}")

async def main():
    """Run all tests"""
    print("🚀 Testing Financial Analytics Hub APIs...")
    print("=" * 60)
    
    await test_api_status()
    await test_individual_apis()
    await test_trending_stocks()
    await test_market_overview()
    
    print("\n" + "=" * 60)
    print("🏁 API Testing Complete!")

if __name__ == "__main__":
    asyncio.run(main()) 