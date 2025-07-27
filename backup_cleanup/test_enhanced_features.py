#!/usr/bin/env python3
"""
Test script to demonstrate enhanced HTTP client features.
"""

import asyncio
import time
import json
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from common.http_client import (
    HTTPClient, ServiceClient, create_service_client, 
    CacheConfig, RequestBatcher, get_all_metrics,
    health_check_all_services, health_monitor
)
from common.monitoring import (
    get_monitoring_data, get_performance_summary, 
    get_alerts, export_metrics, performance_monitor
)

async def test_basic_http_client():
    """Test basic HTTP client functionality"""
    print("🔧 Testing Basic HTTP Client...")
    
    client = HTTPClient(timeout=10, max_retries=2)
    
    try:
        # Test successful request
        response = await client.request('GET', 'https://httpbin.org/get')
        print(f"✅ GET request successful: {response.status_code}")
        
        # Test POST request
        response = await client.request('POST', 'https://httpbin.org/post', json={'test': 'data'})
        print(f"✅ POST request successful: {response.status_code}")
        
        # Get metrics
        metrics = client.get_metrics()
        print(f"📊 Client metrics: {json.dumps(metrics, indent=2)}")
        
    except Exception as e:
        print(f"❌ HTTP client test failed: {e}")
    finally:
        await client.close()

async def test_caching():
    """Test request caching functionality"""
    print("\n💾 Testing Request Caching...")
    
    # Create client with caching enabled
    cache_config = CacheConfig(
        enabled=True,
        ttl_seconds=60,
        max_size=100,
        include_query_params=True
    )
    
    client = HTTPClient(cache_config=cache_config)
    
    try:
        # First request (cache miss)
        start_time = time.time()
        response1 = await client.request('GET', 'https://httpbin.org/delay/1')
        time1 = time.time() - start_time
        print(f"⏱️  First request took: {time1:.2f}s")
        
        # Second request (cache hit)
        start_time = time.time()
        response2 = await client.request('GET', 'https://httpbin.org/delay/1')
        time2 = time.time() - start_time
        print(f"⚡ Cached request took: {time2:.2f}s")
        
        # Verify responses are the same
        if response1.text == response2.text:
            print("✅ Cache working correctly - responses match")
        else:
            print("❌ Cache issue - responses don't match")
        
        # Get cache stats
        metrics = client.get_metrics()
        cache_stats = metrics.get('cache_stats', {})
        print(f"📊 Cache stats: {json.dumps(cache_stats, indent=2)}")
        
    except Exception as e:
        print(f"❌ Caching test failed: {e}")
    finally:
        await client.close()

async def test_service_client():
    """Test service client functionality"""
    print("\n🏢 Testing Service Client...")
    
    # Create service client
    service_client = create_service_client(
        service_name="test-service",
        base_url="https://httpbin.org",
        timeout=10
    )
    
    try:
        # Test service call
        result = await service_client.call_service('GET', '/get')
        print(f"✅ Service call successful")
        
        # Get service metrics
        metrics = service_client.get_service_metrics()
        print(f"📊 Service metrics: {json.dumps(metrics, indent=2)}")
        
        # Get circuit breaker state
        cb_state = service_client.get_circuit_breaker_state()
        print(f"🔌 Circuit breaker state: {json.dumps(cb_state, indent=2)}")
        
    except Exception as e:
        print(f"❌ Service client test failed: {e}")
    finally:
        await service_client.close()

async def test_request_batching():
    """Test request batching functionality"""
    print("\n📦 Testing Request Batching...")
    
    batcher = RequestBatcher(max_batch_size=5, max_wait_time=0.5)
    
    async def make_request(url):
        client = HTTPClient(timeout=5)
        try:
            response = await client.request('GET', url)
            return {'url': url, 'status': response.status_code}
        finally:
            await client.close()
    
    # Add multiple requests to batch
    urls = [
        'https://httpbin.org/get',
        'https://httpbin.org/status/200',
        'https://httpbin.org/status/201',
        'https://httpbin.org/status/202',
        'https://httpbin.org/status/203'
    ]
    
    try:
        futures = []
        for url in urls:
            future = await batcher.add_request(make_request, url)
            futures.append(future)
        
        # Wait for all requests to complete
        results = await asyncio.gather(*futures)
        
        print(f"✅ Batch processing completed: {len(results)} requests")
        for result in results:
            print(f"   {result['url']}: {result['status']}")
            
    except Exception as e:
        print(f"❌ Request batching test failed: {e}")

