#!/usr/bin/env python3
"""
Background Stock Tracker - Runs alongside Financial Analytics Hub
Background Stock Tracker
Runs silently in background while dashboard is active
"""

import yfinance as yf
import numpy as np
import smtplib
import time
import datetime
import logging
import threading
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import deque
import os
import signal
import sys
import pytz  # Add timezone support

# Import configuration
try:
    from config import EMAIL_CONFIG, STOCK_CONFIG, TRACKING_CONFIG, STOCK_CATEGORIES
except ImportError:
    # Fallback configuration if config.py is not found
    EMAIL_CONFIG = {
            'sender': 'your-email@gmail.com',
    'recipient': 'your-email@gmail.com',
        'password': 'your_app_password_here'
    }
    
    STOCK_CATEGORIES = {
        'tech': {
            'name': 'Technology Companies',
            'stocks': {
                'TCS.NS': {'name': 'Tata Consultancy Services', 'sector': 'IT Services'},
                'INFY.NS': {'name': 'Infosys Limited', 'sector': 'IT Services'},
                'RELIANCE.NS': {'name': 'Reliance Industries', 'sector': 'Oil & Gas'}
            }
        }
    }
    
    STOCK_CONFIG = {
        'category': 'tech',
        'symbol': 'TCS.NS',
        'sma_period': 5,
        'volume_threshold': 1.5
    }
    
    TRACKING_CONFIG = {
        'update_interval': 60,
        'default_duration': 60,
        'email_cooldown': 300,
        'min_signal_strength': 2,
        'status_email_interval': 1800,
        'send_status_emails': True
    }

