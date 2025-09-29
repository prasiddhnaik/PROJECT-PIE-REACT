# Comprehensive Financial Analytics Platform Documentation

## 📋 Table of Contents

1. [Platform Overview](#platform-overview)
2. [Architecture](#architecture)
3. [Enhanced Features](#enhanced-features)
4. [API Documentation](#api-documentation)
5. [Installation & Setup](#installation--setup)
6. [Usage Guides](#usage-guides)
7. [Configuration](#configuration)
8. [Monitoring & Analytics](#monitoring--analytics)
9. [Troubleshooting](#troubleshooting)
10. [Development Guide](#development-guide)
11. [API Reference](#api-reference)
12. [Best Practices](#best-practices)

---

## 🚀 Platform Overview

The Enhanced Financial Analytics Platform is a comprehensive microservices-based application that combines traditional financial data with modern AI capabilities and 10 free non-finance APIs to provide a rich, engaging user experience.

### Key Features
- **Real-time Financial Data**: Stock prices, crypto data, market analytics
- **AI-Powered Insights**: Machine learning predictions and analysis
- **10 Free Non-Finance APIs**: Weather, nutrition, entertainment, and more
- **Advanced Monitoring**: Comprehensive system health and performance tracking
- **Enhanced HTTP Client**: Caching, retry logic, circuit breakers
- **Microservices Architecture**: Scalable, maintainable design
- **Windows XP UI Theme**: Nostalgic, functional interface

### Technology Stack
- **Backend**: Python, FastAPI, asyncio
- **Frontend**: React, TypeScript, Tailwind CSS
- **Database**: Multiple data sources with caching
- **Monitoring**: Custom metrics, health checks, alerts
- **APIs**: 10+ external APIs with intelligent integration

---

## 🏗️ Architecture

### Microservices Structure

```
Financial Analytics Platform
├── API Gateway (Port 8001)
│   ├── Enhanced API Routes
│   ├── Monitoring Routes
│   ├── Financial Routes
│   └── Authentication
├── AI Service (Port 8002)
│   ├── OpenRouter Integration
│   ├── Chat Memory
│   └── AI Predictions
├── Data Service (Port 8003)
│   ├── Multi-source Data
│   ├── Caching Layer
│   └── Data Processing
├── Chart Service (Port 8004)
│   ├── Technical Analysis
│   └── Chart Generation
└── Common Libraries
    ├── HTTP Client
    ├── Monitoring
    ├── Rate Limiting
    └── Error Handling
```

### Data Flow

1. **Client Request** → API Gateway
2. **Authentication** → Rate Limiting → Route Selection
3. **Service Call** → Enhanced HTTP Client (with caching/retry)
4. **External API** → Data Processing → Response
5. **Monitoring** → Metrics Collection → Health Updates

### Enhanced HTTP Client Architecture

```
HTTP Client
├── Request Interceptors
├── Circuit Breaker
├── Retry Logic (Exponential Backoff)
├── Request Caching (TTL-based)
├── Connection Pooling
├── Request Batching
└── Response Interceptors
```

---

## ⚡ Enhanced Features

### 1. Advanced HTTP Client

#### Caching System
- **TTL-based caching** with configurable expiration
- **LRU eviction** for memory management
- **Cache invalidation** strategies
- **Cache statistics** and monitoring

```python
# Example: Configure caching
cache_config = CacheConfig(
    enabled=True,
    ttl_seconds=300,  # 5 minutes
    max_size=1000,
    include_query_params=True
)
```

#### Circuit Breaker Pattern
- **Failure threshold**: 5 consecutive failures
- **Recovery timeout**: 60 seconds
- **Half-open state**: Test requests before full recovery
- **State monitoring**: Real-time circuit breaker status

#### Retry Logic
- **Exponential backoff**: 1s, 2s, 4s, 8s, 16s
- **Jitter**: ±25% randomization to prevent thundering herd
- **Maximum retries**: 3 attempts
- **Retryable status codes**: 429, 500, 502, 503, 504

### 2. Comprehensive Monitoring

#### System Metrics
- **CPU usage**: Real-time processor utilization
- **Memory usage**: RAM consumption and availability
- **Disk I/O**: Storage performance metrics
- **Network I/O**: Bandwidth usage and latency
- **Process count**: Active service instances

#### API Metrics
- **Request counts**: Total, successful, failed
- **Response times**: Min, max, average, percentiles
- **Error rates**: By status code and service
- **Cache hit rates**: Performance optimization tracking
- **Rate limiting**: Throttling statistics

#### Health Monitoring
- **Service health**: Individual service status
- **Dependency health**: External API availability
- **Resource health**: System resource monitoring
- **Alert system**: Configurable thresholds and notifications

### 3. 10 Free Non-Finance APIs

#### Weather APIs (OpenWeather)
- **Current weather**: Real-time conditions
- **Forecasts**: 5-day weather predictions
- **Market impact analysis**: Weather-based trading insights
- **Energy demand predictions**: Weather correlation with energy stocks

#### Health & Nutrition (API Ninjas)
- **Nutrition data**: Detailed food information
- **Calorie tracking**: Health-conscious features
- **Macronutrient analysis**: Protein, carbs, fat breakdown
- **Multi-item analysis**: Batch nutrition processing

#### Motivation & Entertainment
- **Inspirational quotes**: Daily motivation for traders
- **Random jokes**: Stress relief and engagement
- **Cat images**: Entertainment content
- **NASA data**: Educational space content

#### Utility & Development
- **IP geolocation**: Location-based insights
- **Random user data**: Testing and development
- **Public APIs directory**: API discovery
- **Batch operations**: Efficient multi-API calls

---

## 📚 API Documentation

### Financial APIs

#### Stock Data
```http
GET /api/stocks/price?symbol=AAPL
GET /api/stocks/history?symbol=AAPL&period=1y
GET /api/stocks/search?query=apple
```

#### Crypto Data
```http
GET /api/crypto/price?symbol=BTC
GET /api/crypto/market-data?symbol=ETH
GET /api/crypto/top-100
```

#### Market Analysis
```http
GET /api/analytics/technical?symbol=AAPL
GET /api/analytics/sentiment?symbol=AAPL
GET /api/analytics/portfolio/performance
```

### Enhanced APIs

#### Weather & Market Impact
```http
GET /api/enhanced/weather/current?city=New York&country_code=US
GET /api/enhanced/weather/forecast?city=London&country_code=GB
GET /api/enhanced/weather/insights?city=Tokyo&country_code=JP
GET /api/enhanced/weather/market-impact?city=New York&country_code=US
```

#### Health & Nutrition
```http
GET /api/enhanced/nutrition?food_item=apple
GET /api/enhanced/nutrition/analysis?food_items=apple,banana,chicken
```

#### Entertainment & Motivation
```http
GET /api/enhanced/quotes/random?category=success
GET /api/enhanced/entertainment/cat
GET /api/enhanced/entertainment/joke?category=Programming
GET /api/enhanced/nasa/apod
```

#### Utility & Development
```http
GET /api/enhanced/geolocation/ip?ip_address=8.8.8.8
GET /api/enhanced/testing/user
GET /api/enhanced/apis/public?category=finance
```

#### Combined Features
```http
GET /api/enhanced/insights/daily
GET /api/enhanced/batch?apis=weather,quote,cat&city=London
GET /api/enhanced/health
```

### Monitoring APIs

#### System Health
```http
GET /api/monitoring/health
GET /api/monitoring/metrics
GET /api/monitoring/alerts
GET /api/monitoring/services
```

#### Performance Data
```http
GET /api/monitoring/metrics/summary
GET /api/monitoring/history?service=weather
GET /api/monitoring/cache/stats
GET /api/monitoring/circuit-breakers
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Docker (optional)
- Git

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd project-pie-react
```

2. **Install Python dependencies**
```bash
cd backup_cleanup
pip install -r requirements_enhanced.txt
```

3. **Install Node.js dependencies**
```bash
cd ../apps/web
npm install
```

4. **Set up environment variables**
```bash
cp env.example .env
# Edit .env with your API keys and configuration
```

5. **Start the services**
```bash
# Start API Gateway
cd backup_cleanup/api-gateway
python main.py

# Start AI Service
cd ../ai-service
python main.py

# Start Data Service
cd ../data-service
python main.py

# Start Chart Service
cd ../chart-service
python main.py

# Start Frontend
cd ../../apps/web
npm run dev
```

### Docker Setup

```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Configuration

```bash
# API Keys
OPENROUTER_API_KEY=your_openrouter_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
POLYGON_API_KEY=your_polygon_key

# Service Configuration
API_GATEWAY_PORT=8001
AI_SERVICE_PORT=8002
DATA_SERVICE_PORT=8003
CHART_SERVICE_PORT=8004

# Monitoring
ENABLE_MONITORING=true
METRICS_EXPORT_PORT=9090
ALERT_EMAIL=admin@example.com

# Caching
REDIS_URL=redis://localhost:6379
CACHE_TTL=300
MAX_CACHE_SIZE=1000
```

---

## 📖 Usage Guides

### Getting Started with Financial Data

1. **Fetch Stock Prices**
```python
import requests

# Get current stock price
response = requests.get(
    "http://localhost:8001/api/stocks/price",
    params={"symbol": "AAPL"}
)
stock_data = response.json()
print(f"AAPL: ${stock_data['price']}")
```

2. **Get Historical Data**
```python
# Get 1 year of historical data
response = requests.get(
    "http://localhost:8001/api/stocks/history",
    params={"symbol": "AAPL", "period": "1y"}
)
history = response.json()
print(f"Data points: {len(history['data'])}")
```

3. **Technical Analysis**
```python
# Get technical indicators
response = requests.get(
    "http://localhost:8001/api/analytics/technical",
    params={"symbol": "AAPL"}
)
analysis = response.json()
print(f"RSI: {analysis['rsi']}")
print(f"MACD: {analysis['macd']}")
```

### Using Enhanced APIs

1. **Weather-Based Trading**
```python
# Get weather insights for trading
response = requests.get(
    "http://localhost:8001/api/enhanced/weather/insights",
    params={"city": "New York", "country_code": "US"}
)
insights = response.json()

market_impact = insights['market_impact']
print(f"Energy demand: {market_impact['energy_demand']}")
print(f"Agriculture impact: {market_impact['agriculture']}")
```

2. **Daily Motivation**
```python
# Get daily inspirational quote
response = requests.get(
    "http://localhost:8001/api/enhanced/quotes/random",
    params={"category": "success"}
)
quote = response.json()
print(f"Quote: {quote['quote']}")
print(f"Author: {quote['author']}")
```

3. **Health Tracking**
```python
# Analyze nutrition for multiple foods
response = requests.get(
    "http://localhost:8001/api/enhanced/nutrition/analysis",
    params={"food_items": ["apple", "banana", "chicken breast"]}
)
nutrition = response.json()

summary = nutrition['summary']
print(f"Total calories: {summary['total_calories']}")
print(f"Total protein: {summary['total_protein_g']}g")
```

4. **Batch API Operations**
```python
# Call multiple APIs efficiently
response = requests.get(
    "http://localhost:8001/api/enhanced/batch",
    params={
        "apis": ["weather", "quote", "cat", "joke"],
        "city": "London",
        "food_item": "coffee"
    }
)
results = response.json()

for api_name, result in results['results'].items():
    print(f"{api_name}: {result}")
```

### Monitoring and Analytics

1. **System Health Check**
```python
# Check overall system health
response = requests.get("http://localhost:8001/api/monitoring/health")
health = response.json()
print(f"Status: {health['status']}")
print(f"Services: {health['services']}")
```

2. **Performance Metrics**
```python
# Get detailed metrics
response = requests.get("http://localhost:8001/api/monitoring/metrics")
metrics = response.json()

print(f"Total requests: {metrics['total_requests']}")
print(f"Success rate: {metrics['success_rate']}%")
print(f"Average response time: {metrics['avg_response_time']}ms")
```

3. **Cache Statistics**
```python
# Monitor cache performance
response = requests.get("http://localhost:8001/api/monitoring/cache/stats")
cache_stats = response.json()

print(f"Cache hits: {cache_stats['hits']}")
print(f"Cache misses: {cache_stats['misses']}")
print(f"Hit rate: {cache_stats['hit_rate']}%")
```

---

## ⚙️ Configuration

### Service Configuration

#### API Gateway
```python
# config.py
API_GATEWAY_CONFIG = {
    "host": "0.0.0.0",
    "port": 8001,
    "debug": False,
    "rate_limit": {
        "requests_per_minute": 100,
        "burst_size": 20
    },
    "cors": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "headers": ["*"]
    }
}
```

#### Enhanced HTTP Client
```python
# http_client_config.py
HTTP_CLIENT_CONFIG = {
    "timeout": 30,
    "max_retries": 3,
    "retry_delay": 1,
    "circuit_breaker": {
        "failure_threshold": 5,
        "recovery_timeout": 60,
        "expected_exception": Exception
    },
    "caching": {
        "enabled": True,
        "ttl_seconds": 300,
        "max_size": 1000
    }
}
```

#### Monitoring Configuration
```python
# monitoring_config.py
MONITORING_CONFIG = {
    "enabled": True,
    "metrics_interval": 60,
    "health_check_interval": 30,
    "alert_thresholds": {
        "cpu_usage": 80,
        "memory_usage": 85,
        "error_rate": 5,
        "response_time": 2000
    },
    "export_formats": ["json", "prometheus", "influxdb"]
}
```

### API Rate Limits

| API Category | Rate Limit | Burst Size |
|-------------|------------|------------|
| Financial Data | 100/min | 20 |
| Weather APIs | 60/min | 10 |
| Nutrition APIs | 50/min | 8 |
| Entertainment APIs | 120/min | 15 |
| Monitoring APIs | 200/min | 30 |

### Caching Configuration

| Data Type | TTL | Max Size | Strategy |
|-----------|-----|----------|----------|
| Stock Prices | 30s | 1000 | LRU |
| Weather Data | 10min | 500 | TTL |
| Nutrition Data | 24h | 200 | TTL |
| Quotes | 2h | 100 | LRU |
| Entertainment | 30min | 300 | TTL |

---

## 📊 Monitoring & Analytics

### Dashboard Access

1. **Main Dashboard**: `http://localhost:8001/monitoring/dashboard`
2. **Metrics Export**: `http://localhost:8001/api/monitoring/metrics`
3. **Health Status**: `http://localhost:8001/api/monitoring/health`
4. **Alert Management**: `http://localhost:8001/api/monitoring/alerts`

### Key Metrics

#### Performance Metrics
- **Response Time**: Average, 95th percentile, 99th percentile
- **Throughput**: Requests per second
- **Error Rate**: Percentage of failed requests
- **Availability**: Uptime percentage

#### Business Metrics
- **API Usage**: Most popular endpoints
- **User Engagement**: Daily active users
- **Feature Adoption**: Enhanced API usage
- **Revenue Impact**: Trading volume correlation

#### System Metrics
- **Resource Utilization**: CPU, memory, disk, network
- **Service Health**: Individual service status
- **Dependency Health**: External API availability
- **Cache Performance**: Hit rates and efficiency

### Alert Configuration

```python
# alerts.py
ALERT_RULES = {
    "high_error_rate": {
        "condition": "error_rate > 5%",
        "duration": "5 minutes",
        "action": "email_admin"
    },
    "slow_response": {
        "condition": "avg_response_time > 2000ms",
        "duration": "2 minutes",
        "action": "scale_service"
    },
    "high_cpu": {
        "condition": "cpu_usage > 80%",
        "duration": "1 minute",
        "action": "alert_ops"
    }
}
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. API Rate Limiting
**Symptoms**: 429 errors, slow responses
**Solutions**:
- Check rate limit configuration
- Implement request batching
- Use caching to reduce API calls
- Monitor usage patterns

#### 2. Circuit Breaker Trips
**Symptoms**: Service unavailable errors
**Solutions**:
- Check external API health
- Review circuit breaker configuration
- Implement fallback mechanisms
- Monitor failure patterns

#### 3. Cache Performance Issues
**Symptoms**: High cache miss rates, slow responses
**Solutions**:
- Adjust TTL settings
- Increase cache size
- Review cache key strategy
- Monitor memory usage

#### 4. Memory Leaks
**Symptoms**: Increasing memory usage, slow performance
**Solutions**:
- Review cache eviction policies
- Check for memory leaks in code
- Monitor object lifecycle
- Implement memory profiling

### Debug Mode

Enable debug mode for detailed logging:

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable HTTP client debugging
HTTP_CLIENT_CONFIG["debug"] = True

# Enable service debugging
SERVICE_CONFIG["debug"] = True
```

### Health Check Commands

```bash
# Check API Gateway health
curl http://localhost:8001/api/monitoring/health

# Check individual service health
curl http://localhost:8002/health  # AI Service
curl http://localhost:8003/health  # Data Service
curl http://localhost:8004/health  # Chart Service

# Check external API health
curl http://localhost:8001/api/monitoring/services

# Get detailed metrics
curl http://localhost:8001/api/monitoring/metrics
```

---

## 👨‍💻 Development Guide

### Adding New APIs

1. **Create API Integration**
```python
# common/api_integrations.py
class NewAPIIntegration:
    def __init__(self):
        self.base_url = "https://api.example.com"
        self.rate_limit = 100
    
    async def get_data(self, params):
        # Implementation
        pass
```

2. **Add API Routes**
```python
# api-gateway/new_api_routes.py
@router.get("/new-api/data")
async def get_new_api_data(
    param: str = Query(...),
    _: bool = Depends(api_gateway_rate_limit())
):
    # Implementation
    pass
```

3. **Update Main Application**
```python
# api-gateway/main.py
from new_api_routes import router as new_api_router
app.include_router(new_api_router)
```

### Creating Custom Components

1. **Enhanced HTTP Client**
```python
# Custom HTTP client with specific features
class CustomHTTPClient(HTTPClient):
    def __init__(self, custom_config):
        super().__init__()
        self.custom_config = custom_config
    
    async def custom_request(self, method, url, **kwargs):
        # Custom implementation
        pass
```

2. **Custom Monitoring**
```python
# Custom metrics collector
class CustomMetricsCollector:
    def __init__(self):
        self.metrics = {}
    
    def record_metric(self, name, value):
        self.metrics[name] = value
    
    def get_metrics(self):
        return self.metrics
```

### Testing Guidelines

1. **Unit Tests**
```python
# test_api_integrations.py
import pytest
from common.api_integrations import get_weather_data

@pytest.mark.asyncio
async def test_weather_api():
    result = await get_weather_data("New York", "US")
    assert result["temperature"] is not None
    assert result["location"] == "New York,US"
```

2. **Integration Tests**
```python
# test_api_gateway.py
import requests

def test_weather_endpoint():
    response = requests.get(
        "http://localhost:8001/api/enhanced/weather/current",
        params={"city": "London", "country_code": "GB"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "temperature" in data
```

3. **Performance Tests**
```python
# test_performance.py
import time
import asyncio

async def test_batch_performance():
    start_time = time.time()
    
    # Test batch API calls
    tasks = [
        get_weather_data("New York", "US"),
        get_nutrition_info("apple"),
        get_random_quote()
    ]
    
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    assert end_time - start_time < 5.0  # Should complete within 5 seconds
```

---

## 📖 API Reference

### Authentication

All API endpoints support optional authentication:

```http
Authorization: Bearer <your-token>
```

### Error Responses

Standard error format:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 60 seconds.",
    "details": {
      "limit": 100,
      "reset_time": "2024-01-15T10:30:00Z"
    }
  }
}
```

### Common Status Codes

- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Authentication required
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Pagination

For endpoints that return lists:

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

### Rate Limiting Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642234567
```

---

## 🎯 Best Practices

### API Design

1. **Consistent Naming**: Use kebab-case for URLs, camelCase for JSON
2. **Versioning**: Include API version in URL path
3. **Error Handling**: Provide detailed error messages
4. **Documentation**: Keep API docs up to date
5. **Rate Limiting**: Implement appropriate limits

### Performance

1. **Caching**: Cache frequently accessed data
2. **Connection Pooling**: Reuse HTTP connections
3. **Batch Operations**: Combine multiple requests
4. **Async Processing**: Use async/await for I/O operations
5. **Monitoring**: Track performance metrics

### Security

1. **Authentication**: Implement proper auth mechanisms
2. **Rate Limiting**: Prevent abuse
3. **Input Validation**: Validate all inputs
4. **HTTPS**: Use secure connections
5. **API Keys**: Rotate keys regularly

### Monitoring

1. **Health Checks**: Monitor service health
2. **Metrics Collection**: Track key metrics
3. **Alerting**: Set up appropriate alerts
4. **Logging**: Implement structured logging
5. **Tracing**: Track request flow

### Development

1. **Code Quality**: Follow coding standards
2. **Testing**: Write comprehensive tests
3. **Documentation**: Document code and APIs
4. **Version Control**: Use proper branching strategy
5. **CI/CD**: Automate deployment pipeline

---

## 📞 Support

### Getting Help

1. **Documentation**: Check this comprehensive guide
2. **API Documentation**: Visit `/docs` endpoint
3. **GitHub Issues**: Report bugs and feature requests
4. **Community**: Join our developer community
5. **Email Support**: Contact support@example.com

### Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Write tests**
5. **Submit a pull request**

### Resources

- **API Documentation**: [Interactive Docs](http://localhost:8001/docs)
- **GitHub Repository**: [Project Repository](https://github.com/your-repo)
- **Community Forum**: [Developer Community](https://community.example.com)
- **Video Tutorials**: [YouTube Channel](https://youtube.com/example)

---

This comprehensive documentation provides everything you need to understand, deploy, and extend the Enhanced Financial Analytics Platform. The platform combines traditional financial data with modern AI capabilities and 10 free non-finance APIs to create a rich, engaging user experience that goes beyond typical financial applications.

For more detailed information about specific components, refer to the individual README files in each service directory. 