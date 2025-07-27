"""
Market Data Fetcher
===================

Handles fetching stock data from multiple sources:
- Yahoo Finance (Primary)
- NSE India
- Alpha Vantage
- Finnhub
- Twelve Data

Provides real-time and historical data for:
- NSE stocks (7000+ symbols)
- International markets
- Indices (Nifty, Sensex, etc.)
- Cryptocurrency
"""

import asyncio
import aiohttp
import yfinance as yf
import pandas as pd
import numpy as np
import os
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import logging
from cachetools import TTLCache
from alpha_vantage.timeseries import TimeSeries
import finnhub
from twelvedata import TDClient

logger = logging.getLogger(__name__)

class MarketDataFetcher:
    """
    Comprehensive market data fetcher supporting multiple APIs and exchanges
    """
    
    def __init__(self):
        self.cache = TTLCache(maxsize=1000, ttl=300)  # 5-minute cache
        
        # API configurations
        self.alpha_vantage_key = "3J52FQXN785RGJX0"  # Your provided API key
        self.finnhub_key = os.getenv("FINNHUB_API_KEY", None) 
        self.twelve_data_key = os.getenv("TWELVE_DATA_API_KEY", None)
        
        # Initialize API clients
        self.av_client = TimeSeries(key=self.alpha_vantage_key, output_format='pandas')
        self.finnhub_client = finnhub.Client(api_key=self.finnhub_key) if self.finnhub_key else None
        self.td_client = TDClient(apikey=self.twelve_data_key) if self.twelve_data_key else None
        
        # NSE symbol lists
        self.nse_symbols = self._load_nse_symbols()
        self.nifty_50 = self._load_nifty_50()
        self.nifty_500 = self._load_nifty_500()
        
    def _load_nse_symbols(self) -> List[str]:
        """Load NSE stock symbols"""
        try:
            # Top NSE stocks - in production, load from NSE API or file
            return [
                "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "HINDUNILVR.NS",
                "INFY.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
                "ASIANPAINT.NS", "LT.NS", "AXISBANK.NS", "MARUTI.NS", "SUNPHARMA.NS",
                "TITAN.NS", "ULTRACEMCO.NS", "BAJFINANCE.NS", "NESTLEIND.NS", "WIPRO.NS",
                "ONGC.NS", "TECHM.NS", "NTPC.NS", "POWERGRID.NS", "TATAMOTORS.NS",
                "HCLTECH.NS", "M&M.NS", "BAJAJFINSV.NS", "TATASTEEL.NS", "ADANIGREEN.NS"
            ]
        except Exception as e:
            logger.error(f"Error loading NSE symbols: {e}")
            return []
    
    def _load_nifty_50(self) -> List[str]:
        """Load Nifty 50 constituent symbols"""
        return [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "HINDUNILVR.NS",
            "INFY.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
            "ASIANPAINT.NS", "LT.NS", "AXISBANK.NS", "MARUTI.NS", "SUNPHARMA.NS",
            "TITAN.NS", "ULTRACEMCO.NS", "BAJFINANCE.NS", "NESTLEIND.NS", "WIPRO.NS"
        ]
    
    def _load_nifty_500(self) -> List[str]:
        """Load Nifty 500 constituent symbols"""
        # Extended list for Nifty 500 - in production, fetch from NSE
        return self.nse_symbols  # Simplified for demo
    
    async def get_stock_data(self, symbol: str, period: str = "1d", 
                           interval: str = "1m") -> Optional[pd.DataFrame]:
        """
        Fetch stock data with fallback across multiple sources
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE.NS", "AAPL")
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            DataFrame with OHLCV data and additional metrics
        """
        cache_key = f"{symbol}_{period}_{interval}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Primary: Yahoo Finance
            data = await self._fetch_yahoo_data(symbol, period, interval)
            
            if data is not None and not data.empty:
                # Add technical indicators
                data = self._add_basic_indicators(data)
                self.cache[cache_key] = data
                return data
            
            # Fallback: Alpha Vantage
            if self.alpha_vantage_key:
                data = await self._fetch_alpha_vantage_data(symbol, interval)
                if data is not None and not data.empty:
                    data = self._add_basic_indicators(data)
                    self.cache[cache_key] = data
                    return data
            
            # Fallback: Finnhub
            if self.finnhub_client:
                data = await self._fetch_finnhub_data(symbol, period)
                if data is not None and not data.empty:
                    data = self._add_basic_indicators(data)
                    self.cache[cache_key] = data
                    return data
                    
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            
        return None
    
    async def _fetch_yahoo_data(self, symbol: str, period: str, 
                               interval: str) -> Optional[pd.DataFrame]:
        """Fetch data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval, 
                                prepost=True, repair=True)
            
            if data.empty:
                return None
                
            # Standardize column names
            data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            data.index.name = 'Datetime'
            
            return data
            
        except Exception as e:
            logger.error(f"Yahoo Finance error for {symbol}: {e}")
            return None
    
    async def _fetch_alpha_vantage_data(self, symbol: str, 
                                      interval: str) -> Optional[pd.DataFrame]:
        """Fetch data from Alpha Vantage"""
        try:
            # Convert symbol format
            clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
            
            if interval in ['1m', '5m', '15m', '30m']:
                data, _ = self.av_client.get_intraday(
                    symbol=clean_symbol, interval=interval, outputsize='full'
                )
            else:
                data, _ = self.av_client.get_daily_adjusted(
                    symbol=clean_symbol, outputsize='full'
                )
            
            if data.empty:
                return None
                
            # Standardize column names
            data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            data.index.name = 'Datetime'
            
            return data.sort_index()
            
        except Exception as e:
            logger.error(f"Alpha Vantage error for {symbol}: {e}")
            return None
    
    async def _fetch_finnhub_data(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """Fetch data from Finnhub"""
        try:
            # Convert symbol format
            clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
            
            # Calculate date range
            end_date = datetime.now()
            days_map = {
                '1d': 1, '5d': 5, '1mo': 30, '3mo': 90, 
                '6mo': 180, '1y': 365, '2y': 730
            }
            days = days_map.get(period, 30)
            start_date = end_date - timedelta(days=days)
            
            # Fetch data
            result = self.finnhub_client.stock_candles(
                clean_symbol, 'D', 
                int(start_date.timestamp()), 
                int(end_date.timestamp())
            )
            
            if result.get('s') != 'ok':
                return None
            
            # Convert to DataFrame
            data = pd.DataFrame({
                'Open': result['o'],
                'High': result['h'],
                'Low': result['l'],
                'Close': result['c'],
                'Volume': result['v']
            })
            
            # Add datetime index
            data.index = pd.to_datetime(result['t'], unit='s')
            data.index.name = 'Datetime'
            
            return data.sort_index()
            
        except Exception as e:
            logger.error(f"Finnhub error for {symbol}: {e}")
            return None
    
    def _add_basic_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add basic technical indicators to the data"""
        try:
            # Moving averages
            data['SMA_20'] = data['Close'].rolling(window=20).mean()
            data['SMA_50'] = data['Close'].rolling(window=50).mean()
            data['EMA_12'] = data['Close'].ewm(span=12).mean()
            data['EMA_26'] = data['Close'].ewm(span=26).mean()
            
            # RSI
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD
            data['MACD'] = data['EMA_12'] - data['EMA_26']
            data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
            data['MACD_Histogram'] = data['MACD'] - data['MACD_Signal']
            
            # Bollinger Bands
            data['BB_Middle'] = data['Close'].rolling(window=20).mean()
            bb_std = data['Close'].rolling(window=20).std()
            data['BB_Upper'] = data['BB_Middle'] + (bb_std * 2)
            data['BB_Lower'] = data['BB_Middle'] - (bb_std * 2)
            
            # Volume indicators
            data['Volume_SMA'] = data['Volume'].rolling(window=20).mean()
            data['Volume_Ratio'] = data['Volume'] / data['Volume_SMA']
            
            return data
            
        except Exception as e:
            logger.error(f"Error adding indicators: {e}")
            return data
    
    async def get_multiple_stocks_data(self, symbols: List[str], 
                                     period: str = "1d", 
                                     interval: str = "1d") -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple stocks concurrently
        """
        tasks = []
        for symbol in symbols:
            task = self.get_stock_data(symbol, period, interval)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        stock_data = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, pd.DataFrame) and not result.empty:
                stock_data[symbol] = result
            else:
                logger.warning(f"Failed to fetch data for {symbol}")
        
        return stock_data
    
    async def get_nifty_data(self, period: str = "1d", 
                           interval: str = "1d") -> Optional[pd.DataFrame]:
        """Get Nifty 50 index data"""
        return await self.get_stock_data("^NSEI", period, interval)
    
    async def get_sensex_data(self, period: str = "1d", 
                            interval: str = "1d") -> Optional[pd.DataFrame]:
        """Get Sensex index data"""
        return await self.get_stock_data("^BSESN", period, interval)
    
    async def get_nifty_constituents_data(self, period: str = "1d", 
                                        interval: str = "1d") -> Dict[str, pd.DataFrame]:
        """Get data for all Nifty 50 constituents"""
        return await self.get_multiple_stocks_data(self.nifty_50, period, interval)
    
    def get_available_symbols(self, exchange: str = "NSE") -> List[str]:
        """Get list of available symbols for an exchange"""
        if exchange.upper() == "NSE":
            return self.nse_symbols
        elif exchange.upper() == "NIFTY50":
            return self.nifty_50
        elif exchange.upper() == "NIFTY500":
            return self.nifty_500
        else:
            return []
    
    async def search_symbol(self, query: str, exchange: str = "NSE") -> List[str]:
        """Search for symbols matching the query"""
        symbols = self.get_available_symbols(exchange)
        query_upper = query.upper()
        
        # Simple text matching - in production, use fuzzy matching
        matches = [symbol for symbol in symbols 
                  if query_upper in symbol.upper()]
        
        return matches[:20]  # Limit results
    
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote for a symbol - Yahoo Finance (unlimited free)"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get current info and recent history for accurate data
            info = ticker.info
            hist = ticker.history(period="2d", interval="1d")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                change = current_price - prev_close
                change_percent = (change / prev_close * 100) if prev_close != 0 else 0
                
                # Get market cap
                market_cap = info.get("marketCap", 0)
                if not market_cap:
                    shares = info.get("sharesOutstanding", 0)
                    if shares and shares > 0:
                        market_cap = shares * current_price
                
                return {
                    "symbol": symbol,
                    "price": round(float(current_price), 2),
                    "change": round(float(change), 2),
                    "changePercent": round(float(change_percent), 2),
                    "volume": int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns and not pd.isna(hist['Volume'].iloc[-1]) else info.get("volume", 0),
                    "marketCap": int(market_cap) if market_cap else 0,
                    "high": round(float(hist['High'].iloc[-1]), 2),
                    "low": round(float(hist['Low'].iloc[-1]), 2),
                    "open": round(float(hist['Open'].iloc[-1]), 2),
                    "previousClose": round(float(prev_close), 2),
                    "timestamp": datetime.now().isoformat(),
                    "source": "yahoo_finance"
                }
            else:
                # Fallback to info only if no history available
                price = info.get("regularMarketPrice", info.get("currentPrice", 0))
                if price and price > 0:
                    return {
                        "symbol": symbol,
                        "price": round(float(price), 2),
                        "change": round(float(info.get("regularMarketChange", 0)), 2),
                        "changePercent": round(float(info.get("regularMarketChangePercent", 0)), 2),
                        "volume": int(info.get("regularMarketVolume", info.get("volume", 0))),
                        "marketCap": int(info.get("marketCap", 0)),
                        "high": round(float(info.get("dayHigh", 0)), 2),
                        "low": round(float(info.get("dayLow", 0)), 2),
                        "open": round(float(info.get("regularMarketOpen", 0)), 2),
                        "previousClose": round(float(info.get("regularMarketPreviousClose", 0)), 2),
                        "timestamp": datetime.now().isoformat(),
                        "source": "yahoo_finance_info"
                    }
                    
            logger.warning(f"No valid data available for {symbol}")
            return None
                
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            return None

    def _get_sector_stocks(self) -> Dict[str, List[str]]:
        """Get 50 stocks for each major sector"""
        return {
            "Technology": [
                # US Tech Giants
                "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "TSLA", "NVDA", "NFLX", "ADBE",
                "CRM", "ORCL", "INTC", "CSCO", "IBM", "QCOM", "AMD", "AVGO", "TXN", "MU",
                "AMAT", "LRCX", "KLAC", "MCHP", "ADI", "MRVL", "SWKS", "XLNX", "SNPS", "CDNS",
                "FTNT", "PANW", "CRWD", "ZS", "OKTA", "DDOG", "NET", "SNOW", "PLTR", "U",
                # Indian Tech
                "TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS", "LTI.NS", "MINDTREE.NS", "MPHASIS.NS", "LTTS.NS", "COFORGE.NS"
            ],
            "Healthcare": [
                # US Healthcare & Pharma
                "JNJ", "PFE", "UNH", "ABBV", "MRK", "TMO", "DHR", "ABT", "BMY", "AMGN",
                "GILD", "CVS", "MDT", "SYK", "BDX", "ISRG", "REGN", "VRTX", "BIIB", "ILMN",
                "MRNA", "JCI", "EW", "ALGN", "DXCM", "VEEV", "IQVIA", "CTLT", "VAR", "TECH",
                "GEHC", "EXR", "HOLX", "PODD", "TDOC", "PINS", "ZBH", "BAX", "BSX", "ANTM",
                # Indian Healthcare
                "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "AUROPHARMA.NS", "LUPIN.NS", "BIOCON.NS", "TORNTPHARM.NS", "ALKEM.NS", "CADILAHC.NS", "GLENMARK.NS"
            ],
            "Finance": [
                # US Financial Services
                "JPM", "BAC", "WFC", "GS", "MS", "C", "AXP", "USB", "PNC", "TFC",
                "COF", "SCHW", "BLK", "SPGI", "CME", "ICE", "MCO", "MSCI", "TROW", "BEN",
                "STT", "NTRS", "RF", "CFG", "KEY", "FITB", "HBAN", "ZION", "CMA", "PBCT",
                "V", "MA", "PYPL", "SQ", "AFRM", "UPST", "LC", "SOFI", "NU", "HOOD",
                # Indian Financial Services  
                "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS", "INDUSINDBK.NS", "FEDERALBNK.NS", "BANDHANBNK.NS", "RBLBANK.NS", "YESBANK.NS"
            ],
            "Energy": [
                # US Energy
                "XOM", "CVX", "COP", "EOG", "SLB", "PSX", "VLO", "MPC", "KMI", "OKE",
                "EPD", "ET", "WMB", "TRGP", "LNG", "FANG", "DVN", "PXD", "CTRA", "MRO",
                "APA", "HAL", "BKR", "NOV", "RIG", "VAL", "FTI", "OII", "PTEN", "CLR",
                "SM", "DINO", "DK", "CDEV", "AR", "WLL", "MTDR", "FANG", "VNOM", "RRC",
                # Indian Energy
                "ONGC.NS", "RELIANCE.NS", "IOC.NS", "BPCL.NS", "HPCL.NS", "GAIL.NS", "OIL.NS", "MRPL.NS", "PETRONET.NS", "IGL.NS"
            ],
            "Consumer": [
                # US Consumer Goods & Retail
                "AMZN", "TSLA", "HD", "WMT", "PG", "KO", "PEP", "MCD", "SBUX", "NKE",
                "COST", "TGT", "LOW", "TJX", "BKNG", "ABNB", "UBER", "DIS", "NFLX", "CMCSA",
                "VZ", "T", "CL", "KMB", "CHD", "CLX", "SJM", "CPB", "GIS", "K",
                "HSY", "MDLZ", "MNST", "KDP", "STZ", "BF.B", "PM", "MO", "BTI", "UL",
                # Indian Consumer
                "HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "MARICO.NS", "DABUR.NS", "GODREJCP.NS", "COLPAL.NS", "UBL.NS", "PGHH.NS"
            ],
            "Industrial": [
                # US Industrial
                "GE", "CAT", "BA", "MMM", "HON", "UPS", "RTX", "LMT", "NOC", "GD",
                "FDX", "UNP", "CSX", "NSC", "KSU", "CP", "CNI", "TRN", "JBHT", "CHRW",
                "GWW", "MSI", "EMR", "ETN", "PH", "CMI", "FTV", "AME", "ROP", "ITW",
                "IR", "DOV", "XYL", "FLS", "PNR", "SWK", "TXT", "ROK", "FAST", "PWR",
                # Indian Industrial  
                "LT.NS", "BHARTIARTL.NS", "M&M.NS", "TATAMOTORS.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS", "HEROMOTOCO.NS", "MARUTI.NS", "ASHOKLEY.NS", "TVSMOTOR.NS"
            ]
        }

    async def get_trending_stocks(self) -> Dict[str, Any]:
        """Get trending stocks data with sector diversity"""
        try:
            sector_stocks = self._get_sector_stocks()
            trending_stocks = []
            
            # Get top stocks from each sector
            for sector, symbols in sector_stocks.items():
                sector_trending = []
                
                # Get data for top 10 stocks from each sector
                for symbol in symbols[:10]:
                    try:
                        quote = await self.get_quote(symbol)
                        if quote:
                            # Get additional data
                            ticker = yf.Ticker(symbol)
                            info = ticker.info
                            stock_data = {
                                "symbol": symbol,
                                "name": info.get("longName", symbol),
                                "current_price": quote["price"],
                                "change": quote["change"],
                                "change_percent": quote["changePercent"],
                                "volume": quote["volume"],
                                "market_cap": quote["marketCap"],
                                "sector": sector,
                                "industry": info.get("industry", "Unknown"),
                                "pe_ratio": info.get("trailingPE", None),
                                "day_high": info.get("dayHigh", None),
                                "day_low": info.get("dayLow", None),
                                "52_week_high": info.get("fiftyTwoWeekHigh", None),
                                "52_week_low": info.get("fiftyTwoWeekLow", None),
                                "avg_volume": info.get("averageVolume", None),
                                "dividend_yield": info.get("dividendYield", None),
                                "beta": info.get("beta", None)
                            }
                            sector_trending.append(stock_data)
                    except Exception as e:
                        logger.error(f"Error processing {symbol}: {e}")
                        continue
            
                # Add best performing stocks from this sector
                if sector_trending:
                    # Sort by volume and change percent for trending
                    sector_trending.sort(key=lambda x: (x.get("volume", 0) * abs(x.get("change_percent", 0))), reverse=True)
                    trending_stocks.extend(sector_trending[:8])  # Top 8 from each sector
            
            # Sort overall by trending score (volume * abs(change%))
            trending_stocks.sort(key=lambda x: (x.get("volume", 0) * abs(x.get("change_percent", 0))), reverse=True)
            
            return {
                "trending_stocks": trending_stocks[:50],  # Top 50 overall
                "sector_breakdown": {
                    sector: [s for s in trending_stocks if s.get("sector") == sector][:10] 
                    for sector in sector_stocks.keys()
                },
                "total_sectors": len(sector_stocks),
                "stocks_per_sector": 50,
                "timestamp": datetime.now().isoformat(),
                "source": "yahoo_finance_with_alpha_vantage_fallback",
                "count": len(trending_stocks[:50])
            }
            
        except Exception as e:
            logger.error(f"Error getting trending stocks: {e}")
            return {
                "trending_stocks": [],
                "sector_breakdown": {},
                "timestamp": datetime.now().isoformat(),
                "source": "error",
                "error": str(e)
            }

    async def get_historical_data(self, symbol: str, period: str = "1y") -> Optional[Dict[str, Any]]:
        """Get historical data for a symbol"""
        try:
            data = await self.get_stock_data(symbol, period, "1d")
            if data is not None and not data.empty:
                return {
                    "symbol": symbol,
                    "period": period,
                    "data": data.to_dict("records"),
                    "count": len(data),
                    "latest_close": float(data["Close"].iloc[-1]) if len(data) > 0 else None,
                    "timestamp": datetime.now().isoformat()
                }
            return None
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return None 