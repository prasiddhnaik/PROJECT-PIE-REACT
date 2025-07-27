"""
Pattern Scanner Module
=====================

Comprehensive pattern detection system:
- Chart patterns (triangles, flags, head & shoulders, etc.)
- Candlestick patterns (doji, hammer, engulfing, etc.)
- Volume patterns
- Support/Resistance patterns
- Trend line patterns
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime
from scipy.signal import argrelextrema
from scipy.stats import linregress

logger = logging.getLogger(__name__)

class PatternScanner:
    """
    Advanced pattern detection and analysis
    """
    
    def __init__(self):
        self.min_pattern_length = 5
        self.max_pattern_length = 50
        self.tolerance = 0.02  # 2% tolerance for pattern matching
        
    def scan_all_patterns(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """
        Scan for all types of patterns in the data
        
        Args:
            data: OHLCV DataFrame
            symbol: Stock symbol
        
        Returns:
            Dictionary containing all detected patterns
        """
        try:
            patterns = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'chart_patterns': self._detect_chart_patterns(data),
                'candlestick_patterns': self._detect_candlestick_patterns(data),
                'volume_patterns': self._detect_volume_patterns(data),
                'support_resistance': self._detect_support_resistance_patterns(data),
                'trend_patterns': self._detect_trend_patterns(data),
                'harmonic_patterns': self._detect_harmonic_patterns(data),
                'pattern_summary': self._summarize_patterns(data)
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error scanning patterns for {symbol}: {e}")
            return {'error': str(e)}
    
    def _detect_chart_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect classic chart patterns"""
        patterns = []
        
        try:
            # Triangle Patterns
            triangle_patterns = self._detect_triangles(data)
            patterns.extend(triangle_patterns)
            
            # Flag and Pennant Patterns
            flag_patterns = self._detect_flags(data)
            patterns.extend(flag_patterns)
            
            # Head and Shoulders
            hs_patterns = self._detect_head_shoulders(data)
            patterns.extend(hs_patterns)
            
            # Double Top/Bottom
            double_patterns = self._detect_double_patterns(data)
            patterns.extend(double_patterns)
            
            # Cup and Handle
            cup_patterns = self._detect_cup_handle(data)
            patterns.extend(cup_patterns)
            
            # Wedge Patterns
            wedge_patterns = self._detect_wedges(data)
            patterns.extend(wedge_patterns)
            
        except Exception as e:
            logger.error(f"Error detecting chart patterns: {e}")
        
        return patterns
    
    def _detect_candlestick_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect candlestick patterns"""
        patterns = []
        
        try:
            if len(data) < 3:
                return patterns
            
            # Single candlestick patterns
            patterns.extend(self._detect_single_candle_patterns(data))
            
            # Double candlestick patterns
            patterns.extend(self._detect_double_candle_patterns(data))
            
            # Triple candlestick patterns
            patterns.extend(self._detect_triple_candle_patterns(data))
            
        except Exception as e:
            logger.error(f"Error detecting candlestick patterns: {e}")
        
        return patterns
    
    def _detect_volume_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect volume-based patterns"""
        patterns = []
        
        try:
            volume = data['Volume']
            close = data['Close']
            
            # Volume spike pattern
            volume_avg = volume.rolling(window=20).mean()
            volume_spike = volume > (volume_avg * 2.5)
            
            for i in range(len(volume_spike)):
                if volume_spike.iloc[i]:
                    price_change = (close.iloc[i] - close.iloc[i-1]) / close.iloc[i-1] * 100 if i > 0 else 0
                    
                    patterns.append({
                        'pattern': 'Volume Spike',
                        'type': 'volume',
                        'date': data.index[i],
                        'strength': min(volume.iloc[i] / volume_avg.iloc[i] * 20, 100),
                        'description': f'Volume spike with {price_change:.1f}% price change',
                        'bullish': price_change > 0,
                        'details': {
                            'volume_ratio': float(volume.iloc[i] / volume_avg.iloc[i]),
                            'price_change': price_change
                        }
                    })
            
            # Volume divergence
            volume_trend = self._calculate_trend(volume.tail(10))
            price_trend = self._calculate_trend(close.tail(10))
            
            if (volume_trend > 0 and price_trend < 0) or (volume_trend < 0 and price_trend > 0):
                patterns.append({
                    'pattern': 'Volume Divergence',
                    'type': 'volume',
                    'date': data.index[-1],
                    'strength': 70,
                    'description': 'Volume and price moving in opposite directions',
                    'bullish': volume_trend > 0 and price_trend < 0,
                    'details': {
                        'volume_trend': volume_trend,
                        'price_trend': price_trend
                    }
                })
            
        except Exception as e:
            logger.error(f"Error detecting volume patterns: {e}")
        
        return patterns
    
    def _detect_support_resistance_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Detect support and resistance patterns"""
        try:
            high = data['High']
            low = data['Low']
            close = data['Close']
            
            # Find pivot points
            pivot_highs = self._find_pivot_highs(high)
            pivot_lows = self._find_pivot_lows(low)
            
            # Detect horizontal support/resistance
            support_levels = self._find_horizontal_levels(pivot_lows, close.iloc[-1])
            resistance_levels = self._find_horizontal_levels(pivot_highs, close.iloc[-1])
            
            # Detect trend lines
            support_trendlines = self._find_trendlines(pivot_lows, 'support')
            resistance_trendlines = self._find_trendlines(pivot_highs, 'resistance')
            
            return {
                'horizontal_support': support_levels,
                'horizontal_resistance': resistance_levels,
                'support_trendlines': support_trendlines,
                'resistance_trendlines': resistance_trendlines,
                'current_price': float(close.iloc[-1]),
                'nearest_support': min(support_levels, key=lambda x: abs(x - close.iloc[-1])) if support_levels else None,
                'nearest_resistance': min(resistance_levels, key=lambda x: abs(x - close.iloc[-1])) if resistance_levels else None
            }
            
        except Exception as e:
            logger.error(f"Error detecting support/resistance patterns: {e}")
            return {}
    
    def _detect_trend_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect trend-based patterns"""
        patterns = []
        
        try:
            close = data['Close']
            
            # Channel patterns
            channels = self._detect_channels(data)
            patterns.extend(channels)
            
            # Trend breaks
            trend_breaks = self._detect_trend_breaks(data)
            patterns.extend(trend_breaks)
            
            # Momentum divergence
            momentum_div = self._detect_momentum_divergence(data)
            patterns.extend(momentum_div)
            
        except Exception as e:
            logger.error(f"Error detecting trend patterns: {e}")
        
        return patterns
    
    def _detect_harmonic_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect harmonic patterns (simplified)"""
        patterns = []
        
        try:
            # Simplified ABCD pattern detection
            abcd_patterns = self._detect_abcd_patterns(data)
            patterns.extend(abcd_patterns)
            
            # Gartley pattern (simplified)
            gartley_patterns = self._detect_gartley_patterns(data)
            patterns.extend(gartley_patterns)
            
        except Exception as e:
            logger.error(f"Error detecting harmonic patterns: {e}")
        
        return patterns
    
    # Chart Pattern Detection Methods
    def _detect_triangles(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect triangle patterns"""
        patterns = []
        
        try:
            high = data['High']
            low = data['Low']
            
            if len(data) < 20:
                return patterns
            
            # Look for triangle patterns in the last 30 days
            window_data = data.tail(30)
            window_high = window_data['High']
            window_low = window_data['Low']
            
            # Find trend lines for highs and lows
            high_trend = self._fit_trendline(window_high)
            low_trend = self._fit_trendline(window_low)
            
            if high_trend and low_trend:
                high_slope = high_trend['slope']
                low_slope = low_trend['slope']
                
                # Ascending triangle: flat resistance, rising support
                if abs(high_slope) < 0.001 and low_slope > 0.001:
                    patterns.append({
                        'pattern': 'Ascending Triangle',
                        'type': 'continuation',
                        'date': data.index[-1],
                        'strength': 75,
                        'description': 'Bullish continuation pattern with flat resistance and rising support',
                        'bullish': True,
                        'target': window_high.max() * 1.05,
                        'stop_loss': low_trend['current_value'] * 0.98,
                        'details': {
                            'resistance_level': window_high.max(),
                            'support_slope': low_slope,
                            'duration_days': len(window_data)
                        }
                    })
                
                # Descending triangle: declining resistance, flat support
                elif high_slope < -0.001 and abs(low_slope) < 0.001:
                    patterns.append({
                        'pattern': 'Descending Triangle',
                        'type': 'continuation',
                        'date': data.index[-1],
                        'strength': 75,
                        'description': 'Bearish continuation pattern with declining resistance and flat support',
                        'bullish': False,
                        'target': window_low.min() * 0.95,
                        'stop_loss': high_trend['current_value'] * 1.02,
                        'details': {
                            'support_level': window_low.min(),
                            'resistance_slope': high_slope,
                            'duration_days': len(window_data)
                        }
                    })
                
                # Symmetrical triangle: converging trend lines
                elif high_slope < -0.001 and low_slope > 0.001:
                    patterns.append({
                        'pattern': 'Symmetrical Triangle',
                        'type': 'consolidation',
                        'date': data.index[-1],
                        'strength': 70,
                        'description': 'Consolidation pattern with converging trend lines',
                        'bullish': None,  # Direction depends on breakout
                        'details': {
                            'resistance_slope': high_slope,
                            'support_slope': low_slope,
                            'duration_days': len(window_data),
                            'apex_distance': self._calculate_apex_distance(high_trend, low_trend)
                        }
                    })
            
        except Exception as e:
            logger.error(f"Error detecting triangles: {e}")
        
        return patterns
    
    def _detect_flags(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect flag and pennant patterns"""
        patterns = []
        
        try:
            if len(data) < 15:
                return patterns
            
            close = data['Close']
            volume = data['Volume']
            
            # Look for strong move followed by consolidation
            for i in range(10, len(data) - 5):
                # Check for strong initial move (flagpole)
                flagpole_start = close.iloc[i-10]
                flagpole_end = close.iloc[i]
                flagpole_move = (flagpole_end - flagpole_start) / flagpole_start
                
                if abs(flagpole_move) > 0.08:  # 8% move
                    # Check for consolidation (flag)
                    flag_data = close.iloc[i:i+5]
                    flag_high = flag_data.max()
                    flag_low = flag_data.min()
                    flag_range = (flag_high - flag_low) / flag_high
                    
                    if flag_range < 0.05:  # Tight consolidation
                        # Check volume pattern (should decrease during flag)
                        flagpole_volume = volume.iloc[i-10:i].mean()
                        flag_volume = volume.iloc[i:i+5].mean()
                        volume_decline = flag_volume < flagpole_volume * 0.8
                        
                        pattern_type = 'Bull Flag' if flagpole_move > 0 else 'Bear Flag'
                        
                        patterns.append({
                            'pattern': pattern_type,
                            'type': 'continuation',
                            'date': data.index[i+5],
                            'strength': 80 if volume_decline else 65,
                            'description': f'{pattern_type} - continuation pattern after {flagpole_move*100:.1f}% move',
                            'bullish': flagpole_move > 0,
                            'target': flagpole_end + flagpole_move * flagpole_end,
                            'stop_loss': flag_low * 0.98 if flagpole_move > 0 else flag_high * 1.02,
                            'details': {
                                'flagpole_move_percent': flagpole_move * 100,
                                'flag_range_percent': flag_range * 100,
                                'volume_confirmation': volume_decline,
                                'flag_duration': 5
                            }
                        })
            
        except Exception as e:
            logger.error(f"Error detecting flags: {e}")
        
        return patterns
    
    def _detect_head_shoulders(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect head and shoulders patterns"""
        patterns = []
        
        try:
            if len(data) < 30:
                return patterns
            
            high = data['High']
            low = data['Low']
            
            # Find pivot highs for head and shoulders
            pivot_highs = self._find_pivot_highs(high, window=5)
            pivot_lows = self._find_pivot_lows(low, window=5)
            
            if len(pivot_highs) >= 3:
                # Look for head and shoulders pattern
                for i in range(1, len(pivot_highs) - 1):
                    left_shoulder = pivot_highs[i-1]
                    head = pivot_highs[i]
                    right_shoulder = pivot_highs[i+1]
                    
                    # Check if head is higher than both shoulders
                    if (head['value'] > left_shoulder['value'] * 1.02 and 
                        head['value'] > right_shoulder['value'] * 1.02):
                        
                        # Check if shoulders are roughly equal
                        shoulder_diff = abs(left_shoulder['value'] - right_shoulder['value']) / left_shoulder['value']
                        
                        if shoulder_diff < 0.05:  # Shoulders within 5% of each other
                            # Find neckline
                            neckline = self._find_neckline(left_shoulder, right_shoulder, pivot_lows)
                            
                            if neckline:
                                patterns.append({
                                    'pattern': 'Head and Shoulders',
                                    'type': 'reversal',
                                    'date': data.index[right_shoulder['index']],
                                    'strength': 85,
                                    'description': 'Bearish reversal pattern with clear head and shoulders formation',
                                    'bullish': False,
                                    'target': neckline - (head['value'] - neckline),
                                    'stop_loss': right_shoulder['value'] * 1.02,
                                    'details': {
                                        'left_shoulder': left_shoulder['value'],
                                        'head': head['value'],
                                        'right_shoulder': right_shoulder['value'],
                                        'neckline': neckline,
                                        'pattern_height': head['value'] - neckline
                                    }
                                })
            
            # Inverse head and shoulders (using pivot lows)
            if len(pivot_lows) >= 3:
                for i in range(1, len(pivot_lows) - 1):
                    left_shoulder = pivot_lows[i-1]
                    head = pivot_lows[i]
                    right_shoulder = pivot_lows[i+1]
                    
                    # Check if head is lower than both shoulders
                    if (head['value'] < left_shoulder['value'] * 0.98 and 
                        head['value'] < right_shoulder['value'] * 0.98):
                        
                        shoulder_diff = abs(left_shoulder['value'] - right_shoulder['value']) / left_shoulder['value']
                        
                        if shoulder_diff < 0.05:
                            neckline = self._find_neckline_inverse(left_shoulder, right_shoulder, pivot_highs)
                            
                            if neckline:
                                patterns.append({
                                    'pattern': 'Inverse Head and Shoulders',
                                    'type': 'reversal',
                                    'date': data.index[right_shoulder['index']],
                                    'strength': 85,
                                    'description': 'Bullish reversal pattern with inverse head and shoulders formation',
                                    'bullish': True,
                                    'target': neckline + (neckline - head['value']),
                                    'stop_loss': right_shoulder['value'] * 0.98,
                                    'details': {
                                        'left_shoulder': left_shoulder['value'],
                                        'head': head['value'],
                                        'right_shoulder': right_shoulder['value'],
                                        'neckline': neckline,
                                        'pattern_height': neckline - head['value']
                                    }
                                })
            
        except Exception as e:
            logger.error(f"Error detecting head and shoulders: {e}")
        
        return patterns
    
    def _detect_double_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect double top and double bottom patterns"""
        patterns = []
        
        try:
            if len(data) < 20:
                return patterns
            
            high = data['High']
            low = data['Low']
            
            # Find pivot points
            pivot_highs = self._find_pivot_highs(high, window=5)
            pivot_lows = self._find_pivot_lows(low, window=5)
            
            # Double top detection
            for i in range(len(pivot_highs) - 1):
                first_peak = pivot_highs[i]
                for j in range(i + 1, len(pivot_highs)):
                    second_peak = pivot_highs[j]
                    
                    # Check if peaks are roughly equal
                    peak_diff = abs(first_peak['value'] - second_peak['value']) / first_peak['value']
                    
                    if peak_diff < 0.03 and (second_peak['index'] - first_peak['index']) > 10:
                        # Find valley between peaks
                        valley_data = low.iloc[first_peak['index']:second_peak['index']]
                        valley_min = valley_data.min()
                        
                        # Check if valley is significantly lower than peaks
                        if valley_min < first_peak['value'] * 0.95:
                            patterns.append({
                                'pattern': 'Double Top',
                                'type': 'reversal',
                                'date': data.index[second_peak['index']],
                                'strength': 80,
                                'description': 'Bearish reversal pattern with two equal peaks',
                                'bullish': False,
                                'target': valley_min - (first_peak['value'] - valley_min) * 0.5,
                                'stop_loss': second_peak['value'] * 1.02,
                                'details': {
                                    'first_peak': first_peak['value'],
                                    'second_peak': second_peak['value'],
                                    'valley': valley_min,
                                    'peak_separation_days': second_peak['index'] - first_peak['index']
                                }
                            })
                        break
            
            # Double bottom detection
            for i in range(len(pivot_lows) - 1):
                first_trough = pivot_lows[i]
                for j in range(i + 1, len(pivot_lows)):
                    second_trough = pivot_lows[j]
                    
                    trough_diff = abs(first_trough['value'] - second_trough['value']) / first_trough['value']
                    
                    if trough_diff < 0.03 and (second_trough['index'] - first_trough['index']) > 10:
                        # Find peak between troughs
                        peak_data = high.iloc[first_trough['index']:second_trough['index']]
                        peak_max = peak_data.max()
                        
                        if peak_max > first_trough['value'] * 1.05:
                            patterns.append({
                                'pattern': 'Double Bottom',
                                'type': 'reversal',
                                'date': data.index[second_trough['index']],
                                'strength': 80,
                                'description': 'Bullish reversal pattern with two equal troughs',
                                'bullish': True,
                                'target': peak_max + (peak_max - first_trough['value']) * 0.5,
                                'stop_loss': second_trough['value'] * 0.98,
                                'details': {
                                    'first_trough': first_trough['value'],
                                    'second_trough': second_trough['value'],
                                    'peak': peak_max,
                                    'trough_separation_days': second_trough['index'] - first_trough['index']
                                }
                            })
                        break
            
        except Exception as e:
            logger.error(f"Error detecting double patterns: {e}")
        
        return patterns
    
    # Candlestick Pattern Detection Methods
    def _detect_single_candle_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect single candlestick patterns"""
        patterns = []
        
        try:
            for i in range(len(data)):
                candle = data.iloc[i]
                pattern_info = self._analyze_single_candle(candle, i, data)
                
                if pattern_info:
                    patterns.append({
                        'pattern': pattern_info['name'],
                        'type': 'candlestick',
                        'date': data.index[i],
                        'strength': pattern_info['strength'],
                        'description': pattern_info['description'],
                        'bullish': pattern_info['bullish'],
                        'details': pattern_info['details']
                    })
            
        except Exception as e:
            logger.error(f"Error detecting single candle patterns: {e}")
        
        return patterns
    
    def _detect_double_candle_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect double candlestick patterns"""
        patterns = []
        
        try:
            for i in range(1, len(data)):
                prev_candle = data.iloc[i-1]
                curr_candle = data.iloc[i]
                
                pattern_info = self._analyze_double_candle(prev_candle, curr_candle, i, data)
                
                if pattern_info:
                    patterns.append({
                        'pattern': pattern_info['name'],
                        'type': 'candlestick',
                        'date': data.index[i],
                        'strength': pattern_info['strength'],
                        'description': pattern_info['description'],
                        'bullish': pattern_info['bullish'],
                        'details': pattern_info['details']
                    })
            
        except Exception as e:
            logger.error(f"Error detecting double candle patterns: {e}")
        
        return patterns
    
    def _detect_triple_candle_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect triple candlestick patterns"""
        patterns = []
        
        try:
            for i in range(2, len(data)):
                candle1 = data.iloc[i-2]
                candle2 = data.iloc[i-1]
                candle3 = data.iloc[i]
                
                pattern_info = self._analyze_triple_candle(candle1, candle2, candle3, i, data)
                
                if pattern_info:
                    patterns.append({
                        'pattern': pattern_info['name'],
                        'type': 'candlestick',
                        'date': data.index[i],
                        'strength': pattern_info['strength'],
                        'description': pattern_info['description'],
                        'bullish': pattern_info['bullish'],
                        'details': pattern_info['details']
                    })
            
        except Exception as e:
            logger.error(f"Error detecting triple candle patterns: {e}")
        
        return patterns
    
    # Helper Methods
    def _analyze_single_candle(self, candle: pd.Series, index: int, data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Analyze single candlestick for patterns"""
        try:
            open_price = candle['Open']
            high_price = candle['High']
            low_price = candle['Low']
            close_price = candle['Close']
            
            body = abs(close_price - open_price)
            total_range = high_price - low_price
            upper_shadow = high_price - max(open_price, close_price)
            lower_shadow = min(open_price, close_price) - low_price
            
            # Avoid division by zero
            if total_range == 0:
                return None
            
            # Doji pattern
            if body <= total_range * 0.05:  # Body is less than 5% of total range
                return {
                    'name': 'Doji',
                    'strength': 70,
                    'description': 'Indecision pattern with small body',
                    'bullish': None,  # Neutral
                    'details': {
                        'body_size': body,
                        'total_range': total_range,
                        'body_percentage': (body / total_range) * 100
                    }
                }
            
            # Hammer pattern
            if (lower_shadow >= body * 2 and 
                upper_shadow <= body * 0.3 and 
                close_price < open_price):  # Bearish body
                
                # Context check - should be in downtrend
                if index >= 5:
                    recent_trend = self._calculate_trend(data['Close'].iloc[index-5:index])
                    if recent_trend < -0.01:  # Downtrend
                        return {
                            'name': 'Hammer',
                            'strength': 75,
                            'description': 'Bullish reversal pattern with long lower shadow',
                            'bullish': True,
                            'details': {
                                'lower_shadow_ratio': lower_shadow / body,
                                'body_size': body,
                                'trend_context': recent_trend
                            }
                        }
            
            # Shooting Star pattern
            if (upper_shadow >= body * 2 and 
                lower_shadow <= body * 0.3 and 
                close_price < open_price):  # Bearish body
                
                if index >= 5:
                    recent_trend = self._calculate_trend(data['Close'].iloc[index-5:index])
                    if recent_trend > 0.01:  # Uptrend
                        return {
                            'name': 'Shooting Star',
                            'strength': 75,
                            'description': 'Bearish reversal pattern with long upper shadow',
                            'bullish': False,
                            'details': {
                                'upper_shadow_ratio': upper_shadow / body,
                                'body_size': body,
                                'trend_context': recent_trend
                            }
                        }
            
            # Spinning Top
            if (body <= total_range * 0.3 and 
                upper_shadow >= body * 0.5 and 
                lower_shadow >= body * 0.5):
                return {
                    'name': 'Spinning Top',
                    'strength': 60,
                    'description': 'Indecision pattern with small body and long shadows',
                    'bullish': None,
                    'details': {
                        'body_percentage': (body / total_range) * 100,
                        'upper_shadow': upper_shadow,
                        'lower_shadow': lower_shadow
                    }
                }
            
        except Exception as e:
            logger.error(f"Error analyzing single candle: {e}")
        
        return None
    
    def _analyze_double_candle(self, prev_candle: pd.Series, curr_candle: pd.Series, 
                              index: int, data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Analyze double candlestick patterns"""
        try:
            # Bullish Engulfing
            if (prev_candle['Close'] < prev_candle['Open'] and  # Previous bearish
                curr_candle['Close'] > curr_candle['Open'] and  # Current bullish
                curr_candle['Open'] < prev_candle['Close'] and  # Gap down or overlap
                curr_candle['Close'] > prev_candle['Open']):    # Engulfs previous body
                
                return {
                    'name': 'Bullish Engulfing',
                    'strength': 80,
                    'description': 'Bullish reversal pattern engulfing previous bearish candle',
                    'bullish': True,
                    'details': {
                        'prev_body': abs(prev_candle['Close'] - prev_candle['Open']),
                        'curr_body': abs(curr_candle['Close'] - curr_candle['Open']),
                        'engulfing_ratio': abs(curr_candle['Close'] - curr_candle['Open']) / abs(prev_candle['Close'] - prev_candle['Open'])
                    }
                }
            
            # Bearish Engulfing
            if (prev_candle['Close'] > prev_candle['Open'] and  # Previous bullish
                curr_candle['Close'] < curr_candle['Open'] and  # Current bearish
                curr_candle['Open'] > prev_candle['Close'] and  # Gap up or overlap
                curr_candle['Close'] < prev_candle['Open']):    # Engulfs previous body
                
                return {
                    'name': 'Bearish Engulfing',
                    'strength': 80,
                    'description': 'Bearish reversal pattern engulfing previous bullish candle',
                    'bullish': False,
                    'details': {
                        'prev_body': abs(prev_candle['Close'] - prev_candle['Open']),
                        'curr_body': abs(curr_candle['Close'] - curr_candle['Open']),
                        'engulfing_ratio': abs(curr_candle['Close'] - curr_candle['Open']) / abs(prev_candle['Close'] - prev_candle['Open'])
                    }
                }
            
            # Piercing Pattern
            if (prev_candle['Close'] < prev_candle['Open'] and  # Previous bearish
                curr_candle['Close'] > curr_candle['Open'] and  # Current bullish
                curr_candle['Open'] < prev_candle['Low'] and    # Gap down
                curr_candle['Close'] > (prev_candle['Open'] + prev_candle['Close']) / 2):  # Closes above midpoint
                
                return {
                    'name': 'Piercing Pattern',
                    'strength': 75,
                    'description': 'Bullish reversal pattern piercing into previous bearish candle',
                    'bullish': True,
                    'details': {
                        'gap_size': prev_candle['Low'] - curr_candle['Open'],
                        'penetration': curr_candle['Close'] - ((prev_candle['Open'] + prev_candle['Close']) / 2)
                    }
                }
            
            # Dark Cloud Cover
            if (prev_candle['Close'] > prev_candle['Open'] and  # Previous bullish
                curr_candle['Close'] < curr_candle['Open'] and  # Current bearish
                curr_candle['Open'] > prev_candle['High'] and   # Gap up
                curr_candle['Close'] < (prev_candle['Open'] + prev_candle['Close']) / 2):  # Closes below midpoint
                
                return {
                    'name': 'Dark Cloud Cover',
                    'strength': 75,
                    'description': 'Bearish reversal pattern covering previous bullish candle',
                    'bullish': False,
                    'details': {
                        'gap_size': curr_candle['Open'] - prev_candle['High'],
                        'penetration': ((prev_candle['Open'] + prev_candle['Close']) / 2) - curr_candle['Close']
                    }
                }
            
        except Exception as e:
            logger.error(f"Error analyzing double candle: {e}")
        
        return None
    
    def _analyze_triple_candle(self, candle1: pd.Series, candle2: pd.Series, candle3: pd.Series,
                              index: int, data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Analyze triple candlestick patterns"""
        try:
            # Morning Star
            if (candle1['Close'] < candle1['Open'] and  # First candle bearish
                abs(candle2['Close'] - candle2['Open']) < abs(candle1['Close'] - candle1['Open']) * 0.3 and  # Small second candle
                candle3['Close'] > candle3['Open'] and  # Third candle bullish
                candle3['Close'] > (candle1['Open'] + candle1['Close']) / 2):  # Third closes above first midpoint
                
                return {
                    'name': 'Morning Star',
                    'strength': 85,
                    'description': 'Strong bullish reversal pattern with three candles',
                    'bullish': True,
                    'details': {
                        'first_candle_body': abs(candle1['Close'] - candle1['Open']),
                        'second_candle_body': abs(candle2['Close'] - candle2['Open']),
                        'third_candle_body': abs(candle3['Close'] - candle3['Open']),
                        'reversal_strength': candle3['Close'] - candle1['Close']
                    }
                }
            
            # Evening Star
            if (candle1['Close'] > candle1['Open'] and  # First candle bullish
                abs(candle2['Close'] - candle2['Open']) < abs(candle1['Close'] - candle1['Open']) * 0.3 and  # Small second candle
                candle3['Close'] < candle3['Open'] and  # Third candle bearish
                candle3['Close'] < (candle1['Open'] + candle1['Close']) / 2):  # Third closes below first midpoint
                
                return {
                    'name': 'Evening Star',
                    'strength': 85,
                    'description': 'Strong bearish reversal pattern with three candles',
                    'bullish': False,
                    'details': {
                        'first_candle_body': abs(candle1['Close'] - candle1['Open']),
                        'second_candle_body': abs(candle2['Close'] - candle2['Open']),
                        'third_candle_body': abs(candle3['Close'] - candle3['Open']),
                        'reversal_strength': candle1['Close'] - candle3['Close']
                    }
                }
            
            # Three White Soldiers
            if (candle1['Close'] > candle1['Open'] and  # All three bullish
                candle2['Close'] > candle2['Open'] and
                candle3['Close'] > candle3['Open'] and
                candle2['Close'] > candle1['Close'] and  # Each closes higher
                candle3['Close'] > candle2['Close'] and
                candle2['Open'] > candle1['Open'] and   # Each opens higher
                candle3['Open'] > candle2['Open']):
                
                return {
                    'name': 'Three White Soldiers',
                    'strength': 90,
                    'description': 'Very strong bullish continuation pattern',
                    'bullish': True,
                    'details': {
                        'total_advance': candle3['Close'] - candle1['Open'],
                        'consistency': True,
                        'momentum': 'Strong'
                    }
                }
            
            # Three Black Crows
            if (candle1['Close'] < candle1['Open'] and  # All three bearish
                candle2['Close'] < candle2['Open'] and
                candle3['Close'] < candle3['Open'] and
                candle2['Close'] < candle1['Close'] and  # Each closes lower
                candle3['Close'] < candle2['Close'] and
                candle2['Open'] < candle1['Open'] and   # Each opens lower
                candle3['Open'] < candle2['Open']):
                
                return {
                    'name': 'Three Black Crows',
                    'strength': 90,
                    'description': 'Very strong bearish continuation pattern',
                    'bullish': False,
                    'details': {
                        'total_decline': candle1['Open'] - candle3['Close'],
                        'consistency': True,
                        'momentum': 'Strong'
                    }
                }
            
        except Exception as e:
            logger.error(f"Error analyzing triple candle: {e}")
        
        return None
    
    # Additional Helper Methods
    def _summarize_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Summarize all detected patterns"""
        try:
            # This would typically aggregate all patterns found
            return {
                'total_patterns_found': 0,  # Would be calculated from all patterns
                'pattern_strength_average': 0,
                'bullish_patterns': 0,
                'bearish_patterns': 0,
                'neutral_patterns': 0,
                'most_recent_pattern': None,
                'strongest_pattern': None
            }
        except Exception as e:
            logger.error(f"Error summarizing patterns: {e}")
            return {}
    
    # Placeholder methods for complex calculations
    def _find_pivot_highs(self, data: pd.Series, window: int = 5) -> List[Dict[str, Any]]:
        """Find pivot high points"""
        # Simplified implementation
        pivots = []
        for i in range(window, len(data) - window):
            if all(data.iloc[i] >= data.iloc[j] for j in range(i-window, i+window+1) if j != i):
                pivots.append({'index': i, 'value': data.iloc[i]})
        return pivots
    
    def _find_pivot_lows(self, data: pd.Series, window: int = 5) -> List[Dict[str, Any]]:
        """Find pivot low points"""
        # Simplified implementation
        pivots = []
        for i in range(window, len(data) - window):
            if all(data.iloc[i] <= data.iloc[j] for j in range(i-window, i+window+1) if j != i):
                pivots.append({'index': i, 'value': data.iloc[i]})
        return pivots
    
    def _calculate_trend(self, data: pd.Series) -> float:
        """Calculate trend slope"""
        try:
            if len(data) < 2:
                return 0
            x = np.arange(len(data))
            slope, _, _, _, _ = linregress(x, data.values)
            return slope
        except:
            return 0
    
    def _fit_trendline(self, data: pd.Series) -> Optional[Dict[str, Any]]:
        """Fit trendline to data"""
        try:
            if len(data) < 2:
                return None
            x = np.arange(len(data))
            slope, intercept, r_value, _, _ = linregress(x, data.values)
            current_value = slope * (len(data) - 1) + intercept
            return {
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_value**2,
                'current_value': current_value
            }
        except:
            return None
    
    # Additional placeholder methods
    def _detect_channels(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        return []
    
    def _detect_trend_breaks(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        return []
    
    def _detect_momentum_divergence(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        return []
    
    def _detect_abcd_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        return []
    
    def _detect_gartley_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        return []
    
    def _detect_cup_handle(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        return []
    
    def _detect_wedges(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        return []
    
    def _find_horizontal_levels(self, pivot_points: List[Dict[str, Any]], current_price: float) -> List[float]:
        """Find horizontal support/resistance levels"""
        levels = []
        for pivot in pivot_points:
            levels.append(pivot['value'])
        return list(set(levels))  # Remove duplicates
    
    def _find_trendlines(self, pivot_points: List[Dict[str, Any]], line_type: str) -> List[Dict[str, Any]]:
        """Find trend lines"""
        return []  # Simplified
    
    def _find_neckline(self, left_shoulder: Dict, right_shoulder: Dict, pivot_lows: List[Dict]) -> Optional[float]:
        """Find neckline for head and shoulders"""
        # Simplified - would find the connecting line between shoulders
        return (left_shoulder['value'] + right_shoulder['value']) / 2
    
    def _find_neckline_inverse(self, left_shoulder: Dict, right_shoulder: Dict, pivot_highs: List[Dict]) -> Optional[float]:
        """Find neckline for inverse head and shoulders"""
        return (left_shoulder['value'] + right_shoulder['value']) / 2
    
    def _calculate_apex_distance(self, high_trend: Dict, low_trend: Dict) -> float:
        """Calculate distance to triangle apex"""
        return 10.0  # Placeholder 