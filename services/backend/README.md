# Financial Data Server 💹

A fast, reliable financial data API server providing real-time stock market data with intelligent caching.

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd project-pie-react/services/backend

# Install dependencies
pip install -r requirements.txt
```

### Start the Server
```bash
# Option 1: Use the starter script (recommended)
python3 start_server.py

# Option 2: Run directly
python3 quick_server.py
```

The server will start on `http://localhost:4000`

## 📊 API Endpoints

### Test Server
```bash
GET /test
```
**Example:**
```bash
curl http://localhost:4000/test
```

### Get Single Stock
```bash
GET /stock/<symbol>
```
**Example:**
```bash
curl http://localhost:4000/stock/AAPL
```

**Response:**
```json
{
  "symbol": "AAPL",
  "current_price": 196.58,
  "change": 0.94,
  "change_percent": 0.48,
  "volume": 45394700,
  "high": 197.57,
  "low": 195.07,
  "timestamp": "2025-06-20T18:24:20.228702",
  "source": "yahoo_finance"
}
```

### Get Multiple Stocks
```bash
POST /stocks
Content-Type: application/json

{
  "symbols": ["AAPL", "GOOGL", "MSFT"]
}
```

**Example:**
```bash
curl -X POST http://localhost:4000/stocks \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "GOOGL", "MSFT"]}'
```

### Get Popular Stocks
```bash
GET /popular
```
**Example:**
```bash
curl http://localhost:4000/popular
```

### Clear Cache
```bash
GET /clear-cache
```

## 🏗️ Architecture

### Simple & Fast
- **Single reliable data source**: Yahoo Finance via `yfinance`
- **In-memory caching**: 60-second cache for optimal performance
- **Auto cache cleanup**: Keeps only the most recent 50 entries
- **CORS enabled**: Ready for web applications

### Performance Features
- ⚡ Sub-second response times after first load
- 🧠 Smart caching with automatic cleanup
- 📊 Handles multiple stocks efficiently
- 🔄 Real-time data updates

## 🛠️ Dependencies

Core dependencies (install via pip):
```
flask
flask-cors
yfinance
pandas
```

Full requirements in `requirements.txt`

## 🔧 Configuration

The server runs on:
- **Host**: `0.0.0.0` (all interfaces)
- **Port**: `4000`
- **Cache Duration**: 60 seconds
- **Max Cache Size**: 50 entries

## 📁 Project Structure

```
services/backend/
├── quick_server.py          # Main server (recommended)
├── start_server.py          # Server starter script
├── simplified_multi_source.py  # Advanced multi-API system
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔄 Alternative Servers

### Advanced Multi-API Server
For more robust data with fallback sources:
```bash
python3 simple_web_server.py  # Full-featured server
python3 fast_api_server.py    # Optimized version
```

**Note**: These require fixing indentation in `simplified_multi_source.py`

## 🧪 Testing

Test the server manually:
```bash
# Test basic functionality
curl http://localhost:4000/test

# Test stock data
curl http://localhost:4000/stock/AAPL

# Test popular stocks
curl http://localhost:4000/popular
```

## 🚨 Troubleshooting

### Connection Refused
1. Make sure you're in the correct directory: `services/backend/`
2. Check if port 4000 is available: `lsof -i :4000`
3. Use the starter script: `python3 start_server.py`

### Import Errors
1. Install dependencies: `pip install -r requirements.txt`
2. Use Python 3.7+: `python3 --version`

### Indentation Errors
If you encounter indentation errors with the advanced servers:
1. Use `quick_server.py` (recommended)
2. Or fix indentation in `simplified_multi_source.py`

## 📈 Usage Examples

### Web Frontend Integration
```javascript
// Fetch single stock
const response = await fetch('http://localhost:4000/stock/AAPL');
const data = await response.json();

// Fetch multiple stocks
const response = await fetch('http://localhost:4000/stocks', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ symbols: ['AAPL', 'GOOGL'] })
});
```

### Python Client
```python
import requests

# Get single stock
response = requests.get('http://localhost:4000/stock/AAPL')
data = response.json()

# Get multiple stocks
response = requests.post('http://localhost:4000/stocks', 
                        json={'symbols': ['AAPL', 'GOOGL']})
data = response.json()
```

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Ready to use! Start the server and begin fetching real-time financial data.** 🚀 