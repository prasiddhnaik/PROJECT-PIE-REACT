# XP Trading Platform

A Windows XP-style trading platform built with Next.js frontend and Node.js backend, featuring real-time NSE stock data.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- pnpm 8+

### Installation
```bash
# Install dependencies
pnpm install

# Start development servers
pnpm dev
```

### Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8002

## 📁 Project Structure

```
xp-trading-platform/
├── apps/
│   └── web/                 # Next.js frontend
├── services/
│   └── backend/             # Node.js backend API
├── xp-trading-platform.html # Original HTML template
└── backup_cleanup/          # Archived files
```

## 🛠️ Development

### Frontend (Next.js)
```bash
cd apps/web
pnpm dev
```

### Backend (Node.js)
```bash
cd services/backend
pnpm start
```

## 📊 Features

- **Windows XP UI**: Authentic Windows XP interface
- **Real-time Data**: Live NSE stock data
- **Portfolio Management**: Track your investments
- **Order Management**: Place buy/sell orders
- **Market Watch**: Real-time market updates
- **Interactive Charts**: Technical analysis tools

## 🔧 API Endpoints

- `GET /stocks/popular` - Popular NSE stocks
- `GET /stock/:symbol` - Individual stock data
- `GET /market/indices` - Market indices
- `GET /market/gainers-losers` - Top gainers/losers
- `GET /market/status` - Market status

## 📝 License

MIT License 