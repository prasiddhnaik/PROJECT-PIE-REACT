#!/usr/bin/env python3
"""
Test Stock Tracker - Quick Demo Version
For: legoprasiddh@gmail.com
"""

import yfinance as yf
import datetime
import time
import numpy as np
from collections import deque

class QuickStockTest:
    def __init__(self):
        self.stock_symbol = "RELIANCE.NS"
        self.price_data = deque(maxlen=5)  # 5-minute SMA
        
        print("🚀 Quick Stock Tracker Test")
        print(f"📊 Testing: {self.stock_symbol}")
        print("=" * 50)
    
    def get_stock_data(self):
        """Get current stock data"""
        try:
            ticker = yf.Ticker(self.stock_symbol)
            
            # Try different data sources
            print("📡 Fetching data...")
            
            # Method 1: Recent history
            data1 = ticker.history(period="1d")
            if not data1.empty:
                latest = data1.iloc[-1]
                return {
                    'price': latest['Close'],
                    'volume': latest['Volume'],
                    'high': latest['High'],
                    'low': latest['Low'],
                    'timestamp': datetime.datetime.now(),
                    'source': '1-day history'
                }
            
            # Method 2: Current info
            info = ticker.info
            if 'currentPrice' in info:
                return {
                    'price': info['currentPrice'],
                    'volume': info.get('volume', 0),
                    'high': info.get('dayHigh', info['currentPrice']),
                    'low': info.get('dayLow', info['currentPrice']),
                    'timestamp': datetime.datetime.now(),
                    'source': 'ticker info'
                }
            
            # Method 3: Fast info
            fast_info = ticker.fast_info
            if hasattr(fast_info, 'last_price'):
                return {
                    'price': fast_info.last_price,
                    'volume': 0,
                    'high': fast_info.last_price,
                    'low': fast_info.last_price,
                    'timestamp': datetime.datetime.now(),
                    'source': 'fast info'
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def calculate_sma(self):
        """Calculate Simple Moving Average"""
        if len(self.price_data) < 3:  # Need at least 3 points
            return None
        return np.mean(list(self.price_data))
    
    def test_data_connection(self):
        """Test the data connection"""
        print("\n🔍 Testing Data Connection...")
        
        # Test basic connection
        stock_data = self.get_stock_data()
        
        if stock_data:
            print("✅ Connection successful!")
            print(f"💰 Current Price: ₹{stock_data['price']:.2f}")
            print(f"📊 Volume: {stock_data['volume']:,}")
            print(f"📈 High: ₹{stock_data['high']:.2f}")
            print(f"📉 Low: ₹{stock_data['low']:.2f}")
            print(f"🔗 Source: {stock_data['source']}")
            print(f"⏰ Time: {stock_data['timestamp'].strftime('%H:%M:%S')}")
            return True
        else:
            print("❌ Could not fetch data")
            print("💡 This might be because:")
            print("  - Markets are closed")
            print("  - Internet connection issues")
            print("  - API rate limiting")
            return False
    
    def run_demo(self, iterations=5):
        """Run a quick demo"""
        print(f"\n🚀 Running {iterations}-iteration demo...")
        print("📊 Collecting price data for SMA calculation")
        print("-" * 40)
        
        for i in range(iterations):
            print(f"\n📊 Update #{i+1}")
            
            stock_data = self.get_stock_data()
            
            if stock_data:
                price = stock_data['price']
                self.price_data.append(price)
                
                print(f"💰 Price: ₹{price:.2f}")
                print(f"📦 Volume: {stock_data['volume']:,}")
                
                # Calculate SMA if we have enough data
                sma = self.calculate_sma()
                if sma:
                    print(f"📈 SMA({len(self.price_data)}): ₹{sma:.2f}")
                    
                    # Simple signal
                    if price > sma:
                        signal = "🟢 BULLISH (Price > SMA)"
                    else:
                        signal = "🔴 BEARISH (Price < SMA)"
                    
                    print(f"🎯 Signal: {signal}")
                else:
                    print(f"📈 SMA: Collecting data... ({len(self.price_data)}/3)")
                
                print(f"🔗 Source: {stock_data['source']}")
                
            else:
                print("❌ Could not fetch data this iteration")
            
            # Wait between iterations (except last one)
            if i < iterations - 1:
                print("⏳ Waiting 10 seconds...")
                time.sleep(10)
        
        # Summary
        print(f"\n📈 Demo Summary:")
        print(f"✅ Completed {iterations} iterations")
        print(f"📊 Collected {len(self.price_data)} price points")
        if len(self.price_data) >= 3:
            final_sma = self.calculate_sma()
            latest_price = list(self.price_data)[-1]
            print(f"💰 Latest Price: ₹{latest_price:.2f}")
            print(f"📈 Final SMA: ₹{final_sma:.2f}")
            print(f"🎯 Trend: {'🟢 BULLISH' if latest_price > final_sma else '🔴 BEARISH'}")

def main():
    """Main function"""
    print("🎯 Quick Stock Tracker Test")
    print("📧 Configured for: prasiddhnaik40@gmail.com")
    print("📊 Testing Reliance Industries (RELIANCE.NS)")
    print("=" * 60)
    
    # Create tester
    tester = QuickStockTest()
    
    # Test connection first
    if tester.test_data_connection():
        print("\n🎉 Data connection working!")
        
        # Ask if user wants to run demo
        choice = input("\n🚀 Run 5-iteration demo? (y/n, default=y): ").strip().lower()
        if choice != 'n':
            tester.run_demo(5)
        
        print("\n✅ Test completed!")
        print("💡 If this works, your full tracker should work too!")
        print("🔧 Next step: Set up Gmail App Password and run enhanced_stock_tracker.py")
        
    else:
        print("\n⚠️ Data connection failed")
        print("💡 Possible solutions:")
        print("  1. Wait for market hours (9:15 AM - 3:30 PM IST)")
        print("  2. Check internet connection")
        print("  3. Try running again in a few minutes")
        print("  4. The full tracker has fallback methods")

if __name__ == "__main__":
    main() 