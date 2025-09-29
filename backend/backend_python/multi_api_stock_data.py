"""
Multi-API stock data fetcher using multiple real data sources
Provides ACCURATE live market data from multiple APIs for reliability
"""

import requests
import yfinance as yf
import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import time

logger = logging.getLogger(__name__)

# API Keys and endpoints
ALPHA_VANTAGE_API_KEY = "3J52FQXN785RGJX0"
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

# Major S&P 500 stocks for real data
STOCK_SYMBOLS = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "META", "TSLA", "NFLX", "ADBE", "CRM", "ORCL",
    "JPM", "BAC", "WFC", "GS", "MS", "V", "MA", "AXP", "PYPL", "BRK-B",
    "JNJ", "PFE", "UNH", "ABBV", "LLY", "TMO", "AMGN", "DHR", "BMY", "GILD",
    "XOM", "CVX", "COP", "SLB", "EOG", "PSX", "VLO", "MPC", "KMI", "OKE",
    "AMZN", "PG", "KO", "PEP", "WMT", "COST", "HD", "MCD", "NKE", "SBUX"
]

COMPANY_INFO = {
    "AAPL": {"name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics"},
    "MSFT": {"name": "Microsoft Corporation", "sector": "Technology", "industry": "Software"},
    "NVDA": {"name": "NVIDIA Corporation", "sector": "Technology", "industry": "Semiconductors"},
    "GOOGL": {"name": "Alphabet Inc.", "sector": "Technology", "industry": "Internet Software"},
    "META": {"name": "Meta Platforms Inc.", "sector": "Technology", "industry": "Social Media"},
    "TSLA": {"name": "Tesla Inc.", "sector": "Technology", "industry": "Electric Vehicles"},
    "NFLX": {"name": "Netflix Inc.", "sector": "Technology", "industry": "Streaming"},
    "ADBE": {"name": "Adobe Inc.", "sector": "Technology", "industry": "Software"},
    "CRM": {"name": "Salesforce Inc.", "sector": "Technology", "industry": "Cloud Software"},
    "ORCL": {"name": "Oracle Corporation", "sector": "Technology", "industry": "Database Software"},
    "JPM": {"name": "JPMorgan Chase & Co.", "sector": "Finance", "industry": "Banking"},
    "BAC": {"name": "Bank of America Corp.", "sector": "Finance", "industry": "Banking"},
    "WFC": {"name": "Wells Fargo & Company", "sector": "Finance", "industry": "Banking"},
    "GS": {"name": "Goldman Sachs Group Inc.", "sector": "Finance", "industry": "Investment Banking"},
    "MS": {"name": "Morgan Stanley", "sector": "Finance", "industry": "Investment Banking"},
    "BRK-B": {"name": "Berkshire Hathaway Inc.", "sector": "Finance", "industry": "Diversified Investments"},
    "V": {"name": "Visa Inc.", "sector": "Finance", "industry": "Payment Processing"},
    "MA": {"name": "Mastercard Incorporated", "sector": "Finance", "industry": "Payment Processing"},
    "AXP": {"name": "American Express Company", "sector": "Finance", "industry": "Credit Services"},
    "PYPL": {"name": "PayPal Holdings Inc.", "sector": "Finance", "industry": "Digital Payments"},
    "JNJ": {"name": "Johnson & Johnson", "sector": "Healthcare", "industry": "Pharmaceuticals"},
    "PFE": {"name": "Pfizer Inc.", "sector": "Healthcare", "industry": "Pharmaceuticals"},
    "UNH": {"name": "UnitedHealth Group Inc.", "sector": "Healthcare", "industry": "Health Insurance"},
    "ABBV": {"name": "AbbVie Inc.", "sector": "Healthcare", "industry": "Biotechnology"},
    "LLY": {"name": "Eli Lilly and Company", "sector": "Healthcare", "industry": "Pharmaceuticals"},
    "TMO": {"name": "Thermo Fisher Scientific Inc.", "sector": "Healthcare", "industry": "Medical Devices"},
    "AMGN": {"name": "Amgen Inc.", "sector": "Healthcare", "industry": "Biotechnology"},
    "DHR": {"name": "Danaher Corporation", "sector": "Healthcare", "industry": "Medical Equipment"},
    "BMY": {"name": "Bristol-Myers Squibb Company", "sector": "Healthcare", "industry": "Pharmaceuticals"},
    "GILD": {"name": "Gilead Sciences Inc.", "sector": "Healthcare", "industry": "Biotechnology"},
    "XOM": {"name": "Exxon Mobil Corporation", "sector": "Energy", "industry": "Oil & Gas"},
    "CVX": {"name": "Chevron Corporation", "sector": "Energy", "industry": "Oil & Gas"},
    "COP": {"name": "ConocoPhillips", "sector": "Energy", "industry": "Oil & Gas Exploration"},
    "SLB": {"name": "Schlumberger Limited", "sector": "Energy", "industry": "Oil Services"},
    "EOG": {"name": "EOG Resources Inc.", "sector": "Energy", "industry": "Oil & Gas Exploration"},
    "PSX": {"name": "Phillips 66", "sector": "Energy", "industry": "Oil Refining"},
    "VLO": {"name": "Valero Energy Corporation", "sector": "Energy", "industry": "Oil Refining"},
    "MPC": {"name": "Marathon Petroleum Corporation", "sector": "Energy", "industry": "Oil Refining"},
    "KMI": {"name": "Kinder Morgan Inc.", "sector": "Energy", "industry": "Pipeline"},
    "OKE": {"name": "ONEOK Inc.", "sector": "Energy", "industry": "Pipeline"},
    "AMZN": {"name": "Amazon.com Inc.", "sector": "Consumer Goods", "industry": "E-commerce"},
    "PG": {"name": "Procter & Gamble Company", "sector": "Consumer Goods", "industry": "Consumer Products"},
    "KO": {"name": "The Coca-Cola Company", "sector": "Consumer Goods", "industry": "Beverages"},
    "PEP": {"name": "PepsiCo Inc.", "sector": "Consumer Goods", "industry": "Beverages"},
    "WMT": {"name": "Walmart Inc.", "sector": "Consumer Goods", "industry": "Retail"},
    "COST": {"name": "Costco Wholesale Corporation", "sector": "Consumer Goods", "industry": "Retail"},
    "HD": {"name": "The Home Depot Inc.", "sector": "Consumer Goods", "industry": "Home Improvement"},
    "MCD": {"name": "McDonald's Corporation", "sector": "Consumer Goods", "industry": "Restaurants"},
    "NKE": {"name": "NIKE Inc.", "sector": "Consumer Goods", "industry": "Apparel"},
    "SBUX": {"name": "Starbucks Corporation", "sector": "Consumer Goods", "industry": "Restaurants"}
}

