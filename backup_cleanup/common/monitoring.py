"""
Comprehensive monitoring utilities for the microservices architecture.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import psutil
import os

from .http_client import (
    get_all_metrics, health_check_all_services, health_monitor,
    ServiceClient, HTTPClient, RequestMetrics, CacheConfig
)

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System-level metrics"""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_usage_percent: float = 0.0
    network_io: Dict[str, float] = field(default_factory=dict)
    process_count: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ServiceHealth:
    """Service health information"""
    service_name: str
    status: str  # healthy, unhealthy, degraded
    response_time: float
    last_check: datetime
    error_count: int = 0
    success_rate: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)

class PerformanceMonitor:
    """Comprehensive performance monitoring"""
    
    def __init__(self):
        self.metrics_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        self.alert_thresholds = {
            'response_time_ms': 5000,  # 5 seconds
            'error_rate': 0.1,  # 10%
            'cpu_percent': 80.0,
            'memory_percent': 85.0
        }
        self.alerts: List[Dict[str, Any]] = []
    
    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect system-level metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage_percent=disk.percent,
                network_io={
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                process_count=len(psutil.pids()),
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return SystemMetrics()
    
    async def collect_service_metrics(self) -> Dict[str, Any]:
        """Collect service-level metrics"""
        try:
            return get_all_metrics()
        except Exception as e:
            logger.error(f"Failed to collect service metrics: {e}")
            return {}
    
    async def check_service_health(self) -> List[ServiceHealth]:
        """Check health of all services"""
        try:
            health_results = await health_check_all_services()
            service_health = []
            
            for service_name, result in health_results.items():
                status = "healthy" if result.get('healthy', False) else "unhealthy"
                response_time = result.get('check_time', 0.0)
                
                service_health.append(ServiceHealth(
                    service_name=service_name,
                    status=status,
                    response_time=response_time,
                    last_check=datetime.fromisoformat(result.get('last_check', datetime.now().isoformat())),
                    details=result
                ))
            
            return service_health
        except Exception as e:
            logger.error(f"Failed to check service health: {e}")
            return []
    
    async def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect all metrics"""
        system_metrics = await self.collect_system_metrics()
        service_metrics = await self.collect_service_metrics()
        service_health = await self.check_service_health()
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_percent': system_metrics.cpu_percent,
                'memory_percent': system_metrics.memory_percent,
                'disk_usage_percent': system_metrics.disk_usage_percent,
                'network_io': system_metrics.network_io,
                'process_count': system_metrics.process_count
            },
            'services': service_metrics,
            'health': {
                service.service_name: {
                    'status': service.status,
                    'response_time': service.response_time,
                    'last_check': service.last_check.isoformat(),
                    'error_count': service.error_count,
                    'success_rate': service.success_rate
                }
                for service in service_health
            }
        }
        
        # Store in history
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history.pop(0)
        
        # Check for alerts
        await self._check_alerts(metrics)
        
        return metrics
    
    async def _check_alerts(self, metrics: Dict[str, Any]):
        """Check for alert conditions"""
        alerts = []
        
        # System alerts
        system = metrics.get('system', {})
        if system.get('cpu_percent', 0) > self.alert_thresholds['cpu_percent']:
            alerts.append({
                'type': 'system_cpu_high',
                'message': f"CPU usage is {system['cpu_percent']}%",
                'severity': 'warning',
                'timestamp': datetime.now().isoformat()
            })
        
        if system.get('memory_percent', 0) > self.alert_thresholds['memory_percent']:
            alerts.append({
                'type': 'system_memory_high',
                'message': f"Memory usage is {system['memory_percent']}%",
                'severity': 'warning',
                'timestamp': datetime.now().isoformat()
            })
        
        # Service alerts
        services = metrics.get('services', {}).get('service_clients', {})
        for service_name, service_data in services.items():
            avg_response_time = service_data.get('average_response_time', 0)
            success_rate = service_data.get('success_rate', 1.0)
            
            if avg_response_time * 1000 > self.alert_thresholds['response_time_ms']:
                alerts.append({
                    'type': 'service_slow',
                    'service': service_name,
                    'message': f"Service {service_name} response time is {avg_response_time:.2f}s",
                    'severity': 'warning',
                    'timestamp': datetime.now().isoformat()
                })
            
            if success_rate < (1 - self.alert_thresholds['error_rate']):
                alerts.append({
                    'type': 'service_errors',
                    'service': service_name,
                    'message': f"Service {service_name} success rate is {success_rate:.2%}",
                    'severity': 'error',
                    'timestamp': datetime.now().isoformat()
                })
        
        # Health alerts
        health = metrics.get('health', {})
        for service_name, health_data in health.items():
            if health_data.get('status') == 'unhealthy':
                alerts.append({
                    'type': 'service_unhealthy',
                    'service': service_name,
                    'message': f"Service {service_name} is unhealthy",
                    'severity': 'error',
                    'timestamp': datetime.now().isoformat()
                })
        
        # Add new alerts
        self.alerts.extend(alerts)
        
        # Keep only recent alerts (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']) > cutoff_time
        ]
    
    def get_alerts(self, severity: str = None) -> List[Dict[str, Any]]:
        """Get alerts, optionally filtered by severity"""
        if severity:
            return [alert for alert in self.alerts if alert['severity'] == severity]
        return self.alerts
    
    def get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get metrics history for the specified number of hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            metrics for metrics in self.metrics_history
            if datetime.fromisoformat(metrics['timestamp']) > cutoff_time
        ]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of performance metrics"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = self.get_metrics_history(hours=1)  # Last hour
        
        if not recent_metrics:
            return {}
        
        # Calculate averages
        cpu_values = [m['system']['cpu_percent'] for m in recent_metrics]
        memory_values = [m['system']['memory_percent'] for m in recent_metrics]
        
        # Service performance
        service_performance = {}
        services = recent_metrics[-1].get('services', {}).get('service_clients', {})
        
        for service_name, service_data in services.items():
            service_performance[service_name] = {
                'success_rate': service_data.get('success_rate', 0),
                'avg_response_time': service_data.get('average_response_time', 0),
                'total_requests': service_data.get('total_requests', 0),
                'error_count': service_data.get('failed_requests', 0)
            }
        
        return {
            'summary_timestamp': datetime.now().isoformat(),
            'time_period_hours': 1,
            'system_averages': {
                'cpu_percent': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                'memory_percent': sum(memory_values) / len(memory_values) if memory_values else 0
            },
            'service_performance': service_performance,
            'active_alerts': len([a for a in self.alerts if a['severity'] == 'error']),
            'total_metrics_collected': len(self.metrics_history)
        }

class MetricsExporter:
    """Export metrics to various formats and destinations"""
    
    def __init__(self):
        self.export_formats = {
            'json': self._export_json,
            'prometheus': self._export_prometheus,
            'influxdb': self._export_influxdb
        }
    
    def _export_json(self, metrics: Dict[str, Any]) -> str:
        """Export metrics as JSON"""
        return json.dumps(metrics, indent=2, default=str)
    
    def _export_prometheus(self, metrics: Dict[str, Any]) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        
        # System metrics
        system = metrics.get('system', {})
        lines.append(f"# HELP system_cpu_percent CPU usage percentage")
        lines.append(f"# TYPE system_cpu_percent gauge")
        lines.append(f"system_cpu_percent {system.get('cpu_percent', 0)}")
        
        lines.append(f"# HELP system_memory_percent Memory usage percentage")
        lines.append(f"# TYPE system_memory_percent gauge")
        lines.append(f"system_memory_percent {system.get('memory_percent', 0)}")
        
        lines.append(f"# HELP system_disk_usage_percent Disk usage percentage")
        lines.append(f"# TYPE system_disk_usage_percent gauge")
        lines.append(f"system_disk_usage_percent {system.get('disk_usage_percent', 0)}")
        
        # Service metrics
        services = metrics.get('services', {}).get('service_clients', {})
        for service_name, service_data in services.items():
            lines.append(f"# HELP service_requests_total Total requests for {service_name}")
            lines.append(f"# TYPE service_requests_total counter")
            lines.append(f'service_requests_total{{service="{service_name}"}} {service_data.get("total_requests", 0)}')
            
            lines.append(f"# HELP service_response_time_seconds Response time for {service_name}")
            lines.append(f"# TYPE service_response_time_seconds gauge")
            lines.append(f'service_response_time_seconds{{service="{service_name}"}} {service_data.get("average_response_time", 0)}')
            
            lines.append(f"# HELP service_success_rate Success rate for {service_name}")
            lines.append(f"# TYPE service_success_rate gauge")
            lines.append(f'service_success_rate{{service="{service_name}"}} {service_data.get("success_rate", 0)}')
        
        return '\n'.join(lines)
    
    def _export_influxdb(self, metrics: Dict[str, Any]) -> List[str]:
        """Export metrics in InfluxDB line protocol format"""
        lines = []
        timestamp = int(datetime.fromisoformat(metrics['timestamp']).timestamp() * 1e9)
        
        # System metrics
        system = metrics.get('system', {})
        lines.append(f"system_metrics cpu_percent={system.get('cpu_percent', 0)},"
                    f"memory_percent={system.get('memory_percent', 0)},"
                    f"disk_usage_percent={system.get('disk_usage_percent', 0)} {timestamp}")
        
        # Service metrics
        services = metrics.get('services', {}).get('service_clients', {})
        for service_name, service_data in services.items():
            lines.append(f"service_metrics,service={service_name} "
                        f"total_requests={service_data.get('total_requests', 0)},"
                        f"success_rate={service_data.get('success_rate', 0)},"
                        f"avg_response_time={service_data.get('average_response_time', 0)} {timestamp}")
        
        return lines
    
    def export(self, metrics: Dict[str, Any], format: str = 'json') -> str:
        """Export metrics in the specified format"""
        if format not in self.export_formats:
            raise ValueError(f"Unsupported format: {format}")
        
        return self.export_formats[format](metrics)

# Global monitoring instance
performance_monitor = PerformanceMonitor()
metrics_exporter = MetricsExporter()

# Convenience functions
async def get_monitoring_data() -> Dict[str, Any]:
    """Get comprehensive monitoring data"""
    return await performance_monitor.collect_all_metrics()

async def get_performance_summary() -> Dict[str, Any]:
    """Get performance summary"""
    return performance_monitor.get_performance_summary()

def get_alerts(severity: str = None) -> List[Dict[str, Any]]:
    """Get alerts"""
    return performance_monitor.get_alerts(severity)

def export_metrics(metrics: Dict[str, Any], format: str = 'json') -> str:
    """Export metrics in specified format"""
    return metrics_exporter.export(metrics, format)

# Health check functions for services
async def check_http_client_health() -> bool:
    """Check if HTTP client is working"""
    try:
        client = HTTPClient(timeout=5)
        response = await client.request('GET', 'http://httpbin.org/get')
        await client.close()
        return response.status_code == 200
    except Exception:
        return False

async def check_service_connectivity(service_name: str, base_url: str) -> bool:
    """Check if a specific service is reachable"""
    try:
        client = ServiceClient(base_url=base_url, service_name=service_name, timeout=5)
        await client.call_service('GET', '/health')
        await client.close()
        return True
    except Exception:
        return False

# Setup default health monitors
def setup_default_health_monitors():
    """Setup default health monitors"""
    health_monitor.add_monitor('http_client', check_http_client_health)
    
    # Add service-specific monitors
    service_configs = {
        'data-service': 'http://data-service:8002',
        'chart-service': 'http://chart-service:8003',
        'graph-service': 'http://graph-service:8004',
        'ai-service': 'http://ai-service:8005'
    }
    
    for service_name, base_url in service_configs.items():
        health_monitor.add_monitor(
            service_name,
            lambda s=service_name, u=base_url: check_service_connectivity(s, u)
        )

# Initialize monitoring
setup_default_health_monitors() 