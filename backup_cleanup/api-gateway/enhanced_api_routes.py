"""
Enhanced API Routes - 10 Free Non-Finance APIs
Provides endpoints for weather, nutrition, quotes, and other non-financial data.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from common.api_integrations import (
    api_integrations, get_weather_data, get_nutrition_info, 
    get_random_quote, get_weather_insights, get_daily_insights
)
from common.auth import get_optional_user
from common.rate_limiter import api_gateway_rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/enhanced", tags=["enhanced-apis"])

@router.get("/weather/current")
async def get_current_weather(
    city: str = Query(..., description="City name"),
    country_code: Optional[str] = Query(None, description="Country code (e.g., US, GB)"),
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get current weather data for a city"""
    try:
        weather_data = await get_weather_data(city, country_code)
        return JSONResponse(content=weather_data)
    except Exception as e:
        logger.error(f"Failed to get weather data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")

@router.get("/weather/forecast")
async def get_weather_forecast(
    city: str = Query(..., description="City name"),
    country_code: Optional[str] = Query(None, description="Country code (e.g., US, GB)"),
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get 5-day weather forecast for a city"""
    try:
        forecast_data = await api_integrations.get_weather_forecast(city, country_code)
        return JSONResponse(content=forecast_data)
    except Exception as e:
        logger.error(f"Failed to get weather forecast: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch weather forecast")

@router.get("/weather/insights")
async def get_weather_insights_endpoint(
    city: str = Query(..., description="City name"),
    country_code: Optional[str] = Query(None, description="Country code (e.g., US, GB)"),
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get comprehensive weather insights with market impact analysis"""
    try:
        insights = await get_weather_insights(city, country_code)
        return JSONResponse(content=insights)
    except Exception as e:
        logger.error(f"Failed to get weather insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch weather insights")

@router.get("/nutrition")
async def get_nutrition_endpoint(
    food_item: str = Query(..., description="Food item to analyze"),
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get nutrition information for a food item"""
    try:
        nutrition_data = await get_nutrition_info(food_item)
        return JSONResponse(content=nutrition_data)
    except Exception as e:
        logger.error(f"Failed to get nutrition data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch nutrition data")

@router.get("/quotes/random")
async def get_random_quote_endpoint(
    category: Optional[str] = Query(None, description="Quote category (e.g., success, motivation)"),
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get a random inspirational quote"""
    try:
        quote_data = await get_random_quote(category)
        return JSONResponse(content=quote_data)
    except Exception as e:
        logger.error(f"Failed to get random quote: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch quote")

@router.get("/quotes/categories")
async def get_quote_categories(
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get available quote categories"""
    categories = [
        "success", "motivation", "inspiration", "leadership", 
        "business", "wisdom", "life", "happiness", "courage", "determination"
    ]
    return JSONResponse(content={
        "categories": categories,
        "timestamp": datetime.now().isoformat()
    })

@router.get("/geolocation/ip")
async def get_ip_geolocation(
    ip_address: str = Query(..., description="IP address to lookup"),
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get geolocation information for an IP address"""
    try:
        geo_data = await api_integrations.get_ip_geolocation(ip_address)
        return JSONResponse(content=geo_data)
    except Exception as e:
        logger.error(f"Failed to get IP geolocation: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch geolocation data")

@router.get("/nasa/apod")
async def get_nasa_apod(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get NASA Astronomy Picture of the Day"""
    try:
        apod_data = await api_integrations.get_nasa_apod(date)
        return JSONResponse(content=apod_data)
    except Exception as e:
        logger.error(f"Failed to get NASA APOD: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch NASA data")

@router.get("/entertainment/cat")
async def get_random_cat(
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get a random cat image and information"""
    try:
        cat_data = await api_integrations.get_random_cat()
        return JSONResponse(content=cat_data)
    except Exception as e:
        logger.error(f"Failed to get random cat: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch cat data")

@router.get("/entertainment/joke")
async def get_random_joke(
    category: Optional[str] = Query(None, description="Joke category"),
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get a random joke"""
    try:
        joke_data = await api_integrations.get_random_joke(category)
        return JSONResponse(content=joke_data)
    except Exception as e:
        logger.error(f"Failed to get random joke: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch joke")

@router.get("/entertainment/joke/categories")
async def get_joke_categories(
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get available joke categories"""
    categories = [
        "Any", "Programming", "Misc", "Dark", "Pun", 
        "Spooky", "Christmas", "Coding", "Development"
    ]
    return JSONResponse(content={
        "categories": categories,
        "timestamp": datetime.now().isoformat()
    })

@router.get("/testing/user")
async def get_random_user(
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get random user data for testing purposes"""
    try:
        user_data = await api_integrations.get_random_user()
        return JSONResponse(content=user_data)
    except Exception as e:
        logger.error(f"Failed to get random user: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user data")

@router.get("/apis/public")
async def get_public_apis(
    category: Optional[str] = Query(None, description="API category to filter"),
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get list of public APIs"""
    try:
        apis_data = await api_integrations.get_public_apis(category)
        return JSONResponse(content=apis_data)
    except Exception as e:
        logger.error(f"Failed to get public APIs: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch public APIs")

@router.get("/insights/daily")
async def get_daily_insights_endpoint(
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get daily insights combining multiple APIs"""
    try:
        insights = await get_daily_insights()
        return JSONResponse(content=insights)
    except Exception as e:
        logger.error(f"Failed to get daily insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch daily insights")

@router.get("/health")
async def enhanced_apis_health(
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Health check for enhanced APIs"""
    try:
        # Test a simple API call
        test_quote = await get_random_quote()
        
        return JSONResponse(content={
            "status": "healthy",
            "message": "Enhanced APIs are working",
            "test_quote": test_quote.get('quote', 'No quote available'),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Enhanced APIs health check failed: {e}")
        raise HTTPException(status_code=503, detail="Enhanced APIs are not healthy")

@router.get("/batch")
async def batch_enhanced_apis(
    apis: List[str] = Query(..., description="List of APIs to call (weather, nutrition, quote, cat, joke)"),
    city: Optional[str] = Query(None, description="City for weather API"),
    food_item: Optional[str] = Query(None, description="Food item for nutrition API"),
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Batch call multiple enhanced APIs"""
    try:
        results = {}
        tasks = []
        
        for api in apis:
            if api == "weather" and city:
                tasks.append(("weather", get_weather_data(city)))
            elif api == "nutrition" and food_item:
                tasks.append(("nutrition", get_nutrition_info(food_item)))
            elif api == "quote":
                tasks.append(("quote", get_random_quote()))
            elif api == "cat":
                tasks.append(("cat", api_integrations.get_random_cat()))
            elif api == "joke":
                tasks.append(("joke", api_integrations.get_random_joke()))
        
        # Execute all tasks
        for name, task in tasks:
            try:
                results[name] = await task
            except Exception as e:
                results[name] = {"error": str(e)}
        
        return JSONResponse(content={
            "results": results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to execute batch API calls: {e}")
        raise HTTPException(status_code=500, detail="Failed to execute batch API calls")

@router.get("/weather/market-impact")
async def get_weather_market_impact(
    city: str = Query(..., description="City name"),
    country_code: Optional[str] = Query(None, description="Country code"),
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get weather-based market impact analysis"""
    try:
        insights = await get_weather_insights(city, country_code)
        market_impact = insights.get('market_impact', {})
        
        return JSONResponse(content={
            "city": city,
            "country_code": country_code,
            "market_impact": market_impact,
            "analysis": {
                "energy_sector": "High energy demand expected" if market_impact.get('energy_demand') == 'high' else "Normal energy demand",
                "agriculture": "Weather conditions favorable" if market_impact.get('agriculture') == 'positive' else "Weather may impact agriculture",
                "transportation": "Transportation may be affected" if market_impact.get('transportation') == 'negative' else "Normal transportation conditions",
                "retail": "Retail activity may be impacted" if market_impact.get('retail') != 'normal' else "Normal retail conditions"
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to get weather market impact: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze weather market impact")

@router.get("/nutrition/analysis")
async def analyze_nutrition_impact(
    food_items: List[str] = Query(..., description="List of food items to analyze"),
    _: bool = Depends(api_gateway_rate_limit()),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Analyze nutrition impact of multiple food items"""
    try:
        results = {}
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0
        
        for item in food_items:
            try:
                nutrition_data = await get_nutrition_info(item)
                if nutrition_data.get('nutrition'):
                    nutrition = nutrition_data['nutrition']
                    results[item] = nutrition
                    
                    # Accumulate totals
                    total_calories += nutrition.get('calories', 0)
                    total_protein += nutrition.get('protein_g', 0)
                    total_fat += nutrition.get('fat_total_g', 0)
                    total_carbs += nutrition.get('carbohydrates_total_g', 0)
                else:
                    results[item] = {"error": "No nutrition data found"}
            except Exception as e:
                results[item] = {"error": str(e)}
        
        return JSONResponse(content={
            "individual_items": results,
            "summary": {
                "total_calories": round(total_calories, 2),
                "total_protein_g": round(total_protein, 2),
                "total_fat_g": round(total_fat, 2),
                "total_carbs_g": round(total_carbs, 2),
                "items_analyzed": len([r for r in results.values() if 'error' not in r])
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to analyze nutrition impact: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze nutrition impact") 