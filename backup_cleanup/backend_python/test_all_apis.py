import asyncio
import aiohttp
import logging
from datetime import datetime
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our API key manager
try:
    from api_key_manager import api_keys
    logger.info("API key manager imported successfully")
except ImportError as e:
    logger.error(f"Failed to import API key manager: {e}")
    print(f"Error: Failed to import API key manager: {e}")
    sys.exit(1)

async def test_polygon():
    """Test Polygon.io API"""
    key = api_keys.get_key('polygon')
    if not key:
        return "❌ Polygon: No key configured"
    
    url = f"https://api.polygon.io/v2/aggs/ticker/AAPL/prev?apiKey={key}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return f"✅ Polygon: Working! Status: {data.get('status', 'Unknown')}"
                else:
                    return f"❌ Polygon: HTTP {response.status}"
    except Exception as e:
        return f"❌ Polygon: {str(e)}"

async def test_marketstack():
    """Test Marketstack API"""
    key = api_keys.get_key('marketstack')
    if not key:
        return "❌ Marketstack: No key configured"
    
    # Note: Marketstack uses HTTP (not HTTPS) for free tier
    url = f"http://api.marketstack.com/v1/eod/latest?access_key={key}&symbols=AAPL"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return f"✅ Marketstack: Working! ({100 - api_keys.keys['marketstack']['usage']['month']}/100 calls remaining this month)"
                else:
                    return f"❌ Marketstack: HTTP {response.status}"
    except Exception as e:
        return f"❌ Marketstack: {str(e)}"

async def test_alpha_vantage():
    """Test Alpha Vantage API"""
    key = api_keys.get_key('alpha_vantage')
    if not key:
        return "❌ Alpha Vantage: No key configured"
    
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey={key}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if "Global Quote" in data:
                        return "✅ Alpha Vantage: Working!"
                    elif "Note" in data:
                        return "⚠️ Alpha Vantage: Rate limit warning"
                    else:
                        return "❌ Alpha Vantage: Invalid response"
                else:
                    return f"❌ Alpha Vantage: HTTP {response.status}"
    except Exception as e:
        return f"❌ Alpha Vantage: {str(e)}"

async def test_twelve_data():
    """Test Twelve Data API"""
    key = api_keys.get_key('twelve_data')
    if not key:
        return "❌ Twelve Data: No key configured"
    
    url = f"https://api.twelvedata.com/quote?symbol=AAPL&apikey={key}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if "price" in data:
                        return f"✅ Twelve Data: Working! Price: ${data['price']}"
                    else:
                        return "❌ Twelve Data: Invalid response"
                else:
                    return f"❌ Twelve Data: HTTP {response.status}"
    except Exception as e:
        return f"❌ Twelve Data: {str(e)}"

async def test_yahoo():
    """Test Yahoo Finance (unofficial)"""
    try:
        import yfinance as yf
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        if info and len(info) > 5:
            price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            return f"✅ Yahoo Finance: Working! Price: ${price}"
        else:
            return "❌ Yahoo Finance: Failed to get data"
    except Exception as e:
        return f"❌ Yahoo Finance: {str(e)}"

async def main():
    print("🔑 Testing All Configured API Keys")
    print("=" * 50)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Show safe version of keys
    print("📋 Configured Keys (masked):")
    for service, masked_key in api_keys.export_keys_safely().items():
        print(f"  {service}: {masked_key}")
    
    print("\n🧪 API Tests:")
    
    # Test all APIs
    tests = await asyncio.gather(
        test_polygon(),
        test_marketstack(),
        test_alpha_vantage(),
        test_twelve_data(),
        test_yahoo()
    )
    
    for result in tests:
        print(f"  {result}")
    
    print("\n📊 API Availability:")
    available = api_keys.get_available_apis()
    for service, is_available in available.items():
        status = "✅ Available" if is_available else "❌ Limit reached or no key"
        print(f"  {service}: {status}")
    
    print("\n💡 Recommendations:")
    print("  1. Yahoo Finance (no key needed) - Use as primary")
    print("  2. Finnhub (60/min) - Get free key at finnhub.io")
    print("  3. Twelve Data (8/min, 800/day) - Good secondary option")
    print("  4. Alpha Vantage (5/min, 500/day) - Good tertiary option")
    print("  5. Marketstack - Very limited (100/month), use sparingly")

if __name__ == "__main__":
    asyncio.run(main()) 