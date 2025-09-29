"""
Crypto Provider Adapters Package

This package contains adapters for various crypto data providers,
implementing a standard interface for data fetching and normalization.
"""

from .base_crypto_provider import BaseCryptoProvider
from .coinbase_provider import CoinbaseProvider
from .binance_provider import BinanceProvider
from .kraken_provider import KrakenProvider
from .coingecko_provider import CoinGeckoProvider
from .generic_crypto_provider import GenericCryptoProvider

__all__ = [
    'BaseCryptoProvider',
    'CoinbaseProvider', 
    'BinanceProvider',
    'KrakenProvider',
    'CoinGeckoProvider',
    'GenericCryptoProvider'
] 