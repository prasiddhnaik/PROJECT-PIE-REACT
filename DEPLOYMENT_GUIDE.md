# 🚀 Deployment Guide - Financial Analytics Platform

**Complete guide to deploy your Financial Analytics Platform with real-time data, XP theme, and multi-provider system.**

## 📋 Prerequisites

- **GitHub Account** ✅ (Already have)
- **Node.js 18+** and **Python 3.8+** ✅ (Already installed)
- **Docker** (optional, for containerized deployment)

## 🌐 Hosting Options

### **1. Railway (Recommended - Easiest)**

**Best for:** Quick deployment, automatic scaling, easy setup

#### Setup Steps:
1. **Connect to Railway:**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login to Railway
   railway login
   ```

2. **Deploy from GitHub:**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository: `prasiddhnaik/PROJECT-PIE-REACT`
   - Railway will auto-detect and deploy

3. **Configure Environment Variables:**
   ```bash
   # Add your API keys
   railway variables set OPENROUTER_API_KEY=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
   railway variables set ALPHA_VANTAGE_API_KEY=22TNS9NWXVD5CPVF
   railway variables set POLYGON_API_KEY=SavZMeuTDTxjWJuFzBO6zES7mBFK68RJ
   railway variables set FINNHUB_API_KEY=d16k039r01qvtdbj2gtgd16k039r01qvtdbj2gu0
   ```

4. **Access Your App:**
   - Railway provides a public URL automatically
   - Your app will be live at: `https://your-app-name.railway.app`

**Cost:** Free tier → $5-20/month for production

---

### **2. Vercel + Railway (Hybrid - Best Performance)**

**Best for:** Optimal performance, separate frontend/backend

#### Frontend (Next.js) on Vercel:
1. **Deploy to Vercel:**
   ```bash
   # Install Vercel CLI
   npm install -g vercel
   
   # Deploy
   cd apps/web
   vercel --prod
   ```

2. **Configure Environment:**
   ```bash
   vercel env add NEXT_PUBLIC_BACKEND_URL
   # Set to your Railway backend URL
   ```

#### Backend (FastAPI) on Railway:
1. **Deploy Backend:**
   ```bash
   cd backup_cleanup/backend_python
   railway init
   railway up
   ```

2. **Update Frontend Backend URL:**
   - Go to Vercel dashboard
   - Update `NEXT_PUBLIC_BACKEND_URL` to Railway backend URL

**Cost:** Vercel (Free) + Railway ($5-20/month)

---

### **3. Heroku (Alternative)**

**Best for:** Traditional hosting, good free tier

#### Setup:
1. **Install Heroku CLI:**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Login
   heroku login
   ```

2. **Deploy:**
   ```bash
   # Create app
   heroku create your-financial-app
   
   # Deploy
   git push heroku main
   ```

3. **Configure:**
   ```bash
   heroku config:set OPENROUTER_API_KEY=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
   heroku config:set ALPHA_VANTAGE_API_KEY=22TNS9NWXVD5CPVF
   ```

**Cost:** Free tier → $7-25/month

---

### **4. DigitalOcean App Platform**

**Best for:** Scalable, professional hosting

#### Setup:
1. **Create App:**
   - Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
   - Click "Create App" → "GitHub"
   - Select your repository

2. **Configure:**
   - Set build command: `npm run build`
   - Set run command: `npm start`
   - Add environment variables

3. **Deploy:**
   - Click "Create Resources"
   - Your app will be live at: `https://your-app-name.ondigitalocean.app`

**Cost:** $5-50/month

---

## 🔧 Environment Configuration

### Required Environment Variables:

```bash
# AI Integration
OPENROUTER_API_KEY=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

# Financial APIs
ALPHA_VANTAGE_API_KEY=22TNS9NWXVD5CPVF
POLYGON_API_KEY=SavZMeuTDTxjWJuFzBO6zES7mBFK68RJ
FINNHUB_API_KEY=d16k039r01qvtdbj2gtgd16k039r01qvtdbj2gu0

# Frontend Configuration
NEXT_PUBLIC_BACKEND_URL=https://your-backend-url.com
NODE_ENV=production
```

### Optional Environment Variables:

```bash
# Redis (for caching)
REDIS_URL=redis://localhost:6379

# Database (if using)
DATABASE_URL=postgresql://user:pass@host:port/db

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
```

---

## 🐳 Docker Deployment

### Docker Compose Setup:

