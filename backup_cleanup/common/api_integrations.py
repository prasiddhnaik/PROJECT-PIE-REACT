"""
Enhanced API Integrations - 10 Free Non-Finance APIs
Provides additional data sources to enrich the financial analytics platform.
"""

import asyncio
import logging
import time
import random
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import hashlib

from .http_client import HTTPClient, CacheConfig, ServiceClient, create_service_client
from .errors import ExternalAPIError, ExternalAPITimeoutError, ExternalAPIRateLimitError

logger = logging.getLogger(__name__)

@dataclass
class APIProvider:
    """API provider configuration"""
    name: str
    base_url: str
    api_key: Optional[str] = None
    rate_limit_per_minute: int = 60
    cache_ttl: int = 300  # 5 minutes default
    timeout: int = 30
    headers: Dict[str, str] = None

class EnhancedAPIIntegrations:
    """Enhanced API integrations with 10 free non-finance APIs"""
    
    def __init__(self):
        self.providers = self._initialize_providers()
        self.clients = {}
        self._setup_clients()
    
    def _initialize_providers(self) -> Dict[str, APIProvider]:
        """Initialize API providers with configuration"""
        return {
            # 1. OpenWeather API - Weather data for location-based insights
            "openweather": APIProvider(
                name="OpenWeather",
                base_url="https://api.openweathermap.org/data/2.5",
                api_key=None,  # Free tier doesn't require API key for basic calls
                rate_limit_per_minute=60,
                cache_ttl=600,  # 10 minutes for weather data
                headers={"User-Agent": "FinancialAnalytics/1.0"}
            ),
            
            # 2. API Ninjas - Multiple free APIs (nutrition, quotes, etc.)
            "api_ninjas": APIProvider(
                name="API Ninjas",
                base_url="https://api.api-ninjas.com/v1",
                api_key=None,  # Free tier available
                rate_limit_per_minute=50,
                cache_ttl=3600,  # 1 hour for static data
                headers={"User-Agent": "FinancialAnalytics/1.0"}
            ),
            
            # 3. NASA API - Space and astronomy data
            "nasa": APIProvider(
                name="NASA",
                base_url="https://api.nasa.gov",
                api_key=None,  # Free with registration
                rate_limit_per_minute=1000,
                cache_ttl=1800,  # 30 minutes
                headers={"User-Agent": "FinancialAnalytics/1.0"}
            ),
            
            # 4. The Cat API - Fun content and stress relief
            "cat_api": APIProvider(
                name="The Cat API",
                base_url="https://api.thecatapi.com/v1",
                api_key=None,  # Free tier available
                rate_limit_per_minute=100,
                cache_ttl=300,
                headers={"User-Agent": "FinancialAnalytics/1.0"}
            ),
            
            # 5. IP Geolocation API (via API Ninjas)
            "ip_geolocation": APIProvider(
                name="IP Geolocation",
                base_url="https://api.api-ninjas.com/v1",
                api_key=None,
                rate_limit_per_minute=50,
                cache_ttl=3600,  # 1 hour for IP data
                headers={"User-Agent": "FinancialAnalytics/1.0"}
            ),
            
            # 6. Quotes API (via API Ninjas)
            "quotes": APIProvider(
                name="Quotes API",
                base_url="https://api.api-ninjas.com/v1",
                api_key=None,
                rate_limit_per_minute=50,
                cache_ttl=7200,  # 2 hours for quotes
                headers={"User-Agent": "FinancialAnalytics/1.0"}
            ),
            
            # 7. Nutrition API (via API Ninjas)
            "nutrition": APIProvider(
                name="Nutrition API",
                base_url="https://api.api-ninjas.com/v1",
                api_key=None,
                rate_limit_per_minute=50,
                cache_ttl=86400,  # 24 hours for nutrition data
                headers={"User-Agent": "FinancialAnalytics/1.0"}
            ),
            
            # 8. Joke API - Entertainment and stress relief
            "jokes": APIProvider(
                name="Joke API",
                base_url="https://v2.jokeapi.dev",
                api_key=None,
                rate_limit_per_minute=120,
                cache_ttl=1800,  # 30 minutes
                headers={"User-Agent": "FinancialAnalytics/1.0"}
            ),
            
            # 9. Random User API - User data for testing
            "random_user": APIProvider(
                name="Random User",
                base_url="https://randomuser.me/api",
                api_key=None,
                rate_limit_per_minute=1000,
                cache_ttl=300,
                headers={"User-Agent": "FinancialAnalytics/1.0"}
            ),
            
            # 10. Public APIs - Various free APIs
            "public_apis": APIProvider(
                name="Public APIs",
                base_url="https://api.publicapis.org",
                api_key=None,
                rate_limit_per_minute=100,
                cache_ttl=3600,
                headers={"User-Agent": "FinancialAnalytics/1.0"}
            )
        }
    
    def _setup_clients(self):
        """Setup HTTP clients for each provider"""
        for provider_name, provider in self.providers.items():
            cache_config = CacheConfig(
                enabled=True,
                ttl_seconds=provider.cache_ttl,
                max_size=1000,
                include_query_params=True
            )
            
            self.clients[provider_name] = HTTPClient(
                timeout=provider.timeout,
                max_retries=3,
                cache_config=cache_config
            )
    
    async def get_weather_data(self, city: str, country_code: str = None) -> Dict[str, Any]:
        """Get current weather data for a location"""
        try:
            client = self.clients["openweather"]
            
            # Build location string
            location = f"{city},{country_code}" if country_code else city
            
            # Get current weather
            response = await client.request(
                'GET',
                f"{self.providers['openweather'].base_url}/weather",
                params={
                    'q': location,
                    'appid': self.providers['openweather'].api_key or 'demo',
                    'units': 'metric'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'location': location,
                    'temperature': data['main']['temp'],
                    'feels_like': data['main']['feels_like'],
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'description': data['weather'][0]['description'],
                    'icon': data['weather'][0]['icon'],
                    'wind_speed': data['wind']['speed'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise ExternalAPIError(f"Weather API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to get weather data: {e}")
            raise
    
    async def get_weather_forecast(self, city: str, country_code: str = None) -> Dict[str, Any]:
        """Get 5-day weather forecast"""
        try:
            client = self.clients["openweather"]
            location = f"{city},{country_code}" if country_code else city
            
            response = await client.request(
                'GET',
                f"{self.providers['openweather'].base_url}/forecast",
                params={
                    'q': location,
                    'appid': self.providers['openweather'].api_key or 'demo',
                    'units': 'metric'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'location': location,
                    'forecast': data['list'][:8],  # Next 24 hours (3-hour intervals)
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise ExternalAPIError(f"Weather forecast API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to get weather forecast: {e}")
            raise
    
    async def get_nutrition_info(self, food_item: str) -> Dict[str, Any]:
        """Get nutrition information for a food item"""
        try:
            client = self.clients["nutrition"]
            
            response = await client.request(
                'GET',
                f"{self.providers['nutrition'].base_url}/nutrition",
                params={'query': food_item}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return {
                        'food_item': food_item,
                        'nutrition': data[0],
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {'food_item': food_item, 'nutrition': None, 'error': 'No data found'}
            else:
                raise ExternalAPIError(f"Nutrition API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to get nutrition info: {e}")
            raise
    
    async def get_random_quote(self, category: str = None) -> Dict[str, Any]:
        """Get a random inspirational quote"""
        try:
            client = self.clients["quotes"]
            
            params = {}
            if category:
                params['category'] = category
            
            response = await client.request(
                'GET',
                f"{self.providers['quotes'].base_url}/quotes",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return {
                        'quote': data[0]['quote'],
                        'author': data[0]['author'],
                        'category': category or 'general',
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {'error': 'No quotes found'}
            else:
                raise ExternalAPIError(f"Quotes API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to get random quote: {e}")
            raise
    
    async def get_ip_geolocation(self, ip_address: str) -> Dict[str, Any]:
        """Get geolocation information for an IP address"""
        try:
            client = self.clients["ip_geolocation"]
            
            response = await client.request(
                'GET',
                f"{self.providers['ip_geolocation'].base_url}/iplookup",
                params={'address': ip_address}
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'ip_address': ip_address,
                    'location': data,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise ExternalAPIError(f"IP Geolocation API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to get IP geolocation: {e}")
            raise
    
    async def get_nasa_apod(self, date: str = None) -> Dict[str, Any]:
        """Get NASA Astronomy Picture of the Day"""
        try:
            client = self.clients["nasa"]
            
            params = {}
            if date:
                params['date'] = date
            
            response = await client.request(
                'GET',
                f"{self.providers['nasa'].base_url}/planetary/apod",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'title': data.get('title'),
                    'explanation': data.get('explanation'),
                    'url': data.get('url'),
                    'date': data.get('date'),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise ExternalAPIError(f"NASA API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to get NASA APOD: {e}")
            raise
    
    async def get_random_cat(self) -> Dict[str, Any]:
        """Get a random cat image and information"""
        try:
            client = self.clients["cat_api"]
            
            response = await client.request(
                'GET',
                f"{self.providers['cat_api'].base_url}/images/search",
                params={
                    'size': 'med',
                    'mime_types': 'jpg',
                    'has_breeds': 'true',
                    'limit': 1
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    cat_data = data[0]
                    return {
                        'image_url': cat_data.get('url'),
                        'breed': cat_data.get('breeds', [{}])[0] if cat_data.get('breeds') else None,
                        'width': cat_data.get('width'),
                        'height': cat_data.get('height'),
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {'error': 'No cat data found'}
            else:
                raise ExternalAPIError(f"Cat API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to get random cat: {e}")
            raise
    
    async def get_random_joke(self, category: str = None) -> Dict[str, Any]:
        """Get a random joke"""
        try:
            client = self.clients["jokes"]
            
            params = {}
            if category:
                params['category'] = category
            
            response = await client.request(
                'GET',
                f"{self.providers['jokes'].base_url}/joke/Any",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'joke': data.get('joke') or f"{data.get('setup', '')} {data.get('delivery', '')}",
                    'category': data.get('category'),
                    'type': data.get('type'),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise ExternalAPIError(f"Joke API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to get random joke: {e}")
            raise
    
    async def get_random_user(self) -> Dict[str, Any]:
        """Get random user data for testing"""
        try:
            client = self.clients["random_user"]
            
            response = await client.request(
                'GET',
                f"{self.providers['random_user'].base_url}/",
                params={'nat': 'us,gb,ca'}
            )
            
            if response.status_code == 200:
                data = response.json()
                user = data['results'][0]
                return {
                    'name': f"{user['name']['first']} {user['name']['last']}",
                    'email': user['email'],
                    'location': f"{user['location']['city']}, {user['location']['country']}",
                    'picture': user['picture']['medium'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise ExternalAPIError(f"Random User API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to get random user: {e}")
            raise
    
    async def get_public_apis(self, category: str = None) -> Dict[str, Any]:
        """Get list of public APIs"""
        try:
            client = self.clients["public_apis"]
            
            params = {}
            if category:
                params['category'] = category
            
            response = await client.request(
                'GET',
                f"{self.providers['public_apis'].base_url}/entries",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'apis': data.get('entries', [])[:10],  # Limit to 10 results
                    'count': data.get('count', 0),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise ExternalAPIError(f"Public APIs error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to get public APIs: {e}")
            raise
    
    async def get_weather_insights(self, city: str, country_code: str = None) -> Dict[str, Any]:
        """Get comprehensive weather insights for financial analysis"""
        try:
            # Get current weather and forecast
            current_weather = await self.get_weather_data(city, country_code)
            forecast = await self.get_weather_forecast(city, country_code)
            
            # Analyze weather impact on markets
            weather_analysis = self._analyze_weather_impact(current_weather)
            
            return {
                'location': f"{city},{country_code}" if country_code else city,
                'current_weather': current_weather,
                'forecast': forecast,
                'market_impact': weather_analysis,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get weather insights: {e}")
            raise
    
    def _analyze_weather_impact(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze potential weather impact on financial markets"""
        temp = weather_data.get('temperature', 0)
        description = weather_data.get('description', '').lower()
        
        impact_analysis = {
            'energy_demand': 'normal',
            'agriculture': 'neutral',
            'transportation': 'normal',
            'retail': 'normal',
            'overall_sentiment': 'neutral'
        }
        
        # Temperature-based analysis
        if temp > 30:
            impact_analysis['energy_demand'] = 'high'
            impact_analysis['agriculture'] = 'negative'
        elif temp < 0:
            impact_analysis['energy_demand'] = 'high'
            impact_analysis['transportation'] = 'negative'
        
        # Weather condition analysis
        if 'rain' in description or 'storm' in description:
            impact_analysis['transportation'] = 'negative'
            impact_analysis['retail'] = 'negative'
        elif 'sunny' in description or 'clear' in description:
            impact_analysis['retail'] = 'positive'
            impact_analysis['agriculture'] = 'positive'
        
        return impact_analysis
    
    async def get_daily_insights(self) -> Dict[str, Any]:
        """Get daily insights combining multiple APIs"""
        try:
            # Gather data from multiple APIs
            tasks = [
                self.get_random_quote('success'),
                self.get_weather_data('New York', 'US'),
                self.get_random_cat(),
                self.get_nutrition_info('coffee')
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return {
                'quote': results[0] if not isinstance(results[0], Exception) else None,
                'weather': results[1] if not isinstance(results[1], Exception) else None,
                'cat': results[2] if not isinstance(results[2], Exception) else None,
                'nutrition': results[3] if not isinstance(results[3], Exception) else None,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get daily insights: {e}")
            raise
    
    async def close(self):
        """Close all HTTP clients"""
        for client in self.clients.values():
            await client.close()

# Global instance
api_integrations = EnhancedAPIIntegrations()

# Convenience functions
async def get_weather_data(city: str, country_code: str = None) -> Dict[str, Any]:
    """Get weather data for a city"""
    return await api_integrations.get_weather_data(city, country_code)

async def get_nutrition_info(food_item: str) -> Dict[str, Any]:
    """Get nutrition information for a food item"""
    return await api_integrations.get_nutrition_info(food_item)

async def get_random_quote(category: str = None) -> Dict[str, Any]:
    """Get a random inspirational quote"""
    return await api_integrations.get_random_quote(category)

async def get_weather_insights(city: str, country_code: str = None) -> Dict[str, Any]:
    """Get comprehensive weather insights"""
    return await api_integrations.get_weather_insights(city, country_code)

async def get_daily_insights() -> Dict[str, Any]:
    """Get daily insights from multiple APIs"""
    return await api_integrations.get_daily_insights() 