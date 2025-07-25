# Financial Analytics Hub - Startup Guide

## 🚨 Quick Fix for "Connection Refused" Error

If you're seeing "localhost refused to connect" when trying to access the Financial Analytics Hub, follow these steps:

### Immediate Solution (Recommended)

```bash
# Run the quick start script
./quick-start.sh
```

This script will automatically:
- Check and install dependencies
- Clean up port conflicts
- Start both backend and frontend services
- Verify connectivity

### Alternative: Manual Steps

If the quick start doesn't work, follow these manual steps:

1. **Check if services are running:**
   ```bash
   # Check backend (port 8001)
   curl http://localhost:8001/health
   
   # Check frontend (port 3000)
   curl http://localhost:3000
   ```

2. **If backend is not running:**
   ```bash
   cd services/backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python main.py
   ```

3. **If frontend is not running:**
   ```bash
   cd apps/web
   pnpm install
   pnpm dev
   ```

## 📋 Troubleshooting Guide

### Common Issues and Solutions

#### 1. Port Already in Use

**Error:** `EADDRINUSE: address already in use :::3000` or `:::8001`

**Solution:**
```bash
# Kill processes on port 3000 and 8001
./fix-ports.sh

# Or manually:
lsof -ti:3000 | xargs kill -9
lsof -ti:8001 | xargs kill -9
```

**Port Ownership:**
- **Frontend (Next.js)**: Port 3000
- **Main Backend (FastAPI)**: Port 8001  
- **Demo Flask server**: Port 4000 (moved from 3000 to avoid conflicts)
- **Other microservices**: Ports 8002+

#### 2. Python Dependencies Missing

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
cd services/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Node.js Dependencies Missing

**Error:** `Cannot find module 'next'`

**Solution:**
```bash
cd apps/web
pnpm install
# or if pnpm is not installed:
npm install -g pnpm
pnpm install
```

#### 4. Python Virtual Environment Issues

**Error:** Virtual environment not activating or Python packages not found

**Solution:**
```bash
cd services/backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 5. API Connection Errors

**Error:** Frontend can't connect to backend APIs

**Solution:**
1. Ensure backend is running first
2. Check backend health: `python services/backend/check-backend.py`
3. Verify API endpoints are responding
4. Check firewall settings

#### 6. Demo Server Port Conflict

**Note:** The demo Flask server (`fast_api_server.py`) now runs on **port 4000** instead of port 3000 to avoid conflicts with the Next.js frontend.

**Access the demo server at:**
- http://localhost:4000/health
- http://localhost:4000/fast/stock/AAPL

## 🛠 Advanced Troubleshooting

### Run Comprehensive Diagnostics

```bash
# Full system diagnosis
./troubleshoot-startup.sh

# Check backend health
cd services/backend && python check-backend.py

# Check frontend health
cd apps/web && node check-frontend.js
```

### Environment Setup Verification

1. **Required Software Versions:**
   - Python 3.8 or higher
   - Node.js 18 or higher
   - pnpm (recommended) or npm

2. **Check versions:**
   ```bash
   python3 --version
   node --version
   pnpm --version
   ```

### Network and Firewall Issues

If services start but can't connect:

1. **Check firewall settings:**
   ```bash
   # macOS
   sudo pfctl -sr | grep -E "(3000|8001)"
   
   # Linux
   sudo ufw status | grep -E "(3000|8001)"
   ```

2. **Test local network connectivity:**
   ```bash
   telnet localhost 3000  # Frontend
   telnet localhost 8001  # Main Backend
   telnet localhost 4000  # Demo Flask server
   ```

## 🚀 Multiple Startup Options

### Option 1: Quick Start (Recommended)
```bash
./quick-start.sh
```
- Fastest way to get running
- Automatic dependency management
- Built-in health checks

### Option 2: Comprehensive Troubleshooting
```bash
./troubleshoot-startup.sh
```
- Detailed diagnostics
- Step-by-step problem resolution
- Extensive logging

### Option 3: Manual Development Setup
```bash
# Terminal 1: Backend
cd services/backend
source venv/bin/activate
python main.py

# Terminal 2: Frontend
cd apps/web
pnpm dev
```

### Option 4: Docker Compose (If Available)
```bash
docker-compose up -d
```

## 🔍 Service Verification

### Backend Health Check
```bash
# Basic health check
curl http://localhost:8001/health

# Detailed diagnostics
cd services/backend && python check-backend.py

