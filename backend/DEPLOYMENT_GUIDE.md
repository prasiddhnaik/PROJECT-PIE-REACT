# Crypto Analytics Platform - Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the enhanced crypto analytics platform with 100+ provider failover system, real-time sentiment analysis, and full-stack architecture.

## Table of Contents

1. [Environment Setup](#environment-setup)
2. [Development Setup](#development-setup)
3. [Production Deployment](#production-deployment)
4. [API Provider Configuration](#api-provider-configuration)
5. [Performance Optimization](#performance-optimization)
6. [Maintenance & Operations](#maintenance--operations)

## Environment Setup

### Core Configuration

Create a `.env` file in your project root with the following variables:

```bash
# =============================================================================
# CORE APPLICATION SETTINGS
# =============================================================================
NODE_ENV=production
PORT=3000
NEXT_PUBLIC_BACKEND_URL=https://your-api-domain.com
DATABASE_URL=postgresql://user:pass@localhost:5432/crypto_analytics
REDIS_URL=redis://localhost:6379
```

### Major Crypto Exchanges (High Priority Providers)

These providers offer professional-grade APIs with high rate limits:

```bash
# Coinbase Pro (Priority: 95) - Rate Limit: 10,000 requests/hour
# Sign up: https://pro.coinbase.com/profile/api
COINBASE_API_KEY=your_coinbase_pro_api_key

# Binance (Priority: 98) - Rate Limit: 1,200 requests/minute
# Sign up: https://www.binance.com/en/my/settings/api-management
BINANCE_API_KEY=your_binance_api_key

# Kraken Pro (Priority: 92) - Rate Limit: 15-20 calls/second
# Sign up: https://www.kraken.com/u/security/api
KRAKEN_API_KEY=your_kraken_api_key

# Bitfinex (Priority: 88) - Rate Limit: 90 requests/minute
# Sign up: https://setting.bitfinex.com/api
BITFINEX_API_KEY=your_bitfinex_api_key

# Huobi Global (Priority: 85) - Rate Limit: 100 requests/10 seconds
# Sign up: https://www.huobi.com/en-us/apikey/
HUOBI_API_KEY=your_huobi_api_key

# OKX (Priority: 83) - Rate Limit: 20 requests/2 seconds
# Sign up: https://www.okx.com/account/my-api
OKX_API_KEY=your_okx_api_key

# KuCoin (Priority: 80) - Rate Limit: 18,000 requests/10 minutes
# Sign up: https://www.kucoin.com/account/api
KUCOIN_API_KEY=your_kucoin_api_key

# Gate.io (Priority: 78) - Rate Limit: 900 requests/minute
# Sign up: https://www.gate.io/myaccount/apiv4keys
GATE_IO_API_KEY=your_gate_io_api_key

# Bybit (Priority: 75) - Rate Limit: 120 requests/minute
# Sign up: https://www.bybit.com/app/user/api-management
BYBIT_API_KEY=your_bybit_api_key

# Bitget (Priority: 72) - Rate Limit: 20 requests/second
# Sign up: https://www.bitget.com/api-doc
BITGET_API_KEY=your_bitget_api_key

# MEXC (Priority: 70) - Rate Limit: 20 requests/second
# Sign up: https://www.mexc.com/user/openapi
MEXC_API_KEY=your_mexc_api_key
```

### Data Aggregators (Market Data Providers)

```bash
# CoinGecko Pro (Priority: 89) - Rate Limit: 500 calls/minute
# Sign up: https://www.coingecko.com/en/api/pricing
# Free tier: 50 calls/minute
COINGECKO_API_KEY=your_coingecko_pro_api_key

# CoinMarketCap Pro (Priority: 87) - Rate Limit: 333 calls/minute
# Sign up: https://coinmarketcap.com/api/pricing/
# Free tier: 333 calls/month
COINMARKETCAP_API_KEY=your_coinmarketcap_pro_api_key

# CryptoCompare (Priority: 84) - Rate Limit: 250,000 calls/month
# Sign up: https://min-api.cryptocompare.com/pricing
# Free tier: 100,000 calls/month
CRYPTOCOMPARE_API_KEY=your_cryptocompare_api_key

# Nomics (Priority: 81) - Rate Limit: 1 request/second
# Sign up: https://p.nomics.com/pricing
# Free tier: 1 request/second
NOMICS_API_KEY=your_nomics_api_key

# CoinAPI (Priority: 79) - Rate Limit: 100 requests/day (Free)
# Sign up: https://www.coinapi.io/pricing
COINAPI_KEY=your_coinapi_key

# CoinCap (Priority: 76) - Rate Limit: 1,000 requests/minute
# Sign up: https://docs.coincap.io/
COINCAP_API_KEY=your_coincap_api_key

# CoinRanking (Priority: 73) - Rate Limit: 1,000 requests/month (Free)
# Sign up: https://developers.coinranking.com/api
COINRANKING_API_KEY=your_coinranking_api_key
```

### Blockchain APIs (On-Chain Data)

```bash
# Etherscan (Priority: 82) - Rate Limit: 5 calls/second (Free)
# Sign up: https://etherscan.io/apis
ETHERSCAN_API_KEY=your_etherscan_api_key

# BSCScan (Priority: 77) - Rate Limit: 5 calls/second (Free)
# Sign up: https://bscscan.com/apis
BSCSCAN_API_KEY=your_bscscan_api_key

# PolygonScan (Priority: 74) - Rate Limit: 5 calls/second (Free)
# Sign up: https://polygonscan.com/apis
POLYGONSCAN_API_KEY=your_polygonscan_api_key

# Moralis (Priority: 86) - Rate Limit: 1,500 requests/minute (Free)
# Sign up: https://moralis.io/pricing/
MORALIS_API_KEY=your_moralis_api_key

# Alchemy (Priority: 90) - Rate Limit: 300 requests/second (Free)
# Sign up: https://www.alchemy.com/pricing
ALCHEMY_API_KEY=your_alchemy_api_key

# Infura (Priority: 91) - Rate Limit: 100,000 requests/day (Free)
# Sign up: https://infura.io/pricing
INFURA_API_KEY=your_infura_project_id
```

### News & Sentiment Analysis

```bash
# CryptoPanic (Priority: 71) - Rate Limit: 500 requests/day (Free)
# Sign up: https://cryptopanic.com/developers/api/
CRYPTOPANIC_API_KEY=your_cryptopanic_api_key

# NewsAPI (Priority: 68) - Rate Limit: 1,000 requests/day (Free)
# Sign up: https://newsapi.org/pricing
NEWSAPI_KEY=your_newsapi_key

# LunarCrush (Priority: 69) - Rate Limit: 1,000 requests/day (Free)
# Sign up: https://lunarcrush.com/developers/docs
LUNARCRUSH_API_KEY=your_lunarcrush_api_key

# Santiment (Priority: 67) - Rate Limit: 1,000 requests/month (Free)
# Sign up: https://santiment.net/pricing/
SANTIMENT_API_KEY=your_santiment_api_key
```

### Feature Flags & Configuration

```bash
# Enable/disable major platform features
ENABLE_CRYPTO_MULTISOURCE=true
ENABLE_SENTIMENT_ANALYSIS=true
ENABLE_REAL_TIME_UPDATES=true
ENABLE_MOCK_DATA=false
ENABLE_PROVIDER_HEALTH_MONITORING=true

# Performance settings
CRYPTO_PROVIDER_HEALTH_CHECK_INTERVAL=300
CRYPTO_DATA_CACHE_TTL=60
CRYPTO_BATCH_SIZE_LIMIT=50
CRYPTO_CONCURRENT_REQUESTS_LIMIT=10
```

## Development Setup

### Prerequisites

- Node.js 18.0 or higher
- PostgreSQL 14 or higher
- Redis 6.0 or higher
- Docker (optional, for containerized development)

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd crypto-analytics-platform
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   pnpm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb crypto_analytics
   
   # Run migrations
   npm run db:migrate
   ```

5. **Start Redis server**
   ```bash
   redis-server
   ```

6. **Start development servers**
   ```bash
   # Terminal 1: Backend API
   cd services/backend
   python -m uvicorn main:app --reload --port 8000
   
   # Terminal 2: Frontend
   cd apps/web
   npm run dev
   
   # Terminal 3: Additional services (optional)
   cd services
   docker-compose up -d
   ```

### Mock Mode for Development

For development without API keys, enable mock mode:

```bash
ENABLE_MOCK_DATA=true
ENABLE_CRYPTO_MULTISOURCE=false
```

### Docker Development Environment

```bash
# Start all services with Docker Compose
docker-compose -f docker-compose.dev.yml up

# Access services:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Redis: localhost:6379
# PostgreSQL: localhost:5432
```

## Production Deployment

### Environment Configuration Checklist

- [ ] All required API keys configured
- [ ] Database connection string set
- [ ] Redis connection configured
- [ ] SSL certificates installed
- [ ] Environment variables validated
- [ ] Feature flags configured for production
- [ ] Rate limiting properly configured
- [ ] Monitoring and logging enabled

### Security Hardening

1. **API Key Management**
   ```bash
   # Use environment variables, never hardcode keys
   # Rotate keys regularly
   # Use least privilege principle for API permissions
   # Monitor API usage and set alerts
   ```

2. **Database Security**
   ```bash
   # Use connection pooling
   # Enable SSL connections
   # Regular backups
   # Access control and user permissions
   ```

3. **Redis Security**
   ```bash
   # Enable authentication
   # Use SSL/TLS for connections
   # Configure proper firewall rules
   # Set memory limits and eviction policies
   ```

### Load Balancing & Scaling

1. **Horizontal Scaling**
   ```yaml
   # Example Kubernetes deployment
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: crypto-analytics-api
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: crypto-analytics-api
     template:
       metadata:
         labels:
           app: crypto-analytics-api
       spec:
         containers:
         - name: api
           image: crypto-analytics/api:latest
           ports:
           - containerPort: 8000
           env:
           - name: DATABASE_URL
             valueFrom:
               secretKeyRef:
                 name: db-secret
                 key: url
   ```

2. **Load Balancer Configuration**
   ```nginx
   upstream crypto_api {
       server api1.example.com:8000;
       server api2.example.com:8000;
       server api3.example.com:8000;
   }
   
   server {
       listen 443 ssl;
       server_name api.cryptoanalytics.com;
       
       location / {
           proxy_pass http://crypto_api;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## API Provider Configuration

### Priority-Based Failover

The system uses a priority-based failover chain:

1. **Tier 1 (Priority 90-98)**: Binance, Coinbase Pro, Infura, Alchemy
2. **Tier 2 (Priority 80-89)**: Kraken, CoinGecko Pro, CoinMarketCap Pro, Bitfinex
3. **Tier 3 (Priority 70-79)**: KuCoin, Gate.io, Bybit, CoinCap
4. **Tier 4 (Priority 60-69)**: News APIs, Sentiment sources

### Rate Limit Configuration

```python
# Example rate limit configuration
RATE_LIMITS = {
    'binance': {'requests_per_minute': 1200, 'burst': 100},
    'coinbase': {'requests_per_minute': 600, 'burst': 50},
    'kraken': {'requests_per_minute': 900, 'burst': 75},
    'coingecko': {'requests_per_minute': 500, 'burst': 40}
}
```

### Provider Health Monitoring

```bash
# Health check configuration
HEALTH_CHECK_INTERVAL=60  # seconds
HEALTH_CHECK_TIMEOUT=10   # seconds
CIRCUIT_BREAKER_THRESHOLD=5  # failures before circuit opens
CIRCUIT_BREAKER_TIMEOUT=300  # seconds before retry
```

## Performance Optimization

### Caching Strategy

1. **Redis Configuration**
   ```bash
   # Cache TTL settings
   CACHE_CRYPTO_DATA_TTL=60      # 1 minute for live prices
   CACHE_MARKET_DATA_TTL=300     # 5 minutes for market overview
   CACHE_SENTIMENT_TTL=900       # 15 minutes for sentiment data
   CACHE_PROVIDER_HEALTH_TTL=180 # 3 minutes for health status
   ```

2. **Database Optimization**
   ```sql
   -- Create indexes for performance
   CREATE INDEX idx_crypto_data_symbol_timestamp ON crypto_data(symbol, timestamp);
   CREATE INDEX idx_provider_health_provider_timestamp ON provider_health(provider_id, timestamp);
   ```

### Rate Limiting

```python
# Backend rate limiter configuration
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/crypto/{symbol}")
@limiter.limit("100/minute")
async def get_crypto_data(request: Request, symbol: str):
    # API implementation
```

### Background Tasks

```python
# Celery configuration for background tasks
CELERY_BROKER_URL = "redis://localhost:6379/1"
CELERY_RESULT_BACKEND = "redis://localhost:6379/1"

# Tasks
@celery.task
def update_provider_health():
    # Health check implementation
    
@celery.task
def refresh_sentiment_data():
    # Sentiment refresh implementation
```

## Maintenance & Operations

### Provider Health Monitoring

1. **Setup Monitoring Dashboard**
   ```bash
   # Access provider status
   curl https://api.yoursite.com/api/crypto/providers/status
   
   # Check provider usage
   curl https://api.yoursite.com/api/crypto/providers/usage
   ```

2. **Automated Alerts**
   ```python
   # Example alert configuration
   ALERTS = {
       'provider_down': {
           'threshold': 3,  # providers down
           'action': 'send_email'
       },
       'high_error_rate': {
           'threshold': 0.1,  # 10% error rate
           'action': 'send_slack'
       }
   }
   ```

### Backup & Disaster Recovery

1. **Database Backups**
   ```bash
   # Daily automated backups
   pg_dump crypto_analytics > backup_$(date +%Y%m%d).sql
   
   # Upload to cloud storage
   aws s3 cp backup_$(date +%Y%m%d).sql s3://your-backup-bucket/
   ```

2. **Redis Persistence**
   ```bash
   # Configure Redis persistence
   save 900 1      # Save if at least 1 key changed in 900 seconds
   save 300 10     # Save if at least 10 keys changed in 300 seconds
   save 60 10000   # Save if at least 10000 keys changed in 60 seconds
   ```

### API Key Rotation

1. **Automated Key Rotation**
   ```python
   # Key rotation script
   def rotate_api_keys():
       for provider in PROVIDERS:
           old_key = get_current_key(provider)
           new_key = generate_new_key(provider)
           update_provider_key(provider, new_key)
           schedule_old_key_deactivation(old_key, delay=3600)
   ```

2. **Key Validation**
   ```python
   # Validate all keys on startup
   def validate_api_keys():
       invalid_keys = []
       for provider, key in API_KEYS.items():
           if not test_api_key(provider, key):
               invalid_keys.append(provider)
       return invalid_keys
   ```

### System Monitoring

1. **Metrics Collection**
   ```python
   # Prometheus metrics
   from prometheus_client import Counter, Histogram, Gauge
   
   api_requests_total = Counter('api_requests_total', 'Total API requests', ['provider', 'status'])
   api_response_time = Histogram('api_response_seconds', 'API response time', ['provider'])
   provider_health = Gauge('provider_health_status', 'Provider health status', ['provider'])
   ```

2. **Log Configuration**
   ```python
   LOGGING = {
       'version': 1,
       'handlers': {
           'file': {
               'level': 'INFO',
               'class': 'logging.FileHandler',
               'filename': 'crypto_analytics.log',
           },
           'sentry': {
               'level': 'ERROR',
               'class': 'sentry_sdk.integrations.logging.SentryHandler',
           }
       },
       'root': {
           'level': 'INFO',
           'handlers': ['file', 'sentry']
       }
   }
   ```

## Troubleshooting

### Common Issues

1. **Provider API Failures**
   ```bash
   # Check provider status
   curl -X GET "http://localhost:8000/api/crypto/providers/status"
   
   # Test specific provider
   curl -X GET "http://localhost:8000/api/crypto/bitcoin" -H "X-Provider: binance"
   ```

2. **Rate Limit Exceeded**
   ```bash
   # Check current usage
   curl -X GET "http://localhost:8000/api/crypto/providers/usage"
   
   # Reduce request frequency or upgrade API plans
   ```

3. **Database Connection Issues**
   ```bash
   # Test database connection
   psql $DATABASE_URL -c "SELECT 1;"
   
   # Check connection pool status
   ```

### Support & Documentation

- **API Documentation**: `/docs` endpoint (Swagger/OpenAPI)
- **Provider Registry**: `config/provider_registry.yaml`
- **Health Checks**: `/health` endpoint
- **Metrics**: `/metrics` endpoint (Prometheus format)

### Performance Tuning

1. **Database Tuning**
   ```sql
   -- Optimize PostgreSQL for crypto data
   ALTER SYSTEM SET shared_buffers = '256MB';
   ALTER SYSTEM SET effective_cache_size = '1GB';
   ALTER SYSTEM SET random_page_cost = 1.1;
   ```

2. **Redis Optimization**
   ```bash
   # Optimize Redis for caching
   maxmemory 1gb
   maxmemory-policy allkeys-lru
   tcp-keepalive 60
   ```

This deployment guide covers all aspects of setting up and maintaining the crypto analytics platform with 100+ provider failover system. For specific issues or advanced configurations, refer to the individual component documentation. 