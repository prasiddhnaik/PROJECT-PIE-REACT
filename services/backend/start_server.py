#!/usr/bin/env python3
"""
Simple Server Starter for GitHub Deployment
This bypasses any complex cache system issues
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Start the quick server"""
    # Get the directory of this script
    script_dir = Path(__file__).parent
    server_file = script_dir / "quick_server.py"
    
    if not server_file.exists():
        print("❌ quick_server.py not found!")
        sys.exit(1)
    
    print("🚀 Starting Financial Data Server...")
    print("📍 Working directory:", script_dir)
    print("🌐 Server will be available at: http://localhost:4000")
    print("📊 Endpoints:")
    print("   GET  /test              - Test server")
    print("   GET  /stock/<symbol>    - Get single stock")
    print("   POST /stocks            - Get multiple stocks")
    print("   GET  /popular           - Get popular stocks")
    print("   GET  /clear-cache       - Clear cache")
    print()
    
    try:
        # Change to the script directory
        os.chdir(script_dir)
        
        # Start the server
        subprocess.run([sys.executable, "quick_server.py"])
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 