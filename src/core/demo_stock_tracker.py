#!/usr/bin/env python3
"""
Demo Stock Tracker with Simulated Data
For: legoprasiddh@gmail.com
Shows how the tracker works with realistic Reliance stock data
"""

import datetime
import time
import numpy as np
import random
from collections import deque

class DemoStockTracker:
    def __init__(self):
        self.stock_symbol = "RELIANCE.NS"
        self.price_data = deque(maxlen=5)  # 5-minute SMA
        self.current_price = 2450.00  # Starting price around current Reliance price
        
        print("🚀 Demo Stock Tracker with Simulated Data")
        print(f"📊 Simulating: {self.stock_symbol}")
        print(f"📧 Email configured for: prasiddhnaik40@gmail.com")
        print("=" * 60)
    
    def generate_realistic_price(self):
        """Generate realistic price movement"""
        # Simulate realistic price movements (±0.5% typical)
        change_percent = random.uniform(-0.8, 0.8)  # ±0.8% change
        price_change = self.current_price * (change_percent / 100)
        self.current_price = max(2000, self.current_price + price_change)  # Min price 2000
        
        # Generate volume (realistic range for Reliance)
        base_volume = random.randint(80000, 250000)
        volume_multiplier = random.uniform(0.5, 2.5)
        volume = int(base_volume * volume_multiplier)
        
        return {
            'price': round(self.current_price, 2),
            'volume': volume,
            'volume_ratio': volume_multiplier,
            'high': round(self.current_price * random.uniform(1.001, 1.015), 2),
            'low': round(self.current_price * random.uniform(0.985, 0.999), 2),
            'change_pct': change_percent,
            'timestamp': datetime.datetime.now()
        }
    
    def calculate_sma(self):
        """Calculate Simple Moving Average"""
        if len(self.price_data) < 3:
            return None
        return round(np.mean(list(self.price_data)), 2)
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI (simplified)"""
        if len(prices) < 5:
            return 50 + random.uniform(-15, 15)  # Random RSI for demo
        
        # Simplified RSI calculation for demo
        recent_changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [change for change in recent_changes if change > 0]
        losses = [-change for change in recent_changes if change < 0]
        
        avg_gain = np.mean(gains) if gains else 0.1
        avg_loss = np.mean(losses) if losses else 0.1
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 1)
    
    def generate_signal(self, price, sma, rsi, volume_ratio):
        """Generate trading signal"""
        signal_strength = 0
        reasons = []
        
        # SMA-based signals
        if price > sma:
            signal_strength += 1
            reasons.append("Price above SMA")
        else:
            signal_strength -= 1
            reasons.append("Price below SMA")
        
        # RSI-based signals
        if rsi < 30:  # Oversold
            signal_strength += 2
            reasons.append(f"Oversold (RSI: {rsi})")
        elif rsi > 70:  # Overbought
            signal_strength -= 2
            reasons.append(f"Overbought (RSI: {rsi})")
        
        # Volume confirmation
        if volume_ratio > 1.5:
            signal_strength += 1 if signal_strength > 0 else -1
            reasons.append(f"High volume ({volume_ratio:.1f}x avg)")
        
        # Determine signal type
        if signal_strength >= 2:
            signal_type = "BUY"
            signal_emoji = "🟢"
        elif signal_strength <= -2:
            signal_type = "SELL"
            signal_emoji = "🔴"
        else:
            signal_type = "HOLD"
            signal_emoji = "🟡"
        
        return {
            'signal': signal_type,
            'emoji': signal_emoji,
            'strength': signal_strength,
            'reasons': reasons
        }
    
    def simulate_email_alert(self, signal, stock_data):
        """Simulate email alert"""
        if signal['signal'] in ['BUY', 'SELL']:
            print(f"\n📧 EMAIL ALERT SIMULATION:")
            print(f"📨 To: prasiddhnaik40@gmail.com")
            print(f"📋 Subject: {signal['emoji']} {signal['signal']} Signal: Reliance at ₹{stock_data['price']}")
            print(f"📄 Content: {signal['signal']} signal generated")
            print(f"💪 Strength: {signal['strength']}/5")
            print(f"💡 Reasons: {', '.join(signal['reasons'])}")
            print(f"📧 ✅ Email would be sent!")
    
    def run_demo(self, iterations=10):
        """Run the demo tracker"""
        print(f"\n🚀 Running {iterations}-iteration demo...")
        print("📊 Simulating real-time stock tracking with 5-minute SMA")
        print("-" * 60)
        
        signals_generated = []
        
        for i in range(iterations):
            print(f"\n📊 Update #{i+1} - {datetime.datetime.now().strftime('%H:%M:%S')}")
            
            # Generate stock data
            stock_data = self.generate_realistic_price()
            self.price_data.append(stock_data['price'])
            
            # Display current data
            print(f"💰 Price: ₹{stock_data['price']} ({stock_data['change_pct']:+.2f}%)")
            print(f"📦 Volume: {stock_data['volume']:,} ({stock_data['volume_ratio']:.1f}x avg)")
            print(f"📈 High: ₹{stock_data['high']} | 📉 Low: ₹{stock_data['low']}")
            
            # Calculate SMA if we have enough data
            sma = self.calculate_sma()
            if sma:
                prices_list = list(self.price_data)
                rsi = self.calculate_rsi(prices_list)
                
                print(f"📈 5-min SMA: ₹{sma}")
                print(f"📊 RSI: {rsi}")
                
                # Generate signal
                signal = self.generate_signal(
                    stock_data['price'], 
                    sma, 
                    rsi, 
                    stock_data['volume_ratio']
                )
                
                print(f"{signal['emoji']} Signal: {signal['signal']} (Strength: {signal['strength']})")
                
                if signal['reasons']:
                    print(f"💡 Reasons: {', '.join(signal['reasons'])}")
                
                # Simulate email for BUY/SELL signals
                if signal['signal'] != 'HOLD':
                    self.simulate_email_alert(signal, stock_data)
                    signals_generated.append(signal['signal'])
                
            else:
                print(f"📈 SMA: Collecting data... ({len(self.price_data)}/3)")
            
            # Wait between iterations (except last one)
            if i < iterations - 1:
                print("⏳ Next update in 5 seconds...")
                time.sleep(5)
        
        # Final summary
        print(f"\n📈 Demo Summary:")
        print(f"✅ Completed {iterations} updates")
        print(f"📊 Final Price: ₹{self.current_price:.2f}")
        print(f"📈 Final SMA: ₹{self.calculate_sma()}")
        print(f"🎯 Trading Signals Generated: {len(signals_generated)}")
        if signals_generated:
            buy_count = signals_generated.count('BUY')
            sell_count = signals_generated.count('SELL')
            print(f"   🟢 BUY signals: {buy_count}")
            print(f"   🔴 SELL signals: {sell_count}")
        
        print(f"\n💡 This demonstrates how the real tracker works!")
        print(f"📧 In real mode, emails would be sent to: prasiddhnaik40@gmail.com")

def main():
    """Main demo function"""
    print("🎯 Enhanced Stock Tracker - DEMO MODE")
    print("📧 Configured for: prasiddhnaik40@gmail.com")
    print("📊 Simulating Reliance Industries (RELIANCE.NS)")
    print("💡 This shows how the tracker works with real data")
    print("=" * 70)
    
    # Create demo tracker
    demo = DemoStockTracker()
    
    # Ask user for demo preferences
    print("\n⚙️ Demo Configuration:")
    try:
        iterations = int(input("Number of price updates to simulate (default 8): ") or "8")
        if iterations <= 0:
            iterations = 8
    except ValueError:
        iterations = 8
    
    # Run the demo
    demo.run_demo(iterations)
    
    print("\n🎉 Demo completed!")
    print("\n📋 Next Steps:")
    print("1. 🔑 Set up Gmail App Password:")
    print("   - Go to Google Account > Security > App Passwords")
    print("   - Create password for 'Stock Tracker'")
    print("2. 🚀 Run: python3 enhanced_stock_tracker.py")
    print("3. 📧 Enter your App Password when prompted")
    print("4. 💰 Get real-time alerts for Reliance stock!")
    
    print(f"\n✅ Your email (prasiddhnaik40@gmail.com) is pre-configured!")

if __name__ == "__main__":
    main() 