# Test specific endpoints
curl http://localhost:8001/api/status
curl http://localhost:8001/api/crypto/trending
```

### Frontend Health Check
```bash
# Basic connectivity test
curl http://localhost:3000

# Detailed diagnostics
cd apps/web && node check-frontend.js

# Check if Next.js is serving correctly
curl -I http://localhost:3000
```

### Full System Test
```bash
# Test complete data flow
curl http://localhost:3000/api/test
```

## 🌍 Environment Configuration

### Required Environment Variables

Create `.env` files in appropriate directories:

**services/backend/.env:**
```env
# Optional: API keys for external services
ALPHA_VANTAGE_API_KEY=your_key_here
COINAPI_KEY=your_key_here
POLYGON_API_KEY=your_key_here

# Server configuration
HOST=localhost
PORT=8001
DEBUG=true
```

**apps/web/.env.local:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_APP_ENV=development
```

### API Key Setup (Optional)

The application works without API keys using free data sources, but for enhanced functionality:

1. **Alpha Vantage (Stock Data):**
   - Sign up at https://www.alphavantage.co/
   - Add `ALPHA_VANTAGE_API_KEY` to backend `.env`

2. **CoinAPI (Crypto Data):**
   - Sign up at https://www.coinapi.io/
   - Add `COINAPI_KEY` to backend `.env`

## 📊 Performance Optimization

### Development Mode Optimization

1. **Reduce build time:**
   ```bash
   cd apps/web
   # Use development mode with faster builds
   NEXT_TELEMETRY_DISABLED=1 pnpm dev
   ```

2. **Enable caching:**
   ```bash
   cd services/backend
   # Add caching for API responses
   pip install redis
   # Configure caching in main.py
   ```

### Production Considerations

1. **Build for production:**
   ```bash
   cd apps/web
   pnpm build
   pnpm start
   ```

2. **Optimize backend:**
   ```bash
   cd services/backend
   # Use production WSGI server
   pip install gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
   ```

## 🆘 Still Having Issues?

### Step-by-Step Diagnosis

1. **Run full diagnostics:**
   ```bash
   ./troubleshoot-startup.sh
   ```

2. **Check individual components:**
   ```bash
   # Backend check
   cd services/backend && python check-backend.py
   
   # Frontend check
   cd apps/web && node check-frontend.js
   
   # Port conflicts
   ./fix-ports.sh
   ```

3. **Verify system requirements:**
   - Operating System: macOS, Linux, or Windows WSL
   - Python 3.8+
   - Node.js 18+
   - Available memory: 2GB+
   - Available disk space: 1GB+

### Common Error Patterns

| Error | Likely Cause | Solution |
|-------|--------------|----------|
| Connection refused | Service not running | Start the service |
| Port in use | Another process using the port | Kill the process or use different port |
| Module not found | Dependencies not installed | Install dependencies |
| Permission denied | Insufficient permissions | Check file permissions |
| Network timeout | Firewall or network issue | Check firewall settings |

### Log Files and Debugging

1. **Backend logs:**
   ```bash
   cd services/backend
   python main.py 2>&1 | tee backend.log
   ```

2. **Frontend logs:**
   ```bash
   cd apps/web
   pnpm dev 2>&1 | tee frontend.log
   ```

3. **System logs:**
   ```bash
   # macOS
   log show --predicate 'process == "node" OR process == "python"' --last 10m
   
   # Linux
   journalctl -f | grep -E "(node|python)"
   ```

## 🎯 Success Indicators

When everything is working correctly, you should see:

1. **Backend running:** `✅ Backend is accessible at http://localhost:8001`
2. **Frontend running:** `✅ Frontend is accessible at http://localhost:3000`
3. **API connectivity:** `✅ Backend health check passed`
4. **Data loading:** Cryptocurrency data displays in the UI

### Final Test

Visit http://localhost:3000 in your browser. You should see:
- Financial Analytics Hub homepage
- Cryptocurrency data loading
- Charts and market information
- No error messages in browser console

---

## 🔧 Script Reference

- `./quick-start.sh` - Fast startup with automatic setup
- `./troubleshoot-startup.sh` - Comprehensive diagnostics and startup
- `./fix-ports.sh` - Resolve port conflicts
- `services/backend/check-backend.py` - Backend health diagnostics
- `apps/web/check-frontend.js` - Frontend health diagnostics

For additional help, check the logs or run the troubleshooting scripts for detailed error information. 