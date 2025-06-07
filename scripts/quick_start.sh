#!/bin/bash

# Quick Start - Financial Analytics Hub
# Works with organized directory structure
# For: prasiddhnaik40@gmail.com

echo "🚀 Financial Analytics Hub - Quick Start"
echo "========================================="

# Check if we're in the right directory
if [ ! -f "financial_analytics_hub.py" ]; then
    echo "❌ financial_analytics_hub.py not found!"
    echo "💡 Please run this script from the project root directory"
    exit 1
fi

echo "📊 Choose your launch mode:"
echo ""
echo "1) 🌟 Normal Dashboard Only"
echo "2) 📈 Dashboard + Background Stock Tracker"
echo "3) 🥷 Stealth Mode (Hidden Stock Tracker)"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo "🚀 Starting Dashboard Only..."
        streamlit run financial_analytics_hub.py --server.port=8506
        ;;
    2)
        echo "🚀 Starting Dashboard + Background Tracker..."
        if [ -f "launchers/launch_hub.sh" ]; then
            bash launchers/launch_hub.sh
        else
            echo "❌ Background tracker launcher not found!"
        fi
        ;;
    3)
        echo "🥷 Starting Stealth Mode..."
        if [ -f "launchers/stealth_start.sh" ]; then
            bash launchers/stealth_start.sh
        else
            echo "❌ Stealth launcher not found!"
        fi
        ;;
    *)
        echo "❌ Invalid choice. Please select 1, 2, or 3."
        exit 1
        ;;
esac 