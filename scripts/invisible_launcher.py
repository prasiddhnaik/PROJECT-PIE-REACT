#!/usr/bin/env python3
"""
Invisible Launcher - Starts dashboard with hidden stock tracker
For: prasiddhnaik40@gmail.com
Dashboard users see normal interface, tracker runs completely hidden
"""

import subprocess
import threading
import time
import os
import sys
import signal
from trackers.silent_background_tracker import start_silent_tracker, stop_silent_tracker

class InvisibleLauncher:
    def __init__(self):
        """Initialize invisible launcher"""
        self.dashboard_process = None
        self.silent_tracker_started = False
        
    def start_dashboard_only(self):
        """Start dashboard without any tracker indication"""
        try:
            # Start regular dashboard
            cmd = [sys.executable, "-m", "streamlit", "run", "financial_analytics_hub.py", "--server.port=8506"]
            
            self.dashboard_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            return True
            
        except Exception as e:
            return False
    
    def start_silent_tracker_secretly(self):
        """Start silent tracker in complete secrecy"""
        def secret_start():
            # Wait a bit for dashboard to start
            time.sleep(5)
            
            # Start silent tracker with no output
            try:
                start_silent_tracker()
                self.silent_tracker_started = True
            except:
                pass  # Fail silently
        
        # Start in daemon thread
        secret_thread = threading.Thread(target=secret_start, daemon=True)
        secret_thread.start()
    
    def monitor_dashboard(self):
        """Monitor dashboard and restart if needed"""
        while True:
            try:
                if self.dashboard_process:
                    # Check if dashboard is still running
                    if self.dashboard_process.poll() is not None:
                        # Dashboard stopped, restart it
                        print("Dashboard stopped, restarting...")
                        self.start_dashboard_only()
                
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                break
            except:
                time.sleep(60)  # Wait longer on error
    
    def shutdown(self):
        """Clean shutdown"""
        if self.silent_tracker_started:
            stop_silent_tracker()
        
        if self.dashboard_process:
            self.dashboard_process.terminate()
            self.dashboard_process.wait()
    
    def run(self):
        """Run the invisible launcher"""
        print("🚀 Starting Financial Analytics Hub...")
        print("📊 Dashboard will be available at: http://localhost:8506")
        print("💡 Loading financial data and initializing APIs...")
        
        # Start dashboard
        if self.start_dashboard_only():
            print("✅ Financial Analytics Hub is running!")
            print("🔗 Open http://localhost:8506 in your browser")
            print("📈 Enjoy exploring 170+ cryptocurrencies and global markets!")
            print()
            print("⏹️ Press Ctrl+C to stop")
            
            # Secretly start tracker
            self.start_silent_tracker_secretly()
            
            try:
                # Monitor dashboard
                self.monitor_dashboard()
            except KeyboardInterrupt:
                print("\n🛑 Shutting down Financial Analytics Hub...")
                self.shutdown()
                print("✅ Goodbye! Thanks for using the Financial Analytics Hub!")
        else:
            print("❌ Failed to start Financial Analytics Hub")

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    print("\n🛑 Shutting down...")
    # Stop silent tracker first
    try:
        stop_silent_tracker()
    except:
        pass
    sys.exit(0)

def main():
    """Main function"""
    print("🌟 Financial Analytics Hub")
    print("=" * 50)
    print("📊 Advanced Financial Dashboard with Multi-API Integration")
    print("🚀 170+ Cryptocurrencies | 50+ Global Economies | Live Data")
    print()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start launcher
    launcher = InvisibleLauncher()
    launcher.run()

if __name__ == "__main__":
    main() 