```bash
# Clone and setup
git clone https://github.com/prasiddhnaik/PROJECT-PIE-REACT.git
cd PROJECT-PIE-REACT

# Create .env file
cp backup_cleanup/backend_python/env.example .env
# Edit .env with your API keys

# Deploy with Docker
docker-compose up -d
```

### Individual Services:

```bash
# Backend only
cd backup_cleanup/backend_python
docker build -t financial-backend .
docker run -p 8001:8001 financial-backend

# Frontend only
cd apps/web
docker build -t financial-frontend .
docker run -p 3000:3000 financial-frontend
```

---

## 📊 Monitoring & Health Checks

### Health Check Endpoints:

```bash
# Backend Health
curl https://your-backend-url.com/health

# API Status
curl https://your-backend-url.com/api/status

# Data Sources
curl https://your-backend-url.com/api/data/market/overview
```

### Monitoring Dashboard:

Access the XP-themed monitoring dashboard:
- **URL:** `https://your-app-url.com/backup_cleanup/monitoring-dashboard.html`
- **Features:** Real-time metrics, API health, system status

---

## 🔒 Security Considerations

### API Key Security:
- ✅ Never commit API keys to Git
- ✅ Use environment variables
- ✅ Rotate keys regularly
- ✅ Use least privilege access

### SSL/TLS:
- ✅ Enable HTTPS (automatic on Railway/Vercel)
- ✅ Use secure headers
- ✅ Implement rate limiting

### Data Protection:
- ✅ Validate all inputs
- ✅ Sanitize outputs
- ✅ Implement proper error handling

---

## 🚀 Quick Deploy Commands

### Railway (Recommended):
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Deploy
railway up

# 4. Set environment variables
railway variables set OPENROUTER_API_KEY=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
railway variables set ALPHA_VANTAGE_API_KEY=22TNS9NWXVD5CPVF
railway variables set POLYGON_API_KEY=SavZMeuTDTxjWJuFzBO6zES7mBFK68RJ
railway variables set FINNHUB_API_KEY=d16k039r01qvtdbj2gtgd16k039r01qvtdbj2gu0

# 5. Open your app
railway open
```

### Vercel:
```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Deploy frontend
cd apps/web
vercel --prod

# 3. Set environment variables
vercel env add NEXT_PUBLIC_BACKEND_URL
```

---

## 📈 Performance Optimization

### Frontend:
- ✅ Next.js automatic optimization
- ✅ Image optimization
- ✅ Code splitting
- ✅ Caching strategies

### Backend:
- ✅ Redis caching
- ✅ Rate limiting
- ✅ Connection pooling
- ✅ Async processing

### Database:
- ✅ Index optimization
- ✅ Query optimization
- ✅ Connection pooling

---

## 🔧 Troubleshooting

### Common Issues:

1. **Port Conflicts:**
   ```bash
   # Check what's using the port
   lsof -i :8001
   lsof -i :3000
   
   # Kill process if needed
   kill -9 <PID>
   ```

2. **API Key Issues:**
   ```bash
   # Test API keys
   curl "https://api.openrouter.ai/api/v1/chat/completions" \
     -H "Authorization: Bearer $OPENROUTER_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model": "openai/gpt-3.5-turbo", "messages": [{"role": "user", "content": "Hello"}]}'
   ```

3. **Build Failures:**
   ```bash
   # Clear cache
   npm run clean
   rm -rf node_modules
   npm install
   ```

4. **Database Connection:**
   ```bash
   # Test database connection
   python3 -c "import psycopg2; print('DB OK')"
   ```

---

## 📞 Support

### Documentation:
- **Platform Summary:** `backup_cleanup/PLATFORM_SUMMARY.md`
- **Quick Start:** `backup_cleanup/QUICK_START_WORKING.md`
- **Status Report:** `backup_cleanup/COMPREHENSIVE_STATUS_REPORT.md`

### Testing:
```bash
# Test everything locally
cd backup_cleanup
python3 test_everything_working.py

# Test real data fetching
python3 test_real_data_fetching.py
```

### Monitoring:
- **Health Dashboard:** `backup_cleanup/monitoring-dashboard.html`
- **XP Dashboard:** `backup_cleanup/xp-theme/xp-dashboard-xp-css.html`

---

## 🎉 Success Checklist

- ✅ Repository updated on GitHub
- ✅ Environment variables configured
- ✅ SSL/HTTPS enabled
- ✅ Health checks passing
- ✅ Real-time data working
- ✅ XP theme functional
- ✅ Monitoring active
- ✅ Documentation complete

**Your Financial Analytics Platform is now ready for production! 🚀** 