#!/usr/bin/env python3
"""
Simplified FastAPI app for Render deployment
"""
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Create a simple FastAPI app
app = FastAPI(
    title="XP Trading Platform API",
    description="Financial analytics and trading platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🚀 XP Trading Platform API",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "XP Trading Platform"
    }

@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Get port from environment or default to 10000
    port = int(os.getenv("PORT", 10000))
    host = "0.0.0.0"
    
    print(f"🚀 Starting simplified FastAPI server on {host}:{port}")
    print(f"📊 Environment: PORT={port}")
    
    # Start the server
    uvicorn.run(app, host=host, port=port, log_level="info") 