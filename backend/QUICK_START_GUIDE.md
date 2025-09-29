# 🚀 Quick Start Guide - Enhanced Financial Analytics Platform

Get up and running with the enhanced financial analytics platform in under 10 minutes!

## 📋 What You'll Get

- **Real-time financial data** (stocks, crypto, market analytics)
- **10 free non-finance APIs** (weather, nutrition, entertainment, etc.)
- **AI-powered insights** with OpenRouter integration
- **Advanced monitoring** and health checks
- **Enhanced HTTP client** with caching and circuit breakers
- **Windows XP UI theme** for nostalgic appeal

## ⚡ 5-Minute Setup

### 1. Clone and Install

```bash
# Clone the repository
git clone <your-repo-url>
cd project-pie-react

# Install Python dependencies
cd backup_cleanup
pip install -r requirements_enhanced.txt

# Install Node.js dependencies
cd ../apps/web
npm install
```

### 2. Configure Environment

```bash
# Copy environment template
cd backup_cleanup
cp env.example .env

# Edit .env with your API keys (optional for basic functionality)
nano .env
```

**Minimal .env configuration:**
```bash
# Optional API keys (platform works without them)
OPENROUTER_API_KEY=your_key_here
ALPHA_VANTAGE_API_KEY=your_key_here

# Service ports
API_GATEWAY_PORT=8001
AI_SERVICE_PORT=8002
DATA_SERVICE_PORT=8003
CHART_SERVICE_PORT=8004

# Enable monitoring
ENABLE_MONITORING=true
```

### 3. Start Services

```bash
# Terminal 1: API Gateway
cd backup_cleanup/api-gateway
python main.py

# Terminal 2: AI Service
cd backup_cleanup/ai-service
python main.py

# Terminal 3: Data Service
cd backup_cleanup/data-service
python main.py

# Terminal 4: Chart Service
cd backup_cleanup/chart-service
python main.py

# Terminal 5: Frontend
cd ../../apps/web
npm run dev
```

### 4. Verify Installation

```bash
# Check API Gateway health
curl http://localhost:8001/api/monitoring/health

# Test enhanced APIs
curl http://localhost:8001/api/enhanced/health

# Test weather API
curl "http://localhost:8001/api/enhanced/weather/current?city=New York&country_code=US"

# Test quotes API
curl http://localhost:8001/api/enhanced/quotes/random
```

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main web application |
| **API Gateway** | http://localhost:8001 | All API endpoints |
| **API Docs** | http://localhost:8001/docs | Interactive API documentation |
| **Monitoring** | http://localhost:8001/monitoring/dashboard | System health dashboard |
| **Health Check** | http://localhost:8001/api/monitoring/health | Service status |

## 🎯 Quick Examples

### 1. Get Stock Data

```python
import requests

# Get current stock price
response = requests.get(
    "http://localhost:8001/api/stocks/price",
    params={"symbol": "AAPL"}
)
print(f"AAPL: ${response.json()['price']}")
```

### 2. Weather-Based Trading

```python
# Get weather insights for trading decisions
response = requests.get(
    "http://localhost:8001/api/enhanced/weather/insights",
    params={"city": "New York", "country_code": "US"}
)
insights = response.json()
print(f"Energy demand: {insights['market_impact']['energy_demand']}")
```

### 3. Daily Motivation

```python
# Get inspirational quote
response = requests.get(
    "http://localhost:8001/api/enhanced/quotes/random",
    params={"category": "success"}
)
quote = response.json()
print(f"Quote: {quote['quote']}")
```

### 4. Health Tracking

```python
# Analyze nutrition
response = requests.get(
    "http://localhost:8001/api/enhanced/nutrition/analysis",
    params={"food_items": ["apple", "banana", "chicken breast"]}
)
nutrition = response.json()
print(f"Total calories: {nutrition['summary']['total_calories']}")
```

### 5. Batch API Operations

```python
# Call multiple APIs efficiently
response = requests.get(
    "http://localhost:8001/api/enhanced/batch",
    params={
        "apis": ["weather", "quote", "cat", "joke"],
        "city": "London"
    }
)
results = response.json()
for api_name, result in results['results'].items():
    print(f"{api_name}: {result}")
```

## 🔧 Available APIs

