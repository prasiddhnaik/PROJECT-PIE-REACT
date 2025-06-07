#!/bin/bash

# Financial Analytics Hub with Background Stock Tracker
# Comprehensive launcher for all services
# For: prasiddhnaik40@gmail.com

echo "🌟 Financial Analytics Hub with Background Stock Tracker"
echo "=============================================================="
echo "📊 Starting comprehensive financial monitoring system..."
echo "🔄 Initializing dashboard and background tracker..."
echo

# Check if config exists
if [ ! -f "configs/config.py" ]; then
    echo "❌ Configuration file not found!"
    echo "💡 Please ensure configs/config.py exists with your email settings"
    exit 1
fi

# Check if required files exist
required_files=("financial_analytics_hub.py" "trackers/background_stock_tracker.py" "launchers/start_analytics_hub.py")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required file missing: $file"
        exit 1
    fi
done

echo "✅ Configuration verified"
echo "🚀 Launching Financial Analytics Hub with Stock Tracker..."
echo

# Kill any existing processes
echo "🔄 Cleaning up any existing processes..."
pkill -f "streamlit.*financial_analytics_hub" 2>/dev/null
pkill -f "background_stock_tracker" 2>/dev/null
sleep 2

# Start the combined launcher
python3 launchers/start_analytics_hub.py

echo
echo "🛑 Financial Analytics Hub stopped"
echo "✅ All services terminated cleanly"
echo "📧 Check your email for any final alerts" 