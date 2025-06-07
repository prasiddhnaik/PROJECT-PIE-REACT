#!/usr/bin/env python3
"""
Easy Stock Tracker - Pre-configured for prasiddhnaik40@gmail.com
No setup required - just run and go!
"""

import yfinance as yf
import pandas as pd
import numpy as np
import smtplib
import time
import datetime
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import deque
import json
import os

# Import configuration
from configs.config import EMAIL_CONFIG, STOCK_CONFIG, TRACKING_CONFIG

class EasyStockTracker:
    def __init__(self):
        """Initialize with pre-configured settings"""
        self.email_config = EMAIL_CONFIG
        self.stock_symbol = STOCK_CONFIG['symbol']
        self.sma_period = STOCK_CONFIG['sma_period']
        self.price_data = deque(maxlen=self.sma_period)
        self.signals = []
        self.last_signal = None
        self.last_email_time = datetime.datetime.now() - datetime.timedelta(minutes=30)
        
        # Setup logging
        logging.basicConfig(
            filename=f'easy_tracker_{datetime.date.today()}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        print("🚀 Easy Stock Tracker - Pre-configured!")
        print(f"📧 Email: {self.email_config['sender']}")
        print(f"📊 Tracking: {self.stock_symbol}")
        print(f"📈 SMA Period: {self.sma_period} minutes")
        print("=" * 60)
    
    def get_live_price(self):
        """Get live stock price with multiple fallback methods"""
        try:
            ticker = yf.Ticker(self.stock_symbol)
            
            # Try 1-day data first (most reliable)
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                latest = data.iloc[-1]
                previous = data.iloc[-2] if len(data) > 1 else latest
                
                price_change = latest['Close'] - previous['Close']
                price_change_pct = (price_change / previous['Close']) * 100
                
                avg_volume = data['Volume'].rolling(window=20).mean().iloc[-1]
                volume_ratio = latest['Volume'] / avg_volume if avg_volume > 0 else 1
                
                return {
                    'timestamp': datetime.datetime.now(),
                    'price': latest['Close'],
                    'volume': latest['Volume'],
                    'high': latest['High'],
                    'low': latest['Low'],
                    'open': latest['Open'],
                    'price_change': price_change,
                    'price_change_pct': price_change_pct,
                    'volume_ratio': volume_ratio,
                    'source': 'live_data'
                }
            
            # Fallback: Try ticker info
            info = ticker.info
            if 'currentPrice' in info:
                return {
                    'timestamp': datetime.datetime.now(),
                    'price': info['currentPrice'],
                    'volume': info.get('volume', 0),
                    'high': info.get('dayHigh', info['currentPrice']),
                    'low': info.get('dayLow', info['currentPrice']),
                    'open': info.get('previousClose', info['currentPrice']),
                    'price_change': 0,
                    'price_change_pct': 0,
                    'volume_ratio': 1,
                    'source': 'ticker_info'
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching price: {e}")
            print(f"⚠️ Data fetch error: {e}")
            return None
    
    def calculate_sma(self):
        """Calculate SMA"""
        if len(self.price_data) < self.sma_period:
            return None
        return np.mean(list(self.price_data))
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        if len(prices) < period + 1:
            return 50
            
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def generate_signal(self, current_price, sma, rsi, volume_ratio):
        """Generate trading signals"""
        signal_strength = 0
        reasons = []
        
        # Price vs SMA
        if current_price > sma:
            signal_strength += 1
            reasons.append("Price above SMA")
        else:
            signal_strength -= 1
            reasons.append("Price below SMA")
        
        # RSI signals
        if rsi < 30:
            signal_strength += 2
            reasons.append(f"Oversold (RSI: {rsi:.1f})")
        elif rsi > 70:
            signal_strength -= 2
            reasons.append(f"Overbought (RSI: {rsi:.1f})")
        
        # Volume confirmation
        if volume_ratio > STOCK_CONFIG['volume_threshold']:
            signal_strength += 1 if signal_strength > 0 else -1
            reasons.append(f"High volume ({volume_ratio:.1f}x avg)")
        
        # Signal type
        if signal_strength >= TRACKING_CONFIG['min_signal_strength']:
            signal_type = "BUY"
        elif signal_strength <= -TRACKING_CONFIG['min_signal_strength']:
            signal_type = "SELL"
        else:
            signal_type = "HOLD"
        
        return {
            'timestamp': datetime.datetime.now(),
            'price': current_price,
            'sma': sma,
            'rsi': rsi,
            'volume_ratio': volume_ratio,
            'signal': signal_type,
            'strength': signal_strength,
            'reasons': reasons
        }
    
    def send_email_alert(self, signal, stock_data):
        """Send email alert"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender']
            msg['To'] = self.email_config['recipient']
            msg['Subject'] = f"🚨 {signal['signal']} Signal: Reliance at ₹{signal['price']:.2f}"
            
            # HTML email body
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>📊 Trading Signal Alert - Reliance Industries</h2>
                
                <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px;">
                    <h3>🎯 Signal: {signal['signal']} (Strength: {signal['strength']})</h3>
                    <p><strong>Price:</strong> ₹{stock_data['price']:.2f} ({stock_data['price_change_pct']:+.2f}%)</p>
                    <p><strong>5-min SMA:</strong> ₹{signal['sma']:.2f}</p>
                    <p><strong>RSI:</strong> {signal['rsi']:.1f}</p>
                    <p><strong>Volume:</strong> {stock_data['volume']:,} ({signal['volume_ratio']:.1f}x avg)</p>
                </div>
                
                <div style="background-color: #e8f4fd; padding: 15px; border-radius: 5px; margin-top: 10px;">
                    <h3>💡 Reasons:</h3>
                    <ul>
                        {''.join([f'<li>{reason}</li>' for reason in signal['reasons']])}
                    </ul>
                </div>
                
                <p style="color: #666; font-size: 12px;">
                    Generated at {signal['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} | Easy Stock Tracker
                </p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_config['sender'], self.email_config['password'])
            server.sendmail(self.email_config['sender'], self.email_config['recipient'], msg.as_string())
            server.quit()
            
            self.last_email_time = datetime.datetime.now()
            print(f"📧 ✅ Email sent: {signal['signal']} signal")
            self.logger.info(f"Email sent: {signal['signal']} at ₹{signal['price']:.2f}")
            
        except Exception as e:
            print(f"📧 ❌ Email error: {e}")
            self.logger.error(f"Email error: {e}")
    
    def should_send_email(self, signal):
        """Check if email should be sent"""
        # Only BUY/SELL signals
        if signal['signal'] == 'HOLD':
            return False
        
        # Cooldown period
        time_since_last = datetime.datetime.now() - self.last_email_time
        if time_since_last.total_seconds() < TRACKING_CONFIG['email_cooldown']:
            return False
        
        # Don't repeat same signal
        if self.last_signal and self.last_signal['signal'] == signal['signal']:
            return False
        
        return True
    
    def run_tracker(self, duration_minutes=None):
        """Run the tracker"""
        if duration_minutes is None:
            duration_minutes = TRACKING_CONFIG['default_duration']
        
        print(f"\n🚀 Starting Easy Stock Tracker")
        print(f"⏰ Running for {duration_minutes} minutes")
        print(f"📊 Updates every {TRACKING_CONFIG['update_interval']} seconds")
        print("-" * 60)
        
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(minutes=duration_minutes)
        update_count = 0
        
        try:
            while datetime.datetime.now() < end_time:
                update_count += 1
                current_time = datetime.datetime.now()
                
                print(f"\n📊 Update #{update_count} - {current_time.strftime('%H:%M:%S')}")
                
                # Get stock data
                stock_data = self.get_live_price()
                
                if stock_data is None:
                    print("⚠️ No data available - retrying in 60 seconds...")
                    time.sleep(60)
                    continue
                
                # Add to price data
                self.price_data.append(stock_data['price'])
                
                # Display current info
                print(f"💰 Price: ₹{stock_data['price']:.2f} ({stock_data['price_change_pct']:+.2f}%)")
                print(f"📦 Volume: {stock_data['volume']:,} | 🔗 Source: {stock_data['source']}")
                
                # Calculate indicators
                sma = self.calculate_sma()
                if sma:
                    prices_list = list(self.price_data)
                    rsi = self.calculate_rsi(prices_list)
                    
                    print(f"📈 5-min SMA: ₹{sma:.2f}")
                    print(f"📊 RSI: {rsi:.1f}")
                    
                    # Generate signal
                    signal = self.generate_signal(stock_data['price'], sma, rsi, stock_data['volume_ratio'])
                    self.signals.append(signal)
                    
                    # Display signal
                    signal_emoji = "🟢" if signal['signal'] == "BUY" else "🔴" if signal['signal'] == "SELL" else "🟡"
                    print(f"{signal_emoji} Signal: {signal['signal']} (Strength: {signal['strength']})")
                    
                    if signal['reasons']:
                        print(f"💡 Reasons: {', '.join(signal['reasons'])}")
                    
                    # Send email if needed
                    if self.should_send_email(signal):
                        self.send_email_alert(signal, stock_data)
                        self.last_signal = signal
                    
                else:
                    print(f"📈 Collecting data for SMA... ({len(self.price_data)}/{self.sma_period})")
                
                # Wait for next update
                print(f"⏳ Next update in {TRACKING_CONFIG['update_interval']} seconds...")
                time.sleep(TRACKING_CONFIG['update_interval'])
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Tracker stopped by user")
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
            self.logger.error(f"Tracker error: {e}")
        
        # Summary
        runtime = datetime.datetime.now() - start_time
        signals_count = len([s for s in self.signals if s['signal'] != 'HOLD'])
        
        print(f"\n📈 Tracking Summary:")
        print(f"⏰ Runtime: {runtime}")
        print(f"📊 Total Updates: {update_count}")
        print(f"🎯 Trading Signals: {signals_count}")
        print(f"📧 Email: {self.email_config['sender']}")

def main():
    """Main function - no configuration needed!"""
    print("🎯 Easy Stock Tracker - Pre-configured for prasiddhnaik40@gmail.com")
    print("✅ No setup required - your email is already configured!")
    print("=" * 70)
    
    # Simple duration input
    try:
        duration = input(f"⏰ Duration in minutes (default {TRACKING_CONFIG['default_duration']}): ").strip()
        duration = int(duration) if duration else TRACKING_CONFIG['default_duration']
    except ValueError:
        duration = TRACKING_CONFIG['default_duration']
    
    # Create and run tracker
    try:
        tracker = EasyStockTracker()
        tracker.run_tracker(duration)
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        print("💡 Make sure you have internet connection and try again")

if __name__ == "__main__":
    main() 