def fetch_yfinance_data(symbol: str) -> Optional[Dict[str, Any]]:
    """Fetch stock data using yfinance (Yahoo Finance) - Most reliable free API"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="2d")
        
        if hist.empty:
            return None
            
        current_price = float(hist['Close'].iloc[-1])
        prev_close = float(hist['Close'].iloc[-2]) if len(hist) >= 2 else current_price
        volume = int(hist['Volume'].iloc[-1])
        high = float(hist['High'].iloc[-1])
        low = float(hist['Low'].iloc[-1])
        open_price = float(hist['Open'].iloc[-1])
        
        price_change = current_price - prev_close
        price_change_percent = (price_change / prev_close * 100) if prev_close > 0 else 0
        
        company_info = COMPANY_INFO.get(symbol, {})
        
        return {
            "symbol": symbol,
            "name": company_info.get("name", info.get("longName", f"{symbol} Corp")),
            "current_price": round(current_price, 2),
            "volume": volume,
            "market_cap": info.get("marketCap"),
            "sector": company_info.get("sector", info.get("sector", "Unknown")),
            "industry": company_info.get("industry", info.get("industry", "Unknown")),
            "country": "US",
            "currency": "USD",
            "price_change": round(price_change, 2),
            "price_change_percent": round(price_change_percent, 2),
            "last_updated": datetime.now().isoformat(),
            "asset_type": "stock",
            "high": round(high, 2),
            "low": round(low, 2),
            "open": round(open_price, 2),
            "previous_close": round(prev_close, 2),
            "pe_ratio": info.get("trailingPE"),
            "dividend_yield": info.get("dividendYield"),
            "data_source": "yfinance"
        }
        
    except Exception as e:
        logger.error(f"Error fetching yfinance data for {symbol}: {e}")
        return None

def fetch_alpha_vantage_data(symbol: str) -> Optional[Dict[str, Any]]:
    """Fetch stock data using Alpha Vantage API"""
    try:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "Global Quote" in data and data["Global Quote"]:
            quote = data["Global Quote"]
            company_info = COMPANY_INFO.get(symbol, {})
            
            current_price = float(quote.get("05. price", 0))
            change = float(quote.get("09. change", 0))
            change_percent = float(quote.get("10. change percent", "0%").replace("%", ""))
            
            return {
                "symbol": symbol,
                "name": company_info.get("name", f"{symbol} Corp"),
                "current_price": round(current_price, 2),
                "volume": int(quote.get("06. volume", 0)),
                "market_cap": None,
                "sector": company_info.get("sector", "Unknown"),
                "industry": company_info.get("industry", "Unknown"),
                "country": "US",
                "currency": "USD",
                "price_change": round(change, 2),
                "price_change_percent": round(change_percent, 2),
                "last_updated": datetime.now().isoformat(),
                "asset_type": "stock",
                "high": float(quote.get("03. high", 0)),
                "low": float(quote.get("04. low", 0)),
                "open": float(quote.get("02. open", 0)),
                "previous_close": float(quote.get("08. previous close", 0)),
                "data_source": "alpha_vantage"
            }
        return None
            
    except Exception as e:
        logger.error(f"Error fetching Alpha Vantage data for {symbol}: {e}")
        return None

def fetch_finnhub_data(symbol: str) -> Optional[Dict[str, Any]]:
    """Fetch stock data using Finnhub free API"""
    try:
        # Finnhub free API endpoint
        quote_url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token=demo"
        profile_url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token=demo"
        
        quote_response = requests.get(quote_url, timeout=10)
        if quote_response.status_code == 200:
            quote_data = quote_response.json()
            
            if quote_data.get('c') and quote_data.get('c') > 0:  # current price exists
                company_info = COMPANY_INFO.get(symbol, {})
                current_price = float(quote_data['c'])
                change = float(quote_data.get('d', 0))
                change_percent = float(quote_data.get('dp', 0))
                
                return {
                    "symbol": symbol,
                    "name": company_info.get("name", f"{symbol} Corp"),
                    "current_price": round(current_price, 2),
                    "volume": None,
                    "market_cap": None,
                    "sector": company_info.get("sector", "Unknown"),
                    "industry": company_info.get("industry", "Unknown"),
                    "country": "US",
                    "currency": "USD",
                    "price_change": round(change, 2),
                    "price_change_percent": round(change_percent, 2),
                    "last_updated": datetime.now().isoformat(),
                    "asset_type": "stock",
                    "high": float(quote_data.get('h', 0)),
                    "low": float(quote_data.get('l', 0)),
                    "open": float(quote_data.get('o', 0)),
                    "previous_close": float(quote_data.get('pc', 0)),
                    "data_source": "finnhub"
                }
        return None
        
    except Exception as e:
        logger.error(f"Error fetching Finnhub data for {symbol}: {e}")
        return None

def get_best_stock_data(symbol: str) -> Optional[Dict[str, Any]]:
    """Get the best available stock data by trying multiple APIs"""
    
    # Try Yahoo Finance first (most reliable)
    data = fetch_yfinance_data(symbol)
    if data and data.get('current_price', 0) > 0:
        return data
    
    # Try Finnhub as backup
    data = fetch_finnhub_data(symbol)
    if data and data.get('current_price', 0) > 0:
        return data
        
    # Try Alpha Vantage as last resort
    data = fetch_alpha_vantage_data(symbol)
    if data and data.get('current_price', 0) > 0:
        return data
    
    logger.warning(f"Could not fetch data for {symbol} from any API")
    return None

def get_multi_api_stocks_data() -> List[Dict[str, Any]]:
    """Fetch live stock data using multiple APIs for maximum accuracy"""
    live_stocks = []
    
    # Priority stocks for testing - focus on the ones you mentioned
    priority_symbols = ["MSFT", "AAPL", "JPM", "GOOGL", "TSLA", "NVDA", "AMZN", "META", "NFLX", "V"]
    
    for symbol in priority_symbols:
        try:
            stock_data = get_best_stock_data(symbol)
            if stock_data:
                live_stocks.append(stock_data)
                logger.info(f"Fetched {symbol}: ${stock_data['current_price']} from {stock_data.get('data_source', 'unknown')}")
            else:
                logger.warning(f"Failed to fetch data for {symbol}")
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
    
    return live_stocks

# Test the accuracy with specific stocks
def test_stock_accuracy():
    """Test function to verify stock prices"""
    msft_data = get_best_stock_data("MSFT")
    if msft_data:
        print(f"Microsoft (MSFT): ${msft_data['current_price']} from {msft_data.get('data_source')}")
    
    jpm_data = get_best_stock_data("JPM")
    if jpm_data:
        print(f"JPMorgan (JPM): ${jpm_data['current_price']} from {jpm_data.get('data_source')}")

if __name__ == "__main__":
    test_stock_accuracy() 