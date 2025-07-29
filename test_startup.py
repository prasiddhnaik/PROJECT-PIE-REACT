#!/usr/bin/env python3
"""
Minimal startup test for FastAPI app
"""
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, 'backup_cleanup/backend_python')

# Set environment variables for testing
os.environ['PORT'] = '10000'
os.environ['API_HOST'] = '0.0.0.0'
os.environ['DEBUG'] = 'False'

print("🧪 Testing FastAPI app startup...")

try:
    # Test basic imports
    print("📦 Testing imports...")
    from backup_cleanup.backend_python.main import app
    print("✅ FastAPI app imported successfully")
    
    # Test app creation
    print("🔧 Testing app creation...")
    if app:
        print("✅ FastAPI app created successfully")
    else:
        print("❌ FastAPI app creation failed")
        sys.exit(1)
    
    # Test basic endpoint
    print("🌐 Testing basic endpoint...")
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/health")
    print(f"✅ Health endpoint response: {response.status_code}")
    
    print("🎉 All tests passed! App should start successfully on Render.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Startup error: {e}")
    sys.exit(1) 