### Financial APIs
- `GET /api/stocks/price?symbol=AAPL` - Stock prices
- `GET /api/crypto/price?symbol=BTC` - Crypto prices
- `GET /api/analytics/technical?symbol=AAPL` - Technical analysis

### Enhanced APIs (10 Free Non-Finance APIs)

#### Weather & Market Impact
- `GET /api/enhanced/weather/current?city=New York&country_code=US`
- `GET /api/enhanced/weather/forecast?city=London&country_code=GB`
- `GET /api/enhanced/weather/insights?city=Tokyo&country_code=JP`
- `GET /api/enhanced/weather/market-impact?city=New York&country_code=US`

#### Health & Nutrition
- `GET /api/enhanced/nutrition?food_item=apple`
- `GET /api/enhanced/nutrition/analysis?food_items=apple,banana,chicken`

#### Entertainment & Motivation
- `GET /api/enhanced/quotes/random?category=success`
- `GET /api/enhanced/entertainment/cat`
- `GET /api/enhanced/entertainment/joke?category=Programming`
- `GET /api/enhanced/nasa/apod`

#### Utility & Development
- `GET /api/enhanced/geolocation/ip?ip_address=8.8.8.8`
- `GET /api/enhanced/testing/user`
- `GET /api/enhanced/apis/public?category=finance`

#### Combined Features
- `GET /api/enhanced/insights/daily`
- `GET /api/enhanced/batch?apis=weather,quote,cat&city=London`
- `GET /api/enhanced/health`

### Monitoring APIs
- `GET /api/monitoring/health` - System health
- `GET /api/monitoring/metrics` - Performance metrics
- `GET /api/monitoring/alerts` - Active alerts
- `GET /api/monitoring/cache/stats` - Cache performance

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Test all enhanced APIs
cd backup_cleanup
python test_enhanced_apis.py

# Test enhanced HTTP client features
python test_enhanced_features.py
```

## 📊 Monitoring Dashboard

Access the monitoring dashboard at `http://localhost:8001/monitoring/dashboard` to see:

- **System Health**: CPU, memory, disk usage
- **API Performance**: Response times, error rates
- **Cache Statistics**: Hit rates, efficiency
- **Service Status**: Individual service health
- **Alerts**: Active system alerts

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use**
```bash
# Check what's using the port
lsof -i :8001

# Kill the process
kill -9 <PID>
```

2. **API Rate Limiting**
```bash
# Check rate limit headers
curl -I http://localhost:8001/api/enhanced/weather/current?city=London
```

3. **Service Not Starting**
```bash
# Check logs
tail -f backup_cleanup/api-gateway/logs/app.log

# Check health
curl http://localhost:8001/api/monitoring/health
```

### Debug Mode

Enable debug logging:

```bash
# Set debug environment variable
export DEBUG=true

# Or edit .env file
echo "DEBUG=true" >> .env
```

## 🎨 Windows XP UI Theme

The platform includes a nostalgic Windows XP UI theme:

- **Classic window styling** with title bars and controls
- **Luna Blue color scheme** for authentic XP look
- **System icons** and familiar UI patterns
- **Responsive design** that works on modern devices

## 🚀 Next Steps

1. **Explore the API Documentation**: Visit `http://localhost:8001/docs`
2. **Try the Enhanced APIs**: Test the 10 free non-finance APIs
3. **Check the Monitoring Dashboard**: Monitor system performance
4. **Read the Full Documentation**: See `COMPREHENSIVE_DOCUMENTATION.md`
5. **Join the Community**: Connect with other developers

## 📞 Support

- **Documentation**: `COMPREHENSIVE_DOCUMENTATION.md`
- **API Docs**: `http://localhost:8001/docs`
- **Health Check**: `http://localhost:8001/api/monitoring/health`
- **Issues**: GitHub repository issues

## 🎯 What's Next?

After getting started, you can:

1. **Add your own APIs** using the enhanced HTTP client
2. **Customize the monitoring** with your own metrics
3. **Extend the UI** with the Windows XP theme
4. **Integrate with your applications** using the REST APIs
5. **Scale the platform** with Docker and Kubernetes

---

**You're all set!** 🎉 

The Enhanced Financial Analytics Platform is now running with 10 free non-finance APIs, advanced monitoring, and a nostalgic Windows XP interface. Start exploring the APIs and building amazing applications! 