class BackgroundStockTracker:
    def __init__(self, category=None, stock_symbol=None):
        """Initialize background tracker with category support"""
        self.email_config = EMAIL_CONFIG
        
        # Set up stock tracking
        self.current_category = category or STOCK_CONFIG.get('category', 'tech')
        self.stock_symbol = stock_symbol or STOCK_CONFIG['symbol']
        
        # Validate category and stock
        if self.current_category not in STOCK_CATEGORIES:
            print(f"⚠️ Category '{self.current_category}' not found, using 'tech'")
            self.current_category = 'tech'
        
        available_stocks = STOCK_CATEGORIES[self.current_category]['stocks']
        if self.stock_symbol not in available_stocks:
            # Use first stock in category if specified stock not found
            self.stock_symbol = list(available_stocks.keys())[0]
            print(f"⚠️ Stock not found in category, using {self.stock_symbol}")
        
        # Get stock details
        self.stock_info = available_stocks[self.stock_symbol]
        self.category_info = STOCK_CATEGORIES[self.current_category]
        
        self.sma_period = STOCK_CONFIG['sma_period']
        self.price_data = deque(maxlen=self.sma_period)
        self.signals = []
        self.last_signal = None
        self.last_email_time = datetime.datetime.now() - datetime.timedelta(minutes=30)
        self.last_status_email_time = datetime.datetime.now()  # Track status emails separately
        self.running = False
        self.thread = None
        
        # Setup logging for background operation
        logging.basicConfig(
            filename=f'background_tracker_{datetime.date.today()}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filemode='a'
        )
        self.logger = logging.getLogger(__name__)
        
        # Load existing data if available
        self.load_data()
        
        print(f"🔄 Background Stock Tracker initialized for {self.email_config['sender']}")
        print(f"📂 Category: {self.category_info['name']} ({self.current_category})")
        print(f"📊 Stock: {self.stock_info['name']} ({self.stock_symbol}) - {self.stock_info['sector']}")
        print(f"📧 Status emails will be sent every {TRACKING_CONFIG['status_email_interval']//60} minutes (market hours only)")
        
        # Show available categories
        print(f"\n📋 Available Categories:")
        for cat_key, cat_info in STOCK_CATEGORIES.items():
            status = "🔵 ACTIVE" if cat_key == self.current_category else "⚪"
            print(f"   {status} {cat_key}: {cat_info['name']} ({len(cat_info['stocks'])} stocks)")
    
    def load_data(self):
        """Load existing tracking data"""
        try:
            if os.path.exists('background_tracker_data.json'):
                with open('background_tracker_data.json', 'r') as f:
                    data = json.load(f)
                    self.signals = data.get('signals', [])[-50:]  # Keep last 50
                    print(f"📚 Loaded {len(self.signals)} previous signals")
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
    
    def save_data(self):
        """Save tracking data"""
        try:
            data = {
                'signals': self.signals[-100:],  # Keep last 100
                'last_update': datetime.datetime.now().isoformat(),
                'tracker_info': {
                    'stock': self.stock_symbol,
                    'email': self.email_config['sender'],
                    'sma_period': self.sma_period
                }
            }
            with open('background_tracker_data.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving data: {e}")
    
    def get_live_price(self):
        """Get live stock price quietly"""
        try:
            ticker = yf.Ticker(self.stock_symbol)
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
                    'price_change': price_change,
                    'price_change_pct': price_change_pct,
                    'volume_ratio': volume_ratio
                }
            return None
        except Exception as e:
            self.logger.error(f"Error fetching price: {e}")
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
    
    def is_market_open(self):
        """Check if Indian stock market (NSE) is open"""
        try:
            # Get current time in IST
            ist = pytz.timezone('Asia/Kolkata')
            now_ist = datetime.datetime.now(ist)
            
            # Check if it's a weekday (Monday=0, Sunday=6)
            if now_ist.weekday() >= 5:  # Saturday or Sunday
                return False
            
            # NSE trading hours: 9:15 AM to 3:30 PM IST
            market_open = now_ist.replace(hour=9, minute=15, second=0, microsecond=0)
            market_close = now_ist.replace(hour=15, minute=30, second=0, microsecond=0)
            
            # Check if current time is within trading hours
            if market_open <= now_ist <= market_close:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking market hours: {e}")
            # Default to True if we can't determine market status
            return True
    
    def generate_signal(self, current_price, sma, rsi, volume_ratio):
        """Generate trading signals"""
        signal_strength = 0
        reasons = []
        
        if current_price > sma:
            signal_strength += 1
            reasons.append("Price above SMA")
        else:
            signal_strength -= 1
            reasons.append("Price below SMA")
        
        if rsi < 30:
            signal_strength += 2
            reasons.append(f"Oversold (RSI: {rsi:.1f})")
        elif rsi > 70:
            signal_strength -= 2
            reasons.append(f"Overbought (RSI: {rsi:.1f})")
        
        if volume_ratio > STOCK_CONFIG['volume_threshold']:
            signal_strength += 1 if signal_strength > 0 else -1
            reasons.append(f"High volume ({volume_ratio:.1f}x avg)")
        
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
        """Send email alert quietly"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender']
            msg['To'] = self.email_config['recipient']
            msg['Subject'] = f"🚨 {signal['signal']} Signal: {self.stock_info['name']} at ₹{signal['price']:.2f} ({self.current_category.upper()})"
            
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>📊 Background Trading Alert - {self.stock_info['name']}</h2>
                <p><em>Alert from Financial Analytics Hub Background Tracker</em></p>
                
                <div style="background-color: #f0f8ff; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
                    <h3>📂 Stock Information</h3>
                    <p><strong>Category:</strong> {self.category_info['name']} ({self.current_category.upper()})</p>
                    <p><strong>Company:</strong> {self.stock_info['name']} ({self.stock_symbol})</p>
                    <p><strong>Sector:</strong> {self.stock_info['sector']}</p>
                </div>
                
                <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px;">
                    <h3>🎯 Signal: {signal['signal']} (Strength: {signal['strength']})</h3>
                    <p><strong>Price:</strong> ₹{stock_data['price']:.2f} ({stock_data['price_change_pct']:+.2f}%)</p>
                    <p><strong>5-min SMA:</strong> ₹{signal['sma']:.2f}</p>
                    <p><strong>RSI:</strong> {signal['rsi']:.1f}</p>
                    <p><strong>Volume:</strong> {stock_data['volume']:,} ({signal['volume_ratio']:.1f}x avg)</p>
                </div>
                
                <div style="background-color: #e8f4fd; padding: 15px; border-radius: 5px; margin-top: 10px;">
                    <h3>💡 Signal Reasons:</h3>
                    <ul>
                        {''.join([f'<li>{reason}</li>' for reason in signal['reasons']])}
                    </ul>
                </div>
                
                <div style="background-color: #fff9e6; padding: 15px; border-radius: 5px; margin-top: 10px;">
                    <p><strong>📊 Dashboard Integration:</strong> This alert was generated by your background stock tracker running alongside the Financial Analytics Hub.</p>
                    <p><strong>🔗 Check Dashboard:</strong> View detailed analysis at localhost:8501</p>
                    <p><strong>🔄 Category Switch:</strong> You can switch between {len(STOCK_CATEGORIES)} categories (tech, banking, pharma, energy, fmcg, auto)</p>
                </div>
                
                <p style="color: #666; font-size: 12px;">
                    Generated at {signal['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} | Background Stock Tracker v2.0
                </p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_config['sender'], self.email_config['password'])
            server.sendmail(self.email_config['sender'], self.email_config['recipient'], msg.as_string())
            server.quit()
            
            self.last_email_time = datetime.datetime.now()
            self.logger.info(f"Background email sent: {signal['signal']} at ₹{signal['price']:.2f}")
            
        except Exception as e:
            self.logger.error(f"Email error: {e}")
    
    def send_status_email(self, stock_data, signal):
        """Send 30-minute status email"""
        try:
            # Get market status
            market_open = self.is_market_open()
            ist = pytz.timezone('Asia/Kolkata')
            now_ist = datetime.datetime.now(ist)
            
            # Calculate next market open time
            if market_open:
                market_status = "🟢 OPEN"
                next_close = now_ist.replace(hour=15, minute=30, second=0, microsecond=0)
                time_info = f"Closes at {next_close.strftime('%H:%M IST')}"
            else:
                market_status = "🔴 CLOSED"
                # Calculate next market open
                if now_ist.weekday() >= 5:  # Weekend
                    days_until_monday = 7 - now_ist.weekday()
                    next_open = (now_ist + datetime.timedelta(days=days_until_monday)).replace(hour=9, minute=15, second=0, microsecond=0)
                elif now_ist.hour >= 15 and now_ist.minute >= 30:  # After market close
                    next_open = (now_ist + datetime.timedelta(days=1)).replace(hour=9, minute=15, second=0, microsecond=0)
                else:  # Before market open
                    next_open = now_ist.replace(hour=9, minute=15, second=0, microsecond=0)
                time_info = f"Opens at {next_open.strftime('%H:%M IST on %B %d')}"
            
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender']
            msg['To'] = self.email_config['recipient']
            msg['Subject'] = f"📊 Status Update: {self.stock_info['name']} at ₹{stock_data['price']:.2f} - Market {market_status.split()[1]} ({self.current_category.upper()})"
            
            # Calculate uptime
            uptime = datetime.datetime.now() - (self.last_status_email_time - datetime.timedelta(seconds=TRACKING_CONFIG['status_email_interval']))
            uptime_str = f"{int(uptime.total_seconds()//3600)}h {int((uptime.total_seconds()%3600)//60)}m"
            
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>📊 Financial Analytics Hub - Status Update</h2>
                <p><em>30-minute status report from your Background Stock Tracker</em></p>
                
                <div style="background-color: #e8f5e8; padding: 15px; border-radius: 5px; border-left: 5px solid #4caf50;">
                    <h3>✅ System Status: Running</h3>
                    <p><strong>Uptime:</strong> {uptime_str}</p>
                    <p><strong>Category:</strong> {self.category_info['name']} ({self.current_category.upper()})</p>
                    <p><strong>Stock:</strong> {self.stock_info['name']} ({self.stock_symbol})</p>
                    <p><strong>Sector:</strong> {self.stock_info['sector']}</p>
                    <p><strong>Email:</strong> {self.email_config['sender']}</p>
                </div>
                
                <div style="background-color: {'#e8f5e8' if market_open else '#ffe8e8'}; padding: 15px; border-radius: 5px; margin-top: 10px; border-left: 5px solid {'#4caf50' if market_open else '#f44336'};">
                    <h3>🏛️ Market Status: {market_status}</h3>
                    <p><strong>NSE Trading Hours:</strong> 9:15 AM - 3:30 PM IST (Mon-Fri)</p>
                    <p><strong>Current Time:</strong> {now_ist.strftime('%H:%M IST on %B %d, %Y')}</p>
                    <p><strong>Next:</strong> {time_info}</p>
                </div>
                
                <div style="background-color: #f0f8ff; padding: 15px; border-radius: 5px; margin-top: 10px;">
                    <h3>📈 Current Market Data</h3>
                    <p><strong>Price:</strong> ₹{stock_data['price']:.2f} ({stock_data['price_change_pct']:+.2f}%)</p>
                    <p><strong>High:</strong> ₹{stock_data['high']:.2f} | <strong>Low:</strong> ₹{stock_data['low']:.2f}</p>
                    <p><strong>Volume:</strong> {stock_data['volume']:,} ({signal['volume_ratio']:.1f}x avg)</p>
                    <p><strong>5-min SMA:</strong> ₹{signal['sma']:.2f}</p>
                    <p><strong>RSI:</strong> {signal['rsi']:.1f}</p>
                </div>
                
                <div style="background-color: #fff3e0; padding: 15px; border-radius: 5px; margin-top: 10px;">
                    <h3>🎯 Current Signal: {signal['signal']} (Strength: {signal['strength']})</h3>
                    <p><strong>Analysis:</strong></p>
                    <ul>
                        {''.join([f'<li>{reason}</li>' for reason in signal['reasons']])}
                    </ul>
                </div>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-top: 10px;">
                    <h3>📊 Recent Activity</h3>
                    <p><strong>Total Signals Today:</strong> {len([s for s in self.signals if datetime.datetime.fromisoformat(s['timestamp']).date() == datetime.date.today()])}</p>
                    <p><strong>Last Alert:</strong> {self.last_signal['signal'] if self.last_signal else 'None'} at {self.last_signal['timestamp'] if self.last_signal else 'Never'}</p>
                    <p><strong>Next Status Update:</strong> {'During market hours only' if not market_open else (datetime.datetime.now() + datetime.timedelta(seconds=TRACKING_CONFIG['status_email_interval'])).strftime('%H:%M')}</p>
                </div>
                
                <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin-top: 10px;">
                    <p><strong>🔗 Dashboard:</strong> Access your Financial Analytics Hub at <a href="http://localhost:8501">localhost:8501</a></p>
                    <p><strong>⚙️ Settings:</strong> Status emails every 30 minutes (market hours only) | Trading signals when strength ≥ 2</p>
                    <p><strong>🔄 Available Categories:</strong> {', '.join(STOCK_CATEGORIES.keys())} ({len(STOCK_CATEGORIES)} total)</p>
                </div>
                
                <p style="color: #666; font-size: 12px;">
                    Generated at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Background Stock Tracker v2.0
                </p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_config['sender'], self.email_config['password'])
            server.sendmail(self.email_config['sender'], self.email_config['recipient'], msg.as_string())
            server.quit()
            
            self.last_status_email_time = datetime.datetime.now()
            self.logger.info(f"Status email sent: {signal['signal']} at ₹{stock_data['price']:.2f}")
            print(f"📧 Status email sent to {self.email_config['recipient']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending status email: {e}")
            return False
    
    def should_send_email(self, signal):
        """Check if email should be sent"""
        if signal['signal'] == 'HOLD':
            return False
        
        time_since_last = datetime.datetime.now() - self.last_email_time
        if time_since_last.total_seconds() < TRACKING_CONFIG['email_cooldown']:
            return False
        
        if self.last_signal and self.last_signal['signal'] == signal['signal']:
            return False
        
        return True
    
    def tracking_loop(self):
        """Main tracking loop that runs in background"""
        self.logger.info("Background tracker started")
        
        while self.running:
            try:
                # Get stock data
                stock_data = self.get_live_price()
                
                if stock_data:
                    self.price_data.append(stock_data['price'])
                    
                    # Calculate indicators
                    sma = self.calculate_sma()
                    if sma:
                        prices_list = list(self.price_data)
                        rsi = self.calculate_rsi(prices_list)
                        
                        # Generate signal
                        signal = self.generate_signal(
                            stock_data['price'], sma, rsi, stock_data['volume_ratio']
                        )
                        
                        self.signals.append(signal)
                        
                        # Log the update
                        self.logger.info(
                            f"Price: ₹{stock_data['price']:.2f}, SMA: ₹{sma:.2f}, "
                            f"RSI: {rsi:.1f}, Signal: {signal['signal']}"
                        )
                        
                        # Send email if needed
                        if self.should_send_email(signal):
                            self.send_email_alert(signal, stock_data)
                            self.last_signal = signal
                        
                        # Send status email every 30 minutes
                        time_since_status = datetime.datetime.now() - self.last_status_email_time
                        if (TRACKING_CONFIG.get('send_status_emails', True) and 
                            time_since_status.total_seconds() >= TRACKING_CONFIG['status_email_interval'] and
                            self.is_market_open()):
                            self.send_status_email(stock_data, signal)
                        
                        # Save data every 10 updates
                        if len(self.signals) % 10 == 0:
                            self.save_data()
                
                # Wait for next update
                time.sleep(TRACKING_CONFIG['update_interval'])
                
            except Exception as e:
                self.logger.error(f"Tracking loop error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def start_background_tracking(self):
        """Start tracking in background thread"""
        if self.running:
            print("⚠️ Background tracker already running")
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self.tracking_loop, daemon=True)
        self.thread.start()
        
        print(f"🚀 Background stock tracker started!")
        print(f"📊 Tracking: {self.stock_symbol}")
        print(f"📧 Alerts to: {self.email_config['sender']}")
        print(f"📁 Logs: background_tracker_{datetime.date.today()}.log")
        
        self.logger.info("Background tracking started")
        return True
    
    def stop_background_tracking(self):
        """Stop background tracking"""
        if not self.running:
            return False
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        self.save_data()
        print("⏹️ Background stock tracker stopped")
        self.logger.info("Background tracking stopped")
        return True
    
    def get_status(self):
        """Get current tracker status"""
        if not self.running:
            return "⏹️ Stopped"
        
        latest_signal = self.signals[-1] if self.signals else None
        status = {
            'running': self.running,
            'stock': self.stock_symbol,
            'email': self.email_config['sender'],
            'signals_count': len(self.signals),
            'latest_signal': latest_signal['signal'] if latest_signal else 'None',
            'latest_price': latest_signal['price'] if latest_signal else 0,
            'last_update': latest_signal['timestamp'].strftime('%H:%M:%S') if latest_signal else 'Never'
        }
        return status

# Global tracker instance
background_tracker = None

def start_background_tracker():
    """Start the background tracker"""
    global background_tracker
    
    if background_tracker is None:
        background_tracker = BackgroundStockTracker()
    
    return background_tracker.start_background_tracking()

def stop_background_tracker():
    """Stop the background tracker"""
    global background_tracker
    
    if background_tracker:
        return background_tracker.stop_background_tracking()
    return False

def get_tracker_status():
    """Get tracker status"""
    global background_tracker
    
    if background_tracker:
        return background_tracker.get_status()
    return "⏹️ Not initialized"

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    print("\n🛑 Shutting down background tracker...")
    stop_background_tracker()
    sys.exit(0)

def main():
    """Main function for standalone operation"""
    print("🔄 Background Stock Tracker for Financial Analytics Hub")
    print("=" * 60)
    print(f"📧 Email: {EMAIL_CONFIG['sender']}")
    print(f"📊 Stock: {STOCK_CONFIG['symbol']}")
    print("💡 This runs silently alongside your dashboard")
    print()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start tracker
    if start_background_tracker():
        print("✅ Background tracker started successfully!")
        print("📊 Check your dashboard at localhost:8506")
        print("📧 You'll receive email alerts for BUY/SELL signals")
        print("🔄 Press Ctrl+C to stop")
        
        try:
            # Keep main thread alive
            while True:
                time.sleep(60)
                status = get_tracker_status()
                if isinstance(status, dict):
                    print(f"🔄 Running... Latest: {status['latest_signal']} at ₹{status['latest_price']:.2f} ({status['last_update']})")
        except KeyboardInterrupt:
            pass
    else:
        print("❌ Failed to start background tracker")

if __name__ == "__main__":
    main() 