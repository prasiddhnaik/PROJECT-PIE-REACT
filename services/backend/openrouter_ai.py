"""
OpenRouter AI Integration
========================

Best free AI models for financial analysis via OpenRouter:
- GPT-4o Mini (OpenAI) - Best overall free model
- Claude 3 Haiku (Anthropic) - Fast reasoning
- Gemini Flash 2.0 (Google) - Latest multimodal
- Llama 3.1 405B (Meta) - Open source powerhouse
- Qwen 2.5 72B (Alibaba) - Excellent for data analysis

Features:
- Stock analysis and recommendations
- Market sentiment analysis
- Portfolio optimization suggestions
- Technical analysis interpretation
- Real-time financial news analysis
- Risk assessment insights
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime
import os
from dataclasses import dataclass
from enum import Enum
import tiktoken

logger = logging.getLogger(__name__)

class AIModel(Enum):
    """Best free OpenRouter models for financial analysis"""
    GPT_4O_MINI = "openai/gpt-4o-mini"  # Best overall free model - $0.15/1M tokens
    CLAUDE_HAIKU = "anthropic/claude-3-haiku"  # Fast reasoning - $0.25/1M tokens
    GEMINI_FLASH = "google/gemini-flash-1.5"  # Latest Google model - Free tier
    LLAMA_405B = "meta-llama/llama-3.1-405b-instruct"  # Most powerful open source
    QWEN_72B = "qwen/qwen-2.5-72b-instruct"  # Great for data analysis - Free
    MISTRAL_7B = "mistralai/mistral-7b-instruct"  # Fast and efficient - Free
    
    @property
    def display_name(self):
        """Human-readable model names"""
        names = {
            "openai/gpt-4o-mini": "GPT-4o Mini",
            "anthropic/claude-3-haiku": "Claude 3 Haiku", 
            "google/gemini-flash-1.5": "Gemini Flash 1.5",
            "meta-llama/llama-3.1-405b-instruct": "Llama 3.1 405B",
            "qwen/qwen-2.5-72b-instruct": "Qwen 2.5 72B",
            "mistralai/mistral-7b-instruct": "Mistral 7B"
        }
        return names.get(self.value, self.value)

@dataclass
class AIResponse:
    """Structure for AI responses"""
    content: str
    model: str
    tokens_used: int
    cost_estimate: float
    timestamp: datetime
    confidence: float = 0.0
    
class FinancialAI:
    """
    OpenRouter AI integration for financial analysis
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        self.session = None
        
        # Model configurations with cost per 1M tokens
        self.model_configs = {
            AIModel.GPT_4O_MINI: {"cost_per_1m": 0.15, "max_tokens": 128000, "best_for": "general_analysis"},
            AIModel.CLAUDE_HAIKU: {"cost_per_1m": 0.25, "max_tokens": 200000, "best_for": "reasoning"},
            AIModel.GEMINI_FLASH: {"cost_per_1m": 0.0, "max_tokens": 1000000, "best_for": "multimodal"},
            AIModel.LLAMA_405B: {"cost_per_1m": 0.0, "max_tokens": 128000, "best_for": "open_source"},
            AIModel.QWEN_72B: {"cost_per_1m": 0.0, "max_tokens": 32000, "best_for": "data_analysis"},
            AIModel.MISTRAL_7B: {"cost_per_1m": 0.0, "max_tokens": 32000, "best_for": "speed"}
        }
        
        # Financial analysis prompts
        self.system_prompts = {
            "stock_analysis": """You are a professional financial analyst with deep expertise in stock analysis, technical indicators, and market trends. Provide detailed, actionable insights based on data provided. Focus on:
- Technical analysis interpretation
- Risk assessment
- Price target suggestions
- Market sentiment analysis
- Entry/exit strategies

Always include confidence levels and potential risks in your analysis.""",

            "portfolio_optimization": """You are a portfolio management expert specializing in risk-adjusted returns and diversification strategies. Analyze portfolios considering:
- Asset allocation optimization
- Risk-return profiles
- Correlation analysis
- Rebalancing suggestions
- Tax implications
- Market cycle positioning

Provide specific, implementable recommendations.""",

            "market_sentiment": """You are a market sentiment analyst with expertise in behavioral finance and news impact analysis. Focus on:
- News sentiment analysis
- Market psychology indicators
- Fear/greed index interpretation
- Social media sentiment
- Institutional vs retail sentiment
- Contrarian opportunities

Provide sentiment scores and trading implications.""",

            "risk_analysis": """You are a risk management specialist focusing on downside protection and volatility analysis. Evaluate:
- Value at Risk (VaR) calculations
- Maximum drawdown analysis
- Correlation risks
- Black swan event probability
- Hedging strategies
- Position sizing recommendations

Emphasize risk mitigation strategies."""
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://financial-analytics-hub.com",
                "X-Title": "Financial Analytics Hub"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def analyze_stock(self, symbol: str, market_data: Dict[str, Any], 
                           technical_analysis: Dict[str, Any],
                           model: AIModel = AIModel.GPT_4O_MINI) -> AIResponse:
        """
        Comprehensive AI-powered stock analysis
        """
        try:
            prompt = f"""
Analyze {symbol} based on the following data:

MARKET DATA:
- Current Price: ${market_data.get('current_price', 'N/A')}
- Price Change: {market_data.get('change_percent', 'N/A')}%
- Volume: {market_data.get('volume', 'N/A')}
- 52W High/Low: ${market_data.get('high_52w', 'N/A')} / ${market_data.get('low_52w', 'N/A')}

TECHNICAL INDICATORS:
{self._format_technical_data(technical_analysis)}

Provide a comprehensive analysis including:
1. Overall assessment (BUY/HOLD/SELL)
2. Price target (1-3 months)
3. Key support/resistance levels
4. Risk factors
5. Catalyst opportunities
6. Confidence level (1-10)

Format as structured analysis with clear sections.
"""
            
            response = await self._make_request(
                prompt, 
                model, 
                system_prompt=self.system_prompts["stock_analysis"]
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in stock analysis: {e}")
            return AIResponse(
                content=f"Error analyzing {symbol}: {str(e)}",
                model=model.value,
                tokens_used=0,
                cost_estimate=0.0,
                timestamp=datetime.now()
            )
    
    async def analyze_portfolio(self, portfolio_data: List[Dict[str, Any]], 
                               model: AIModel = AIModel.CLAUDE_HAIKU) -> AIResponse:
        """
        AI-powered portfolio optimization analysis
        """
        try:
            portfolio_summary = self._format_portfolio_data(portfolio_data)
            
            prompt = f"""
Analyze this investment portfolio:

{portfolio_summary}

Provide detailed optimization recommendations:

1. ASSET ALLOCATION ANALYSIS
   - Current allocation assessment
   - Optimal allocation suggestions
   - Overweight/underweight positions

2. RISK ASSESSMENT
   - Portfolio beta and volatility
   - Correlation risks
   - Sector concentration risks

3. OPTIMIZATION STRATEGIES
   - Rebalancing recommendations
   - New position suggestions
   - Position sizing adjustments

4. PERFORMANCE ENHANCEMENT
   - Expected return improvements
   - Risk-adjusted return optimization
   - Tax efficiency considerations

5. ACTION ITEMS
   - Immediate actions (next 30 days)
   - Medium-term strategy (3-6 months)
   - Long-term positioning (1+ years)

Include confidence scores for each recommendation.
"""
            
            response = await self._make_request(
                prompt,
                model,
                system_prompt=self.system_prompts["portfolio_optimization"]
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in portfolio analysis: {e}")
            return AIResponse(
                content=f"Error analyzing portfolio: {str(e)}",
                model=model.value,
                tokens_used=0,
                cost_estimate=0.0,
                timestamp=datetime.now()
            )
    
    async def analyze_market_sentiment(self, news_data: List[str], 
                                     market_indicators: Dict[str, Any],
                                     model: AIModel = AIModel.GEMINI_FLASH) -> AIResponse:
        """
        AI-powered market sentiment analysis
        """
        try:
            news_summary = "\n".join([f"- {news}" for news in news_data[:10]])
            
            prompt = f"""
Analyze current market sentiment based on:

RECENT NEWS:
{news_summary}

MARKET INDICATORS:
- VIX: {market_indicators.get('vix', 'N/A')}
- Market Trend: {market_indicators.get('trend', 'N/A')}
- Volume Trend: {market_indicators.get('volume_trend', 'N/A')}

Provide comprehensive sentiment analysis:

1. OVERALL SENTIMENT SCORE (-100 to +100)
   - Current sentiment level
   - Sentiment trend (improving/declining)
   - Key sentiment drivers

2. NEWS IMPACT ANALYSIS
   - Bullish news themes
   - Bearish news themes
   - Market reaction likelihood

3. CONTRARIAN OPPORTUNITIES
   - Oversold conditions
   - Overhyped sectors
   - Potential reversals

4. TRADING IMPLICATIONS
   - Short-term bias (1-2 weeks)
   - Medium-term outlook (1-3 months)
   - Key levels to watch

5. RISK FACTORS
   - Sentiment extreme warnings
   - Black swan possibilities
   - Volatility expectations

Rate confidence level (1-10) for each assessment.
"""
            
            response = await self._make_request(
                prompt,
                model,
                system_prompt=self.system_prompts["market_sentiment"]
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return AIResponse(
                content=f"Error analyzing market sentiment: {str(e)}",
                model=model.value,
                tokens_used=0,
                cost_estimate=0.0,
                timestamp=datetime.now()
            )
    
    async def get_trading_signals(self, symbols: List[str], 
                                 technical_data: Dict[str, Any],
                                 model: AIModel = AIModel.QWEN_72B) -> AIResponse:
        """
        AI-generated trading signals and alerts
        """
        try:
            prompt = f"""
Generate trading signals for: {', '.join(symbols)}

TECHNICAL DATA SUMMARY:
{self._format_technical_summary(technical_data)}

Provide actionable trading signals:

1. IMMEDIATE SIGNALS (Next 1-5 days)
   For each symbol provide:
   - Signal: BUY/SELL/HOLD
   - Entry price/range
   - Stop loss level
   - Target price(s)
   - Position size recommendation
   - Confidence level (1-10)

2. TECHNICAL SETUP ANALYSIS
   - Chart pattern recognition
   - Key indicator alignments
   - Momentum analysis
   - Support/resistance levels

3. RISK MANAGEMENT
   - Maximum position size
   - Portfolio heat allocation
   - Correlation considerations
   - Market conditions impact

4. ALERT CONDITIONS
   - Price breakout levels
   - Volume confirmation triggers
   - Indicator convergence points

5. TRADE MANAGEMENT
   - Position monitoring criteria
   - Exit strategy refinements
   - Profit-taking levels

Format as clear, actionable trading plan.
"""
            
            response = await self._make_request(
                prompt,
                model,
                system_prompt=self.system_prompts["stock_analysis"]
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating trading signals: {e}")
            return AIResponse(
                content=f"Error generating trading signals: {str(e)}",
                model=model.value,
                tokens_used=0,
                cost_estimate=0.0,
                timestamp=datetime.now()
            )
    
    async def stream_analysis(self, prompt: str, 
                             model: AIModel = AIModel.GPT_4O_MINI) -> AsyncGenerator[str, None]:
        """
        Stream real-time AI analysis responses
        """
        try:
            if not self.session:
                await self.__aenter__()
            
            payload = {
                "model": model.value,
                "messages": [
                    {"role": "system", "content": self.system_prompts["stock_analysis"]},
                    {"role": "user", "content": prompt}
                ],
                "stream": True,
                "max_tokens": 2048,
                "temperature": 0.7
            }
            
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload
            ) as response:
                if response.status == 200:
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            data = line[6:]
                            if data == '[DONE]':
                                break
                            try:
                                chunk = json.loads(data)
                                if 'choices' in chunk and chunk['choices']:
                                    delta = chunk['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        yield delta['content']
                            except json.JSONDecodeError:
                                continue
                else:
                    error_text = await response.text()
                    logger.error(f"Streaming error: {error_text}")
                    yield f"Error: {error_text}"
                    
        except Exception as e:
            logger.error(f"Error in stream analysis: {e}")
            yield f"Error in streaming: {str(e)}"
    
    async def _make_request(self, prompt: str, model: AIModel, 
                           system_prompt: str = None) -> AIResponse:
        """
        Make request to OpenRouter API
        """
        if not self.session:
            await self.__aenter__()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model.value,
            "messages": messages,
            "max_tokens": 2048,
            "temperature": 0.7,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    content = data['choices'][0]['message']['content']
                    tokens_used = data.get('usage', {}).get('total_tokens', 0)
                    
                    # Calculate cost estimate
                    cost_per_1m = self.model_configs[model]["cost_per_1m"]
                    cost_estimate = (tokens_used / 1_000_000) * cost_per_1m
                    
                    return AIResponse(
                        content=content,
                        model=model.value,
                        tokens_used=tokens_used,
                        cost_estimate=cost_estimate,
                        timestamp=datetime.now(),
                        confidence=self._estimate_confidence(content)
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"API error: {error_text}")
                    return AIResponse(
                        content=f"API Error: {error_text}",
                        model=model.value,
                        tokens_used=0,
                        cost_estimate=0.0,
                        timestamp=datetime.now()
                    )
                    
        except Exception as e:
            logger.error(f"Request error: {e}")
            return AIResponse(
                content=f"Request Error: {str(e)}",
                model=model.value,
                tokens_used=0,
                cost_estimate=0.0,
                timestamp=datetime.now()
            )
    
    def _format_technical_data(self, technical_analysis: Dict[str, Any]) -> str:
        """Format technical analysis data for AI prompt"""
        formatted = []
        
        if 'trend_indicators' in technical_analysis:
            trend = technical_analysis['trend_indicators']
            formatted.append(f"RSI: {trend.get('rsi', 'N/A')}")
            formatted.append(f"MACD: {trend.get('macd', {}).get('macd_line', 'N/A')}")
            formatted.append(f"SMA 20: {trend.get('sma_20', 'N/A')}")
            formatted.append(f"SMA 50: {trend.get('sma_50', 'N/A')}")
        
        if 'momentum_indicators' in technical_analysis:
            momentum = technical_analysis['momentum_indicators']
            formatted.append(f"Stochastic: {momentum.get('stochastic', {}).get('k', 'N/A')}")
            formatted.append(f"Williams %R: {momentum.get('williams_r', {}).get('value', 'N/A')}")
        
        if 'volatility_indicators' in technical_analysis:
            volatility = technical_analysis['volatility_indicators']
            bb = volatility.get('bollinger_bands', {})
            formatted.append(f"BB Position: {bb.get('position', 'N/A')}")
            formatted.append(f"ATR: {volatility.get('atr', {}).get('value', 'N/A')}")
        
        return '\n'.join(formatted) if formatted else "Technical data not available"
    
    def _format_portfolio_data(self, portfolio_data: List[Dict[str, Any]]) -> str:
        """Format portfolio data for AI analysis"""
        formatted = ["CURRENT HOLDINGS:"]
        
        total_value = sum(holding.get('value', 0) for holding in portfolio_data)
        
        for holding in portfolio_data:
            symbol = holding.get('symbol', 'Unknown')
            shares = holding.get('shares', 0)
            value = holding.get('value', 0)
            weight = (value / total_value * 100) if total_value > 0 else 0
            
            formatted.append(f"- {symbol}: {shares} shares, ${value:,.2f} ({weight:.1f}%)")
        
        formatted.append(f"\nTOTAL PORTFOLIO VALUE: ${total_value:,.2f}")
        
        return '\n'.join(formatted)
    
    def _format_technical_summary(self, technical_data: Dict[str, Any]) -> str:
        """Format technical data summary"""
        summary = []
        for symbol, data in technical_data.items():
            summary.append(f"{symbol}:")
            summary.append(f"  Current Price: ${data.get('current_price', 'N/A')}")
            summary.append(f"  RSI: {data.get('rsi', 'N/A')}")
            summary.append(f"  Trend: {data.get('trend', 'N/A')}")
            summary.append("")
        
        return '\n'.join(summary)
    
    def _estimate_confidence(self, content: str) -> float:
        """Estimate confidence based on response content"""
        # Simple confidence estimation based on response characteristics
        confidence_indicators = [
            'high confidence', 'very likely', 'strong signal', 'clear trend',
            'definitive', 'certain', 'obvious', 'strong evidence'
        ]
        
        uncertainty_indicators = [
            'uncertain', 'unclear', 'might', 'possibly', 'perhaps',
            'could be', 'may be', 'potential', 'low confidence'
        ]
        
        content_lower = content.lower()
        confidence_score = 70  # Base confidence
        
        for indicator in confidence_indicators:
            if indicator in content_lower:
                confidence_score += 5
        
        for indicator in uncertainty_indicators:
            if indicator in content_lower:
                confidence_score -= 10
        
        return max(10, min(95, confidence_score))
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models with their capabilities"""
        models_info = []
        
        for model in AIModel:
            config = self.model_configs[model]
            models_info.append({
                "id": model.value,
                "name": model.display_name,
                "cost_per_1m_tokens": config["cost_per_1m"],
                "max_tokens": config["max_tokens"],
                "best_for": config["best_for"],
                "is_free": config["cost_per_1m"] == 0.0
            })
        
        return models_info
    
    def estimate_cost(self, text: str, model: AIModel) -> float:
        """Estimate cost for analyzing given text"""
        try:
            # Use tiktoken for accurate token counting
            encoding = tiktoken.encoding_for_model("gpt-4")
            token_count = len(encoding.encode(text))
            
            cost_per_1m = self.model_configs[model]["cost_per_1m"]
            return (token_count / 1_000_000) * cost_per_1m
            
        except Exception:
            # Fallback estimation (roughly 4 chars per token)
            estimated_tokens = len(text) // 4
            cost_per_1m = self.model_configs[model]["cost_per_1m"]
            return (estimated_tokens / 1_000_000) * cost_per_1m

# Utility functions for easy integration
async def quick_stock_analysis(symbol: str, market_data: Dict[str, Any], 
                              technical_analysis: Dict[str, Any],
                              api_key: str = None) -> str:
    """Quick stock analysis using best free model"""
    async with FinancialAI(api_key) as ai:
        response = await ai.analyze_stock(symbol, market_data, technical_analysis)
        return response.content

async def get_trading_signals(symbols: List[str], technical_data: Dict[str, Any],
                             api_key: str = None) -> str:
    """Get trading signals for multiple stocks"""
    async with FinancialAI(api_key) as ai:
        response = await ai.get_trading_signals(symbols, technical_data)
        return response.content

async def analyze_market_sentiment(news_data: List[str], market_indicators: Dict[str, Any],
                                  api_key: str = None) -> str:
    """Quick market sentiment analysis"""
    async with FinancialAI(api_key) as ai:
        response = await ai.analyze_market_sentiment(news_data, market_indicators)
        return response.content 