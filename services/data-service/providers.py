"""
Data providers for external API integration.
"""

import asyncio
import httpx
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import logging
import os
import json
import time
import random
from datetime import datetime

from common.http_client import HTTPClient
from common.logging import log_structured_error
from common.errors import (
    ServiceError, ExternalAPIError, ExternalAPITimeoutError, 
    ExternalAPIRateLimitError, BadGatewayError, ServiceUnavailableError,
    UnauthorizedError, ForbiddenError, wrap_external_api_error
)

logger = logging.getLogger(__name__)

# Legacy APIError class removed - use unified error taxonomy from common.errors instead

class DataProvider(ABC):
    """Base data provider interface."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is healthy."""
        pass

class CryptoDataProvider(DataProvider):
    """Crypto data provider using CoinGecko and Binance."""
    
    def __init__(self, coingecko_url: str, binance_url: str, rate_limits: Dict[str, int]):
        super().__init__()
        self.coingecko_url = coingecko_url
        self.binance_url = binance_url
        self.rate_limits = rate_limits
    
    async def health_check(self) -> bool:
        """Check CoinGecko API health."""
        try:
            response = await self.client.get(f"{self.coingecko_url}/ping")
            return response.status_code == 200
        except:
            return False
    
    async def get_prices(self, symbols: List[str], vs_currency: str = "usd") -> Dict[str, Any]:
        """Get current crypto prices."""
        ids = ",".join(symbols)
        url = f"{self.coingecko_url}/simple/price"
        params = {"ids": ids, "vs_currencies": vs_currency, "include_24hr_change": "true"}
        
        try:
            response = await self.client.get(url, params=params)
            
            if response.status_code >= 400:
                response.raise_for_status()
                
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise wrap_external_api_error(e, "CoinGecko", {"method": "get_prices", "symbols": symbols})
        except httpx.TimeoutException as e:
            raise ExternalAPITimeoutError("CoinGecko API timeout", api_provider="CoinGecko")
        except httpx.ConnectError as e:
            raise ServiceUnavailableError("CoinGecko API connection failed", 
                                        context={"api_provider": "CoinGecko"})
        except json.JSONDecodeError as e:
            raise BadGatewayError("CoinGecko API returned invalid JSON", 
                                context={"api_provider": "CoinGecko"})
    
    async def get_crypto_details(self, symbol: str) -> Dict[str, Any]:
        """Get detailed crypto information."""
        url = f"{self.coingecko_url}/coins/{symbol}"
        
        try:
            response = await self.client.get(url)
            
            if response.status_code >= 400:
                response.raise_for_status()
                
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise wrap_external_api_error(e, "CoinGecko", {"method": "get_crypto_details", "symbol": symbol})
        except httpx.TimeoutException as e:
            raise ExternalAPITimeoutError("CoinGecko API timeout", api_provider="CoinGecko")
        except httpx.ConnectError as e:
            raise ServiceUnavailableError("CoinGecko API connection failed", 
                                        context={"api_provider": "CoinGecko"})
        except json.JSONDecodeError as e:
            raise BadGatewayError("CoinGecko API returned invalid JSON", 
                                context={"api_provider": "CoinGecko"})
    
    async def get_price_history(self, symbol: str, days: int, interval: str = "daily") -> List[Dict[str, Any]]:
        """Get crypto price history with price and volume merged.

        Transforms CoinGecko market_chart data into a list of objects with the
        structure expected by the frontend:
            {
                "timestamp": str,  # original UNIX ms timestamp
                "price": float,
                "volume": float,
                "date": str       # human readable %Y-%m-%d
            }
        """
        url = f"{self.coingecko_url}/coins/{symbol}/market_chart"
        params = {"vs_currency": "usd", "days": days, "interval": interval}
        
        try:
            response = await self.client.get(url, params=params)
            
            if response.status_code >= 400:
                response.raise_for_status()
            
            data = response.json()
            prices: List[List[float]] = data.get("prices", [])
            volumes: List[List[float]] = data.get("total_volumes", data.get("volumes", []))
            
            # If volumes length mismatched, create placeholder zeros
            if len(volumes) != len(prices):
                volume_dict = {v[0]: v[1] for v in volumes}
                merged: List[Dict[str, Any]] = []
                for ts, price in prices:
                    volume = volume_dict.get(ts, 0.0)
                    merged.append({
                        "timestamp": str(ts),
                        "price": price,
                        "volume": volume,
                        "date": datetime.utcfromtimestamp(ts / 1000).strftime("%Y-%m-%d")
                    })
            else:
                merged = [
                    {
                        "timestamp": str(price_item[0]),
                        "price": price_item[1],
                        "volume": volumes[idx][1] if idx < len(volumes) else 0.0,
                        "date": datetime.utcfromtimestamp(price_item[0] / 1000).strftime("%Y-%m-%d"),
                    }
                    for idx, price_item in enumerate(prices)
                ]
            
            return merged
            
        except httpx.HTTPStatusError as e:
            raise wrap_external_api_error(e, "CoinGecko", {"method": "get_price_history", "symbol": symbol})
        except httpx.TimeoutException:
            raise ExternalAPITimeoutError("CoinGecko API timeout", api_provider="CoinGecko")
        except httpx.ConnectError:
            raise ServiceUnavailableError("CoinGecko API connection failed", context={"api_provider": "CoinGecko"})
        except json.JSONDecodeError:
            raise BadGatewayError("CoinGecko API returned invalid JSON", context={"api_provider": "CoinGecko"})
    
    async def get_top_cryptocurrencies(self, limit: int = 100, vs_currency: str = "usd") -> List[Dict[str, Any]]:
        """Get top cryptocurrencies by market cap."""
        url = f"{self.coingecko_url}/coins/markets"
        params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1,
            "sparkline": "false"
        }
        
        try:
            response = await self.client.get(url, params=params)
            
            if response.status_code >= 400:
                response.raise_for_status()
                
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise wrap_external_api_error(e, "CoinGecko", {"method": "get_top_cryptocurrencies", "limit": limit})
        except httpx.TimeoutException as e:
            raise ExternalAPITimeoutError("CoinGecko API timeout", api_provider="CoinGecko")
        except httpx.ConnectError as e:
            raise ServiceUnavailableError("CoinGecko API connection failed", 
                                        context={"api_provider": "CoinGecko"})
        except json.JSONDecodeError as e:
            raise BadGatewayError("CoinGecko API returned invalid JSON", 
                                context={"api_provider": "CoinGecko"})
    
    async def get_trending_crypto(self) -> Dict[str, Any]:
        """Get trending cryptocurrencies."""
        url = f"{self.coingecko_url}/search/trending"
        
        try:
            response = await self.client.get(url)
            
            if response.status_code >= 400:
                response.raise_for_status()
                
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise wrap_external_api_error(e, "CoinGecko", {"method": "get_trending_crypto"})
        except httpx.TimeoutException as e:
            raise ExternalAPITimeoutError("CoinGecko API timeout", api_provider="CoinGecko")
        except httpx.ConnectError as e:
            raise ServiceUnavailableError("CoinGecko API connection failed", 
                                        context={"api_provider": "CoinGecko"})
        except json.JSONDecodeError as e:
            raise BadGatewayError("CoinGecko API returned invalid JSON", 
                                context={"api_provider": "CoinGecko"})
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """Get crypto market overview."""
        url = f"{self.coingecko_url}/global"
        
        try:
            response = await self.client.get(url)
            
            if response.status_code >= 400:
                response.raise_for_status()
                
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise wrap_external_api_error(e, "CoinGecko", {"method": "get_market_overview"})
        except httpx.TimeoutException as e:
            raise ExternalAPITimeoutError("CoinGecko API timeout", api_provider="CoinGecko")
        except httpx.ConnectError as e:
            raise ServiceUnavailableError("CoinGecko API connection failed", 
                                        context={"api_provider": "CoinGecko"})
        except json.JSONDecodeError as e:
            raise BadGatewayError("CoinGecko API returned invalid JSON", 
                                context={"api_provider": "CoinGecko"})
    
    async def get_fear_greed_index(self) -> Dict[str, Any]:
        """Get Fear & Greed Index."""
        # Using alternative.me API for Fear & Greed Index
        url = "https://api.alternative.me/fng/"
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except:
            return {"data": [{"value": "50", "value_classification": "Neutral"}]}