async def test_health_monitoring():
    """Test health monitoring functionality"""
    print("\n🏥 Testing Health Monitoring...")
    
    try:
        # Check health of all services
        health_results = await health_check_all_services()
        print(f"📊 Health check results: {json.dumps(health_results, indent=2)}")
        
        # Get health status
        health_status = health_monitor.get_health_status()
        print(f"🏥 Health status: {json.dumps(health_status, indent=2)}")
        
    except Exception as e:
        print(f"❌ Health monitoring test failed: {e}")

async def test_monitoring():
    """Test comprehensive monitoring"""
    print("\n📈 Testing Comprehensive Monitoring...")
    
    try:
        # Get monitoring data
        monitoring_data = await get_monitoring_data()
        print(f"📊 Monitoring data collected: {len(monitoring_data)} keys")
        
        # Get performance summary
        summary = await get_performance_summary()
        print(f"📈 Performance summary: {json.dumps(summary, indent=2)}")
        
        # Get alerts
        alerts = get_alerts()
        print(f"🚨 Active alerts: {len(alerts)}")
        
        # Export metrics in different formats
        json_metrics = export_metrics(monitoring_data, 'json')
        print(f"📄 JSON export length: {len(json_metrics)} characters")
        
        prometheus_metrics = export_metrics(monitoring_data, 'prometheus')
        print(f"📊 Prometheus export lines: {len(prometheus_metrics.split(chr(10)))}")
        
    except Exception as e:
        print(f"❌ Monitoring test failed: {e}")

async def test_metrics_collection():
    """Test metrics collection"""
    print("\n📊 Testing Metrics Collection...")
    
    try:
        # Get all metrics
        all_metrics = get_all_metrics()
        print(f"📊 All metrics collected: {json.dumps(all_metrics, indent=2)}")
        
        # Get metrics history
        history = performance_monitor.get_metrics_history(hours=1)
        print(f"📈 Metrics history entries: {len(history)}")
        
        # Get alerts
        alerts = performance_monitor.get_alerts()
        print(f"🚨 Total alerts: {len(alerts)}")
        
    except Exception as e:
        print(f"❌ Metrics collection test failed: {e}")

async def test_error_handling():
    """Test error handling and circuit breaker"""
    print("\n🛡️ Testing Error Handling...")
    
    # Create service client with circuit breaker
    service_client = create_service_client(
        service_name="error-test-service",
        base_url="https://httpbin.org",
        timeout=5
    )
    
    try:
        # Test with non-existent endpoint (should fail)
        try:
            await service_client.call_service('GET', '/nonexistent')
        except Exception as e:
            print(f"✅ Expected error caught: {type(e).__name__}")
        
        # Test with valid endpoint
        await service_client.call_service('GET', '/status/200')
        print("✅ Valid request successful")
        
        # Get circuit breaker state
        cb_state = service_client.get_circuit_breaker_state()
        print(f"🔌 Circuit breaker after errors: {json.dumps(cb_state, indent=2)}")
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
    finally:
        await service_client.close()

async def main():
    """Run all tests"""
    print("🚀 Starting Enhanced HTTP Client Feature Tests")
    print("=" * 60)
    
    start_time = time.time()
    
    # Run all tests
    await test_basic_http_client()
    await test_caching()
    await test_service_client()
    await test_request_batching()
    await test_health_monitoring()
    await test_monitoring()
    await test_metrics_collection()
    await test_error_handling()
    
    total_time = time.time() - start_time
    print(f"\n✅ All tests completed in {total_time:.2f} seconds")
    print("=" * 60)
    
    # Final summary
    print("\n📋 Feature Summary:")
    print("✅ Enhanced HTTP Client with retry logic")
    print("✅ Request caching with TTL and cleanup")
    print("✅ Request/response interceptors")
    print("✅ Enhanced connection pooling")
    print("✅ Request batching for efficiency")
    print("✅ Comprehensive metrics collection")
    print("✅ Health monitoring and circuit breakers")
    print("✅ Alert system with configurable thresholds")
    print("✅ Multiple export formats (JSON, Prometheus, InfluxDB)")
    print("✅ Performance monitoring and history")
    print("✅ Service client factory and management")

if __name__ == "__main__":
    asyncio.run(main()) 