#!/usr/bin/env python3
"""
Test script for Enhanced APIs - 10 Free Non-Finance APIs
Demonstrates and validates all integrated APIs.
"""

import asyncio
import time
import json
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from common.api_integrations import (
    api_integrations, get_weather_data, get_nutrition_info, 
    get_random_quote, get_weather_insights, get_daily_insights
)

async def test_weather_apis():
    """Test weather-related APIs"""
    print("🌤️  Testing Weather APIs...")
    
    try:
        # Test current weather
        weather = await get_weather_data("New York", "US")
        print(f"✅ Current weather in New York: {weather['temperature']}°C, {weather['description']}")
        
        # Test weather forecast
        forecast = await api_integrations.get_weather_forecast("London", "GB")
        print(f"✅ Weather forecast for London: {len(forecast['forecast'])} time periods")
        
        # Test weather insights with market impact
        insights = await get_weather_insights("Tokyo", "JP")
        market_impact = insights.get('market_impact', {})
        print(f"✅ Weather insights for Tokyo - Energy demand: {market_impact.get('energy_demand', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Weather API test failed: {e}")

async def test_nutrition_api():
    """Test nutrition API"""
    print("\n🍎 Testing Nutrition API...")
    
    try:
        # Test nutrition info
        nutrition = await get_nutrition_info("apple")
        if nutrition.get('nutrition'):
            data = nutrition['nutrition']
            print(f"✅ Apple nutrition: {data.get('calories', 0)} calories, {data.get('protein_g', 0)}g protein")
        else:
            print("⚠️  No nutrition data found for apple")
            
        # Test multiple food items
        foods = ["banana", "chicken breast", "coffee"]
        for food in foods:
            try:
                nutrition = await get_nutrition_info(food)
                if nutrition.get('nutrition'):
                    data = nutrition['nutrition']
                    print(f"✅ {food.capitalize()}: {data.get('calories', 0)} calories")
            except Exception as e:
                print(f"❌ Failed to get nutrition for {food}: {e}")
                
    except Exception as e:
        print(f"❌ Nutrition API test failed: {e}")

async def test_quotes_api():
    """Test quotes API"""
    print("\n💬 Testing Quotes API...")
    
    try:
        # Test random quote
        quote = await get_random_quote()
        print(f"✅ Random quote: \"{quote.get('quote', 'No quote')}\" - {quote.get('author', 'Unknown')}")
        
        # Test category-specific quote
        success_quote = await get_random_quote("success")
        print(f"✅ Success quote: \"{success_quote.get('quote', 'No quote')[:50]}...\"")
        
    except Exception as e:
        print(f"❌ Quotes API test failed: {e}")

async def test_geolocation_api():
    """Test IP geolocation API"""
    print("\n🌍 Testing IP Geolocation API...")
    
    try:
        # Test with a known IP
        geo_data = await api_integrations.get_ip_geolocation("8.8.8.8")
        location = geo_data.get('location', {})
        print(f"✅ IP 8.8.8.8 location: {location.get('city', 'Unknown')}, {location.get('country', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ IP Geolocation API test failed: {e}")

async def test_nasa_api():
    """Test NASA API"""
    print("\n🚀 Testing NASA API...")
    
    try:
        # Test Astronomy Picture of the Day
        apod = await api_integrations.get_nasa_apod()
        print(f"✅ NASA APOD: {apod.get('title', 'No title')}")
        print(f"   URL: {apod.get('url', 'No URL')}")
        
    except Exception as e:
        print(f"❌ NASA API test failed: {e}")

async def test_entertainment_apis():
    """Test entertainment APIs"""
    print("\n🎭 Testing Entertainment APIs...")
    
    try:
        # Test cat API
        cat = await api_integrations.get_random_cat()
        print(f"✅ Random cat: {cat.get('width', 0)}x{cat.get('height', 0)} image")
        if cat.get('breed'):
            print(f"   Breed: {cat['breed'].get('name', 'Unknown')}")
        
        # Test joke API
        joke = await api_integrations.get_random_joke()
        print(f"✅ Random joke: {joke.get('joke', 'No joke')[:50]}...")
        
    except Exception as e:
        print(f"❌ Entertainment APIs test failed: {e}")

async def test_testing_apis():
    """Test testing/utility APIs"""
    print("\n🧪 Testing Utility APIs...")
    
    try:
        # Test random user API
        user = await api_integrations.get_random_user()
        print(f"✅ Random user: {user.get('name', 'Unknown')} from {user.get('location', 'Unknown')}")
        
        # Test public APIs list
        apis = await api_integrations.get_public_apis()
        print(f"✅ Public APIs found: {apis.get('count', 0)} total")
        
    except Exception as e:
        print(f"❌ Utility APIs test failed: {e}")

async def test_daily_insights():
    """Test daily insights feature"""
    print("\n📊 Testing Daily Insights...")
    
    try:
        insights = await get_daily_insights()
        print("✅ Daily insights collected:")
        
        if insights.get('quote'):
            print(f"   Quote: \"{insights['quote'].get('quote', 'No quote')[:50]}...\"")
        
        if insights.get('weather'):
            weather = insights['weather']
            print(f"   Weather: {weather.get('temperature', 0)}°C in {weather.get('location', 'Unknown')}")
        
        if insights.get('cat'):
            print(f"   Cat: Random cat image available")
        
        if insights.get('nutrition'):
            nutrition = insights['nutrition']
            if nutrition.get('nutrition'):
                data = nutrition['nutrition']
                print(f"   Nutrition: {data.get('name', 'Unknown')} - {data.get('calories', 0)} calories")
        
    except Exception as e:
        print(f"❌ Daily insights test failed: {e}")

