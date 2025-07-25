"""
Health Cache - Centralized provider health status management in Redis
Provides clean interface for health status storage and retrieval
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any, Union

import redis

logger = logging.getLogger(__name__)

class HealthCache:
    """
    Centralized health cache manager for provider health status
    Uses Redis for storage with TTL management and health scoring
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        
        # Default TTL values (in seconds)
        self.health_ttl = 3600  # 1 hour
        self.uptime_ttl = 86400  # 24 hours
        self.history_ttl = 604800  # 7 days
        
        # Health scoring configuration
        self.health_score_window = 100  # Number of recent checks to consider
        self.healthy_weight = 1.0
        self.unhealthy_weight = -1.0
        self.circuit_breaker_weight = -2.0
    
    async def set_provider_health(self, 
                                provider_id: str, 
                                status: str, 
                                latency: Optional[float] = None, 
                                error: Optional[str] = None,
                                http_status: Optional[int] = None) -> bool:
        """Store provider health status in Redis"""
        try:
            timestamp = time.time()
            
            # Prepare health data
            health_data = {
                'status': status,
                'last_check': timestamp,
                'response_time': latency or 0,
                'error': error or '',
                'http_status': http_status or 0
            }
            
            # Store current health status
            health_key = f"api_health:{provider_id}"
            self.redis_client.hset(health_key, mapping=health_data)
            self.redis_client.expire(health_key, self.health_ttl)
            
            # Update uptime history
            await self._update_uptime_history(provider_id, status)
            
            # Store detailed history
            await self._store_health_history(provider_id, {
                'status': status,
                'timestamp': timestamp,
                'response_time': latency,
                'error': error,
                'http_status': http_status
            })
            
            # Update health score
            await self._update_health_score(provider_id)
            
            logger.debug(f"Updated health for {provider_id}: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set health for {provider_id}: {e}")
            return False
    
    async def get_provider_health(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """Get current provider health status"""
        try:
            health_key = f"api_health:{provider_id}"
            health_data = self.redis_client.hgetall(health_key)
            
            if not health_data:
                return None
            
            # Convert numeric fields
            result = {
                'provider_id': provider_id,
                'status': health_data.get('status', 'unknown'),
                'last_check': float(health_data.get('last_check', 0)),
                'response_time': float(health_data.get('response_time', 0)),
                'error': health_data.get('error', ''),
                'http_status': int(health_data.get('http_status', 0))
            }
            
            # Add health score and uptime
            result['health_score'] = await self.get_health_score(provider_id)
            result['uptime_percentage'] = await self.get_uptime_percentage(provider_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get health for {provider_id}: {e}")
            return None
    
    async def get_healthy_providers(self, category: Optional[str] = None) -> List[str]:
        """Get list of provider IDs that are currently healthy"""
        try:
            # Get all health keys
            pattern = "api_health:*"
            health_keys = self.redis_client.keys(pattern)
            
            healthy_providers = []
            
            for key in health_keys:
                provider_id = key.replace('api_health:', '')
                
                # Get status
                status = self.redis_client.hget(key, 'status')
                if status == 'healthy':
                    healthy_providers.append(provider_id)
            
            return healthy_providers
            
        except Exception as e:
            logger.error(f"Failed to get healthy providers: {e}")
            return []
    
    async def is_provider_healthy(self, provider_id: str) -> bool:
        """Check if a provider is currently healthy"""
        try:
            health_key = f"api_health:{provider_id}"
            status = self.redis_client.hget(health_key, 'status')
            return status == 'healthy'
            
        except Exception as e:
            logger.error(f"Failed to check health for {provider_id}: {e}")
            return False
    
    async def get_all_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get health status for all providers"""
        try:
            pattern = "api_health:*"
            health_keys = self.redis_client.keys(pattern)
            
            all_status = {}
            
            for key in health_keys:
                provider_id = key.replace('api_health:', '')
                health_data = await self.get_provider_health(provider_id)
                if health_data:
                    all_status[provider_id] = health_data
            
            return all_status
            
        except Exception as e:
            logger.error(f"Failed to get all provider status: {e}")
            return {}
    
    async def get_uptime_percentage(self, provider_id: str, window: Optional[int] = None) -> float:
        """Calculate uptime percentage for a provider"""
        try:
            window = window or self.health_score_window
            uptime_key = f"api_uptime:{provider_id}"
            
            # Get recent status history
            status_history = self.redis_client.lrange(uptime_key, 0, window - 1)
            
            if not status_history:
                return 0.0
            
            # Calculate uptime percentage
            healthy_count = sum(1 for status in status_history if status == 'healthy')
            uptime_percentage = (healthy_count / len(status_history)) * 100
            
            return round(uptime_percentage, 2)
            
        except Exception as e:
            logger.error(f"Failed to calculate uptime for {provider_id}: {e}")
            return 0.0
    
    async def get_health_score(self, provider_id: str) -> float:
        """Calculate health score for a provider (0-100)"""
        try:
            score_key = f"api_health_score:{provider_id}"
            cached_score = self.redis_client.get(score_key)
            
            if cached_score:
                return float(cached_score)
            
            # Calculate score from recent history
            uptime_key = f"api_uptime:{provider_id}"
            status_history = self.redis_client.lrange(uptime_key, 0, self.health_score_window - 1)
            
            if not status_history:
                return 0.0
            
            # Weight different statuses
            total_weight = 0
            for status in status_history:
                if status == 'healthy':
                    total_weight += self.healthy_weight
                elif status == 'unhealthy':
                    total_weight += self.unhealthy_weight
                elif status == 'circuit_breaker_open':
                    total_weight += self.circuit_breaker_weight
            
            # Normalize to 0-100 scale
            max_possible_score = len(status_history) * self.healthy_weight
            if max_possible_score > 0:
                score = max(0, (total_weight / max_possible_score) * 100)
            else:
                score = 0.0
            
            # Cache the score for 5 minutes
            self.redis_client.setex(score_key, 300, score)
            
            return round(score, 2)
            
        except Exception as e:
            logger.error(f"Failed to calculate health score for {provider_id}: {e}")
            return 0.0
    
    async def get_provider_summary(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive summary for a provider"""
        try:
            health_data = await self.get_provider_health(provider_id)
            if not health_data:
                return None
            
            # Get additional metrics
            uptime_percentage = await self.get_uptime_percentage(provider_id)
            health_score = await self.get_health_score(provider_id)
            
            # Get recent response times
            avg_response_time = await self._get_average_response_time(provider_id)
            
            # Get failure count in last hour
            failure_count = await self._get_recent_failure_count(provider_id)
            
            return {
                'provider_id': provider_id,
                'current_status': health_data['status'],
                'last_check': health_data['last_check'],
                'uptime_percentage': uptime_percentage,
                'health_score': health_score,
                'average_response_time': avg_response_time,
                'recent_failures': failure_count,
                'error_message': health_data.get('error')
            }
            
        except Exception as e:
            logger.error(f"Failed to get summary for {provider_id}: {e}")
            return None
    
    async def cleanup_expired_data(self) -> int:
        """Clean up expired health data and return count of cleaned items"""
        try:
            cleaned_count = 0
            current_time = time.time()
            
            # Clean old uptime data
            uptime_pattern = "api_uptime:*"
            uptime_keys = self.redis_client.keys(uptime_pattern)
            
            for key in uptime_keys:
                # Keep only recent entries
                self.redis_client.ltrim(key, 0, self.health_score_window - 1)
                cleaned_count += 1
            
            # Clean old history data
            history_pattern = "api_history:*"
            history_keys = self.redis_client.keys(history_pattern)
            
            for key in history_keys:
                # Keep only recent entries
                self.redis_client.ltrim(key, 0, 999)  # Keep last 1000 entries
                cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} expired health data items")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired data: {e}")
            return 0
    
    async def _update_uptime_history(self, provider_id: str, status: str):
        """Update uptime history for provider"""
        try:
            uptime_key = f"api_uptime:{provider_id}"
            
            # Add new status to history
            self.redis_client.lpush(uptime_key, status)
            
            # Keep only recent history
            self.redis_client.ltrim(uptime_key, 0, self.health_score_window - 1)
            
            # Set TTL
            self.redis_client.expire(uptime_key, self.uptime_ttl)
            
        except Exception as e:
            logger.error(f"Failed to update uptime history for {provider_id}: {e}")
    
    async def _store_health_history(self, provider_id: str, health_record: Dict[str, Any]):
        """Store detailed health history"""
        try:
            history_key = f"api_history:{provider_id}"
            
            # Store as JSON
            record_json = json.dumps(health_record)
            self.redis_client.lpush(history_key, record_json)
            
            # Keep only recent history
            self.redis_client.ltrim(history_key, 0, 999)
            
            # Set TTL
            self.redis_client.expire(history_key, self.history_ttl)
            
        except Exception as e:
            logger.error(f"Failed to store health history for {provider_id}: {e}")
    
    async def _update_health_score(self, provider_id: str):
        """Update cached health score"""
        try:
            # Clear cached score to force recalculation
            score_key = f"api_health_score:{provider_id}"
            self.redis_client.delete(score_key)
            
        except Exception as e:
            logger.error(f"Failed to update health score for {provider_id}: {e}")
    
    async def _get_average_response_time(self, provider_id: str, window: int = 10) -> float:
        """Get average response time from recent history"""
        try:
            history_key = f"api_history:{provider_id}"
            recent_history = self.redis_client.lrange(history_key, 0, window - 1)
            
            response_times = []
            for record_json in recent_history:
                try:
                    record = json.loads(record_json)
                    if record.get('response_time') and record['response_time'] > 0:
                        response_times.append(record['response_time'])
                except json.JSONDecodeError:
                    continue
            
            if response_times:
                return round(sum(response_times) / len(response_times), 3)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Failed to get average response time for {provider_id}: {e}")
            return 0.0
    
    async def _get_recent_failure_count(self, provider_id: str, hours: int = 1) -> int:
        """Get count of failures in recent time period"""
        try:
            history_key = f"api_history:{provider_id}"
            recent_history = self.redis_client.lrange(history_key, 0, 100)  # Check last 100 records
            
            cutoff_time = time.time() - (hours * 3600)
            failure_count = 0
            
            for record_json in recent_history:
                try:
                    record = json.loads(record_json)
                    if (record.get('timestamp', 0) > cutoff_time and 
                        record.get('status') in ['unhealthy', 'circuit_breaker_open']):
                        failure_count += 1
                except json.JSONDecodeError:
                    continue
            
            return failure_count
            
        except Exception as e:
            logger.error(f"Failed to get failure count for {provider_id}: {e}")
            return 0 