"""
Prioritized Stock Data Loader
Loads main stocks first for fast response, then loads sector-specific stocks on demand
"""

import yfinance as yf
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import time

logger = logging.getLogger(__name__)

# Main stocks to load immediately (fastest response)
MAIN_STOCKS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "V", "JNJ"
]

# Sector-based stock groups (loaded on demand)
SECTOR_STOCKS = {
    "Technology": {
        "large_cap": ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "TSLA", "NFLX", "ADBE", "CRM", "ORCL"],
        "mid_cap": ["SNOW", "PLTR", "DDOG", "NET", "OKTA", "ZS", "CRWD", "S", "DOCU", "ZM"],
        "growth": ["SHOP", "SQ", "ROKU", "TWLO", "PINS", "SNAP", "UBER", "LYFT", "SPOT", "RBLX"]
    },
    "Healthcare": {
        "pharma": ["JNJ", "PFE", "ABBV", "LLY", "BMY", "GILD", "AMGN", "BIIB", "REGN", "VRTX"],
        "biotech": ["MRNA", "NVAX", "BNTX", "ILMN", "CELG", "INCY", "ALXN", "SGEN", "TECH", "ISRG"],
        "devices": ["MDT", "ABT", "TMO", "DHR", "SYK", "BSX", "EW", "HOLX", "VAR", "ZBH"]
    },
    "Finance": {
        "banks": ["JPM", "BAC", "WFC", "C", "GS", "MS", "USB", "PNC", "TFC", "COF"],
        "payments": ["V", "MA", "PYPL", "SQ", "FIS", "FISV", "AXP", "DFS", "COF", "ALLY"],
        "insurance": ["BRK-B", "PG", "UNH", "ANTM", "CVS", "CI", "HUM", "CNC", "MOH", "ELV"]
    },
    "Consumer": {
        "retail": ["AMZN", "WMT", "HD", "LOW", "TGT", "COST", "NKE", "SBUX", "MCD", "CMG"],
        "ecommerce": ["AMZN", "SHOP", "ETSY", "EBAY", "BABA", "JD", "PDD", "MELI", "SE", "CPNG"],
        "consumer_goods": ["PG", "KO", "PEP", "UL", "CL", "KMB", "GIS", "K", "CPB", "CAG"]
    },
    "Energy": {
        "oil_gas": ["XOM", "CVX", "COP", "EOG", "PXD", "KMI", "OKE", "WMB", "EPD", "ET"],
        "renewable": ["NEE", "DUK", "SO", "AEP", "EXC", "XEL", "ED", "AWK", "ATO", "CMS"],
        "utilities": ["NEE", "DUK", "SO", "D", "AEP", "EXC", "SRE", "PEG", "XEL", "WEC"]
    },
    "Industrial": {
        "aerospace": ["BA", "LMT", "RTX", "NOC", "GD", "TXT", "HON", "MMM", "CAT", "DE"],
        "transportation": ["UPS", "FDX", "DAL", "UAL", "AAL", "LUV", "JBLU", "ALK", "SAVE", "HA"],
        "manufacturing": ["GE", "MMM", "HON", "CAT", "DE", "EMR", "ITW", "PH", "ETN", "ROK"]
    }
}

# API configurations prioritized by speed and reliability
API_CONFIGS = {
    "yahoo_finance": {"priority": 1, "rate_limit": 2000, "fast": True},
    "finnhub": {"priority": 2, "rate_limit": 60, "fast": True},
    "alpha_vantage": {"priority": 3, "rate_limit": 5, "fast": False},
    "fmp": {"priority": 4, "rate_limit": 250, "fast": True},
    "polygon": {"priority": 5, "rate_limit": 5, "fast": False}
}

