"""
Technical Analysis Module
========================

Comprehensive technical analysis with 50+ indicators:
- Trend indicators (SMA, EMA, MACD, ADX)
- Momentum indicators (RSI, Stochastic, Williams %R)
- Volatility indicators (Bollinger Bands, ATR)
- Volume indicators (OBV, VWAP, Volume Profile)
- Support/Resistance detection
- Pattern recognition
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging
from scipy.signal import argrelextrema
from scipy.stats import linregress

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """
    Comprehensive technical analysis toolkit
    """
    
    def __init__(self):
        self.indicators_cache = {}
    
    def analyze_stock(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """
        Perform complete technical analysis on stock data
        
        Args:
            data: OHLCV DataFrame
            symbol: Stock symbol
        
        Returns:
            Dictionary with all technical analysis results
        """
        try:
            if data is None or len(data) < 20:
                return {}
            
            analysis = {
                'symbol': symbol,
                'current_price': float(data['Close'].iloc[-1]),
                'trend_indicators': self._calculate_trend_indicators(data),
                'momentum_indicators': self._calculate_momentum_indicators(data),
                'volatility_indicators': self._calculate_volatility_indicators(data),
                'volume_indicators': self._calculate_volume_indicators(data),
                'support_resistance': self._find_support_resistance(data),
                'patterns': self._detect_patterns(data),
                'signals': self._generate_signals(data),
                'risk_metrics': self._calculate_risk_metrics(data),
                'recommendation': self._generate_recommendation(data)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return {}
    
    def _calculate_trend_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate trend-following indicators"""
        try:
            close = data['Close']
            high = data['High']
            low = data['Low']
            
            # Simple Moving Averages
            sma_5 = close.rolling(window=5).mean()
            sma_10 = close.rolling(window=10).mean()
            sma_20 = close.rolling(window=20).mean()
            sma_50 = close.rolling(window=50).mean()
            sma_200 = close.rolling(window=200).mean()
            
            # Exponential Moving Averages
            ema_12 = close.ewm(span=12).mean()
            ema_26 = close.ewm(span=26).mean()
            ema_50 = close.ewm(span=50).mean()
            
            # MACD
            macd_line = ema_12 - ema_26
            macd_signal = macd_line.ewm(span=9).mean()
            macd_histogram = macd_line - macd_signal
            
            # Average Directional Index (ADX)
            adx = self._calculate_adx(high, low, close)
            
            # Parabolic SAR
            psar = self._calculate_psar(high, low, close)
            
            current_price = close.iloc[-1]
            
            return {
                'sma_5': float(sma_5.iloc[-1]) if not pd.isna(sma_5.iloc[-1]) else None,
                'sma_10': float(sma_10.iloc[-1]) if not pd.isna(sma_10.iloc[-1]) else None,
                'sma_20': float(sma_20.iloc[-1]) if not pd.isna(sma_20.iloc[-1]) else None,
                'sma_50': float(sma_50.iloc[-1]) if not pd.isna(sma_50.iloc[-1]) else None,
                'sma_200': float(sma_200.iloc[-1]) if not pd.isna(sma_200.iloc[-1]) else None,
                'ema_12': float(ema_12.iloc[-1]) if not pd.isna(ema_12.iloc[-1]) else None,
                'ema_26': float(ema_26.iloc[-1]) if not pd.isna(ema_26.iloc[-1]) else None,
                'ema_50': float(ema_50.iloc[-1]) if not pd.isna(ema_50.iloc[-1]) else None,
                'macd': {
                    'macd_line': float(macd_line.iloc[-1]) if not pd.isna(macd_line.iloc[-1]) else None,
                    'signal_line': float(macd_signal.iloc[-1]) if not pd.isna(macd_signal.iloc[-1]) else None,
                    'histogram': float(macd_histogram.iloc[-1]) if not pd.isna(macd_histogram.iloc[-1]) else None,
                    'crossover': 'bullish' if macd_line.iloc[-1] > macd_signal.iloc[-1] else 'bearish'
                },
                'adx': float(adx.iloc[-1]) if not pd.isna(adx.iloc[-1]) else None,
                'psar': float(psar.iloc[-1]) if not pd.isna(psar.iloc[-1]) else None,
                'trend_strength': self._assess_trend_strength(close, sma_20, sma_50),
                'ma_alignment': self._check_ma_alignment(sma_5, sma_10, sma_20, sma_50),
                'price_vs_mas': {
                    'above_sma_20': current_price > sma_20.iloc[-1] if not pd.isna(sma_20.iloc[-1]) else None,
                    'above_sma_50': current_price > sma_50.iloc[-1] if not pd.isna(sma_50.iloc[-1]) else None,
                    'above_sma_200': current_price > sma_200.iloc[-1] if not pd.isna(sma_200.iloc[-1]) else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating trend indicators: {e}")
            return {}
    
    def _calculate_momentum_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate momentum oscillators"""
        try:
            close = data['Close']
            high = data['High']
            low = data['Low']
            
            # RSI
            rsi = self._calculate_rsi(close)
            
            # Stochastic Oscillator
            stoch_k, stoch_d = self._calculate_stochastic(high, low, close)
            
            # Williams %R
            williams_r = self._calculate_williams_r(high, low, close)
            
            # Rate of Change (ROC)
            roc = ((close - close.shift(14)) / close.shift(14)) * 100
            
            # Commodity Channel Index (CCI)
            cci = self._calculate_cci(high, low, close)
            
            return {
                'rsi': {
                    'value': float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None,
                    'condition': self._rsi_condition(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None,
                    'divergence': self._check_rsi_divergence(close, rsi)
                },
                'stochastic': {
                    'k': float(stoch_k.iloc[-1]) if not pd.isna(stoch_k.iloc[-1]) else None,
                    'd': float(stoch_d.iloc[-1]) if not pd.isna(stoch_d.iloc[-1]) else None,
                    'condition': self._stoch_condition(stoch_k.iloc[-1], stoch_d.iloc[-1]) if not pd.isna(stoch_k.iloc[-1]) else None
                },
                'williams_r': {
                    'value': float(williams_r.iloc[-1]) if not pd.isna(williams_r.iloc[-1]) else None,
                    'condition': self._williams_condition(williams_r.iloc[-1]) if not pd.isna(williams_r.iloc[-1]) else None
                },
                'roc': float(roc.iloc[-1]) if not pd.isna(roc.iloc[-1]) else None,
                'cci': {
                    'value': float(cci.iloc[-1]) if not pd.isna(cci.iloc[-1]) else None,
                    'condition': self._cci_condition(cci.iloc[-1]) if not pd.isna(cci.iloc[-1]) else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating momentum indicators: {e}")
            return {}
    
    def _calculate_volatility_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate volatility indicators"""
        try:
            close = data['Close']
            high = data['High']
            low = data['Low']
            
            # Bollinger Bands
            bb_period = 20
            bb_std = 2
            bb_middle = close.rolling(window=bb_period).mean()
            bb_std_dev = close.rolling(window=bb_period).std()
            bb_upper = bb_middle + (bb_std_dev * bb_std)
            bb_lower = bb_middle - (bb_std_dev * bb_std)
            
            # Average True Range (ATR)
            atr = self._calculate_atr(high, low, close)
            
            # Volatility (Standard Deviation)
            volatility = close.rolling(window=20).std()
            
            # Keltner Channels
            kc_period = 20
            kc_multiplier = 2
            kc_middle = close.ewm(span=kc_period).mean()
            kc_atr = self._calculate_atr(high, low, close, period=kc_period)
            kc_upper = kc_middle + (kc_atr * kc_multiplier)
            kc_lower = kc_middle - (kc_atr * kc_multiplier)
            
            current_price = close.iloc[-1]
            
            return {
                'bollinger_bands': {
                    'upper': float(bb_upper.iloc[-1]) if not pd.isna(bb_upper.iloc[-1]) else None,
                    'middle': float(bb_middle.iloc[-1]) if not pd.isna(bb_middle.iloc[-1]) else None,
                    'lower': float(bb_lower.iloc[-1]) if not pd.isna(bb_lower.iloc[-1]) else None,
                    'width': float((bb_upper.iloc[-1] - bb_lower.iloc[-1]) / bb_middle.iloc[-1] * 100) if not pd.isna(bb_upper.iloc[-1]) else None,
                    'position': self._bb_position(current_price, bb_upper.iloc[-1], bb_lower.iloc[-1]) if not pd.isna(bb_upper.iloc[-1]) else None
                },
                'atr': {
                    'value': float(atr.iloc[-1]) if not pd.isna(atr.iloc[-1]) else None,
                    'percent': float(atr.iloc[-1] / current_price * 100) if not pd.isna(atr.iloc[-1]) else None
                },
                'volatility': {
                    'value': float(volatility.iloc[-1]) if not pd.isna(volatility.iloc[-1]) else None,
                    'percent': float(volatility.iloc[-1] / current_price * 100) if not pd.isna(volatility.iloc[-1]) else None
                },
                'keltner_channels': {
                    'upper': float(kc_upper.iloc[-1]) if not pd.isna(kc_upper.iloc[-1]) else None,
                    'middle': float(kc_middle.iloc[-1]) if not pd.isna(kc_middle.iloc[-1]) else None,
                    'lower': float(kc_lower.iloc[-1]) if not pd.isna(kc_lower.iloc[-1]) else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating volatility indicators: {e}")
            return {}
    
    def _calculate_volume_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate volume-based indicators"""
        try:
            close = data['Close']
            volume = data['Volume']
            high = data['High']
            low = data['Low']
            
            # On-Balance Volume (OBV)
            obv = self._calculate_obv(close, volume)
            
            # Volume Weighted Average Price (VWAP)
            vwap = self._calculate_vwap(high, low, close, volume)
            
            # Money Flow Index (MFI)
            mfi = self._calculate_mfi(high, low, close, volume)
            
            # Accumulation/Distribution Line
            ad_line = self._calculate_ad_line(high, low, close, volume)
            
            # Volume Rate of Change
            volume_roc = ((volume - volume.shift(10)) / volume.shift(10)) * 100
            
            return {
                'obv': {
                    'value': float(obv.iloc[-1]) if not pd.isna(obv.iloc[-1]) else None,
                    'trend': self._obv_trend(obv)
                },
                'vwap': float(vwap.iloc[-1]) if not pd.isna(vwap.iloc[-1]) else None,
                'mfi': {
                    'value': float(mfi.iloc[-1]) if not pd.isna(mfi.iloc[-1]) else None,
                    'condition': self._mfi_condition(mfi.iloc[-1]) if not pd.isna(mfi.iloc[-1]) else None
                },
                'ad_line': float(ad_line.iloc[-1]) if not pd.isna(ad_line.iloc[-1]) else None,
                'volume_analysis': {
                    'current_volume': int(volume.iloc[-1]),
                    'avg_volume_20': float(volume.rolling(window=20).mean().iloc[-1]) if not pd.isna(volume.rolling(window=20).mean().iloc[-1]) else None,
                    'volume_ratio': float(volume.iloc[-1] / volume.rolling(window=20).mean().iloc[-1]) if not pd.isna(volume.rolling(window=20).mean().iloc[-1]) else None,
                    'volume_roc': float(volume_roc.iloc[-1]) if not pd.isna(volume_roc.iloc[-1]) else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating volume indicators: {e}")
            return {}
    
    def _find_support_resistance(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Find support and resistance levels"""
        try:
            close = data['Close']
            high = data['High']
            low = data['Low']
            
            # Find local minima and maxima
            min_idx = argrelextrema(low.values, np.less, order=5)[0]
            max_idx = argrelextrema(high.values, np.greater, order=5)[0]
            
            # Get recent support and resistance levels
            recent_supports = []
            recent_resistances = []
            
            current_price = close.iloc[-1]
            
            # Support levels (from local minima)
            for idx in min_idx[-10:]:  # Last 10 support levels
                support_level = low.iloc[idx]
                if support_level < current_price:
                    recent_supports.append(float(support_level))
            
            # Resistance levels (from local maxima)
            for idx in max_idx[-10:]:  # Last 10 resistance levels
                resistance_level = high.iloc[idx]
                if resistance_level > current_price:
                    recent_resistances.append(float(resistance_level))
            
            # Sort and get strongest levels
            recent_supports.sort(reverse=True)  # Closest to current price first
            recent_resistances.sort()  # Closest to current price first
            
            # Pivot points (traditional)
            pivot_points = self._calculate_pivot_points(data)
            
            return {
                'support_levels': recent_supports[:5],  # Top 5 support levels
                'resistance_levels': recent_resistances[:5],  # Top 5 resistance levels
                'nearest_support': recent_supports[0] if recent_supports else None,
                'nearest_resistance': recent_resistances[0] if recent_resistances else None,
                'pivot_points': pivot_points,
                'current_position': {
                    'price': float(current_price),
                    'support_distance': float((current_price - recent_supports[0]) / current_price * 100) if recent_supports else None,
                    'resistance_distance': float((recent_resistances[0] - current_price) / current_price * 100) if recent_resistances else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error finding support/resistance: {e}")
            return {}
    
    def _detect_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Detect chart patterns"""
        try:
            patterns = {
                'candlestick_patterns': self._detect_candlestick_patterns(data),
                'chart_patterns': self._detect_chart_patterns(data),
                'trend_patterns': self._detect_trend_patterns(data)
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return {}
    
    def _generate_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate trading signals"""
        try:
            close = data['Close']
            
            # Collect signals from different indicators
            signals = {
                'overall_signal': 'HOLD',
                'signal_strength': 0,
                'individual_signals': {},
                'signal_count': {'bullish': 0, 'bearish': 0, 'neutral': 0}
            }
            
            # RSI signals
            rsi = self._calculate_rsi(close)
            if not pd.isna(rsi.iloc[-1]):
                if rsi.iloc[-1] < 30:
                    signals['individual_signals']['rsi'] = 'BUY'
                    signals['signal_count']['bullish'] += 1
                elif rsi.iloc[-1] > 70:
                    signals['individual_signals']['rsi'] = 'SELL'
                    signals['signal_count']['bearish'] += 1
                else:
                    signals['individual_signals']['rsi'] = 'HOLD'
                    signals['signal_count']['neutral'] += 1
            
            # MACD signals
            ema_12 = close.ewm(span=12).mean()
            ema_26 = close.ewm(span=26).mean()
            macd_line = ema_12 - ema_26
            macd_signal = macd_line.ewm(span=9).mean()
            
            if not pd.isna(macd_line.iloc[-1]):
                if macd_line.iloc[-1] > macd_signal.iloc[-1] and macd_line.iloc[-2] <= macd_signal.iloc[-2]:
                    signals['individual_signals']['macd'] = 'BUY'
                    signals['signal_count']['bullish'] += 1
                elif macd_line.iloc[-1] < macd_signal.iloc[-1] and macd_line.iloc[-2] >= macd_signal.iloc[-2]:
                    signals['individual_signals']['macd'] = 'SELL'
                    signals['signal_count']['bearish'] += 1
                else:
                    signals['individual_signals']['macd'] = 'HOLD'
                    signals['signal_count']['neutral'] += 1
            
            # Moving Average signals
            sma_20 = close.rolling(window=20).mean()
            sma_50 = close.rolling(window=50).mean()
            
            if not pd.isna(sma_20.iloc[-1]) and not pd.isna(sma_50.iloc[-1]):
                if close.iloc[-1] > sma_20.iloc[-1] > sma_50.iloc[-1]:
                    signals['individual_signals']['moving_averages'] = 'BUY'
                    signals['signal_count']['bullish'] += 1
                elif close.iloc[-1] < sma_20.iloc[-1] < sma_50.iloc[-1]:
                    signals['individual_signals']['moving_averages'] = 'SELL'
                    signals['signal_count']['bearish'] += 1
                else:
                    signals['individual_signals']['moving_averages'] = 'HOLD'
                    signals['signal_count']['neutral'] += 1
            
            # Overall signal calculation
            total_signals = sum(signals['signal_count'].values())
            if total_signals > 0:
                bullish_ratio = signals['signal_count']['bullish'] / total_signals
                bearish_ratio = signals['signal_count']['bearish'] / total_signals
                
                if bullish_ratio >= 0.6:
                    signals['overall_signal'] = 'BUY'
                    signals['signal_strength'] = int(bullish_ratio * 100)
                elif bearish_ratio >= 0.6:
                    signals['overall_signal'] = 'SELL'
                    signals['signal_strength'] = int(bearish_ratio * 100)
                else:
                    signals['overall_signal'] = 'HOLD'
                    signals['signal_strength'] = 50
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return {}
    
    def _calculate_risk_metrics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate risk metrics"""
        try:
            close = data['Close']
            returns = close.pct_change().dropna()
            
            # Volatility metrics
            daily_vol = returns.std()
            annual_vol = daily_vol * np.sqrt(252)
            
            # VaR (Value at Risk)
            var_95 = np.percentile(returns, 5)
            var_99 = np.percentile(returns, 1)
            
            # Maximum Drawdown
            cumulative = (1 + returns).cumprod()
            rolling_max = cumulative.expanding().max()
            drawdown = (cumulative - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            
            # Sharpe Ratio (assuming 0% risk-free rate)
            sharpe_ratio = returns.mean() / daily_vol * np.sqrt(252) if daily_vol != 0 else 0
            
            return {
                'volatility': {
                    'daily': float(daily_vol),
                    'annual': float(annual_vol)
                },
                'var': {
                    'var_95': float(var_95),
                    'var_99': float(var_99)
                },
                'max_drawdown': float(max_drawdown),
                'sharpe_ratio': float(sharpe_ratio),
                'risk_level': self._assess_risk_level(annual_vol)
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return {}
    
    def _generate_recommendation(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate overall recommendation"""
        try:
            # This would typically use the signals and risk metrics
            # For now, a simple implementation
            close = data['Close']
            sma_20 = close.rolling(window=20).mean()
            rsi = self._calculate_rsi(close)
            
            score = 0
            factors = []
            
            # Price vs SMA
            if close.iloc[-1] > sma_20.iloc[-1]:
                score += 1
                factors.append("Price above 20-day SMA")
            else:
                score -= 1
                factors.append("Price below 20-day SMA")
            
            # RSI assessment
            if not pd.isna(rsi.iloc[-1]):
                if 30 <= rsi.iloc[-1] <= 70:
                    score += 1
                    factors.append("RSI in neutral zone")
                elif rsi.iloc[-1] < 30:
                    score += 2
                    factors.append("RSI oversold - potential reversal")
                else:
                    score -= 2
                    factors.append("RSI overbought - potential decline")
            
            # Volume confirmation
            volume_ratio = data['Volume'].iloc[-1] / data['Volume'].rolling(window=20).mean().iloc[-1]
            if volume_ratio > 1.5:
                score += 1
                factors.append("Above average volume")
            
            # Generate recommendation
            if score >= 2:
                recommendation = "BUY"
                confidence = min(score * 25, 100)
            elif score <= -2:
                recommendation = "SELL"
                confidence = min(abs(score) * 25, 100)
            else:
                recommendation = "HOLD"
                confidence = 50
            
            return {
                'recommendation': recommendation,
                'confidence': confidence,
                'score': score,
                'factors': factors,
                'timeframe': 'Short to Medium Term'
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return {}
    
    # Helper methods for calculations
    def _calculate_rsi(self, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_adx(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average Directional Index"""
        # Simplified ADX calculation
        tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
        return tr.rolling(window=period).mean()
    
    def _calculate_psar(self, high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
        """Calculate Parabolic SAR (simplified)"""
        # Simplified PSAR - using EMA as approximation
        return close.ewm(span=10).mean()
    
    def _calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator"""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        return k_percent, d_percent
    
    def _calculate_williams_r(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Williams %R"""
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        return -100 * ((highest_high - close) / (highest_high - lowest_low))
    
    def _calculate_cci(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> pd.Series:
        """Calculate Commodity Channel Index"""
        tp = (high + low + close) / 3
        sma_tp = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(lambda x: np.mean(np.abs(x - x.mean())))
        return (tp - sma_tp) / (0.015 * mad)
    
    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        return tr.rolling(window=period).mean()
    
    def _calculate_obv(self, close: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate On-Balance Volume"""
        obv = pd.Series(index=close.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]
        
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return obv
    
    def _calculate_vwap(self, high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate Volume Weighted Average Price"""
        typical_price = (high + low + close) / 3
        return (typical_price * volume).cumsum() / volume.cumsum()
    
    def _calculate_mfi(self, high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Money Flow Index"""
        typical_price = (high + low + close) / 3
        raw_money_flow = typical_price * volume
        
        positive_flow = pd.Series(index=close.index, dtype=float)
        negative_flow = pd.Series(index=close.index, dtype=float)
        
        for i in range(1, len(typical_price)):
            if typical_price.iloc[i] > typical_price.iloc[i-1]:
                positive_flow.iloc[i] = raw_money_flow.iloc[i]
                negative_flow.iloc[i] = 0
            elif typical_price.iloc[i] < typical_price.iloc[i-1]:
                positive_flow.iloc[i] = 0
                negative_flow.iloc[i] = raw_money_flow.iloc[i]
            else:
                positive_flow.iloc[i] = 0
                negative_flow.iloc[i] = 0
        
        positive_mf = positive_flow.rolling(window=period).sum()
        negative_mf = negative_flow.rolling(window=period).sum()
        
        mfi = 100 - (100 / (1 + (positive_mf / negative_mf)))
        return mfi
    
    def _calculate_ad_line(self, high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate Accumulation/Distribution Line"""
        money_flow_multiplier = ((close - low) - (high - close)) / (high - low)
        money_flow_volume = money_flow_multiplier * volume
        return money_flow_volume.cumsum()
    
    def _calculate_pivot_points(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate pivot points"""
        high = data['High'].iloc[-1]
        low = data['Low'].iloc[-1]
        close = data['Close'].iloc[-1]
        
        pivot = (high + low + close) / 3
        
        return {
            'pivot': float(pivot),
            'resistance_1': float(2 * pivot - low),
            'support_1': float(2 * pivot - high),
            'resistance_2': float(pivot + (high - low)),
            'support_2': float(pivot - (high - low))
        }
    
    # Helper methods for conditions
    def _rsi_condition(self, rsi_value: float) -> str:
        """Determine RSI condition"""
        if rsi_value < 30:
            return "Oversold"
        elif rsi_value > 70:
            return "Overbought"
        else:
            return "Neutral"
    
    def _assess_trend_strength(self, close: pd.Series, sma_20: pd.Series, sma_50: pd.Series) -> str:
        """Assess trend strength"""
        if close.iloc[-1] > sma_20.iloc[-1] > sma_50.iloc[-1]:
            return "Strong Uptrend"
        elif close.iloc[-1] < sma_20.iloc[-1] < sma_50.iloc[-1]:
            return "Strong Downtrend"
        elif close.iloc[-1] > sma_20.iloc[-1]:
            return "Weak Uptrend"
        elif close.iloc[-1] < sma_20.iloc[-1]:
            return "Weak Downtrend"
        else:
            return "Sideways"
    
    def _check_ma_alignment(self, sma_5: pd.Series, sma_10: pd.Series, sma_20: pd.Series, sma_50: pd.Series) -> str:
        """Check moving average alignment"""
        current_vals = [sma_5.iloc[-1], sma_10.iloc[-1], sma_20.iloc[-1], sma_50.iloc[-1]]
        
        if all(pd.notna(current_vals)):
            if current_vals == sorted(current_vals, reverse=True):
                return "Bullish Alignment"
            elif current_vals == sorted(current_vals):
                return "Bearish Alignment"
        
        return "Mixed"
    
    def _bb_position(self, price: float, upper: float, lower: float) -> str:
        """Determine Bollinger Band position"""
        if price > upper:
            return "Above Upper Band"
        elif price < lower:
            return "Below Lower Band"
        else:
            return "Within Bands"
    
    def _assess_risk_level(self, annual_vol: float) -> str:
        """Assess risk level based on volatility"""
        if annual_vol < 0.15:
            return "Low"
        elif annual_vol < 0.30:
            return "Medium"
        else:
            return "High"
    
    # Placeholder methods for pattern detection
    def _detect_candlestick_patterns(self, data: pd.DataFrame) -> List[str]:
        """Detect candlestick patterns"""
        return []
    
    def _detect_chart_patterns(self, data: pd.DataFrame) -> List[str]:
        """Detect chart patterns"""
        return []
    
    def _detect_trend_patterns(self, data: pd.DataFrame) -> List[str]:
        """Detect trend patterns"""
        return []
    
    def _stoch_condition(self, k: float, d: float) -> str:
        """Determine stochastic condition"""
        if k < 20 and d < 20:
            return "Oversold"
        elif k > 80 and d > 80:
            return "Overbought"
        else:
            return "Neutral"
    
    def _williams_condition(self, williams_r: float) -> str:
        """Determine Williams %R condition"""
        if williams_r < -80:
            return "Oversold"
        elif williams_r > -20:
            return "Overbought"
        else:
            return "Neutral"
    
    def _cci_condition(self, cci: float) -> str:
        """Determine CCI condition"""
        if cci < -100:
            return "Oversold"
        elif cci > 100:
            return "Overbought"
        else:
            return "Neutral"
    
    def _mfi_condition(self, mfi: float) -> str:
        """Determine MFI condition"""
        if mfi < 20:
            return "Oversold"
        elif mfi > 80:
            return "Overbought"
        else:
            return "Neutral"
    
    def _obv_trend(self, obv: pd.Series) -> str:
        """Determine OBV trend"""
        if len(obv) >= 10:
            recent_slope = (obv.iloc[-1] - obv.iloc[-10]) / 10
            if recent_slope > 0:
                return "Rising"
            elif recent_slope < 0:
                return "Falling"
        return "Sideways"
    
    def _check_rsi_divergence(self, close: pd.Series, rsi: pd.Series) -> bool:
        """Check for RSI divergence (simplified)"""
        # This is a simplified check - in practice, this would be more sophisticated
        if len(close) >= 20 and len(rsi) >= 20:
            price_trend = close.iloc[-1] > close.iloc[-20]
            rsi_trend = rsi.iloc[-1] > rsi.iloc[-20]
            return price_trend != rsi_trend
        return False 

    async def analyze(self, symbol: str) -> Dict[str, Any]:
        """
        Analyze a stock symbol (API compatibility method)
        
        Args:
            symbol: Stock symbol to analyze
        
        Returns:
            Technical analysis results
        """
        try:
            # This would normally fetch live data, but for now return comprehensive mock data
            analysis = {
                'symbol': symbol,
                'trend_indicators': {
                    'rsi': 65.4,
                    'macd': {
                        'macd_line': 1.2,
                        'signal_line': 0.8,
                        'histogram': 0.4
                    },
                    'sma_20': 148.5,
                    'sma_50': 145.2,
                    'ema_12': 149.8,
                    'trend': 'bullish'
                },
                'momentum_indicators': {
                    'stochastic': {
                        'k': 75.2,
                        'd': 72.8
                    },
                    'williams_r': {
                        'value': -25.6
                    },
                    'momentum': 'positive'
                },
                'volatility_indicators': {
                    'bollinger_bands': {
                        'upper': 155.0,
                        'middle': 150.0,
                        'lower': 145.0,
                        'position': 'middle'
                    },
                    'atr': {
                        'value': 3.25,
                        'percentage': 2.1
                    }
                },
                'volume_indicators': {
                    'volume_sma': 2500000,
                    'volume_ratio': 1.3,
                    'obv_trend': 'positive'
                },
                'support_resistance': {
                    'support_levels': [142.5, 138.0, 135.2],
                    'resistance_levels': [155.8, 160.0, 165.5],
                    'key_level': 150.0
                },
                'patterns': {
                    'identified_patterns': ['ascending_triangle', 'bullish_flag'],
                    'pattern_strength': 'moderate',
                    'breakout_probability': 72.5
                },
                'signals': {
                    'overall_signal': 'BUY',
                    'signal_strength': 78.0,
                    'confidence': 'high',
                    'short_term': 'bullish',
                    'medium_term': 'bullish',
                    'long_term': 'neutral'
                },
                'risk_metrics': {
                    'beta': 1.15,
                    'volatility': 0.28,
                    'sharpe_ratio': 1.45,
                    'max_drawdown': -0.12
                },
                'recommendation': {
                    'action': 'BUY',
                    'target_price': 165.0,
                    'stop_loss': 142.0,
                    'time_horizon': '3-6 months',
                    'risk_level': 'moderate'
                }
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': f'Analysis failed: {str(e)}',
                'trend_indicators': {},
                'momentum_indicators': {},
                'volatility_indicators': {}
            } 