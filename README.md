# ₿ Crypto Analytics Platform

<div align="center">

![Crypto Analytics](https://img.shields.io/badge/Crypto-Analytics-orange?style=for-the-badge&logo=bitcoin)
![AI Powered](https://img.shields.io/badge/AI-Powered-purple?style=for-the-badge&logo=robot)
![Python](https://img.shields.io/badge/Python-3.9+-green?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-Next.js-blue?style=for-the-badge&logo=react)

**Advanced crypto analytics platform with AI-powered analysis, real-time cryptocurrency tracking, and OpenRouter AI integration**

[🚀 Quick Start](#-quick-start) • [📊 Features](#-features) • [📖 Documentation](#-documentation) • [🤝 Contributing](#-contributing)

</div>

---

## 🌟 **What is Crypto Analytics Platform?**

A **revolutionary crypto analytics platform** that combines advanced cryptocurrency analysis, artificial intelligence, and modern web technology to deliver professional-grade crypto investment insights.

### **🎯 Key Highlights**
- ⚡ **Lightning-Fast Performance** - Real-time crypto data with optimized caching
- 🤖 **AI-Powered Crypto Analysis** - OpenRouter AI integration with GPT-4, Claude, and Gemini
- 📊 **Professional Crypto Visualizations** - Interactive crypto charts and market data
- ₿ **Comprehensive Crypto Coverage** - Top 100 cryptocurrencies with trending analysis
- 🔗 **Multi-Source Crypto Data** - CoinGecko and Binance API integration
- 🚫 **Real Crypto Data Only** - No demos, only genuine cryptocurrency market data

---

## 🚀 **Quick Start**

### **📋 Prerequisites**
```bash
Python >= 3.9
pip >= 21.0
```

### **⚡ Installation**
```bash
# 1️⃣ Clone the repository
git clone https://github.com/prasiddhnaik/-Financial-Analytics-Hub.git
cd -Financial-Analytics-Hub

# 2️⃣ Install dependencies
pip install -r requirements.txt

# 3️⃣ Configure email settings (optional)
# Edit config.py with your email credentials for stock tracking alerts

# 4️⃣ Launch the application
streamlit run src/apps/api_dashboard.py --server.port=8506

# 5️⃣ Open your browser
# Navigate to: http://localhost:8506
```

## Quick Start (Local)

```bash
# install workspace deps
pnpm install

# create env file for web
cp apps/web/.env.example apps/web/.env.local

# build & run all packages in parallel
pnpm dev
```

The web app will be at http://localhost:3000 and the FastAPI service at http://localhost:8001.

---

## 📊 **Features**

<table>
<tr>
<td width="50%">

### **🧮 Core Analytics**
- **Portfolio Analysis**: Multi-fund comparison with AI insights
- **Risk Assessment**: Professional-grade risk metrics (Sharpe ratio, VaR, Beta)
- **Performance Tracking**: Historical analysis with technical indicators
- **Return Calculations**: Precise mathematical computations

### **🤖 AI Intelligence**
- **Smart Warnings**: Automatic alerts at -5% risk threshold
- **Investment Advice**: Professional-grade recommendations
- **Risk Classification**: 5-tier assessment system
- **Portfolio Optimization**: AI-driven rebalancing suggestions

</td>
<td width="50%">

### **₿ Crypto Analytics**
- **Cryptocurrency Hub**: Top 100 crypto tracking (Bitcoin, Ethereum, Solana, etc.)
- **Market Intelligence**: Real-time crypto prices with multiple API sources
- **Trending Analysis**: Hot cryptocurrencies and market movements
- **AI Integration**: OpenRouter models for crypto analysis and predictions

### **🤖 AI-Powered Features**
- **Crypto Analysis**: GPT-4, Claude, and Gemini integration for market insights
- **Technical Indicators**: RSI, moving averages, and crypto-specific metrics
- **Market Sentiment**: AI-powered sentiment analysis for crypto markets
- **Price Predictions**: Advanced AI models for cryptocurrency forecasting

</td>
</tr>
</table>

---

## 🏗️ **Project Structure**

```
Financial-Analytics-Hub/
├── 🧠 src/                          # Core application source code
│   ├── apps/                        # Streamlit applications
│   ├── core/                        # Core business logic
│   ├── utils/                       # Utility functions
│   └── models/                      # Data models
│
├── 📚 docs/                         # Comprehensive documentation
│   └── guides/                      # 17 professional guides
│
├── 🧪 tests/                        # Professional test suite (595 lines)
│   ├── test_portfolio_calculator.py # Core functionality tests
│   └── test_crypto_fix.py          # API integration tests
│
├── 📦 scripts/                      # Automation scripts
├── 💾 data/                         # Sample datasets
├── 🎨 assets/                       # Images and static files
├── 📝 examples/                     # Usage examples
│
├── 🐳 Dockerfile                    # Container configuration
├── 🔧 Makefile                      # Build automation
├── ⚙️ pytest.ini                   # Test configuration
├── 📋 requirements.txt              # Python dependencies
└── 🛠️ setup.py                     # Package configuration
```

---

## 📖 **Documentation**

### **📚 Quick Links**
- **[📋 Project Summary](docs/guides/PROJECT_SUMMARY.md)** - Comprehensive technical documentation (27KB)
- **[🚀 Quick Start Guide](docs/guides/QUICK_START_GUIDE.md)** - Get up and running in 2 minutes
- **[📊 API Integration](docs/guides/API_INTEGRATION_SUMMARY.md)** - Multi-API setup and usage
- **[🕵️ Stealth Mode](docs/guides/STEALTH_MODE_GUIDE.md)** - Silent background monitoring
- **[🔄 Change Log](docs/guides/CHANGES.md)** - Development history and updates (19KB)

### **🎓 Educational Guides**
- **[📈 Stock Tracker](docs/guides/STOCK_TRACKER_GUIDE.md)** - Real-time monitoring setup
- **[🔄 Background Tracker](docs/guides/BACKGROUND_TRACKER_SETUP.md)** - Silent operation guide
- **[🌐 Financial APIs](docs/guides/FINANCIAL_APIS_SUMMARY.md)** - 9+ API integration
- **[📁 Directory Structure](docs/guides/DIRECTORY_STRUCTURE.md)** - Project organization

---

## 🛠️ **Technology Stack**

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Next.js + React | Modern crypto dashboard |
| **Backend** | FastAPI + Python | High-performance crypto API |
| **Data Analysis** | Real-time processing | Crypto market computations |
| **Visualization** | Tailwind CSS | Responsive crypto charts |
| **APIs** | CoinGecko + Binance | Real-time crypto data |
| **AI Logic** | OpenRouter AI | GPT-4, Claude, Gemini integration |
| **Testing** | TypeScript | Type-safe development |
| **CI/CD** | Modern DevOps | Automated deployment |

---

## 📊 **Real Results**

### **✅ Actual Performance Data**
```
📈 Live Fund Analysis Example
┌─────────────────────┬──────────────┬─────────────┬──────────┬─────────────┐
│ Fund                │ Start NAV    │ End NAV     │ Return   │ AI Status   │
├─────────────────────┼──────────────┼─────────────┼──────────┼─────────────┤
│ Nippon Small Cap    │ ₹35.62       │ ₹32.69      │ -8.23%   │ ⚠️ WARNING  │
│ HDFC Small Cap      │ ₹158.76      │ ₹151.91     │ -4.32%   │ ✅ ACCEPTABLE│
│ Portfolio (60/40)   │ -            │ -           │ -6.67%   │ 🟡 MEDIUM   │
└─────────────────────┴──────────────┴─────────────┴──────────┴─────────────┘
```

### **🎯 AI Decision Examples**
- **Warning Triggered**: Fund below -5% threshold
- **Risk Assessment**: Portfolio classified as MEDIUM risk  
- **Optimization**: Current allocation deemed optimal
- **Action Items**: Review investment strategy

---

## 🔧 **Development**

### **🧪 Running Tests**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test category
pytest -m "unit_tests"
```

### **🐳 Docker Development**
```bash
# Build container
docker build -t financial-analytics-hub .

# Run container
docker run -p 8506:8506 financial-analytics-hub
```

### **🔍 Code Quality**
```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

---

## 🤝 **Contributing**

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes and add tests**
4. **Commit your changes** (`git commit -m 'Add amazing feature'`)
5. **Push to the branch** (`git push origin feature/amazing-feature`)
6. **Open a Pull Request**

### **🐛 Bug Reports & 💡 Feature Requests**
- Use [GitHub Issues](https://github.com/prasiddhnaik/-Financial-Analytics-Hub/issues)
- Provide detailed descriptions
- Include steps to reproduce

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🏆 **Professional Standards**

### **✅ Enterprise Features**
- [x] **Comprehensive Testing** (595-line test suite)
- [x] **CI/CD Pipeline** (GitHub Actions, automated deployment)
- [x] **Security Standards** (Vulnerability scanning, secure defaults)
- [x] **Documentation Excellence** (17 professional guides)
- [x] **Code Quality** (Linting, formatting, type checking)
- [x] **Performance Optimization** (Sub-3s analysis workflow)
- [x] **Containerization** (Docker, multi-stage builds)
- [x] **Package Management** (PyPI ready, dependency management)

---

## 🙏 **Acknowledgments**

- **Financial Industry**: Professional portfolio management practices
- **Open Source Community**: Amazing Python ecosystem  
- **Data Providers**: CoinGecko, Yahoo Finance, Frankfurter APIs

---

<div align="center">

## 🚀 **Transform Your Financial Analysis Today!**

### **[⭐ Star this repository](https://github.com/prasiddhnaik/-Financial-Analytics-Hub) • [📖 Read the docs](docs/guides/PROJECT_SUMMARY.md)**

---

**Built with ❤️ by financial technology enthusiasts**

*Empowering intelligent investment decisions through AI*

[![Made with Love](https://img.shields.io/badge/Made%20with-❤️-red)](https://github.com/prasiddhnaik/-Financial-Analytics-Hub)
[![Python Powered](https://img.shields.io/badge/Python-Powered-blue?logo=python)](https://python.org)
[![AI Enhanced](https://img.shields.io/badge/AI-Enhanced-purple?logo=robot)](https://github.com/prasiddhnaik/-Financial-Analytics-Hub)

*Last updated: January 2025 • Version 2.0.0*

</div> 