def fetch_stock_yahoo(symbol: str) -> Optional[Dict]:
    """Fast Yahoo Finance fetch - highest priority"""
    try:
        ticker = yf.Ticker(symbol)
        
        # Use fast_info for speed
        if hasattr(ticker, 'fast_info'):
            fast_info = ticker.fast_info
            price = fast_info.get('last_price', 0)
            if price and price > 0:
                return {
                    "symbol": symbol,
                    "name": f"{symbol} Corp",  # Will be enriched later
                    "current_price": round(float(price), 2),
                    "volume": fast_info.get('last_volume', 0),
                    "market_cap": fast_info.get('market_cap', 0),
                    "source": "yahoo_fast",
                    "timestamp": datetime.now().isoformat()
                }
        
        # Fallback to regular method
        hist = ticker.history(period="1d")
        if not hist.empty:
            price = float(hist['Close'].iloc[-1])
            volume = int(hist['Volume'].iloc[-1])
            
            return {
                "symbol": symbol,
                "name": f"{symbol} Corp",
                "current_price": round(price, 2),
                "volume": volume,
                "market_cap": None,
                "source": "yahoo_regular",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Yahoo Finance error for {symbol}: {e}")
        return None

def fetch_stock_finnhub(symbol: str) -> Optional[Dict]:
    """Finnhub API - good rate limits"""
    try:
        url = "https://finnhub.io/api/v1/quote"
        params = {"symbol": symbol, "token": "demo"}
        
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        if data.get('c') and data.get('c') > 0:
            return {
                "symbol": symbol,
                "name": f"{symbol} Corp",
                "current_price": round(float(data['c']), 2),
                "volume": None,
                "market_cap": None,
                "change": round(float(data.get('d', 0)), 2),
                "change_percent": round(float(data.get('dp', 0)), 2),
                "source": "finnhub",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Finnhub error for {symbol}: {e}")
        return None

def fetch_main_stocks() -> List[Dict]:
    """Fetch main stocks quickly for initial load"""
    stocks = []
    
    for symbol in MAIN_STOCKS:
        # Try Yahoo first (fastest)
        stock_data = fetch_stock_yahoo(symbol)
        
        # Fallback to Finnhub if Yahoo fails
        if not stock_data:
            stock_data = fetch_stock_finnhub(symbol)
            
        if stock_data:
            stocks.append(stock_data)
            
    logger.info(f"Loaded {len(stocks)} main stocks in fast mode")
    return stocks

def fetch_sector_stocks(sector: str, subcategory: str = None) -> List[Dict]:
    """Fetch stocks for a specific sector"""
    if sector not in SECTOR_STOCKS:
        return []
    
    sector_data = SECTOR_STOCKS[sector]
    
    # Get symbols based on subcategory or all
    if subcategory and subcategory in sector_data:
        symbols = sector_data[subcategory]
    else:
        # Get all symbols from all subcategories
        symbols = []
        for subcat_symbols in sector_data.values():
            symbols.extend(subcat_symbols)
        # Remove duplicates
        symbols = list(set(symbols))
    
    stocks = []
    for symbol in symbols[:15]:  # Limit to 15 per request for speed
        stock_data = fetch_stock_yahoo(symbol)
        if not stock_data:
            stock_data = fetch_stock_finnhub(symbol)
            
        if stock_data:
            # Add sector info
            stock_data.update({
                "sector": sector,
                "subcategory": subcategory,
                "industry": get_industry_for_symbol(symbol)
            })
            stocks.append(stock_data)
    
    logger.info(f"Loaded {len(stocks)} stocks for {sector}/{subcategory}")
    return stocks

def get_industry_for_symbol(symbol: str) -> str:
    """Get industry classification for symbol"""
    industry_map = {
        # Technology
        "AAPL": "Consumer Electronics", "MSFT": "Software", "GOOGL": "Internet Software",
        "META": "Social Media", "NVDA": "Semiconductors", "TSLA": "Electric Vehicles",
        "NFLX": "Streaming", "ADBE": "Software", "CRM": "Cloud Software", "ORCL": "Database Software",
        
        # Healthcare
        "JNJ": "Pharmaceuticals", "PFE": "Pharmaceuticals", "ABBV": "Biotechnology",
        "LLY": "Pharmaceuticals", "UNH": "Health Insurance",
        
        # Finance
        "JPM": "Banking", "BAC": "Banking", "V": "Payment Processing", "MA": "Payment Processing",
        
        # Consumer
        "AMZN": "E-commerce", "WMT": "Retail", "HD": "Home Improvement", "NKE": "Apparel",
        
        # Energy
        "XOM": "Oil & Gas", "CVX": "Oil & Gas"
    }
    
    return industry_map.get(symbol, "Unknown")

def get_available_sectors() -> Dict[str, List[str]]:
    """Get list of available sectors and their subcategories"""
    sectors = {}
    for sector, subcategories in SECTOR_STOCKS.items():
        sectors[sector] = list(subcategories.keys())
    return sectors

def get_stock_counts_by_sector() -> Dict[str, int]:
    """Get count of stocks available in each sector"""
    counts = {}
    for sector, subcategories in SECTOR_STOCKS.items():
        total = 0
        for symbols in subcategories.values():
            total += len(set(symbols))  # Remove duplicates
        counts[sector] = total
    return counts 