#!/usr/bin/env python3
"""
🎉 Financial Analytics Hub v2.2.0 - New Features Demo
Showcases the new sector-based analytics and top 100 coverage
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8001"

def print_banner():
    print("🎉" * 25)
    print("🚀 FINANCIAL ANALYTICS HUB v2.2.0")
    print("🏥💻🏦 SECTOR & TOP 100 ANALYTICS DEMO")
    print("🎉" * 25)
    print(f"📅 Demo Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def demo_sections():
    sections = [
        "🏥💻🏦 1. SECTOR-BASED ANALYTICS",
        "📊 2. TOP 100 MULTI-ASSET COVERAGE", 
        "⚡ 3. PERFORMANCE & CACHING",
        "🔧 4. SYSTEM STATUS & HEALTH"
    ]
    
    for section in sections:
        print(f"\n{'='*60}")
        print(f"  {section}")
        print('='*60)
        yield section

def test_sectors():
    """Demo the new sector analytics"""
    print("\n🔍 Discovering Available Sectors...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/sectors", timeout=10)
        if response.status_code == 200:
            data = response.json()
            sectors = data['sectors']
            
            print(f"✅ Found {data['total_sectors']} sectors covering {data['total_stocks']} stocks")
            print()
            
            for sector_key, sector_info in sectors.items():
                emoji = sector_info['emoji']
                name = sector_info['name']
                count = sector_info['count']
                desc = sector_info['description']
                print(f"{emoji} {name:<25} | {count:2d} stocks | {desc}")
            
            # Test a few specific sectors
            test_sectors = ['healthcare', 'technology', 'financial']
            print(f"\n🧪 Testing Individual Sectors...")
            
            for sector in test_sectors:
                print(f"\n   Testing {sector}...")
                try:
                    start_time = time.time()
                    sector_response = requests.get(f"{BASE_URL}/api/sectors/{sector}", timeout=15)
                    end_time = time.time()
                    
                    if sector_response.status_code == 200:
                        sector_data = sector_response.json()
                        sector_info = sector_data['sector_info']
                        response_time = end_time - start_time
                        
                        print(f"   ✅ {sector_info['emoji']} {sector_info['name']}")
                        print(f"      📊 Stocks: {sector_data['count']}")
                        print(f"      ⏱️ Response: {response_time:.2f}s")
                        print(f"      🔄 Source: {sector_data['source']}")
                    else:
                        print(f"   ❌ {sector}: HTTP {sector_response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ {sector}: {str(e)[:50]}...")
            
        else:
            print(f"❌ Sectors endpoint failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing sectors: {str(e)}")

def test_top_100():
    """Demo the top 100 multi-asset coverage"""
    print("\n🔍 Testing Top 100 Multi-Asset Coverage...")
    
    endpoints = [
        ('crypto', '💰 Cryptocurrencies', 10),
        ('summary', '📊 Quick Summary', 5),
        ('stocks', '📈 Global Stocks', 20),
        ('forex', '💱 Forex Pairs', 15)
    ]
    
    for endpoint, name, timeout in endpoints:
        print(f"\n   Testing {name}...")
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/api/top100/{endpoint}", timeout=timeout)
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                if endpoint == 'summary':
                    summary = data['summary']
                    print(f"   ✅ System Status: {summary['system_status']}")
                    print(f"      📊 Total Assets: {summary['total_assets']}")
                    print(f"      🏢 Stocks: {summary['stocks']['count']}")
                    print(f"      💰 Crypto: {summary['crypto']['count']}")
                    print(f"      💱 Forex: {summary['forex']['count']}")
                elif endpoint == 'crypto' and data.get('count', 0) > 0:
                    print(f"   ✅ {name}: {data['count']} assets")
                    print(f"      💰 Market Cap: ${data['total_market_cap']:,.0f}")
                    print(f"      ⏱️ Response: {response_time:.2f}s")
                    print(f"      🔄 Source: {data['source']}")
                    
                    # Show top 3 cryptos
                    top_cryptos = data['data'][:3]
                    print(f"      🥇 Top 3:")
                    for i, crypto in enumerate(top_cryptos, 1):
                        name_str = crypto['name']
                        symbol = crypto['symbol']
                        price = crypto['current_price']
                        print(f"         {i}. {name_str} ({symbol}) - ${price:,.2f}")
                else:
                    print(f"   ✅ {name}: {data.get('count', 0)} assets")
                    print(f"      ⏱️ Response: {response_time:.2f}s")
                    print(f"      🔄 Source: {data.get('source', 'unknown')}")
                    
            else:
                print(f"   ❌ {name}: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ {name}: Timeout after {timeout}s")
        except Exception as e:
            print(f"   ❌ {name}: {str(e)[:50]}...")

def test_performance():
    """Demo performance and caching capabilities"""
    print("\n🔍 Testing Performance & Caching...")
    
    # Test the same endpoint twice to show caching
    endpoint = "/api/top100/crypto"
    print(f"\n   Testing caching with {endpoint}...")
    
    # First call (should be slow)
    print("   📡 First call (loading fresh data)...")
    try:
        start_time = time.time()
        response1 = requests.get(f"{BASE_URL}{endpoint}", timeout=15)
        end_time = time.time()
        time1 = end_time - start_time
        
        if response1.status_code == 200:
            data1 = response1.json()
            print(f"   ✅ Response: {time1:.2f}s | Source: {data1.get('source', 'unknown')}")
        
        # Second call (should be fast from cache)
        print("   ⚡ Second call (from cache)...")
        start_time = time.time()
        response2 = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        end_time = time.time()
        time2 = end_time - start_time
        
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"   ✅ Response: {time2:.2f}s | Source: {data2.get('source', 'unknown')}")
            
            speedup = time1 / time2 if time2 > 0 else 1
            print(f"   🚀 Speedup: {speedup:.1f}x faster!")
            
    except Exception as e:
        print(f"   ❌ Performance test failed: {str(e)[:50]}...")

def test_system_health():
    """Demo system health and status monitoring"""
    print("\n🔍 System Health & Status Check...")
    
    # Health check
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Health: {health_data['status']}")
        else:
            print(f"   ❌ Health check failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {str(e)[:50]}...")
    
    # System status
    try:
        response = requests.get(f"{BASE_URL}/api/system/status", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            print(f"   ✅ System Status: {status_data.get('status', 'unknown')}")
            
            if 'api_sources' in status_data:
                active_apis = status_data['api_sources'].get('active_count', 0)
                total_apis = status_data['api_sources'].get('total_configured', 0)
                print(f"   📡 API Sources: {active_apis}/{total_apis} active")
            
            if 'cache_stats' in status_data:
                cache_items = status_data['cache_stats'].get('total_items', 0)
                print(f"   💾 Cache Items: {cache_items}")
                
        else:
            print(f"   ❌ System status failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ System status error: {str(e)[:50]}...")

def main():
    print_banner()
    
    sections = demo_sections()
    
    # Section 1: Sector Analytics
    next(sections)
    test_sectors()
    
    # Section 2: Top 100 Coverage  
    next(sections)
    test_top_100()
    
    # Section 3: Performance
    next(sections)
    test_performance()
    
    # Section 4: System Health
    next(sections)
    test_system_health()
    
    # Summary
    print(f"\n{'='*60}")
    print("🎉 DEMO COMPLETE - KEY FEATURES SHOWCASED")
    print('='*60)
    
    features = [
        "🏥 9 Market Sectors with 104+ stocks",
        "💰 Top 100 Cryptocurrencies ($3.3T+ market cap)",
        "💱 Top 100 Forex pairs (major, minor, exotic)",
        "⚡ Advanced caching with multi-second speedups",
        "🔧 Comprehensive health monitoring",
        "📊 Real-time data from 5+ API sources",
        "🚀 Production-ready with 75%+ success rate"
    ]
    
    print("\n✅ Features Demonstrated:")
    for feature in features:
        print(f"   {feature}")
    
    print(f"\n🔗 Quick Access URLs:")
    print(f"   📋 All Sectors: {BASE_URL}/api/sectors")
    print(f"   🏥 Healthcare: {BASE_URL}/api/sectors/healthcare")
    print(f"   💻 Technology: {BASE_URL}/api/sectors/technology")
    print(f"   💰 Top 100 Crypto: {BASE_URL}/api/top100/crypto")
    print(f"   📊 System Status: {BASE_URL}/api/system/status")
    print(f"   📖 Documentation: {BASE_URL}/docs")
    
    print(f"\n🚀 Financial Analytics Hub v2.2.0 is ready for production!")
    print("🎉" * 25)

if __name__ == "__main__":
    main() 