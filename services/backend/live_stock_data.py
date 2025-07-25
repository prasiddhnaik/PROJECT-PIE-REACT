"""
Live stock data fetcher using Alpha Vantage API
Provides REAL market data, not fake placeholder data
"""

import requests
from datetime import datetime
from typing import List, Dict, Any
import logging
import time

logger = logging.getLogger(__name__)

ALPHA_VANTAGE_API_KEY = "3J52FQXN785RGJX0"
BASE_URL = "https://www.alphavantage.co/query"

# Top 50 S&P 500 symbols to fetch real data for
STOCK_SYMBOLS = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "META", "TSLA", "NFLX", "ADBE", "CRM", "ORCL",
    "JPM", "BAC", "WFC", "GS", "MS", "V", "MA", "AXP", "PYPL",
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

def fetch_stock_quote(symbol: str) -> Dict[str, Any]:
    """Fetch real-time stock quote from Alpha Vantage"""
    try:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        
        response = requests.get(BASE_URL, params=params, timeout=10)
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
                "market_cap": None,  # Would need separate API call
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
                "previous_close": float(quote.get("08. previous close", 0))
            }
        else:
            logger.error(f"No quote data for {symbol}: {data}")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {e}")
        return None

def get_live_stocks_data() -> List[Dict[str, Any]]:
    """Fetch live data for top stocks (limited by API rate limits)"""
    live_stocks = []
    
    # Alpha Vantage free tier: 5 requests per minute, 100 per day
    # Let's fetch just the first 5 stocks for now to demonstrate real data
    priority_symbols = ["AAPL", "MSFT", "GOOGL", "JPM", "TSLA"]
    
    for symbol in priority_symbols:
        stock_data = fetch_stock_quote(symbol)
        if stock_data:
            live_stocks.append(stock_data)
        # Rate limit: wait 12 seconds between requests (5 per minute)
        time.sleep(12)
    
    return live_stocks 