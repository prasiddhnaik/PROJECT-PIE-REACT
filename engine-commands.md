# 🏎️ Crypto Analytics Engine - Command Reference

## Quick Health Check
```bash
./performance-monitor.sh
```

## Start Engine Components
```bash
# Backend (Terminal 1)
cd services/backend && python main.py

# Frontend (Terminal 2)  
cd apps/web && npm run dev -- -p 3000
```

## Performance Testing
```bash
# Quick API test
curl "http://localhost:8001/health" | jq

# Load test top 100
time curl -s "http://localhost:8001/api/top100/crypto" > /dev/null

# Check cache performance
for i in {1..5}; do
  echo "Request $i:"
  time curl -s "http://localhost:8001/api/top100/crypto" > /dev/null
done
```

## Engine Status URLs
- **Backend Health**: http://localhost:8001/health
- **API Documentation**: http://localhost:8001/docs
- **Frontend App**: http://localhost:3000
- **Top 100 Cryptos**: http://localhost:8001/api/top100/crypto

## Key Performance Metrics
- **Top 100 API**: < 1.0s (first request), < 0.03s (cached)
- **Individual Crypto**: < 1.5s
- **Market Overview**: < 0.8s
- **Cache Duration**: 2 minutes for optimal balance

## Optimization Features Active
✅ **Smart Caching**: 2-minute cache for top 100 data  
✅ **Field Normalization**: Frontend-compatible data structure  
✅ **Error Reduction**: Clean logs without unnecessary warnings  
✅ **Performance Monitoring**: Built-in health checks  
✅ **Failover System**: CoinGecko → Binance fallback  

## Maintenance Commands
```bash
# Monitor logs
tail -f services/backend/logs/app.log

# Clear cache (restart backend)
# Cache automatically expires every 2 minutes

# Update dependencies
cd services/backend && pip install -r requirements.txt
cd apps/web && npm install
```

---
**🌟 Your engine is now running like a well-oiled machine! 🌟** 