class StockDataProvider(DataProvider):
    """Stock data provider using Yahoo Finance and Alpha Vantage."""
    
    def __init__(self, yahoo_url: str, alpha_vantage_key: Optional[str], 
                 polygon_key: Optional[str], finnhub_key: Optional[str]):
        super().__init__()
        self.yahoo_url = yahoo_url
        self.alpha_vantage_key = alpha_vantage_key
        self.polygon_key = polygon_key
        self.finnhub_key = finnhub_key
    
    async def health_check(self) -> bool:
        """Check Yahoo Finance API health."""
        try:
            response = await self.client.get(f"{self.yahoo_url}/v8/finance/chart/AAPL")
            return response.status_code == 200
        except:
            return False
    
    async def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Get current stock data."""
        url = f"{self.yahoo_url}/v8/finance/chart/{symbol}"
        yahoo_error = None
        alpha_error = None
        
        try:
            response = await self.client.get(url)
            
            if response.status_code >= 400:
                response.raise_for_status()
                
            return response.json()
            
        except httpx.HTTPStatusError as e:
            yahoo_error = wrap_external_api_error(e, "Yahoo Finance", {"method": "get_stock_data", "symbol": symbol})
        except httpx.TimeoutException as e:
            yahoo_error = ExternalAPITimeoutError("Yahoo Finance API timeout", api_provider="Yahoo Finance")
        except httpx.ConnectError as e:
            yahoo_error = ServiceUnavailableError("Yahoo Finance API connection failed", 
                                                 context={"api_provider": "Yahoo Finance"})
        except json.JSONDecodeError as e:
            yahoo_error = BadGatewayError("Yahoo Finance API returned invalid JSON", 
                                        context={"api_provider": "Yahoo Finance"})
        except Exception as e:
            yahoo_error = wrap_external_api_error(e, "Yahoo Finance", {"method": "get_stock_data", "symbol": symbol})
        
        # Fallback to Alpha Vantage if available
        if self.alpha_vantage_key and yahoo_error:
            logger.warning(f"Yahoo Finance failed for {symbol}: {yahoo_error}, trying Alpha Vantage")
            try:
                return await self._get_alpha_vantage_quote(symbol)
            except Exception as e:
                alpha_error = wrap_external_api_error(e, "Alpha Vantage", {"method": "get_stock_data", "symbol": symbol})
                logger.error(f"Both Yahoo Finance and Alpha Vantage failed for {symbol}")
                
                # Raise aggregated error information
                raise ServiceUnavailableError(
                    f"All stock data providers failed for {symbol}",
                    context={
                        "symbol": symbol,
                        "yahoo_error": str(yahoo_error),
                        "alpha_vantage_error": str(alpha_error)
                    }
                )
        
        # If no fallback available, raise the original Yahoo error
        if yahoo_error:
            raise yahoo_error
    
    async def _get_alpha_vantage_quote(self, symbol: str) -> Dict[str, Any]:
        """Get stock quote from Alpha Vantage."""
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.alpha_vantage_key
        }
        
        try:
            response = await self.client.get(url, params=params)
            
            if response.status_code >= 400:
                response.raise_for_status()
                
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise wrap_external_api_error(e, "Alpha Vantage", {"method": "_get_alpha_vantage_quote", "symbol": symbol})
        except httpx.TimeoutException as e:
            raise ExternalAPITimeoutError("Alpha Vantage API timeout", api_provider="Alpha Vantage")
        except httpx.ConnectError as e:
            raise ServiceUnavailableError("Alpha Vantage API connection failed", 
                                        context={"api_provider": "Alpha Vantage"})
        except json.JSONDecodeError as e:
            raise BadGatewayError("Alpha Vantage API returned invalid JSON", 
                                context={"api_provider": "Alpha Vantage"})
    
    async def get_stock_history(self, symbol: str, period: str = "1y", interval: str = "1d") -> Dict[str, Any]:
        """Get stock price history."""
        url = f"{self.yahoo_url}/v8/finance/chart/{symbol}"
        params = {"range": period, "interval": interval}
        
        try:
            response = await self.client.get(url, params=params)
            
            if response.status_code >= 400:
                response.raise_for_status()
                
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise wrap_external_api_error(e, "Yahoo Finance", {"method": "get_stock_history", "symbol": symbol})
        except httpx.TimeoutException as e:
            raise ExternalAPITimeoutError("Yahoo Finance API timeout", api_provider="Yahoo Finance")
        except httpx.ConnectError as e:
            raise ServiceUnavailableError("Yahoo Finance API connection failed", 
                                        context={"api_provider": "Yahoo Finance"})
        except json.JSONDecodeError as e:
            raise BadGatewayError("Yahoo Finance API returned invalid JSON", 
                                context={"api_provider": "Yahoo Finance"})
    
    async def get_market_indices(self) -> Dict[str, Any]:
        """Get major market indices."""
        indices = ["^GSPC", "^DJI", "^IXIC"]  # S&P 500, Dow Jones, NASDAQ
        tasks = [self.get_stock_data(index) for index in indices]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        indices_data = {}
        for i, result in enumerate(results):
            if not isinstance(result, Exception):
                indices_data[indices[i]] = result
        
        return indices_data

class ForexDataProvider(DataProvider):
    """Forex data provider using Alpha Vantage."""
    
    def __init__(self, alpha_vantage_key: Optional[str]):
        super().__init__()
        self.alpha_vantage_key = alpha_vantage_key
    
    async def health_check(self) -> bool:
        """Check Alpha Vantage API health."""
        if not self.alpha_vantage_key:
            return False
        try:
            url = "https://www.alphavantage.co/query"
            params = {"function": "CURRENCY_EXCHANGE_RATE", "from_currency": "USD", 
                     "to_currency": "EUR", "apikey": self.alpha_vantage_key}
            response = await self.client.get(url, params=params)
            return response.status_code == 200
        except:
            return False
    
    async def get_exchange_rates(self, base: str, targets: List[str]) -> Dict[str, Any]:
        """Get exchange rates."""
        if not self.alpha_vantage_key:
            raise Exception("Alpha Vantage API key not configured")
        
        tasks = []
        for target in targets:
            tasks.append(self._get_exchange_rate(base, target))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        rates = {}
        for i, result in enumerate(results):
            if not isinstance(result, Exception):
                rates[f"{base}{targets[i]}"] = result
        
        return rates
    
    async def _get_exchange_rate(self, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """Get single exchange rate."""
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": from_currency,
            "to_currency": to_currency,
            "apikey": self.alpha_vantage_key
        }
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    async def get_major_pairs(self) -> Dict[str, Any]:
        """Get major forex pairs."""
        major_pairs = [("USD", "EUR"), ("USD", "GBP"), ("USD", "JPY"), ("EUR", "GBP")]
        tasks = [self._get_exchange_rate(base, target) for base, target in major_pairs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        pairs_data = {}
        for i, result in enumerate(results):
            if not isinstance(result, Exception):
                base, target = major_pairs[i]
                pairs_data[f"{base}{target}"] = result
        
        return pairs_data 