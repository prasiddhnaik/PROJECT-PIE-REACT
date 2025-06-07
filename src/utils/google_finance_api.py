"""
Google Finance API Integration
Fetches real-time stock prices from Google Finance
"""

import requests
import json
import re
from typing import Dict, Optional, List
import time

class GoogleFinanceAPI:
    """Google Finance API client for fetching real-time stock data"""
    
    def __init__(self):
        self.base_url = "https://www.google.com/finance"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_stock_price(self, symbol: str, exchange: str = "NSE") -> Optional[Dict]:
        """
        Get real-time stock price from Google Finance
        
        Args:
            symbol: Stock symbol (e.g., 'TCS', 'INFY', 'AAPL')
            exchange: Exchange code (e.g., 'NSE', 'BSE', 'NASDAQ', 'NYSE')
        
        Returns:
            Dict with stock data or None if not found
        """
        try:
            # Format the URL for Google Finance
            if exchange == "NSE":
                url = f"{self.base_url}/quote/{symbol}:NSE"
            elif exchange == "NASDAQ":
                url = f"{self.base_url}/quote/{symbol}:NASDAQ"
            elif exchange == "NYSE":
                url = f"{self.base_url}/quote/{symbol}:NYSE"
            else:
                url = f"{self.base_url}/quote/{symbol}:{exchange}"
            
            response = self.session.get(url, timeout=1800)
            
            if response.status_code == 200:
                # Extract price from the HTML content
                content = response.text
                
                # Look for price data in the HTML - try multiple patterns
                price_patterns = [
                    r'"c1":"\$?([0-9,]+\.?[0-9]*)"',
                    r'data-last-price="([0-9,]+\.?[0-9]*)"',
                    r'"price":"([0-9,]+\.?[0-9]*)"',
                    r'class="YMlKec fxKbKc">([0-9,]+\.?[0-9]*)</span>'
                ]
                
                price = None
                for pattern in price_patterns:
                    price_match = re.search(pattern, content)
                    if price_match:
                        price_str = price_match.group(1).replace(',', '')
                        try:
                            price = float(price_str)
                            break
                        except ValueError:
                            continue
                
                if price and price > 0:
                    # Extract additional data
                    change_pattern = r'"c2":"([+-]?\$?[0-9,]+\.?[0-9]*)"'
                    change_match = re.search(change_pattern, content)
                    change = 0.0
                    if change_match:
                        change_str = change_match.group(1).replace('$', '').replace(',', '')
                        try:
                            change = float(change_str)
                        except:
                            change = 0.0
                    
                    # Extract percentage change
                    pct_pattern = r'"c3":"([+-]?[0-9]+\.?[0-9]*)%"'
                    pct_match = re.search(pct_pattern, content)
                    pct_change = 0.0
                    if pct_match:
                        try:
                            pct_change = float(pct_match.group(1))
                        except:
                            pct_change = 0.0
                    
                    return {
                        'symbol': symbol,
                        'exchange': exchange,
                        'price': price,
                        'change': change,
                        'change_percent': pct_change,
                        'currency': self._get_currency_for_exchange(exchange),
                        'timestamp': time.time()
                    }
            
            return None
            
        except Exception as e:
            print(f"Error fetching {symbol} from Google Finance: {e}")
            return None
    
    def _get_currency_for_exchange(self, exchange: str) -> str:
        """Get currency code for exchange"""
        currency_map = {
            'NSE': 'INR',
            'BSE': 'INR',
            'NASDAQ': 'USD',
            'NYSE': 'USD',
            'LSE': 'GBP',
            'TSE': 'JPY'
        }
        return currency_map.get(exchange, 'USD')
    
    def get_multiple_stocks(self, symbols: List[str], exchange: str = "NSE") -> Dict[str, Dict]:
        """
        Get multiple stock prices
        
        Args:
            symbols: List of stock symbols
            exchange: Exchange code
        
        Returns:
            Dict mapping symbols to their data
        """
        results = {}
        
        for symbol in symbols:
            data = self.get_stock_price(symbol, exchange)
            if data:
                results[symbol] = data
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        
        return results
    
    def get_indian_stocks(self) -> Dict[str, Dict]:
        """Get data for major Indian stocks"""
        indian_stocks = [
            'TCS', 'INFY', 'HCLTECH', 'WIPRO', 'TECHM',  # IT
            'RELIANCE', 'ONGC', 'IOC', 'BPCL', 'GAIL',   # Energy
            'ICICIBANK', 'HDFCBANK', 'SBIN', 'AXISBANK', 'KOTAKBANK',  # Banks
            'ITC', 'HINDUNILVR', 'NESTLEIND', 'BRITANNIA', 'DABUR',     # FMCG
            'TATAMOTORS', 'M&M', 'BAJAJ-AUTO', 'MARUTI', 'HEROMOTOCO', # Auto
            'SUNPHARMA', 'DRREDDY', 'CIPLA', 'AUROBINDO', 'LUPIN'       # Pharma
        ]
        
        return self.get_multiple_stocks(indian_stocks, "NSE")

# Alternative method using Google Finance RSS feeds
class GoogleFinanceRSS:
    """Alternative Google Finance client using RSS feeds"""
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_stock_price_rss(self, symbol: str, exchange: str = "NSE") -> Optional[Dict]:
        """Get stock price using Google Finance RSS feed"""
        try:
            # Google Finance RSS URL
            rss_url = f"https://finance.google.com/finance?output=atom&q={exchange}:{symbol}"
            
            response = self.session.get(rss_url, timeout=1800)
            
            if response.status_code == 200:
                content = response.text
                
                # Extract price from RSS content
                price_pattern = r'<span class="pr">([0-9,]+\.?[0-9]*)</span>'
                price_match = re.search(price_pattern, content)
                
                if price_match:
                    price_str = price_match.group(1).replace(',', '')
                    price = float(price_str)
                    
                    return {
                        'symbol': symbol,
                        'exchange': exchange,
                        'price': price,
                        'currency': 'INR' if exchange in ['NSE', 'BSE'] else 'USD',
                        'source': 'Google Finance RSS',
                        'timestamp': time.time()
                    }
            
            return None
            
        except Exception as e:
            print(f"Error fetching {symbol} from Google Finance RSS: {e}")
            return None

# Test function
def test_google_finance():
    """Test Google Finance API"""
    gf = GoogleFinanceAPI()
    
    print("Testing Google Finance API...")
    
    # Test individual stocks
    test_stocks = ['TCS', 'INFY', 'HCLTECH', 'RELIANCE']
    
    for stock in test_stocks:
        data = gf.get_stock_price(stock, 'NSE')
        if data:
            print(f"{stock}: ₹{data['price']:.2f} ({data['change_percent']:+.2f}%)")
        else:
            print(f"{stock}: Failed to fetch")
    
    print("\nTesting multiple stocks...")
    multiple_data = gf.get_multiple_stocks(['TCS', 'INFY', 'HCLTECH'])
    for symbol, data in multiple_data.items():
        print(f"{symbol}: ₹{data['price']:.2f}")

if __name__ == "__main__":
    test_google_finance() 