"""
API Monitor Service - 24x7 Provider Health Monitoring
Continuously monitors 100+ financial data providers and maintains health status in Redis
"""

import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

import redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from pydantic import BaseModel

from health_checker import HealthChecker
from provider_registry import ProviderRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
health_check_counter = Counter('api_monitor_health_checks_total', 'Total health checks performed', ['provider_id', 'status'])
health_check_duration = Histogram('api_monitor_health_check_duration_seconds', 'Health check duration', ['provider_id'])
provider_health_gauge = Gauge('api_monitor_provider_health', 'Provider health status (1=healthy, 0=unhealthy)', ['provider_id', 'category'])
active_providers_gauge = Gauge('api_monitor_active_providers', 'Number of active providers by category', ['category'])

# Global instances
scheduler: Optional[AsyncIOScheduler] = None
health_checker: Optional[HealthChecker] = None
provider_registry: Optional[ProviderRegistry] = None
redis_client: Optional[redis.Redis] = None

class ProviderHealth(BaseModel):
    provider_id: str
    status: str
    last_check: float
    response_time: Optional[float]
    error_message: Optional[str]
    uptime_percentage: float

class HealthSummary(BaseModel):
    total_providers: int
    healthy_providers: int
    unhealthy_providers: int
    categories: Dict[str, Dict[str, int]]
    last_updated: float

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown event handler"""
    await startup_event()
    yield
    await shutdown_event()

app = FastAPI(
    title="API Monitor Service",
    description="24x7 monitoring of 100+ financial data providers",
    version="1.0.0",
    lifespan=lifespan
)

async def startup_event():
    """Initialize services and start background monitoring"""
    global scheduler, health_checker, provider_registry, redis_client
    
    logger.info("Starting API Monitor Service...")
    
    # Initialize Redis connection
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    redis_password = os.getenv("REDIS_PASSWORD")
    
    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        decode_responses=True
    )
    
    # Test Redis connection
    try:
        await asyncio.get_event_loop().run_in_executor(None, redis_client.ping)
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        raise
    
    # Initialize provider registry
    registry_path = os.getenv("PROVIDER_REGISTRY_PATH", "/app/config/provider_registry.yaml")
    provider_registry = ProviderRegistry(registry_path)
    await provider_registry.load_registry()
    
    # Initialize health checker
    health_checker = HealthChecker(provider_registry, redis_client)
    
    # Start background scheduler
    scheduler = AsyncIOScheduler()
    
    # Schedule health checks every 60 seconds
    scheduler.add_job(
        perform_health_checks,
        'interval',
        seconds=60,
        id='health_check_job',
        max_instances=1
    )
    
    # Schedule metrics update every 30 seconds
    scheduler.add_job(
        update_prometheus_metrics,
        'interval',
        seconds=30,
        id='metrics_update_job',
        max_instances=1
    )
    
    scheduler.start()
    logger.info("Background scheduler started")
    
    # Perform initial health check
    await perform_health_checks()
    logger.info("API Monitor Service started successfully")

async def shutdown_event():
    """Cleanup on shutdown"""
    global scheduler, redis_client
    
    logger.info("Shutting down API Monitor Service...")
    
    if scheduler:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    if redis_client:
        redis_client.close()
        logger.info("Redis connection closed")

async def perform_health_checks():
    """Perform health checks on all providers"""
    if not health_checker or not provider_registry:
        logger.warning("Health checker or provider registry not initialized")
        return
    
    start_time = time.time()
    logger.info("Starting health check cycle...")
    
    try:
        # Get all providers from registry
        all_providers = provider_registry.list_providers()
        
        # Perform health checks with concurrency limit
        semaphore = asyncio.Semaphore(10)  # Limit concurrent checks
        
        async def check_provider(provider_config):
            async with semaphore:
                provider_id = provider_config['id']
                start_check = time.time()
                
                try:
                    result = await health_checker.check_provider_health(provider_config)
                    
                    # Record metrics
                    health_check_duration.labels(provider_id=provider_id).observe(time.time() - start_check)
                    health_check_counter.labels(provider_id=provider_id, status=result['status']).inc()
                    
                    logger.debug(f"Health check completed for {provider_id}: {result['status']}")
                    return result
                    
                except Exception as e:
                    logger.error(f"Health check failed for {provider_id}: {e}")
                    health_check_counter.labels(provider_id=provider_id, status='error').inc()
                    return {
                        'provider_id': provider_id,
                        'status': 'unhealthy',
                        'error': str(e)
                    }
        
        # Execute all health checks concurrently
        tasks = [check_provider(provider) for provider in all_providers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        healthy_count = 0
        total_count = len(results)
        
        for result in results:
            if isinstance(result, dict) and result.get('status') == 'healthy':
                healthy_count += 1
        
        duration = time.time() - start_time
        logger.info(f"Health check cycle completed: {healthy_count}/{total_count} providers healthy in {duration:.2f}s")
        
        # Publish health change events to Redis pubsub
        if redis_client:
            try:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    redis_client.publish,
                    'api.health.changed',
                    f'{{"healthy": {healthy_count}, "total": {total_count}, "timestamp": {time.time()}}}'
                )
            except Exception as e:
                logger.error(f"Failed to publish health event: {e}")
        
    except Exception as e:
        logger.error(f"Health check cycle failed: {e}")

async def update_prometheus_metrics():
    """Update Prometheus metrics from Redis health data"""
    if not redis_client or not provider_registry:
        return
    
    try:
        # Get all providers and their health status
        all_providers = provider_registry.list_providers()
        category_counts = {}
        
        for provider in all_providers:
            provider_id = provider['id']
            category = provider['category']
            
            # Get health status from Redis
            health_key = f"api_health:{provider_id}"
            health_data = await asyncio.get_event_loop().run_in_executor(
                None, redis_client.hgetall, health_key
            )
            
            # Update provider health gauge
            is_healthy = 1 if health_data.get('status') == 'healthy' else 0
            provider_health_gauge.labels(provider_id=provider_id, category=category).set(is_healthy)
            
            # Count by category
            if category not in category_counts:
                category_counts[category] = {'healthy': 0, 'total': 0}
            category_counts[category]['total'] += 1
            if is_healthy:
                category_counts[category]['healthy'] += 1
        
        # Update category metrics
        for category, counts in category_counts.items():
            active_providers_gauge.labels(category=category).set(counts['healthy'])
            
    except Exception as e:
        logger.error(f"Failed to update Prometheus metrics: {e}")

@app.get("/health")
async def service_health():
    """Service health check endpoint"""
    if not redis_client:
        raise HTTPException(status_code=503, detail="Redis not available")
    
    try:
        await asyncio.get_event_loop().run_in_executor(None, redis_client.ping)
        return {
            "status": "healthy",
            "service": "api-monitor",
            "timestamp": time.time(),
            "redis_connected": True,
            "scheduler_running": scheduler.running if scheduler else False
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {e}")

@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return PlainTextResponse(generate_latest(), media_type="text/plain")

@app.get("/api/providers/status", response_model=HealthSummary)
async def get_provider_status():
    """Get overall provider health summary"""
    if not redis_client or not provider_registry:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        all_providers = provider_registry.list_providers()
        total_providers = len(all_providers)
        healthy_providers = 0
        categories = {}
        
        for provider in all_providers:
            provider_id = provider['id']
            category = provider['category']
            
            # Initialize category if not exists
            if category not in categories:
                categories[category] = {'healthy': 0, 'total': 0}
            categories[category]['total'] += 1
            
            # Check health status
            health_key = f"api_health:{provider_id}"
            health_data = await asyncio.get_event_loop().run_in_executor(
                None, redis_client.hgetall, health_key
            )
            
            if health_data.get('status') == 'healthy':
                healthy_providers += 1
                categories[category]['healthy'] += 1
        
        return HealthSummary(
            total_providers=total_providers,
            healthy_providers=healthy_providers,
            unhealthy_providers=total_providers - healthy_providers,
            categories=categories,
            last_updated=time.time()
        )
        
    except Exception as e:
        logger.error(f"Failed to get provider status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/providers/{provider_id}/health", response_model=ProviderHealth)
async def get_provider_health(provider_id: str):
    """Get individual provider health status"""
    if not redis_client:
        raise HTTPException(status_code=503, detail="Redis not available")
    
    try:
        health_key = f"api_health:{provider_id}"
        health_data = await asyncio.get_event_loop().run_in_executor(
            None, redis_client.hgetall, health_key
        )
        
        if not health_data:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        # Calculate uptime percentage from history
        uptime_key = f"api_uptime:{provider_id}"
        uptime_data = await asyncio.get_event_loop().run_in_executor(
            None, redis_client.lrange, uptime_key, 0, -1
        )
        
        # Calculate uptime from last 100 checks
        if uptime_data:
            healthy_checks = sum(1 for status in uptime_data if status == 'healthy')
            uptime_percentage = (healthy_checks / len(uptime_data)) * 100
        else:
            uptime_percentage = 0.0
        
        return ProviderHealth(
            provider_id=provider_id,
            status=health_data.get('status', 'unknown'),
            last_check=float(health_data.get('last_check', 0)),
            response_time=float(health_data.get('response_time', 0)) if health_data.get('response_time') else None,
            error_message=health_data.get('error'),
            uptime_percentage=uptime_percentage
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get provider health for {provider_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/providers/{provider_id}/force-check")
async def force_provider_check(provider_id: str, background_tasks: BackgroundTasks):
    """Force immediate health check for a specific provider"""
    if not health_checker or not provider_registry:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        provider_config = provider_registry.get_provider(provider_id)
        if not provider_config:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        # Schedule background check
        background_tasks.add_task(health_checker.check_provider_health, provider_config)
        
        return {
            "message": f"Health check scheduled for provider {provider_id}",
            "provider_id": provider_id,
            "timestamp": time.time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to force check for {provider_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/providers/categories")
async def get_provider_categories():
    """Get list of all provider categories"""
    if not provider_registry:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        all_providers = provider_registry.list_providers()
        categories = {}
        
        for provider in all_providers:
            category = provider['category']
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        
        return {
            "categories": categories,
            "total_providers": sum(categories.values()),
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Failed to get categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8006,
        log_level="info",
        reload=False
    ) 