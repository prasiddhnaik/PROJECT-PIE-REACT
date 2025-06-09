#!/usr/bin/env python3
"""
⚡ SUPABASE HIGH-PERFORMANCE CACHE MANAGER
Ultra-fast financial data caching using Supabase as primary cache store
"""

import time
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import streamlit as st
from supabase_client import get_supabase_manager

class SupabaseCacheManager:
    """⚡ Lightning-fast cache using Supabase for maximum performance"""
    
    def __init__(self):
        self.supabase = get_supabase_manager()
        self.local_cache = {}  # Ultra-fast local cache for immediate responses
        self.cache_ttl = 300  # 5 minutes default TTL
    
    def get_cache_key(self, data_type: str, symbol: str, params: Dict = None) -> str:
        """Generate optimized cache key"""
        key_data = f"{data_type}_{symbol}"
        if params:
            key_data += f"_{hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()[:8]}"
        return key_data
    
    # ⚡ ULTRA-FAST PRICE RETRIEVAL
    async def get_price_data(self, symbol: str, data_type: str) -> Optional[Dict]:
        """Get price data with multi-level caching for maximum speed"""
        cache_key = self.get_cache_key(data_type, symbol)
        
        # Level 1: Ultra-fast local cache (microseconds)
        if cache_key in self.local_cache:
            cached_data, timestamp = self.local_cache[cache_key]
            if (datetime.now() - timestamp).total_seconds() < 60:  # 1 minute local cache
                return {**cached_data, 'cache_level': 'local', 'response_time_ms': 0.1}
        
        # Level 2: Supabase price feed (milliseconds)
        try:
            response = self.supabase.client.table("price_feed")\
                .select("*")\
                .eq("symbol", symbol)\
                .eq("data_type", data_type)\
                .gte("last_updated", (datetime.now() - timedelta(minutes=5)).isoformat())\
                .order("last_updated", desc=True)\
                .limit(1)\
                .execute()
            
            if response.data:
                price_data = response.data[0]
                result = {
                    'price_usd': float(price_data['current_price']),
                    'change_24h': float(price_data.get('change_24h', 0)),
                    'source': f"⚡ Supabase Cache ({price_data['source']})",
                    'cache_level': 'supabase',
                    'response_time_ms': 50,
                    'last_updated': price_data['last_updated']
                }
                
                # Cache locally for even faster next access
                self.local_cache[cache_key] = (result, datetime.now())
                return result
        
        except Exception as e:
            print(f"Supabase cache error: {e}")
        
        # Level 3: API cache fallback
        return await self.get_api_cache(cache_key)
    
    async def get_api_cache(self, cache_key: str) -> Optional[Dict]:
        """Get data from API cache table"""
        try:
            response = self.supabase.client.table("api_cache")\
                .select("*")\
                .eq("cache_key", cache_key)\
                .gt("expires_at", datetime.now().isoformat())\
                .order("updated_at", desc=True)\
                .limit(1)\
                .execute()
            
            if response.data:
                cache_data = response.data[0]
                result = cache_data['response_data']
                result['cache_level'] = 'api_cache'
                result['response_time_ms'] = 100
                return result
        
        except Exception as e:
            print(f"API cache error: {e}")
        
        return None
    
    # 🚀 ULTRA-FAST DATA STORAGE
    async def store_price_data(self, symbol: str, data_type: str, price_data: Dict, source: str = "API"):
        """Store price data for ultra-fast retrieval"""
        try:
            # Store in price feed for immediate access
            feed_data = {
                "symbol": symbol,
                "data_type": data_type,
                "current_price": float(price_data.get('price_usd', 0)),
                "change_24h": float(price_data.get('change_24h', 0)),
                "volume_24h": float(price_data.get('volume_24h', 0)),
                "market_cap": float(price_data.get('market_cap', 0)),
                "source": source,
                "last_updated": datetime.now().isoformat(),
                "is_live": True
            }
            
            # Upsert for maximum speed
            self.supabase.client.table("price_feed")\
                .upsert(feed_data, on_conflict="symbol,data_type")\
                .execute()
            
            # Store in local cache for immediate next access
            cache_key = self.get_cache_key(data_type, symbol)
            self.local_cache[cache_key] = (price_data, datetime.now())
            
        except Exception as e:
            print(f"Error storing price data: {e}")
    
    async def store_api_cache(self, cache_key: str, data_type: str, symbol: str, response_data: Dict):
        """Store API response for fast retrieval"""
        try:
            cache_data = {
                "cache_key": cache_key,
                "data_type": data_type,
                "symbol": symbol,
                "response_data": response_data,
                "price_usd": float(response_data.get('price_usd', 0)),
                "change_24h": float(response_data.get('change_24h', 0)),
                "source": response_data.get('source', 'API'),
                "expires_at": (datetime.now() + timedelta(minutes=5)).isoformat()
            }
            
            self.supabase.client.table("api_cache")\
                .upsert(cache_data, on_conflict="cache_key")\
                .execute()
        
        except Exception as e:
            print(f"Error storing API cache: {e}")
    
    # 🔥 PRE-COMPUTED CALCULATIONS
    async def get_precomputed_calculation(self, calc_type: str, params: Dict) -> Optional[Dict]:
        """Get pre-computed calculation for instant results"""
        try:
            data_key = f"{calc_type}_{hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()}"
            
            response = self.supabase.client.table("precomputed_data")\
                .select("*")\
                .eq("data_key", data_key)\
                .order("updated_at", desc=True)\
                .limit(1)\
                .execute()
            
            if response.data:
                result = response.data[0]['computed_results']
                result['is_precomputed'] = True
                result['response_time_ms'] = 1  # Ultra-fast!
                return result
        
        except Exception as e:
            print(f"Error getting precomputed data: {e}")
        
        return None
    
    async def store_precomputed_calculation(self, calc_type: str, params: Dict, results: Dict, computation_time_ms: int = 0):
        """Store calculation for instant future retrieval"""
        try:
            data_key = f"{calc_type}_{hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()}"
            
            precomputed_data = {
                "data_key": data_key,
                "computation_type": calc_type,
                "input_parameters": params,
                "computed_results": results,
                "computation_time_ms": computation_time_ms,
                "updated_at": datetime.now().isoformat()
            }
            
            self.supabase.client.table("precomputed_data")\
                .upsert(precomputed_data, on_conflict="data_key")\
                .execute()
        
        except Exception as e:
            print(f"Error storing precomputed data: {e}")
    
    # ⚡ POPULAR CALCULATIONS CACHE
    async def get_popular_calculation(self, calc_hash: str) -> Optional[Dict]:
        """Get popular calculation for instant results"""
        try:
            response = self.supabase.client.table("popular_calculations")\
                .select("*")\
                .eq("calculation_hash", calc_hash)\
                .order("usage_count", desc=True)\
                .limit(1)\
                .execute()
            
            if response.data:
                result = response.data[0]['results']
                result['is_popular'] = True
                result['usage_count'] = response.data[0]['usage_count']
                result['response_time_ms'] = 0.5
                
                # Increment usage count
                self.supabase.client.table("popular_calculations")\
                    .update({"usage_count": response.data[0]['usage_count'] + 1, "last_accessed": datetime.now().isoformat()})\
                    .eq("calculation_hash", calc_hash)\
                    .execute()
                
                return result
        
        except Exception as e:
            print(f"Error getting popular calculation: {e}")
        
        return None
    
    async def store_popular_calculation(self, calc_type: str, params: Dict, results: Dict):
        """Store popular calculation for instant access"""
        try:
            calc_hash = hashlib.md5(json.dumps({"type": calc_type, "params": params}, sort_keys=True).encode()).hexdigest()
            
            popular_data = {
                "calculation_hash": calc_hash,
                "calculation_type": calc_type,
                "input_params": params,
                "results": results,
                "usage_count": 1,
                "last_accessed": datetime.now().isoformat()
            }
            
            self.supabase.client.table("popular_calculations")\
                .upsert(popular_data, on_conflict="calculation_hash")\
                .execute()
        
        except Exception as e:
            print(f"Error storing popular calculation: {e}")
    
    # 📊 PERFORMANCE TRACKING
    async def track_performance(self, endpoint: str, response_time_ms: int, cache_hit: bool = False, user_id: str = None):
        """Track performance metrics for optimization"""
        try:
            perf_data = {
                "endpoint": endpoint,
                "response_time_ms": response_time_ms,
                "cache_hit": cache_hit,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
            
            self.supabase.client.table("performance_metrics")\
                .insert(perf_data)\
                .execute()
        
        except Exception as e:
            print(f"Error tracking performance: {e}")
    
    # 🧹 CACHE MANAGEMENT
    async def cleanup_cache(self):
        """Clean up expired cache entries"""
        try:
            # Remove expired API cache
            self.supabase.client.table("api_cache")\
                .delete()\
                .lt("expires_at", datetime.now().isoformat())\
                .execute()
            
            # Clean local cache
            current_time = datetime.now()
            expired_keys = [
                key for key, (_, timestamp) in self.local_cache.items()
                if (current_time - timestamp).total_seconds() > 300  # 5 minutes
            ]
            for key in expired_keys:
                del self.local_cache[key]
        
        except Exception as e:
            print(f"Error cleaning cache: {e}")
    
    def get_cache_stats(self) -> Dict:
        """Get cache performance statistics"""
        return {
            "local_cache_size": len(self.local_cache),
            "cache_ttl_seconds": self.cache_ttl,
            "total_cached_items": len(self.local_cache)
        }

# 🚀 GLOBAL CACHE INSTANCE
@st.cache_resource
def get_supabase_cache() -> SupabaseCacheManager:
    """Get the global Supabase cache manager instance"""
    return SupabaseCacheManager()

# ⚡ PERFORMANCE DECORATORS
def supabase_cache(cache_type: str = "general", ttl_seconds: int = 300):
    """Decorator for ultra-fast Supabase caching"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            cache_manager = get_supabase_cache()
            
            # Generate cache key
            cache_key = f"{func.__name__}_{hashlib.md5(str(args).encode()).hexdigest()[:8]}"
            
            # Try to get cached result
            start_time = time.time()
            cached_result = await cache_manager.get_api_cache(cache_key)
            
            if cached_result:
                await cache_manager.track_performance(func.__name__, int((time.time() - start_time) * 1000), cache_hit=True)
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            execution_time = int((time.time() - start_time) * 1000)
            
            # Cache result
            if result:
                await cache_manager.store_api_cache(cache_key, cache_type, str(args), result)
            
            await cache_manager.track_performance(func.__name__, execution_time, cache_hit=False)
            return result
        
        return wrapper
    return decorator 