async def test_batch_operations():
    """Test batch API operations"""
    print("\n📦 Testing Batch Operations...")
    
    try:
        # Test multiple weather locations
        cities = [("New York", "US"), ("London", "GB"), ("Tokyo", "JP")]
        weather_tasks = [get_weather_data(city, country) for city, country in cities]
        
        start_time = time.time()
        weather_results = await asyncio.gather(*weather_tasks, return_exceptions=True)
        batch_time = time.time() - start_time
        
        print(f"✅ Batch weather request completed in {batch_time:.2f}s")
        for i, (city, country) in enumerate(cities):
            if isinstance(weather_results[i], Exception):
                print(f"   ❌ {city}: {weather_results[i]}")
            else:
                temp = weather_results[i].get('temperature', 0)
                print(f"   ✅ {city}: {temp}°C")
        
        # Test multiple nutrition items
        foods = ["apple", "banana", "orange"]
        nutrition_tasks = [get_nutrition_info(food) for food in foods]
        
        start_time = time.time()
        nutrition_results = await asyncio.gather(*nutrition_tasks, return_exceptions=True)
        batch_time = time.time() - start_time
        
        print(f"✅ Batch nutrition request completed in {batch_time:.2f}s")
        for i, food in enumerate(foods):
            if isinstance(nutrition_results[i], Exception):
                print(f"   ❌ {food}: {nutrition_results[i]}")
            else:
                calories = nutrition_results[i].get('nutrition', {}).get('calories', 0)
                print(f"   ✅ {food}: {calories} calories")
        
    except Exception as e:
        print(f"❌ Batch operations test failed: {e}")

async def test_error_handling():
    """Test error handling for APIs"""
    print("\n🛡️ Testing Error Handling...")
    
    try:
        # Test with invalid city
        try:
            await get_weather_data("InvalidCity12345")
        except Exception as e:
            print(f"✅ Expected error for invalid city: {type(e).__name__}")
        
        # Test with invalid food item
        try:
            await get_nutrition_info("invalid_food_item_12345")
        except Exception as e:
            print(f"✅ Expected error for invalid food: {type(e).__name__}")
        
        # Test with invalid IP
        try:
            await api_integrations.get_ip_geolocation("999.999.999.999")
        except Exception as e:
            print(f"✅ Expected error for invalid IP: {type(e).__name__}")
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")

async def test_performance():
    """Test API performance"""
    print("\n⚡ Testing Performance...")
    
    try:
        # Test response times
        apis_to_test = [
            ("Weather", lambda: get_weather_data("New York", "US")),
            ("Nutrition", lambda: get_nutrition_info("apple")),
            ("Quote", lambda: get_random_quote()),
            ("Cat", lambda: api_integrations.get_random_cat()),
            ("Joke", lambda: api_integrations.get_random_joke())
        ]
        
        for name, api_func in apis_to_test:
            start_time = time.time()
            try:
                await api_func()
                response_time = time.time() - start_time
                print(f"✅ {name} API: {response_time:.2f}s")
            except Exception as e:
                response_time = time.time() - start_time
                print(f"❌ {name} API failed in {response_time:.2f}s: {e}")
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")

async def main():
    """Run all enhanced API tests"""
    print("🚀 Starting Enhanced APIs Test Suite")
    print("=" * 60)
    print("Testing 10 Free Non-Finance APIs:")
    print("1. OpenWeather API - Weather data")
    print("2. API Ninjas - Multiple APIs (nutrition, quotes, geolocation)")
    print("3. NASA API - Space and astronomy data")
    print("4. The Cat API - Cat images and information")
    print("5. Joke API - Entertainment")
    print("6. Random User API - Testing data")
    print("7. Public APIs - API directory")
    print("8. IP Geolocation - Location data")
    print("9. Quotes API - Inspirational quotes")
    print("10. Nutrition API - Food information")
    print("=" * 60)
    
    start_time = time.time()
    
    # Run all tests
    await test_weather_apis()
    await test_nutrition_api()
    await test_quotes_api()
    await test_geolocation_api()
    await test_nasa_api()
    await test_entertainment_apis()
    await test_testing_apis()
    await test_daily_insights()
    await test_batch_operations()
    await test_error_handling()
    await test_performance()
    
    total_time = time.time() - start_time
    print(f"\n✅ All enhanced API tests completed in {total_time:.2f} seconds")
    print("=" * 60)
    
    # Final summary
    print("\n📋 Enhanced APIs Summary:")
    print("✅ Weather data for location-based insights")
    print("✅ Nutrition information for health tracking")
    print("✅ Inspirational quotes for motivation")
    print("✅ IP geolocation for user analytics")
    print("✅ NASA data for educational content")
    print("✅ Entertainment content (cats, jokes)")
    print("✅ Testing utilities and random data")
    print("✅ Public API directory")
    print("✅ Batch operations for efficiency")
    print("✅ Error handling and performance monitoring")
    
    print("\n🌐 API Endpoints Available:")
    print("GET /api/enhanced/weather/current")
    print("GET /api/enhanced/weather/forecast")
    print("GET /api/enhanced/weather/insights")
    print("GET /api/enhanced/nutrition")
    print("GET /api/enhanced/quotes/random")
    print("GET /api/enhanced/geolocation/ip")
    print("GET /api/enhanced/nasa/apod")
    print("GET /api/enhanced/entertainment/cat")
    print("GET /api/enhanced/entertainment/joke")
    print("GET /api/enhanced/testing/user")
    print("GET /api/enhanced/apis/public")
    print("GET /api/enhanced/insights/daily")
    print("GET /api/enhanced/batch")
    print("GET /api/enhanced/health")

if __name__ == "__main__":
    asyncio.run(main()) 