"""
Analytics Integration Module
============================

This package provides advanced analytics functionality for the Financial Analytics Hub.
Delivers comprehensive stock screening, technical analysis, and AI-powered predictions.

Main Features:
- Stock screening with 30+ strategies
- Technical analysis indicators
- AI-powered market predictions
- Real-time data processing
- Pattern recognition
- Risk analysis
"""

__version__ = "1.0.0"
__author__ = "Financial Analytics Hub"

# Core imports
from .data_fetcher import MarketDataFetcher
from .screener import StockScreener
from .technical_analysis import TechnicalAnalyzer
from .ai_predictor import AIPredictor
from .pattern_scanner import PatternScanner

__all__ = [
    'MarketDataFetcher',
    'StockScreener', 
    'TechnicalAnalyzer',
    'AIPredictor',
    'PatternScanner'
] 