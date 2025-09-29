"""
Sentiment Analysis Endpoints - Multi-source sentiment aggregation
Supports news, social media, and technical sentiment analysis
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Query
import os
import aiohttp
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

# Sentiment API Router
sentiment_router = APIRouter(prefix="/api/market/sentiment", tags=["sentiment"])

@dataclass
class SentimentSource:
    name: str
    score: float  # -1 to 1
    confidence: float  # 0 to 1
    weight: float  # 0 to 1
    last_updated: datetime

class SentimentAggregator:
    """Aggregates sentiment from multiple sources with weighted scoring"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sources = {
            'cryptopanic': {
                'api_key': os.getenv('CRYPTOPANIC_API_KEY'),
                'base_url': 'https://cryptopanic.com/api/v1',
                'weight': 0.3
            },
            'newsapi': {
                'api_key': os.getenv('NEWSAPI_KEY'),
                'base_url': 'https://newsapi.org/v2',
                'weight': 0.25
            },
            'lunarcrush': {
                'api_key': os.getenv('LUNARCRUSH_API_KEY'),
                'base_url': 'https://api.lunarcrush.com/v2',
                'weight': 0.25
            },
            'fear_greed': {
                'api_key': None,  # Free API
                'base_url': 'https://api.alternative.me/fng',
                'weight': 0.2
            }
        }
    
    async def get_news_sentiment(self, symbols: List[str] = None, timeframe: str = '24h') -> float:
        """Get sentiment from crypto news sources"""
        try:
            # CryptoPanic News Sentiment
            cryptopanic_sentiment = await self._get_cryptopanic_sentiment(symbols, timeframe)
            
            # NewsAPI Sentiment
            newsapi_sentiment = await self._get_newsapi_sentiment(symbols, timeframe)
            
            # Weighted average
            sentiments = [s for s in [cryptopanic_sentiment, newsapi_sentiment] if s is not None]
            
            if not sentiments:
                return 0.0
            
            return sum(sentiments) / len(sentiments)
            
        except Exception as e:
            self.logger.error(f"Error getting news sentiment: {e}")
            return 0.0
    
    async def _get_cryptopanic_sentiment(self, symbols: List[str], timeframe: str) -> Optional[float]:
        """Get sentiment from CryptoPanic API"""
        try:
            api_key = self.sources['cryptopanic']['api_key']
            if not api_key:
                return None
                
            # Calculate time filter
            hours = {'1h': 1, '24h': 24, '7d': 168}.get(timeframe, 24)
            
            url = f"{self.sources['cryptopanic']['base_url']}/posts/"
            params = {
                'auth_token': api_key,
                'public': 'true',
                'kind': 'news',
                'filter': 'hot',
                'page': 1
            }
            
            if symbols:
                params['currencies'] = ','.join([s.upper() for s in symbols])
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        return None
                        
                    data = await response.json()
                    posts = data.get('results', [])
                    
                    # Analyze sentiment from post titles and votes
                    sentiment_scores = []
                    for post in posts[:20]:  # Analyze last 20 posts
                        votes = post.get('votes', {})
                        positive = votes.get('positive', 0)
                        negative = votes.get('negative', 0)
                        
                        if positive + negative > 0:
                            score = (positive - negative) / (positive + negative)
                            sentiment_scores.append(score)
                    
                    return sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
                    
        except Exception as e:
            self.logger.error(f"CryptoPanic sentiment error: {e}")
            return None
    
    async def _get_newsapi_sentiment(self, symbols: List[str], timeframe: str) -> Optional[float]:
        """Get sentiment from NewsAPI"""
        try:
            api_key = self.sources['newsapi']['api_key']
            if not api_key:
                return None
            
            # Build search query
            query = 'cryptocurrency OR bitcoin OR crypto'
            if symbols:
                symbol_query = ' OR '.join(symbols)
                query = f'({symbol_query}) AND cryptocurrency'
            
            # Calculate date range
            hours = {'1h': 1, '24h': 24, '7d': 168}.get(timeframe, 24)
            from_date = (datetime.utcnow() - timedelta(hours=hours)).strftime('%Y-%m-%d')
            
            url = f"{self.sources['newsapi']['base_url']}/everything"
            params = {
                'apiKey': api_key,
                'q': query,
                'language': 'en',
                'sortBy': 'publishedAt',
                'from': from_date,
                'pageSize': 50
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        return None
                        
                    data = await response.json()
                    articles = data.get('articles', [])
                    
                    # Simple sentiment analysis on headlines
                    sentiment_scores = []
                    positive_words = ['bullish', 'surge', 'rally', 'gains', 'positive', 'rise', 'up', 'high', 'growth']
                    negative_words = ['bearish', 'crash', 'fall', 'drop', 'negative', 'decline', 'down', 'low', 'loss']
                    
                    for article in articles:
                        title = article.get('title', '').lower()
                        description = article.get('description', '').lower()
                        text = f"{title} {description}"
                        
                        positive_count = sum(1 for word in positive_words if word in text)
                        negative_count = sum(1 for word in negative_words if word in text)
                        
                        if positive_count + negative_count > 0:
                            score = (positive_count - negative_count) / (positive_count + negative_count)
                            sentiment_scores.append(score)
                    
                    return sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
                    
        except Exception as e:
            self.logger.error(f"NewsAPI sentiment error: {e}")
            return None
    
    async def get_social_sentiment(self, symbols: List[str] = None) -> float:
        """Get sentiment from social media sources"""
        try:
            # LunarCrush Social Sentiment
            lunarcrush_sentiment = await self._get_lunarcrush_sentiment(symbols)
            
            # Could add Twitter API, Reddit API here
            sentiments = [s for s in [lunarcrush_sentiment] if s is not None]
            
            if not sentiments:
                return 0.0
            
            return sum(sentiments) / len(sentiments)
            
        except Exception as e:
            self.logger.error(f"Error getting social sentiment: {e}")
            return 0.0
    
    async def _get_lunarcrush_sentiment(self, symbols: List[str]) -> Optional[float]:
        """Get sentiment from LunarCrush API"""
        try:
            api_key = self.sources['lunarcrush']['api_key']
            if not api_key:
                return None
                
            url = f"{self.sources['lunarcrush']['base_url']}/assets"
            params = {
                'key': api_key,
                'symbol': symbols[0].upper() if symbols else 'BTC',
                'data_points': 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        return None
                        
                    data = await response.json()
                    
                    if 'data' in data and data['data']:
                        asset_data = data['data'][0]
                        
                        # Extract sentiment indicators
                        social_score = asset_data.get('social_score', 50)  # 0-100 scale
                        sentiment = asset_data.get('sentiment', 3)  # 1-5 scale
                        
                        # Normalize to -1 to 1 scale
                        normalized_social = (social_score - 50) / 50
                        normalized_sentiment = (sentiment - 3) / 2
                        
                        return (normalized_social + normalized_sentiment) / 2
                    
            return None
            
        except Exception as e:
            self.logger.error(f"LunarCrush sentiment error: {e}")
            return None
    
    async def get_fear_greed_index(self) -> float:
        """Get Fear & Greed Index"""
        try:
            url = f"{self.sources['fear_greed']['base_url']}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return 0.0
                        
                    data = await response.json()
                    
                    if 'data' in data and data['data']:
                        index_value = int(data['data'][0]['value'])  # 0-100
                        
                        # Convert to -1 to 1 scale (0-25: very fearful, 75-100: very greedy)
                        if index_value <= 25:
                            return -0.5 - (25 - index_value) / 50  # -0.5 to -1
                        elif index_value >= 75:
                            return 0.5 + (index_value - 75) / 50   # 0.5 to 1
                        else:
                            return (index_value - 50) / 50         # -0.5 to 0.5
                    
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Fear & Greed Index error: {e}")
            return 0.0
    
    async def get_technical_sentiment(self, symbols: List[str] = None) -> float:
        """Get technical analysis sentiment based on price action"""
        try:
            # This would integrate with technical analysis indicators
            # For now, return neutral sentiment
            
            # Could analyze:
            # - RSI levels
            # - Moving average trends
            # - Support/resistance levels
            # - Volume patterns
            
            return 0.0  # Neutral for now
            
        except Exception as e:
            self.logger.error(f"Error getting technical sentiment: {e}")
            return 0.0
    
    async def aggregate_sentiment(self, symbols: List[str] = None, timeframe: str = '24h') -> Dict[str, Any]:
        """Aggregate sentiment from all sources"""
        try:
            # Get sentiment from all sources
            news_sentiment = await self.get_news_sentiment(symbols, timeframe)
            social_sentiment = await self.get_social_sentiment(symbols)
            technical_sentiment = await self.get_technical_sentiment(symbols)
            fear_greed = await self.get_fear_greed_index()
            
            # Calculate weighted overall sentiment
            sentiment_components = {
                'news': news_sentiment,
                'social_media': social_sentiment,
                'technical': technical_sentiment,
                'fear_greed_index': fear_greed
            }
            
            # Weight the components
            weights = {
                'news': 0.3,
                'social_media': 0.25,
                'technical': 0.25,
                'fear_greed_index': 0.2
            }
            
            overall_sentiment = sum(
                sentiment_components[component] * weights[component]
                for component in sentiment_components
            )
            
            # Calculate confidence based on data availability
            available_sources = sum(1 for score in sentiment_components.values() if score != 0)
            confidence = min(available_sources / len(sentiment_components), 1.0)
            
            # Determine trend
            # This would compare with historical data in a real implementation
            trend = 'stable'  # Simplified for now
            
            return {
                'overall_sentiment': overall_sentiment,
                'confidence': confidence,
                'sentiment_sources': sentiment_components,
                'trend': trend,
                'last_updated': datetime.utcnow().isoformat(),
                'data_freshness': 'fresh' if confidence > 0.7 else 'stale',
                'source_breakdown': [
                    {
                        'source_name': source,
                        'sentiment_score': score,
                        'confidence': 1.0 if score != 0 else 0.0,
                        'weight': weights[source]
                    }
                    for source, score in sentiment_components.items()
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error aggregating sentiment: {e}")
            raise

# Initialize aggregator
sentiment_aggregator = SentimentAggregator()

@sentiment_router.get("")
async def get_market_sentiment(
    symbols: Optional[str] = Query(None, description="Comma-separated crypto symbols"),
    timeframe: str = Query("24h", description="Time frame: 1h, 24h, 7d"),
    sources: Optional[str] = Query(None, description="Comma-separated sources to include")
):
    """Get aggregated market sentiment from multiple sources"""
    try:
        # Parse symbols
        symbol_list = symbols.split(',') if symbols else None
        
        # Parse sources filter (for future use)
        source_list = sources.split(',') if sources else None
        
        # Validate timeframe
        if timeframe not in ['1h', '24h', '7d']:
            raise HTTPException(status_code=400, detail="Invalid timeframe. Use: 1h, 24h, 7d")
        
        # Get aggregated sentiment
        sentiment_data = await sentiment_aggregator.aggregate_sentiment(symbol_list, timeframe)
        
        return {
            'status': 'success',
            'data': sentiment_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in sentiment endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

@sentiment_router.get("/history")
async def get_sentiment_history(
    symbol: str = Query(..., description="Crypto symbol"),
    days: int = Query(7, description="Number of days of history", ge=1, le=30)
):
    """Get historical sentiment data for a specific cryptocurrency"""
    try:
        # This would fetch historical sentiment data from database
        # For now, return mock historical data
        
        history_points = []
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days-i)
            
            # Mock sentiment trend
            base_sentiment = 0.1 * (i - days/2) / (days/2)  # Trending sentiment
            
            history_points.append({
                'date': date.strftime('%Y-%m-%d'),
                'overall_sentiment': base_sentiment,
                'confidence': 0.8,
                'data_points': 4  # Number of sources available
            })
        
        return {
            'status': 'success',
            'data': {
                'symbol': symbol,
                'history': history_points,
                'days': days
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in sentiment history endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Sentiment history failed: {str(e)}")

@sentiment_router.get("/sources")
async def get_sentiment_sources():
    """Get available sentiment sources and their status"""
    try:
        sources_status = []
        
        for source_name, config in sentiment_aggregator.sources.items():
            api_key = config.get('api_key')
            sources_status.append({
                'name': source_name,
                'available': bool(api_key),
                'weight': config.get('weight', 0),
                'description': f"{source_name.title()} sentiment analysis"
            })
        
        return {
            'status': 'success',
            'data': {
                'sources': sources_status,
                'total_sources': len(sources_status),
                'available_sources': len([s for s in sources_status if s['available']])
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in sentiment sources endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Sentiment sources failed: {str(e)}")

# Export router for inclusion in main app
__all__ = ['sentiment_router'] 