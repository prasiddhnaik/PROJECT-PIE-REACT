#!/usr/bin/env python3
"""
Project Pie React - Financial Data Server Setup
===============================================

Easy setup script for GitHub deployment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Project Pie React - Financial Data Server Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required. Current version:", sys.version)
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Navigate to backend directory
    backend_dir = Path("services/backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found! Make sure you're in the project root.")
        sys.exit(1)
    
    os.chdir(backend_dir)
    print(f"📍 Working in: {backend_dir.absolute()}")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("💡 Try: pip3 install -r requirements.txt")
        if not run_command("pip3 install -r requirements.txt", "Installing dependencies (pip3)"):
            sys.exit(1)
    
    print()
    print("🎉 Setup completed successfully!")
    print()
    print("🌐 To start the server:")
    print("   cd services/backend")
    print("   python3 start_server.py")
    print()
    print("📊 Server will be available at: http://localhost:4000")
    print("🧪 Test endpoints:")
    print("   curl http://localhost:4000/test")
    print("   curl http://localhost:4000/stock/AAPL")
    print("   curl http://localhost:4000/popular")

if __name__ == "__main__":
    main() 