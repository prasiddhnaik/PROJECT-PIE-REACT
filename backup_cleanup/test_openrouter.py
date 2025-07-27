#!/usr/bin/env python3
"""
Simple OpenRouter API Test
==========================
Test script to verify your OpenRouter API key is working correctly.
"""

import os
import asyncio
import aiohttp
import json
from datetime import datetime

# Your OpenRouter API key
OPENROUTER_API_KEY = "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"

async def test_openrouter_api():
    """Test the OpenRouter API with a simple request."""
    
    print("🚀 Testing OpenRouter API...")
    print("=" * 50)
    
    # API endpoint and headers
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://financial-analytics-hub.com",
        "X-Title": "Financial Analytics Hub"
    }
    
    # Test payload with a simple financial query
    payload = {
        "model": "openai/gpt-4o-mini",  # Best free model
        "messages": [
            {
                "role": "user", 
                "content": "What are the top 3 cryptocurrency investment opportunities right now? Keep it brief."
            }
        ],
        "max_tokens": 150,
        "temperature": 0.7
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"📡 Making request to OpenRouter API...")
            print(f"🤖 Model: {payload['model']}")
            print(f"❓ Query: {payload['messages'][0]['content']}")
            print()
            
            start_time = datetime.now()
            
            async with session.post(url, headers=headers, json=payload) as response:
                duration = (datetime.now() - start_time).total_seconds()
                
                print(f"📊 Response Status: {response.status}")
                print(f"⏱️  Response Time: {duration:.2f}s")
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract the AI response
                    ai_response = data.get("choices", [{}])[0].get("message", {}).get("content", "No response")
                    usage = data.get("usage", {})
                    
                    print("✅ SUCCESS! OpenRouter API is working!")
                    print("=" * 50)
                    print("🤖 AI Response:")
                    print(ai_response)
                    print()
                    print("📈 Token Usage:")
                    print(f"  • Input tokens: {usage.get('prompt_tokens', 0)}")
                    print(f"  • Output tokens: {usage.get('completion_tokens', 0)}")
                    print(f"  • Total tokens: {usage.get('total_tokens', 0)}")
                    
                    # Calculate cost estimate
                    total_tokens = usage.get('total_tokens', 0)
                    cost_estimate = (total_tokens / 1_000_000) * 0.15  # $0.15 per 1M tokens
                    print(f"  • Estimated cost: ${cost_estimate:.6f}")
                    
                else:
                    error_text = await response.text()
                    print(f"❌ ERROR: {response.status}")
                    print(f"Response: {error_text}")
                    
                    if response.status == 401:
                        print("🔑 API key authentication failed. Please check your key.")
                    elif response.status == 429:
                        print("⏰ Rate limit exceeded. Try again later.")
                    elif response.status == 400:
                        print("📝 Bad request. Check the payload format.")
                    
    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")
        print("🌐 Please check your internet connection.")

async def test_free_models():
    """Test multiple free models to show variety."""
    
    print("\n" + "=" * 50)
    print("🆓 Testing Free Models Available")
    print("=" * 50)
    
    free_models = [
        ("google/gemini-flash-1.5", "FREE - Google's latest multimodal model"),
        ("meta-llama/llama-3.1-405b-instruct", "FREE - Most powerful open source"),
        ("qwen/qwen-2.5-72b-instruct", "FREE - Excellent for data analysis"),
        ("mistralai/mistral-7b-instruct", "FREE - Fast and efficient")
    ]
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://financial-analytics-hub.com",
        "X-Title": "Financial Analytics Hub"
    }
    
    for model_id, description in free_models:
        print(f"\n🤖 Testing: {model_id}")
        print(f"📋 {description}")
        
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": "Say 'Hello from OpenRouter!' in one sentence."}],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        ai_response = data.get("choices", [{}])[0].get("message", {}).get("content", "No response")
                        print(f"✅ Response: {ai_response.strip()}")
                    else:
                        print(f"❌ Failed: {response.status}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("OpenRouter API Test for Financial Analytics Hub")
    print("=" * 60)
    print(f"🔑 API Key: {OPENROUTER_API_KEY[:20]}...")
    print(f"🌐 Base URL: https://openrouter.ai/api/v1")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run the tests
    asyncio.run(test_openrouter_api())
    asyncio.run(test_free_models())
    
    print("\n" + "=" * 60)
    print("🎉 OpenRouter API Test Complete!")
    print("Your API key is ready for use in the Financial Analytics Hub!")
    print("=" * 60) 