#!/usr/bin/env python3
"""
Enhanced Stock Tracker - Reliance Live Price Monitor
Features:
- Real-time stock price tracking
- 5-minute Simple Moving Average (SMA) calculation
- Buy/sell signal generation
- Email alerts for trading signals
- Data logging and visualization
- Risk management alerts
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
from email.mime.base import MIMEBase
from email import encoders
import matplotlib.pyplot as plt
import seaborn as sns
from collections import deque
import json
import os

# Import configuration
from configs.config import EMAIL_CONFIG, STOCK_CONFIG, TRACKING_CONFIG

class EnhancedStockTracker:
    def __init__(self, email_config):
        """
        Initialize the Enhanced Stock Tracker
        
        Args:
            email_config (dict): Email configuration with sender, password, recipient
        """
        self.email_config = email_config
        self.stock_symbol = "RELIANCE.NS"  # Reliance Industries on NSE
        self.sma_period = 5  # 5-minute SMA
        self.price_data = deque(maxlen=self.sma_period)
        self.signals = []
        self.last_signal = None
        self.last_email_time = datetime.datetime.now() - datetime.timedelta(minutes=30)
        
        # Trading parameters
        self.rsi_period = 14
        self.volume_threshold = 1.5  # Volume spike threshold
        self.price_change_threshold = 0.5  # % price change for alerts
        
        # Setup logging
        self.setup_logging()
        
        # Load historical data if exists
        self.load_historical_data()
        
        print("🚀 Enhanced Stock Tracker Initialized")
        print(f"📊 Tracking: {self.stock_symbol}")
        print(f"📈 SMA Period: {self.sma_period} minutes")
        print(f"📧 Email alerts enabled for: {email_config['recipient']}")
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            filename=f'stock_tracker_{datetime.date.today()}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def load_historical_data(self):
        """Load historical tracking data if available"""
        try:
            if os.path.exists('tracking_data.json'):
                with open('tracking_data.json', 'r') as f:
                    data = json.load(f)
                    self.signals = data.get('signals', [])
                    print(f"📚 Loaded {len(self.signals)} historical signals")
        except Exception as e:
            print(f"⚠️ Could not load historical data: {e}")
            
    def save_data(self):
        """Save tracking data to file"""
        try:
            data = {
                'signals': self.signals[-100:],  # Keep last 100 signals
                'last_update': datetime.datetime.now().isoformat()
            }
            with open('tracking_data.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save data: {e}")
    
    def get_live_price(self):
        """
        Fetch live stock price and volume data
        
        Returns:
            dict: Stock data including price, volume, change%
        """
        try:
            ticker = yf.Ticker(self.stock_symbol)
            
            # Get real-time data
            todays_data = ticker.history(period="1d", interval="1m")
            
            if todays_data.empty:
                return None
                
            latest = todays_data.iloc[-1]
            previous = todays_data.iloc[-2] if len(todays_data) > 1 else latest
            
            # Calculate additional metrics
            price_change = latest['Close'] - previous['Close']
            price_change_pct = (price_change / previous['Close']) * 100
            
            # Volume analysis
            avg_volume = todays_data['Volume'].rolling(window=20).mean().iloc[-1]
            volume_ratio = latest['Volume'] / avg_volume if avg_volume > 0 else 1
            
            stock_data = {
                'timestamp': datetime.datetime.now(),
                'price': latest['Close'],
                'volume': latest['Volume'],
                'high': latest['High'],
                'low': latest['Low'],
                'open': latest['Open'],
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'volume_ratio': volume_ratio
            }
            
            return stock_data
            
        except Exception as e:
            self.logger.error(f"Error fetching live price: {e}")
            print(f"❌ Error fetching price: {e}")
            return None
    
    def calculate_sma(self):
        """
        Calculate Simple Moving Average
        
        Returns:
            float: Current SMA value or None if insufficient data
        """
        if len(self.price_data) < self.sma_period:
            return None
        
        return np.mean(list(self.price_data))
    
    def calculate_rsi(self, prices, period=14):
        """
        Calculate Relative Strength Index
        
        Args:
            prices (list): List of price values
            period (int): RSI calculation period
            
        Returns:
            float: RSI value
        """
        if len(prices) < period + 1:
            return 50  # Neutral RSI
            
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
        """
        Generate buy/sell signals based on multiple indicators
        
        Args:
            current_price (float): Current stock price
            sma (float): Simple Moving Average
            rsi (float): RSI value
            volume_ratio (float): Volume compared to average
            
        Returns:
            dict: Signal information
        """
        signal_strength = 0
        signal_type = "HOLD"
        reasons = []
        
        # SMA-based signals
        if current_price > sma:
            signal_strength += 1
            reasons.append("Price above SMA")
        else:
            signal_strength -= 1
            reasons.append("Price below SMA")
        
        # RSI-based signals
        if rsi < 30:  # Oversold
            signal_strength += 2
            reasons.append(f"Oversold (RSI: {rsi:.1f})")
        elif rsi > 70:  # Overbought
            signal_strength -= 2
            reasons.append(f"Overbought (RSI: {rsi:.1f})")
        
        # Volume confirmation
        if volume_ratio > self.volume_threshold:
            signal_strength += 1 if signal_strength > 0 else -1
            reasons.append(f"High volume ({volume_ratio:.1f}x avg)")
        
        # Determine signal type
        if signal_strength >= 2:
            signal_type = "BUY"
        elif signal_strength <= -2:
            signal_type = "SELL"
        
        signal = {
            'timestamp': datetime.datetime.now(),
            'price': current_price,
            'sma': sma,
            'rsi': rsi,
            'volume_ratio': volume_ratio,
            'signal': signal_type,
            'strength': signal_strength,
            'reasons': reasons
        }
        
        return signal
    
    def should_send_email(self, signal):
        """
        Determine if an email alert should be sent
        
        Args:
            signal (dict): Generated signal
            
        Returns:
            bool: Whether to send email
        """
        # Don't spam emails
        time_since_last = datetime.datetime.now() - self.last_email_time
        if time_since_last.total_seconds() < 300:  # 5 minutes minimum
            return False
        
        # Only send for BUY/SELL signals
        if signal['signal'] == 'HOLD':
            return False
        
        # Don't repeat same signal type
        if self.last_signal and self.last_signal['signal'] == signal['signal']:
            return False
        
        return True
    
    def send_email_alert(self, signal, stock_data):
        """
        Send email alert for trading signal
        
        Args:
            signal (dict): Trading signal
            stock_data (dict): Current stock data
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender']
            msg['To'] = self.email_config['recipient']
            
            # Email subject
            subject = f"🚨 {signal['signal']} Signal: Reliance at ₹{signal['price']:.2f}"
            msg['Subject'] = subject
            
            # Email body
            signal_emoji = "🟢" if signal['signal'] == "BUY" else "🔴" if signal['signal'] == "SELL" else "🟡"
            
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>{signal_emoji} Trading Signal Alert - Reliance Industries</h2>
                
                <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    <h3>📊 Signal Details</h3>
                    <p><strong>Signal:</strong> <span style="color: {'green' if signal['signal'] == 'BUY' else 'red' if signal['signal'] == 'SELL' else 'orange'}; font-weight: bold;">{signal['signal']}</span></p>
                    <p><strong>Signal Strength:</strong> {signal['strength']}/5</p>
                    <p><strong>Timestamp:</strong> {signal['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div style="background-color: #e8f4fd; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    <h3>💰 Price Information</h3>
                    <p><strong>Current Price:</strong> ₹{stock_data['price']:.2f}</p>
                    <p><strong>Price Change:</strong> ₹{stock_data['price_change']:+.2f} ({stock_data['price_change_pct']:+.2f}%)</p>
                    <p><strong>5-min SMA:</strong> ₹{signal['sma']:.2f}</p>
                    <p><strong>Day High:</strong> ₹{stock_data['high']:.2f}</p>
                    <p><strong>Day Low:</strong> ₹{stock_data['low']:.2f}</p>
                </div>
                
                <div style="background-color: #fff2e8; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    <h3>📈 Technical Indicators</h3>
                    <p><strong>RSI (14):</strong> {signal['rsi']:.1f}</p>
                    <p><strong>Volume Ratio:</strong> {signal['volume_ratio']:.1f}x average</p>
                    <p><strong>Volume:</strong> {stock_data['volume']:,}</p>
                </div>
                
                <div style="background-color: #f0f8e8; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    <h3>🎯 Signal Reasoning</h3>
                    <ul>
                        {''.join([f'<li>{reason}</li>' for reason in signal['reasons']])}
                    </ul>
                </div>
                
                <div style="background-color: #ffe8e8; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    <h3>⚠️ Risk Management</h3>
                    <p><em>This is an automated signal. Please:</em></p>
                    <ul>
                        <li>Verify with additional analysis</li>
                        <li>Consider your risk tolerance</li>
                        <li>Use appropriate position sizing</li>
                        <li>Set stop-loss levels</li>
                    </ul>
                </div>
                
                <p style="font-size: 12px; color: #666;">
                    Generated by Enhanced Stock Tracker | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_config['sender'], self.email_config['password'])
            text = msg.as_string()
            server.sendmail(self.email_config['sender'], self.email_config['recipient'], text)
            server.quit()
            
            self.last_email_time = datetime.datetime.now()
            self.logger.info(f"Email alert sent: {signal['signal']} at ₹{signal['price']:.2f}")
            print(f"📧 Email alert sent: {signal['signal']} signal")
            
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            print(f"❌ Email error: {e}")
    
    def create_visualization(self):
        """Create and save price chart with signals"""
        try:
            if len(self.signals) < 10:
                return
                
            # Prepare data
            df = pd.DataFrame(self.signals[-50:])  # Last 50 signals
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Create figure
            plt.figure(figsize=(15, 10))
            
            # Price and SMA plot
            plt.subplot(3, 1, 1)
            plt.plot(df['timestamp'], df['price'], label='Price', linewidth=2, color='blue')
            plt.plot(df['timestamp'], df['sma'], label='5-min SMA', linewidth=1, color='orange')
            
            # Color-code signals
            buy_signals = df[df['signal'] == 'BUY']
            sell_signals = df[df['signal'] == 'SELL']
            
            plt.scatter(buy_signals['timestamp'], buy_signals['price'], 
                       color='green', marker='^', s=100, label='BUY', zorder=5)
            plt.scatter(sell_signals['timestamp'], sell_signals['price'], 
                       color='red', marker='v', s=100, label='SELL', zorder=5)
            
            plt.title('Reliance Stock Price with Trading Signals', fontsize=14, fontweight='bold')
            plt.ylabel('Price (₹)')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # RSI plot
            plt.subplot(3, 1, 2)
            plt.plot(df['timestamp'], df['rsi'], label='RSI', color='purple', linewidth=2)
            plt.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Overbought (70)')
            plt.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Oversold (30)')
            plt.axhline(y=50, color='gray', linestyle='-', alpha=0.5)
            plt.title('RSI (14)', fontsize=12)
            plt.ylabel('RSI')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # Volume ratio plot
            plt.subplot(3, 1, 3)
            colors = ['green' if x > 1.5 else 'orange' if x > 1 else 'gray' for x in df['volume_ratio']]
            plt.bar(df['timestamp'], df['volume_ratio'], color=colors, alpha=0.7)
            plt.axhline(y=1.5, color='red', linestyle='--', alpha=0.7, label='High Volume (1.5x)')
            plt.title('Volume Ratio vs Average', fontsize=12)
            plt.ylabel('Volume Ratio')
            plt.xlabel('Time')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(f'reliance_analysis_{datetime.date.today()}.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            print("📊 Analysis chart saved")
            
        except Exception as e:
            print(f"⚠️ Visualization error: {e}")
    
    def run_tracker(self, duration_minutes=60):
        """
        Run the stock tracker for specified duration
        
        Args:
            duration_minutes (int): How long to run the tracker
        """
        print(f"\n🚀 Starting Enhanced Stock Tracker")
        print(f"⏰ Running for {duration_minutes} minutes")
        print(f"📊 Monitoring {self.stock_symbol} every minute")
        print("-" * 50)
        
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(minutes=duration_minutes)
        iteration = 0
        
        try:
            while datetime.datetime.now() < end_time:
                iteration += 1
                current_time = datetime.datetime.now()
                
                # Get live data
                stock_data = self.get_live_price()
                
                if stock_data is None:
                    print("⚠️ Could not fetch data, retrying in 60 seconds...")
                    time.sleep(60)
                    continue
                
                # Add price to rolling window
                self.price_data.append(stock_data['price'])
                
                # Calculate indicators
                sma = self.calculate_sma()
                prices_list = list(self.price_data)
                rsi = self.calculate_rsi(prices_list)
                
                if sma is not None:
                    # Generate signal
                    signal = self.generate_signal(
                        stock_data['price'], 
                        sma, 
                        rsi, 
                        stock_data['volume_ratio']
                    )
                    
                    # Store signal
                    self.signals.append(signal)
                    
                    # Display current status
                    print(f"\n📊 Update #{iteration} - {current_time.strftime('%H:%M:%S')}")
                    print(f"💰 Price: ₹{stock_data['price']:.2f} ({stock_data['price_change_pct']:+.2f}%)")
                    print(f"📈 5-min SMA: ₹{sma:.2f}")
                    print(f"📊 RSI: {rsi:.1f}")
                    print(f"📦 Volume: {stock_data['volume']:,} ({stock_data['volume_ratio']:.1f}x avg)")
                    
                    signal_emoji = "🟢" if signal['signal'] == "BUY" else "🔴" if signal['signal'] == "SELL" else "🟡"
                    print(f"{signal_emoji} Signal: {signal['signal']} (Strength: {signal['strength']})")
                    
                    if signal['reasons']:
                        print(f"💡 Reasons: {', '.join(signal['reasons'])}")
                    
                    # Send email if needed
                    if self.should_send_email(signal):
                        self.send_email_alert(signal, stock_data)
                        self.last_signal = signal
                    
                    # Log the data
                    self.logger.info(f"Price: ₹{stock_data['price']:.2f}, SMA: ₹{sma:.2f}, Signal: {signal['signal']}")
                    
                    # Save data periodically
                    if iteration % 10 == 0:
                        self.save_data()
                        self.create_visualization()
                
                else:
                    print(f"📊 Update #{iteration} - Collecting data... ({len(self.price_data)}/{self.sma_period})")
                    print(f"💰 Current Price: ₹{stock_data['price']:.2f}")
                
                # Wait for next update (60 seconds for 1-minute intervals)
                print("⏳ Next update in 60 seconds...")
                time.sleep(60)
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Tracker stopped by user")
        except Exception as e:
            print(f"\n\n❌ Tracker error: {e}")
            self.logger.error(f"Tracker error: {e}")
        
        finally:
            # Final save and cleanup
            self.save_data()
            self.create_visualization()
            
            # Summary
            total_signals = len([s for s in self.signals if s['signal'] != 'HOLD'])
            buy_signals = len([s for s in self.signals if s['signal'] == 'BUY'])
            sell_signals = len([s for s in self.signals if s['signal'] == 'SELL'])
            
            print(f"\n📈 Tracking Summary:")
            print(f"⏰ Runtime: {datetime.datetime.now() - start_time}")
            print(f"📊 Total Updates: {iteration}")
            print(f"🎯 Trading Signals: {total_signals} (🟢{buy_signals} BUY, 🔴{sell_signals} SELL)")
            print(f"💾 Data saved to: tracking_data.json")
            print(f"📊 Chart saved to: reliance_analysis_{datetime.date.today()}.png")

def main():
    """Main function to run the enhanced stock tracker"""
    
    print("🚀 Enhanced Stock Tracker for Reliance Industries")
    print("=" * 60)
    
    # Email configuration with pre-filled email
    print("\n📧 Email Configuration:")
    print("Note: For Gmail, use an App Password instead of your regular password")
    print("Setup: Google Account > Security > 2-Step Verification > App Passwords")
    
            # Pre-fill the user's email
        default_email = "your-email@gmail.com"
    sender_email = input(f"Enter your email address ({default_email}): ").strip()
    if not sender_email:
        sender_email = default_email
    
    password = input("Enter your Gmail App Password (16 characters): ").strip()
    
    recipient_email = input(f"Enter recipient email ({sender_email}): ").strip()
    if not recipient_email:
        recipient_email = sender_email
    
    email_config = {
        'sender': sender_email,
        'password': password,
        'recipient': recipient_email
    }
    
    # Validate email config
    if not all(email_config.values()):
        print("❌ Email configuration incomplete!")
        return
    
    # Duration configuration
    print(f"\n⏰ Duration Configuration:")
    try:
        duration = int(input("Enter tracking duration in minutes (default 60): ") or "60")
        if duration <= 0:
            duration = 60
    except ValueError:
        duration = 60
    
    # Create and run tracker
    try:
        tracker = EnhancedStockTracker(email_config)
        tracker.run_tracker(duration_minutes=duration)
    except Exception as e:
        print(f"❌ Failed to start tracker: {e}")

if __name__ == "__main__":
    main() 