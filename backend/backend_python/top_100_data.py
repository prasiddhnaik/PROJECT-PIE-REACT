"""
Top 100 Financial Assets Data Provider
Provides comprehensive market data for top 100 assets across stocks, crypto, and forex
"""

import asyncio
import aiohttp
import yfinance as yf
import requests
from pycoingecko import CoinGeckoAPI
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class Top100DataProvider:
    def __init__(self):
        self.cg = CoinGeckoAPI()
        
        # Top 50 Stock Symbols per Sector - Comprehensive Coverage
        self.stocks_by_sector = {
            # 🏥 Healthcare & Medical (50 stocks)
            "healthcare": [
                "JNJ", "UNH", "PFE", "ABT", "TMO", "MRK", "ABBV", "LLY", "DHR", "BMY",
                "AMGN", "GILD", "VRTX", "REGN", "BIIB", "CVS", "CI", "HUM", "ANTM", "CNC",
                "MDT", "SYK", "BSX", "EW", "ZBH", "BDX", "BAX", "ISRG", "DXCM", "IQV",
                "A", "RMD", "IDXX", "MTD", "HOLX", "WAT", "PKI", "TFX", "TECH", "ALGN",
                "MRNA", "ZTS", "ILMN", "INCY", "BMRN", "ALNY", "SGEN", "EXAS", "HALO", "VEEV"
            ],
            
            # 💻 Technology (50 stocks)
            "technology": [
                "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "NFLX", "ADBE", "CRM", "ORCL", 
                "AMD", "INTC", "CSCO", "AVGO", "TXN", "QCOM", "NOW", "INTU", "IBM", "AMAT", 
                "LRCX", "KLAC", "CDNS", "SNPS", "MCHP", "ADI", "MU", "NXPI", "MRVL", "FTNT", 
                "PANW", "CRWD", "ZS", "OKTA", "DDOG", "NET", "SNOW", "PLTR", "U", "TWLO", 
                "ZM", "DOCU", "TEAM", "SHOP", "PYPL", "ROKU", "UBER", "LYFT", "DASH", "ABNB"
            ],
            
            # 🏦 Financial Services (50 stocks)
            "financial": [
                "BRK-B", "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "C", "USB",
                "PNC", "TFC", "COF", "AXP", "BLK", "SCHW", "CB", "MMC", "AON", "AJG",
                "SPGI", "MCO", "ICE", "CME", "NDAQ", "MSCI", "TRV", "ALL", "PGR", "AIG",
                "MET", "PRU", "AFL", "AMP", "LNC", "PFG", "TMK", "RJF", "NTRS", "STT",
                "BK", "TROW", "BEN", "IVZ", "AMG", "EVRG", "FNF", "FAF", "CINF", "WRB"
            ],
            
            # 🏭 Industrial & Manufacturing (50 stocks)
            "industrial": [
                "HON", "UNP", "CAT", "RTX", "LMT", "GE", "MMM", "BA", "DE", "EMR",
                "ITW", "ETN", "PH", "CMI", "ROK", "DOV", "FTV", "XYL", "AME", "ROP",
                "IEX", "FAST", "PAYX", "CTAS", "RSG", "WM", "WCN", "VRSK", "EXPD", "CHRW",
                "FDX", "UPS", "NSC", "CSX", "KSU", "ODFL", "JBHT", "SAIA", "ARCB", "LSTR",
                "GWW", "MSM", "WWD", "POOL", "WSO", "SWK", "TT", "IR", "OTIS", "CARR"
            ],
            
            # 🛒 Consumer Goods & Retail (50 stocks)
            "consumer": [
                "WMT", "HD", "PG", "COST", "NKE", "SBUX", "MCD", "TGT", "LOW", "DIS", 
                "CL", "KMB", "CHD", "CLX", "EL", "UL", "NSRGY", "DEO", "BUD", "TAP", 
                "STZ", "FIZZ", "COKE", "YUM", "QSR", "DPZ", "CMG", "TXRH", "DINE", "EAT", 
                "CAKE", "RUTH", "TJX", "ROST", "DLTR", "DG", "BBY", "GPS", "ANF", "AEO",
                "LULU", "DECK", "CROX", "SKX", "VFC", "HBI", "PVH", "RL", "CPRI", "TPG"
            ],
            
            # ⚡ Energy & Utilities (50 stocks)
            "energy": [
                "CVX", "XOM", "COP", "EOG", "SLB", "NEE", "DUK", "SO", "D", "EXC",
                "AEP", "SRE", "PEG", "XEL", "ED", "ES", "FE", "ETR", "WEC", "DTE",
                "PPL", "AEE", "LNT", "NI", "PNW", "AVA", "AGR", "ALE", "ATO", "AWK",
                "PSX", "VLO", "MPC", "HFC", "TSO", "WMB", "KMI", "OKE", "EPD", "ET",
                "MPLX", "PAA", "EQT", "AR", "DVN", "FANG", "MRO", "APA", "OXY", "HAL"
            ],
            
            # 🏠 Real Estate & REITs (50 stocks)
            "real_estate": [
                "AMT", "PLD", "CCI", "EQIX", "PSA", "WELL", "DLR", "O", "SBAC", "EXR",
                "AVB", "EQR", "VTR", "ESS", "MAA", "UDR", "CPT", "FRT", "REG", "KIM",
                "SPG", "MAC", "PEI", "TCO", "WPG", "CBL", "SKT", "ROIC", "AKR", "BRX",
                "HST", "RHP", "PK", "SHO", "RLJ", "APLE", "INN", "DRH", "CLDT", "BHR",
                "ARE", "QTS", "CONE", "FR", "EXP", "JBGS", "BXP", "VNO", "SLG", "HIW"
            ],
            
            # 🚗 Automotive & Transportation (50 stocks)
            "automotive": [
                "TSLA", "F", "GM", "RIVN", "LCID", "NIO", "XPEV", "LI", "NKLA", "RIDE",
                "GOEV", "FSR", "HYLN", "WKHS", "BLNK", "CHPT", "EVGO", "PLUG", "FCEL", "BE",
                "FDX", "UPS", "CHRW", "EXPD", "JBHT", "KNX", "LSTR", "SAIA", "ODFL", "ARCB",
                "XPO", "GXO", "JBLU", "DAL", "UAL", "AAL", "LUV", "ALK", "SAVE", "HA",
                "CAR", "HTZ", "AVIS", "ZIP", "UBER", "LYFT", "DASH", "GRUB", "ABNB", "EXPE"
            ],
            
            # 🌐 International & Emerging Markets (50 stocks)
            "international": [
                "TSM", "ASML", "SAP", "NVO", "BABA", "PDD", "JD", "NTES", "BIDU", "NESN",
                "RHHBY", "TM", "HMC", "SNY", "GSK", "AZN", "BP", "RDS-A", "VOD", "BT", 
                "TEF", "VIV", "ORAN", "TI", "SAN", "BBVA", "BCS", "ING", "DB", "CS", 
                "UBS", "MUFG", "SMFG", "KB", "SHG", "LYG", "RBS", "BARC", "WIT", "GOLD", 
                "NEM", "ABX", "AEM", "KGC", "AU", "EGO", "HMY", "PAAS", "SE", "GRAB"
            ],
            
            # 🎮 Media & Entertainment (50 stocks)
            "media": [
                "DIS", "NFLX", "CMCSA", "T", "VZ", "CHTR", "TMUS", "DISH", "SIRI", "FOXA",
                "PARA", "WBD", "SONY", "EA", "ATVI", "TTWO", "RBLX", "U", "ZNGA", "GLUU",
                "MTCH", "BMBL", "SNAP", "TWTR", "PINS", "SPOT", "ROKU", "FUBO", "PLBY", "GOGO",
                "AMC", "CNK", "IMAX", "MCFE", "RGC", "YELP", "GRPN", "ANGI", "CARS", "QNST",
                "NYT", "GANNETT", "MDP", "NWSA", "SCHL", "CHGG", "STRA", "LNDC", "EDU", "TAL"
            ],
            
            # 🍔 Food & Beverage (50 stocks)
            "food": [
                "KO", "PEP", "MDLZ", "GIS", "K", "CPB", "CAG", "HSY", "TSN", "HRL",
                "SJM", "MKC", "KHC", "MNST", "DPS", "KDP", "CCEP", "FEMSA", "MCD", "YUM", 
                "QSR", "DPZ", "CMG", "SBUX", "DNKN", "PNRA", "DINE", "EAT", "CAKE", "RUTH", 
                "BLMN", "BWLD", "FRGI", "HABT", "JACK", "PZZA", "SONO", "SHAK", "NDLS", "RRGB", 
                "BJRI", "CBRL", "DRI", "PLAY", "PLNT", "WEN", "SONIC", "DAVE", "BROS", "CAVA"
            ]
        }
        
        # Flatten all sectors into top 100 list
        self.top_100_stocks = []
        for sector_stocks in self.stocks_by_sector.values():
            self.top_100_stocks.extend(sector_stocks)
        
        # Top 100 Crypto (will be fetched dynamically from CoinGecko)
        self.top_100_crypto = []
        
        # Top 100 Forex Pairs (Major, Minor, and Exotic)
        self.top_100_forex = [
            # Major Pairs (8 most traded)
            "EURUSD=X", "USDJPY=X", "GBPUSD=X", "USDCHF=X", "AUDUSD=X", "USDCAD=X", "NZDUSD=X",
            
            # Minor/Cross Pairs (No USD)
            "EURGBP=X", "EURJPY=X", "EURCHF=X", "EURAUD=X", "EURCAD=X", "EURNZD=X",
            "GBPJPY=X", "GBPCHF=X", "GBPAUD=X", "GBPCAD=X", "GBPNZD=X",
            "AUDJPY=X", "AUDCHF=X", "AUDCAD=X", "AUDNZD=X",
            "NZDJPY=X", "NZDCHF=X", "NZDCAD=X",
            "CADJPY=X", "CADCHF=X", "CHFJPY=X",
            
            # Commodity Currencies
            "USDRUB=X", "USDBRL=X", "USDMXN=X", "USDZAR=X", "USDTRY=X", "USDINR=X",
            "USDKRW=X", "USDSGD=X", "USDHKD=X", "USDTHB=X", "USDPHP=X", "USDIDR=X",
            "USDMYR=X", "USDVND=X", "USDEGP=X", "USDNGN=X", "USDKES=X", "USDGHC=X",
            
            # European Emerging
            "USDPLN=X", "USDCZK=X", "USDHUF=X", "USDRON=X", "USDBGN=X", "USDHRK=X",
            "USDRSD=X", "USDMKD=X", "USDALL=X", "USDGEL=X", "USDAMD=X", "USDAZN=X",
            
            # Middle East & Africa
            "USDAED=X", "USDSAR=X", "USDQAR=X", "USDOMR=X", "USDBHD=X", "USDKWD=X",
            "USDIQD=X", "USDLBP=X", "USDJOD=X", "USDILS=X", "USDEGP=X", "USDMAD=X",
            
            # Asian Emerging
            "USDCNY=X", "USDTWD=X", "USDHKD=X", "USDSGD=X", "USDKRW=X", "USDJPY=X",
            "USDTHB=X", "USDPHP=X", "USDIDR=X", "USDMYR=X", "USDVND=X", "USDLAK=X",
            "USDMMK=X", "USDBDT=X", "USDLKR=X", "USDNPR=X", "USDBTC=X", "USDPKR=X"
        ]

    async def get_top_100_stocks_data(self) -> List[Dict[str, Any]]:
        """Get comprehensive data for top 100 stocks"""
        try:
            stocks_data = []
            
            # Process stocks in batches to avoid overwhelming APIs
            batch_size = 10
            for i in range(0, len(self.top_100_stocks), batch_size):
                batch = self.top_100_stocks[i:i + batch_size]
                
                # Create tasks for parallel processing
                tasks = [self._get_single_stock_data(symbol) for symbol in batch]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        logger.warning(f"Error fetching {batch[j]}: {result}")
                        continue
                    if result:
                        stocks_data.append(result)
                
                # Small delay between batches to respect rate limits
                await asyncio.sleep(0.5)
            
            # Sort by market cap
            stocks_data.sort(key=lambda x: x.get('market_cap', 0), reverse=True)
            
            return stocks_data[:100]  # Ensure we return exactly 100
            
        except Exception as e:
            logger.error(f"Error fetching top 100 stocks: {e}")
            return []

    async def _get_single_stock_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get data for a single stock"""
        try:
            await asyncio.sleep(0.1)  # Rate limiting
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1d", interval="1d")
            
            if hist.empty:
                return None
                
            current_price = hist['Close'].iloc[-1]
            volume = hist['Volume'].iloc[-1]
            
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'current_price': float(current_price),
                'volume': int(volume) if pd.notna(volume) else 0,
                'market_cap': info.get('marketCap', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'country': info.get('country', 'US'),
                'currency': info.get('currency', 'USD'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
                'price_change': float(current_price - hist['Open'].iloc[-1]) if len(hist) > 0 else 0,
                'price_change_percent': ((current_price - hist['Open'].iloc[-1]) / hist['Open'].iloc[-1] * 100) if len(hist) > 0 else 0,
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'asset_type': 'stock'
            }
            
        except Exception as e:
            logger.warning(f"Error fetching stock {symbol}: {e}")
            return None

    async def get_top_100_crypto_data(self) -> List[Dict[str, Any]]:
        """Get comprehensive data for top 100 cryptocurrencies"""
        try:
            # Get top 100 crypto by market cap from CoinGecko
            crypto_data = self.cg.get_coins_markets(
                vs_currency='usd',
                order='market_cap_desc',
                per_page=100,
                page=1,
                sparkline=False,
                price_change_percentage='1h,24h,7d'
            )
            
            formatted_data = []
            for coin in crypto_data:
                formatted_data.append({
                    'id': coin['id'],
                    'symbol': coin['symbol'].upper(),
                    'name': coin['name'],
                    'current_price': float(coin['current_price']) if coin['current_price'] else 0,
                    'market_cap': coin['market_cap'] or 0,
                    'market_cap_rank': coin['market_cap_rank'],
                    'volume_24h': coin['total_volume'] or 0,
                    'price_change_24h': coin['price_change_24h'] or 0,
                    'price_change_percent_24h': coin['price_change_percentage_24h'] or 0,
                    'price_change_percent_1h': coin.get('price_change_percentage_1h_in_currency') or 0,
                    'price_change_percent_7d': coin.get('price_change_percentage_7d_in_currency') or 0,
                    'circulating_supply': coin['circulating_supply'],
                    'total_supply': coin['total_supply'],
                    'max_supply': coin['max_supply'],
                    'ath': coin['ath'],
                    'ath_change_percentage': coin['ath_change_percentage'],
                    'ath_date': coin['ath_date'],
                    'atl': coin['atl'],
                    'atl_change_percentage': coin['atl_change_percentage'],
                    'atl_date': coin['atl_date'],
                    'last_updated': coin['last_updated'],
                    'asset_type': 'crypto'
                })
            
            return formatted_data
            
        except Exception as e:
            logger.error(f"Error fetching top 100 crypto: {e}")
            return []

    async def get_top_100_forex_data(self) -> List[Dict[str, Any]]:
        """Get comprehensive data for top 100 forex pairs"""
        try:
            forex_data = []
            
            # Process forex in batches
            batch_size = 10
            for i in range(0, len(self.top_100_forex), batch_size):
                batch = self.top_100_forex[i:i + batch_size]
                
                tasks = [self._get_single_forex_data(pair) for pair in batch]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        logger.warning(f"Error fetching {batch[j]}: {result}")
                        continue
                    if result:
                        forex_data.append(result)
                
                await asyncio.sleep(0.5)  # Rate limiting
            
            return forex_data
            
        except Exception as e:
            logger.error(f"Error fetching top 100 forex: {e}")
            return []

    async def _get_single_forex_data(self, pair: str) -> Optional[Dict[str, Any]]:
        """Get data for a single forex pair"""
        try:
            await asyncio.sleep(0.1)  # Rate limiting
            
            ticker = yf.Ticker(pair)
            hist = ticker.history(period="5d", interval="1d")
            info = ticker.info
            
            if hist.empty:
                return None
                
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            
            base_currency = pair.replace('=X', '')[:3]
            quote_currency = pair.replace('=X', '')[3:6]
            
            return {
                'symbol': pair,
                'name': f"{base_currency}/{quote_currency}",
                'base_currency': base_currency,
                'quote_currency': quote_currency,
                'current_price': float(current_price),
                'previous_close': float(prev_close),
                'price_change': float(current_price - prev_close),
                'price_change_percent': float((current_price - prev_close) / prev_close * 100) if prev_close != 0 else 0,
                'volume': int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns and pd.notna(hist['Volume'].iloc[-1]) else 0,
                'high_24h': float(hist['High'].iloc[-1]) if not hist.empty else 0,
                'low_24h': float(hist['Low'].iloc[-1]) if not hist.empty else 0,
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'asset_type': 'forex'
            }
            
        except Exception as e:
            logger.warning(f"Error fetching forex {pair}: {e}")
            return None

    async def get_stocks_by_sector(self, sector: str) -> List[Dict[str, Any]]:
        """Get stock data for a specific sector"""
        try:
            if sector not in self.stocks_by_sector:
                available_sectors = list(self.stocks_by_sector.keys())
                raise ValueError(f"Sector '{sector}' not found. Available sectors: {available_sectors}")
            
            sector_symbols = self.stocks_by_sector[sector]
            stocks_data = []
            
            # Process sector stocks in batches
            batch_size = 5
            for i in range(0, len(sector_symbols), batch_size):
                batch = sector_symbols[i:i + batch_size]
                
                tasks = [self._get_single_stock_data(symbol) for symbol in batch]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        logger.warning(f"Error fetching {batch[j]}: {result}")
                        continue
                    if result:
                        result['sector'] = sector  # Add sector info
                        stocks_data.append(result)
                
                await asyncio.sleep(0.3)  # Rate limiting
            
            # Sort by market cap
            stocks_data.sort(key=lambda x: x.get('market_cap', 0), reverse=True)
            
            return stocks_data
            
        except Exception as e:
            logger.error(f"Error fetching sector {sector} data: {e}")
            return []

    def get_available_sectors(self) -> Dict[str, List[str]]:
        """Get all available sectors and their descriptions"""
        sector_descriptions = {
            "healthcare": {
                "name": "Healthcare & Medical",
                "description": "Pharmaceutical companies, medical devices, healthcare services",
                "emoji": "🏥",
                "count": len(self.stocks_by_sector["healthcare"])
            },
            "technology": {
                "name": "Technology",
                "description": "Software, hardware, semiconductor, and tech services companies",
                "emoji": "💻",
                "count": len(self.stocks_by_sector["technology"])
            },
            "financial": {
                "name": "Financial Services",
                "description": "Banks, insurance, investment, and financial technology companies",
                "emoji": "🏦",
                "count": len(self.stocks_by_sector["financial"])
            },
            "industrial": {
                "name": "Industrial & Manufacturing",
                "description": "Manufacturing, aerospace, defense, and industrial equipment",
                "emoji": "🏭",
                "count": len(self.stocks_by_sector["industrial"])
            },
            "consumer": {
                "name": "Consumer Goods & Retail",
                "description": "Retail, consumer products, food & beverage, entertainment",
                "emoji": "🛒",
                "count": len(self.stocks_by_sector["consumer"])
            },
            "energy": {
                "name": "Energy & Utilities",
                "description": "Oil & gas, renewable energy, utilities, and energy services",
                "emoji": "⚡",
                "count": len(self.stocks_by_sector["energy"])
            },
            "real_estate": {
                "name": "Real Estate & REITs",
                "description": "Real estate investment trusts and property companies",
                "emoji": "🏠",
                "count": len(self.stocks_by_sector["real_estate"])
            },
            "automotive": {
                "name": "Automotive & Transportation",
                "description": "Auto manufacturers, EV companies, and transportation services",
                "emoji": "🚗",
                "count": len(self.stocks_by_sector["automotive"])
            },
            "international": {
                "name": "International & Emerging Markets",
                "description": "Major international companies and emerging market leaders",
                "emoji": "🌐",
                "count": len(self.stocks_by_sector["international"])
            }
        }
        
        return sector_descriptions

    async def get_comprehensive_top_100_data(self) -> Dict[str, Any]:
        """Get all top 100 data for stocks, crypto, and forex"""
        try:
            # Fetch all data in parallel
            stocks_task = self.get_top_100_stocks_data()
            crypto_task = self.get_top_100_crypto_data()
            forex_task = self.get_top_100_forex_data()
            
            stocks, crypto, forex = await asyncio.gather(
                stocks_task, crypto_task, forex_task,
                return_exceptions=True
            )
            
            # Handle any exceptions
            if isinstance(stocks, Exception):
                stocks = []
                logger.error(f"Stocks data error: {stocks}")
            if isinstance(crypto, Exception):
                crypto = []
                logger.error(f"Crypto data error: {crypto}")
            if isinstance(forex, Exception):
                forex = []
                logger.error(f"Forex data error: {forex}")
            
            return {
                'stocks': {
                    'data': stocks,
                    'count': len(stocks),
                    'total_market_cap': sum(stock.get('market_cap', 0) for stock in stocks)
                },
                'crypto': {
                    'data': crypto,
                    'count': len(crypto),
                    'total_market_cap': sum(coin.get('market_cap', 0) for coin in crypto)
                },
                'forex': {
                    'data': forex,
                    'count': len(forex)
                },
                'summary': {
                    'total_assets': len(stocks) + len(crypto) + len(forex),
                    'stocks_count': len(stocks),
                    'crypto_count': len(crypto),
                    'forex_count': len(forex),
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive data fetch: {e}")
            return {
                'stocks': {'data': [], 'count': 0, 'total_market_cap': 0},
                'crypto': {'data': [], 'count': 0, 'total_market_cap': 0},
                'forex': {'data': [], 'count': 0},
                'summary': {
                    'total_assets': 0,
                    'stocks_count': 0,
                    'crypto_count': 0,
                    'forex_count': 0,
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
            }

# Global instance
top_100_provider = Top100DataProvider() 