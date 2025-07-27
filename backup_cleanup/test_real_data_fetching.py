#!/usr/bin/env python3
"""
Real-Time Data Fetching Test
============================
Comprehensive test of all data sources and APIs to fetch real-time
financial data from the internet.

This script demonstrates:
- Stock data from multiple providers
- Crypto data from multiple sources
- Market overview and indices
- Search functionality
- Individual symbol data
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# API Base URL
API_BASE = "http://localhost:8001"

class RealDataFetcher:
    """Comprehensive real-time data fetcher"""
    
    def __init__(self):
        self.session = None
        self.results = {}
        
    async def get_session(self):
        """Get aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def fetch_data(self, endpoint: str, params: Dict = None) -> Dict:
        """Fetch data from API endpoint"""
        session = await self.get_session()
        url = f"{API_BASE}{endpoint}"
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}", "endpoint": endpoint}
        except Exception as e:
            return {"error": str(e), "endpoint": endpoint}
    
    async def test_market_overview(self):
        """Test comprehensive market overview"""
        print("🔍 Testing Market Overview...")
        data = await self.fetch_data("/api/data/market/overview")
        
        if "error" not in data:
            stocks = data.get("data", {}).get("stocks", [])
            crypto = data.get("data", {}).get("crypto", [])
            summary = data.get("data", {}).get("summary", {})
            
            print(f"✅ Market Overview: {len(stocks)} stocks, {len(crypto)} crypto")
            print(f"📊 Top Stock: {summary.get('top_stock', {}).get('symbol', 'N/A')} - ${summary.get('top_stock', {}).get('price', 0):.2f}")
            print(f"🪙 Top Crypto: {summary.get('top_crypto', {}).get('symbol', 'N/A')} - ${summary.get('top_crypto', {}).get('price', 0):.2f}")
        else:
            print(f"❌ Market Overview Error: {data['error']}")
        
        self.results["market_overview"] = data
    
    async def test_stock_data(self):
        """Test stock data fetching"""
        print("\n📈 Testing Stock Data...")
        
        # Test top stocks
        top_stocks = await self.fetch_data("/api/data/stocks/top", {"limit": 5})
        if "error" not in top_stocks:
            stocks = top_stocks.get("data", [])
            print(f"✅ Top Stocks: {len(stocks)} stocks fetched")
            for stock in stocks[:3]:
                print(f"   {stock['symbol']}: ${stock['price']:.2f} ({stock['change_percent']:+.2f}%)")
        else:
            print(f"❌ Top Stocks Error: {top_stocks['error']}")
        
        # Test individual stock
        aapl_data = await self.fetch_data("/api/data/stock/AAPL")
        if "error" not in aapl_data:
            stock = aapl_data.get("data", {})
            print(f"✅ AAPL: ${stock.get('price', 0):.2f} ({stock.get('change_percent', 0):+.2f}%)")
        else:
            print(f"❌ AAPL Error: {aapl_data['error']}")
        
        self.results["stock_data"] = {"top": top_stocks, "individual": aapl_data}
    
    async def test_crypto_data(self):
        """Test crypto data fetching"""
        print("\n🪙 Testing Crypto Data...")
        
        # Test top crypto
        top_crypto = await self.fetch_data("/api/data/crypto/top", {"limit": 5})
        if "error" not in top_crypto:
            crypto = top_crypto.get("data", [])
            print(f"✅ Top Crypto: {len(crypto)} cryptocurrencies fetched")
            for coin in crypto[:3]:
                print(f"   {coin['symbol']}: ${coin['price']:.2f} ({coin['change_24h']:+.2f}%)")
        else:
            print(f"❌ Top Crypto Error: {top_crypto['error']}")
        
        # Test individual crypto
        btc_data = await self.fetch_data("/api/data/crypto/bitcoin")
        if "error" not in btc_data:
            coin = btc_data.get("data", {})
            print(f"✅ Bitcoin: ${coin.get('price', 0):.2f} ({coin.get('change_24h', 0):+.2f}%)")
        else:
            print(f"❌ Bitcoin Error: {btc_data['error']}")
        
        self.results["crypto_data"] = {"top": top_crypto, "individual": btc_data}
    
    async def test_search_functionality(self):
        """Test search functionality"""
        print("\n🔍 Testing Search Functionality...")
        
        # Test stock search
        stock_search = await self.fetch_data("/api/data/search", {"q": "AAPL", "type": "stock"})
        if "error" not in stock_search:
            results = stock_search.get("data", [])
            print(f"✅ Stock Search: Found {len(results)} results for 'AAPL'")
        else:
            print(f"❌ Stock Search Error: {stock_search['error']}")
        
        # Test crypto search
        crypto_search = await self.fetch_data("/api/data/search", {"q": "bitcoin", "type": "crypto"})
        if "error" not in crypto_search:
            results = crypto_search.get("data", [])
            print(f"✅ Crypto Search: Found {len(results)} results for 'bitcoin'")
        else:
            print(f"❌ Crypto Search Error: {crypto_search['error']}")
        
        self.results["search"] = {"stock": stock_search, "crypto": crypto_search}
    
    async def test_nse_data(self):
        """Test NSE specific data"""
        print("\n🇮🇳 Testing NSE Data...")
        
        # Test NSE indices
        indices = await self.fetch_data("/api/nse/indices")
        if "error" not in indices:
            data = indices.get("data", [])
            print(f"✅ NSE Indices: {len(data)} indices fetched")
            for index in data[:3]:
                print(f"   {index.get('symbol', 'N/A')}: {index.get('lastPrice', 0):.2f}")
        else:
            print(f"❌ NSE Indices Error: {indices['error']}")
        
        # Test NSE stock quote
        hdfc_data = await self.fetch_data("/api/nse/quote/HDFCBANK")
        if "error" not in hdfc_data:
            stock = hdfc_data.get("data", {})
            print(f"✅ HDFCBANK: ₹{stock.get('lastPrice', 0):.2f}")
        else:
            print(f"❌ HDFCBANK Error: {hdfc_data['error']}")
        
        self.results["nse_data"] = {"indices": indices, "stock": hdfc_data}
    
    async def test_ai_integration(self):
        """Test AI integration"""
        print("\n🤖 Testing AI Integration...")
        
        # Test AI chat
        chat_data = {
            "message": "What's the current market sentiment for Bitcoin?",
            "context": "financial_analysis"
        }
        
        chat_response = await self.fetch_data("/api/ai/chat", chat_data)
        if "error" not in chat_response:
            print("✅ AI Chat: Response received")
        else:
            print(f"❌ AI Chat Error: {chat_response['error']}")
        
        self.results["ai_integration"] = chat_response
    
    async def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Real-Time Data Fetching Test")
        print("=" * 60)
        print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 API Base: {API_BASE}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        await self.test_market_overview()
        await self.test_stock_data()
        await self.test_crypto_data()
        await self.test_search_functionality()
        await self.test_nse_data()
        await self.test_ai_integration()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        print(f"⏱️  Total Duration: {duration:.2f} seconds")
        print(f"🔗 API Base: {API_BASE}")
        print(f"📈 Data Sources: Multi-Provider System")
        print(f"🌍 Coverage: Global Stocks + Crypto + NSE")
        print(f"🤖 AI Integration: Available")
        
        # Save results
        with open("real_data_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"💾 Results saved to: real_data_test_results.json")
        print("=" * 60)
        print("✅ Comprehensive Real-Time Data Fetching Test Complete!")
        
        if self.session:
            await self.session.close()

async def main():
    """Main function"""
    fetcher = RealDataFetcher()
    await fetcher.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main()) 