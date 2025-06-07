#!/usr/bin/env python3
"""
Financial Analytics Hub with Background Stock Tracker
Starts both the Streamlit dashboard and background stock monitoring
For: prasiddhnaik40@gmail.com
"""

import subprocess
import threading
import time
import signal
import sys
import os
from trackers.background_stock_tracker import start_background_tracker, stop_background_tracker, get_tracker_status

class AnalyticsHubLauncher:
    def __init__(self):
        self.dashboard_process = None
        self.tracker_started = False
        
        print("🚀 Financial Analytics Hub with Background Stock Tracker")
        print("=" * 70)
        print(f"📧 Email alerts to: prasiddhnaik40@gmail.com")
        print(f"📊 Dashboard: http://localhost:8506")
        print(f"🔄 Background tracker: Reliance Industries")
        print()
    
    def start_dashboard(self):
        """Start the Streamlit dashboard"""
        try:
            print("🌐 Starting Financial Analytics Hub dashboard...")
            
            # Check if api_dashboard.py exists
            if not os.path.exists('api_dashboard.py'):
                print("❌ api_dashboard.py not found in current directory")
                print("💡 Make sure you're in the correct directory")
                return False
            
            # Start Streamlit dashboard
            cmd = [
                'streamlit', 'run', 'api_dashboard.py',
                '--server.port=8506',
                '--server.headless=true',
                '--browser.gatherUsageStats=false',
                '--theme.base=dark'
            ]
            
            self.dashboard_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment to see if it starts successfully
            time.sleep(3)
            
            if self.dashboard_process.poll() is None:  # Still running
                print("✅ Dashboard started successfully!")
                print("🌐 Open your browser to: http://localhost:8506")
                return True
            else:
                print("❌ Dashboard failed to start")
                stdout, stderr = self.dashboard_process.communicate()
                print(f"Error: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting dashboard: {e}")
            return False
    
    def start_background_tracker(self):
        """Start the background stock tracker"""
        try:
            print("🔄 Starting background stock tracker...")
            
            if start_background_tracker():
                self.tracker_started = True
                print("✅ Background tracker started!")
                return True
            else:
                print("❌ Failed to start background tracker")
                return False
                
        except Exception as e:
            print(f"❌ Error starting tracker: {e}")
            return False
    
    def monitor_services(self):
        """Monitor both services"""
        print("\n📊 Services Status:")
        print("-" * 40)
        
        while True:
            try:
                # Check dashboard
                if self.dashboard_process and self.dashboard_process.poll() is None:
                    dashboard_status = "🟢 Running"
                else:
                    dashboard_status = "🔴 Stopped"
                
                # Check tracker
                tracker_status = get_tracker_status()
                if isinstance(tracker_status, dict) and tracker_status['running']:
                    tracker_display = f"🟢 Running - {tracker_status['latest_signal']} at ₹{tracker_status['latest_price']:.2f}"
                else:
                    tracker_display = "🔴 Stopped"
                
                # Display status (update same lines)
                print(f"\r🌐 Dashboard: {dashboard_status} | 🔄 Tracker: {tracker_display}    ", end="", flush=True)
                
                time.sleep(30)  # Update every 30 seconds
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\n⚠️ Monitoring error: {e}")
                time.sleep(60)
    
    def shutdown(self):
        """Shutdown all services"""
        print("\n\n🛑 Shutting down services...")
        
        # Stop background tracker
        if self.tracker_started:
            print("⏹️ Stopping background tracker...")
            stop_background_tracker()
        
        # Stop dashboard
        if self.dashboard_process:
            print("⏹️ Stopping dashboard...")
            try:
                self.dashboard_process.terminate()
                self.dashboard_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.dashboard_process.kill()
            except Exception as e:
                print(f"⚠️ Error stopping dashboard: {e}")
        
        print("✅ All services stopped")
    
    def run(self):
        """Run the complete analytics hub"""
        try:
            # Start dashboard
            if not self.start_dashboard():
                return False
            
            # Start background tracker
            if not self.start_background_tracker():
                print("⚠️ Continuing without background tracker...")
            
            print("\n🎉 Financial Analytics Hub is ready!")
            print("📊 Dashboard: http://localhost:8506")
            print("📧 Email alerts: Enabled for BUY/SELL signals")
            print("🔄 Background monitoring: Active")
            print("\n💡 Press Ctrl+C to stop all services")
            print("=" * 70)
            
            # Monitor services
            self.monitor_services()
            
        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    print("\n🛑 Received shutdown signal...")
    sys.exit(0)

def main():
    """Main function"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run launcher
    launcher = AnalyticsHubLauncher()
    launcher.run()

if __name__ == "__main__":
    main() 