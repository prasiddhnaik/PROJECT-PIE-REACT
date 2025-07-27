"""
Monitoring routes for the API Gateway.
Provides comprehensive monitoring and observability endpoints.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse, PlainTextResponse

from common.monitoring import (
    get_monitoring_data, get_performance_summary, get_alerts,
    export_metrics, performance_monitor, metrics_exporter
)
from common.http_client import (
    get_all_metrics, health_check_all_services, health_monitor,
    get_service_client, ServiceClient
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    try:
        # Quick health check
        health_results = await health_check_all_services()
        overall_healthy = all(result.get('healthy', False) for result in health_results.values())
        
        return {
            "status": "healthy" if overall_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "services": health_results
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Health check failed")

@router.get("/metrics")
async def get_metrics(format: str = Query("json", description="Output format: json, prometheus, influxdb")):
    """Get comprehensive metrics"""
    try:
        metrics = await get_monitoring_data()
        
        if format == "json":
            return JSONResponse(content=metrics)
        elif format == "prometheus":
            prometheus_data = export_metrics(metrics, "prometheus")
            return PlainTextResponse(content=prometheus_data)
        elif format == "influxdb":
            influxdb_data = export_metrics(metrics, "influxdb")
            return PlainTextResponse(content="\n".join(influxdb_data))
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
    
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to collect metrics")

@router.get("/metrics/summary")
async def get_metrics_summary():
    """Get performance summary"""
    try:
        summary = await get_performance_summary()
        return summary
    except Exception as e:
        logger.error(f"Failed to get metrics summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics summary")

@router.get("/alerts")
async def get_alerts_endpoint(
    severity: Optional[str] = Query(None, description="Filter by severity: warning, error"),
    limit: int = Query(50, description="Maximum number of alerts to return")
):
    """Get alerts"""
    try:
        alerts = get_alerts(severity)
        # Sort by timestamp (newest first) and limit
        alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        return alerts[:limit]
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alerts")

@router.get("/services")
async def get_services_status():
    """Get detailed status of all services"""
    try:
        # Get service metrics
        service_metrics = get_all_metrics()
        
        # Get health status
        health_results = await health_check_all_services()
        
        # Combine metrics and health
        services_status = {}
        
        for service_name, metrics in service_metrics.get('service_clients', {}).items():
            health = health_results.get(service_name, {})
            
            services_status[service_name] = {
                'metrics': metrics,
                'health': health,
                'status': 'healthy' if health.get('healthy', False) else 'unhealthy',
                'last_check': health.get('last_check', datetime.now().isoformat())
            }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'services': services_status
        }
    
    except Exception as e:
        logger.error(f"Failed to get services status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get services status")

@router.get("/services/{service_name}")
async def get_service_details(service_name: str):
    """Get detailed information about a specific service"""
    try:
        # Get service metrics
        service_metrics = get_all_metrics()
        service_data = service_metrics.get('service_clients', {}).get(service_name)
        
        if not service_data:
            raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
        
        # Get health status
        health_results = await health_check_all_services()
        health_data = health_results.get(service_name, {})
        
        # Get circuit breaker state
        circuit_breaker_state = {}
        try:
            # Try to get circuit breaker state from service client
            service_clients = getattr(health_monitor, '_service_clients', {})
            if service_name in service_clients:
                circuit_breaker_state = service_clients[service_name].get_circuit_breaker_state()
        except Exception:
            pass
        
        return {
            'service_name': service_name,
            'timestamp': datetime.now().isoformat(),
            'metrics': service_data,
            'health': health_data,
            'circuit_breaker': circuit_breaker_state,
            'status': 'healthy' if health_data.get('healthy', False) else 'unhealthy'
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get service details for {service_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get service details")

@router.get("/system")
async def get_system_metrics():
    """Get system-level metrics"""
    try:
        metrics = await get_monitoring_data()
        return {
            'timestamp': datetime.now().isoformat(),
            'system': metrics.get('system', {}),
            'summary': {
                'cpu_percent': metrics.get('system', {}).get('cpu_percent', 0),
                'memory_percent': metrics.get('system', {}).get('memory_percent', 0),
                'disk_usage_percent': metrics.get('system', {}).get('disk_usage_percent', 0),
                'process_count': metrics.get('system', {}).get('process_count', 0)
            }
        }
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system metrics")

@router.get("/history")
async def get_metrics_history(
    hours: int = Query(24, description="Number of hours of history to retrieve"),
    service: Optional[str] = Query(None, description="Filter by service name")
):
    """Get historical metrics"""
    try:
        history = performance_monitor.get_metrics_history(hours)
        
        if service:
            # Filter by service
            filtered_history = []
            for entry in history:
                if service in entry.get('services', {}).get('service_clients', {}):
                    filtered_history.append(entry)
            history = filtered_history
        
        return {
            'timestamp': datetime.now().isoformat(),
            'hours': hours,
            'service_filter': service,
            'entries_count': len(history),
            'history': history
        }
    
    except Exception as e:
        logger.error(f"Failed to get metrics history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics history")

@router.post("/refresh")
async def refresh_metrics(background_tasks: BackgroundTasks):
    """Trigger a metrics refresh"""
    try:
        # Add background task to refresh metrics
        background_tasks.add_task(performance_monitor.collect_all_metrics)
        
        return {
            "message": "Metrics refresh triggered",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to trigger metrics refresh: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger metrics refresh")

@router.get("/dashboard")
async def get_dashboard_data():
    """Get comprehensive dashboard data"""
    try:
        # Collect all data in parallel
        tasks = [
            get_monitoring_data(),
            get_performance_summary(),
            health_check_all_services()
        ]
        
        metrics, summary, health_results = await asyncio.gather(*tasks)
        
        # Get alerts
        alerts = get_alerts()
        error_alerts = [a for a in alerts if a['severity'] == 'error']
        warning_alerts = [a for a in alerts if a['severity'] == 'warning']
        
        # Calculate service status summary
        service_summary = {}
        for service_name, health_data in health_results.items():
            service_summary[service_name] = {
                'status': 'healthy' if health_data.get('healthy', False) else 'unhealthy',
                'response_time': health_data.get('check_time', 0),
                'last_check': health_data.get('last_check', datetime.now().isoformat())
            }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'overview': {
                'total_services': len(service_summary),
                'healthy_services': len([s for s in service_summary.values() if s['status'] == 'healthy']),
                'unhealthy_services': len([s for s in service_summary.values() if s['status'] == 'unhealthy']),
                'error_alerts': len(error_alerts),
                'warning_alerts': len(warning_alerts),
                'system_cpu': metrics.get('system', {}).get('cpu_percent', 0),
                'system_memory': metrics.get('system', {}).get('memory_percent', 0)
            },
            'services': service_summary,
            'alerts': {
                'errors': error_alerts[:5],  # Top 5 error alerts
                'warnings': warning_alerts[:5]  # Top 5 warning alerts
            },
            'performance': summary,
            'system': metrics.get('system', {})
        }
    
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data")

@router.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    try:
        metrics = get_all_metrics()
        cache_stats = {}
        
        # Extract cache stats from service clients
        for service_name, service_data in metrics.get('service_clients', {}).items():
            http_client_metrics = service_data.get('http_client_metrics', {})
            cache_stats[service_name] = http_client_metrics.get('cache_stats', {})
        
        return {
            'timestamp': datetime.now().isoformat(),
            'cache_stats': cache_stats
        }
    
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cache stats")

@router.post("/cache/clear")
async def clear_cache(service: Optional[str] = Query(None, description="Clear cache for specific service")):
    """Clear cache for all services or a specific service"""
    try:
        # This would need to be implemented in the HTTP client
        # For now, return a placeholder response
        return {
            "message": f"Cache clear requested for {'all services' if not service else service}",
            "timestamp": datetime.now().isoformat(),
            "note": "Cache clearing is not yet implemented"
        }
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")

@router.get("/circuit-breakers")
async def get_circuit_breaker_states():
    """Get circuit breaker states for all services"""
    try:
        # Get service metrics to find all services
        service_metrics = get_all_metrics()
        circuit_breaker_states = {}
        
        for service_name in service_metrics.get('service_clients', {}).keys():
            try:
                # Try to get circuit breaker state
                # This is a simplified approach - in practice you'd need to access the actual service clients
                circuit_breaker_states[service_name] = {
                    'state': 'unknown',
                    'note': 'Circuit breaker state not directly accessible'
                }
            except Exception:
                circuit_breaker_states[service_name] = {
                    'state': 'unknown',
                    'error': 'Failed to get circuit breaker state'
                }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'circuit_breakers': circuit_breaker_states
        }
    
    except Exception as e:
        logger.error(f"Failed to get circuit breaker states: {e}")
        raise HTTPException(status_code=500, detail="Failed to get circuit breaker states")

# Health check endpoints for load balancers
@router.get("/health/live")
async def liveness_check():
    """Liveness check for Kubernetes/load balancers"""
    return {"status": "alive", "timestamp": datetime.now().isoformat()}

@router.get("/health/ready")
async def readiness_check():
    """Readiness check for Kubernetes/load balancers"""
    try:
        # Check if we can collect basic metrics
        await get_monitoring_data()
        return {"status": "ready", "timestamp": datetime.now().isoformat()}
    except Exception:
        raise HTTPException(status_code=503, detail="Service not ready") 