# PROJECT-PIE-REACT - Financial Dashboard

A modern financial dashboard built with Next.js and real-time market data APIs.

## 🌟 Features

- **Real-time Stock Data** - Integration with Alpha Vantage, Finnhub, and Polygon APIs
- **Technical Indicators** - MACD, RSI, Bollinger Bands, SMA, EMA calculations
- **Financial News** - Live market news from multiple sources
- **Windows XP Theme** - Nostalgic UI design with modern functionality
- **Responsive Design** - Works on desktop and mobile devices

## 🚀 Quick Start

### Frontend (Next.js)

```bash
cd apps/web
npm install
npm run dev
```

The application will be available at `http://localhost:3000`

### Backend (Python)

```bash
cd backend/backend_python
pip install -r requirements.txt
python main.py
```

The backend API will be available at `http://localhost:8001`

## 📊 API Endpoints

### Frontend API Routes
- `/api/stock-data?symbol=AAPL` - Get stock data with technical indicators
- `/api/news` - Get latest financial news
- `/api/market-overview` - Get market summary and major stock indices

### Backend Python API
- Available in `backend/backend_python/` directory
- Multiple data providers and analytics services
- Real-time data fetching and caching

## 🔑 Environment Variables

Set up your API keys:

```bash
# Alpha Vantage (Free tier: 5 calls/minute, 500 calls/day)
ALPHA_VANTAGE_KEY=your_key_here

# Finnhub (Free tier: 60 calls/minute)
FINNHUB_KEY=your_key_here

# Polygon.io (Free tier: 5 calls/minute)
POLYGON_KEY=your_key_here
```

## 🏗️ Project Structure

```
PROJECT-PIE-REACT/
├── apps/web/                 # Next.js frontend application
│   ├── src/app/             # App router pages and components
│   └── src/app/api/         # API routes
├── backend/                 # Python backend services
│   └── backend_python/      # Main backend application
├── services/               # Additional services
└── docs/                   # Documentation
```

## 🛠️ Technology Stack

- **Frontend**: Next.js 15, React, TypeScript, Tailwind CSS
- **Backend**: Python, FastAPI, Real-time APIs
- **Data Sources**: Alpha Vantage, Finnhub, Polygon.io, Yahoo Finance
- **Technical Analysis**: technicalindicators.js
- **Deployment**: Render, Docker support

## 📈 Available Markets

- US Stocks (NASDAQ, NYSE)
- Major indices (S&P 500, NASDAQ, DOW)
- Technical indicators and chart analysis
- Real-time financial news

## 🎯 Key Features

### Real Data Sources
- No mock data - all information comes from live APIs
- Multiple fallback providers for reliability
- Caching system to reduce API calls

### Technical Analysis
- Moving averages (SMA, EMA)
- MACD with signal and histogram
- RSI (Relative Strength Index)
- Bollinger Bands
- Historical price charts

### News Integration
- Real-time financial news
- Multiple news sources
- Categorized by relevance

## 🚀 Deployment

The project is configured for Render deployment with Docker support.

### Local Development
```bash
# Install dependencies
npm install --force

# Start development server
npm run dev

# Start backend
cd backend/backend_python && python main.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

---

**Note**: This project prioritizes real market data over mock data. All APIs are configured to use live data sources with proper fallback mechanisms.