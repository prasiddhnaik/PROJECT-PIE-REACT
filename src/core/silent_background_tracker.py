#!/usr/bin/env python3
"""
Silent Background Stock Tracker - Completely invisible operation
For: prasiddhnaik40@gmail.com
Runs silently with no console output or user indication
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
import subprocess

# Import configuration
from configs.config import EMAIL_CONFIG, STOCK_CONFIG, TRACKING_CONFIG

class SilentBackgroundTracker:
    def __init__(self):
        """Initialize silent tracker - no console output"""
        self.email_config = EMAIL_CONFIG
        self.stock_symbol = STOCK_CONFIG['symbol']
        self.sma_period = STOCK_CONFIG['sma_period']
        self.price_data = deque(maxlen=self.sma_period)
        self.signals = []
        self.last_signal = None
        self.last_email_time = datetime.datetime.now() - datetime.timedelta(minutes=30)
        self.running = False
        self.thread = None
        
        # Setup silent logging (no console output)
        log_file = f'.silent_tracker_{datetime.date.today()}.log'
        
        # Create logger with file handler only
        self.logger = logging.getLogger('silent_tracker')
        self.logger.setLevel(logging.INFO)
        
        # Remove any existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Add only file handler (no console output)
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Load existing data silently
        self.load_data()
        
        # Log initialization (but no console output)
        self.logger.info(f"Silent tracker initialized for {self.email_config['sender']}")
    
    def load_data(self):
        """Load existing tracking data silently"""
        try:
            if os.path.exists('.silent_tracker_data.json'):
                with open('.silent_tracker_data.json', 'r') as f:
                    data = json.load(f)
                    self.signals = data.get('signals', [])[-50:]
                    self.logger.info(f"Loaded {len(self.signals)} previous signals")
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
    
    def save_data(self):
        """Save tracking data silently"""
        try:
            data = {
                'signals': self.signals[-100:],
                'last_update': datetime.datetime.now().isoformat(),
                'tracker_info': {
                    'stock': self.stock_symbol,
                    'email': self.email_config['sender'],
                    'sma_period': self.sma_period
                }
            }
            with open('.silent_tracker_data.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving data: {e}")
    
    def get_live_price(self):
        """Get live stock price silently"""
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
        """Send email alert silently"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender']
            msg['To'] = self.email_config['recipient']
            msg['Subject'] = f"🚨 {signal['signal']} Signal: Reliance at ₹{signal['price']:.2f}"
            
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>📊 Trading Signal Alert - Reliance Industries</h2>
                <p><em>Automated trading signal from your private monitoring system</em></p>
                
                <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px;">
                    <h3>🎯 Signal: {signal['signal']} (Strength: {signal['strength']})</h3>
                    <p><strong>Price:</strong> ₹{stock_data['price']:.2f} ({stock_data['price_change_pct']:+.2f}%)</p>
                    <p><strong>5-min SMA:</strong> ₹{signal['sma']:.2f}</p>
                    <p><strong>RSI:</strong> {signal['rsi']:.1f}</p>
                    <p><strong>Volume:</strong> {stock_data['volume']:,} ({signal['volume_ratio']:.1f}x avg)</p>
                </div>
                
                <div style="background-color: #e8f4fd; padding: 15px; border-radius: 5px; margin-top: 10px;">
                    <h3>💡 Signal Analysis:</h3>
                    <ul>
                        {''.join([f'<li>{reason}</li>' for reason in signal['reasons']])}
                    </ul>
                </div>
                
                <div style="background-color: #fff9e6; padding: 15px; border-radius: 5px; margin-top: 10px;">
                    <p><strong>⚠️ Disclaimer:</strong> This is an automated signal for informational purposes only. Always conduct your own analysis before making trading decisions.</p>
                    <p><em>Generated by your private monitoring system</em></p>
                </div>
                
                <p style="color: #666; font-size: 12px;">
                    Generated at {signal['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} | Private Stock Monitor
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
            self.logger.info(f"Silent email sent: {signal['signal']} at ₹{signal['price']:.2f}")
            
        except Exception as e:
            self.logger.error(f"Email error: {e}")
    
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
        """Main tracking loop - completely silent"""
        self.logger.info("Silent tracker started")
        
        while self.running:
            try:
                stock_data = self.get_live_price()
                
                if stock_data:
                    self.price_data.append(stock_data['price'])
                    
                    sma = self.calculate_sma()
                    if sma:
                        prices_list = list(self.price_data)
                        rsi = self.calculate_rsi(prices_list)
                        
                        signal = self.generate_signal(
                            stock_data['price'], sma, rsi, stock_data['volume_ratio']
                        )
                        
                        self.signals.append(signal)
                        
                        self.logger.info(
                            f"Price: ₹{stock_data['price']:.2f}, SMA: ₹{sma:.2f}, "
                            f"RSI: {rsi:.1f}, Signal: {signal['signal']}"
                        )
                        
                        if self.should_send_email(signal):
                            self.send_email_alert(signal, stock_data)
                            self.last_signal = signal
                        
                        if len(self.signals) % 10 == 0:
                            self.save_data()
                
                time.sleep(TRACKING_CONFIG['update_interval'])
                
            except Exception as e:
                self.logger.error(f"Tracking loop error: {e}")
                time.sleep(60)
    
    def start_silent_tracking(self):
        """Start tracking silently"""
        if self.running:
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self.tracking_loop, daemon=True)
        self.thread.start()
        
        self.logger.info("Silent tracking started")
        return True
    
    def stop_silent_tracking(self):
        """Stop tracking silently"""
        if not self.running:
            return False
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        self.save_data()
        self.logger.info("Silent tracking stopped")
        return True
    
    def is_running(self):
        """Check if tracker is running"""
        return self.running

# Global silent tracker instance
silent_tracker = None

def start_silent_tracker():
    """Start the silent tracker"""
    global silent_tracker
    
    if silent_tracker is None:
        silent_tracker = SilentBackgroundTracker()
    
    return silent_tracker.start_silent_tracking()

def stop_silent_tracker():
    """Stop the silent tracker"""
    global silent_tracker
    
    if silent_tracker:
        return silent_tracker.stop_silent_tracking()
    return False

def is_tracker_running():
    """Check if tracker is running"""
    global silent_tracker
    return silent_tracker and silent_tracker.is_running()

def main():
    """Main function for daemon operation"""
    # Redirect stdout and stderr to devnull for complete silence
    import os
    
    # Fork process to run in background
    if os.fork() > 0:
        # Parent process exits
        sys.exit(0)
    
    # Child process continues
    os.setsid()  # Create new session
    
    # Redirect standard file descriptors
    with open(os.devnull, 'w') as devnull:
        os.dup2(devnull.fileno(), sys.stdout.fileno())
        os.dup2(devnull.fileno(), sys.stderr.fileno())
    
    # Start silent tracker
    start_silent_tracker()
    
    # Keep running silently
    try:
        while True:
            time.sleep(3600)  # Sleep for 1 hour intervals
    except:
        stop_silent_tracker()

if __name__ == "__main__":
    main() 