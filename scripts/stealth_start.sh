#!/bin/bash

# Stealth Financial Analytics Hub Launcher
# Appears to only start dashboard, but secretly runs stock tracker
# For: prasiddhnaik40@gmail.com

echo "🌟 Financial Analytics Hub - Stealth Mode"
echo "==============================================="
echo "📊 Starting advanced financial dashboard..."
echo "🔄 Initializing APIs and loading data..."
echo

# Check if config exists
if [ ! -f "configs/config.py" ]; then
    echo "❌ Configuration file not found!"
    echo "💡 Please ensure configs/config.py exists with email settings"
    exit 1
fi

# Check if required files exist
required_files=("financial_analytics_hub.py" "trackers/silent_background_tracker.py" "launchers/invisible_launcher.py")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required file missing: $file"
        exit 1
    fi
done

echo "✅ All systems ready"
echo "🚀 Launching Financial Analytics Hub..."
echo

# Kill any existing processes quietly
pkill -f "streamlit.*financial_analytics_hub" 2>/dev/null
pkill -f "silent_background_tracker" 2>/dev/null

# Start invisible launcher (which secretly starts tracker)
python3 launchers/invisible_launcher.py

echo
echo "🛑 Financial Analytics Hub stopped"
echo "✅ All services terminated cleanly" 