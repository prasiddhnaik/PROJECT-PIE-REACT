"""
Technical analysis utilities for chart generation.
"""

import numpy as np
import pandas as pd
import logging
from typing import List, Dict, Any, Optional, Union
import math
import sys
import os

# Add parent directory to path for common imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.errors import (
    InvalidDataError, InsufficientDataError, ComputationError, ValidationError
)

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """Enhanced technical analysis with proper error handling"""
    
    def __init__(self):
        self.logger = logging.getLogger("chart-service.technical-analyzer")
    
    def _validate_price_data(self, prices: List[Union[float, int]], min_length: int = 1) -> np.ndarray:
        """Validate and convert price data to numpy array"""
        if not prices:
            raise InvalidDataError("Price data cannot be empty")
        
        if not isinstance(prices, (list, tuple, np.ndarray)):
            raise InvalidDataError("Price data must be a list, tuple, or numpy array")
        
        # Convert to numpy array
        try:
            price_array = np.array(prices, dtype=float)
        except (ValueError, TypeError) as e:
            raise InvalidDataError(f"Price data contains non-numeric values: {str(e)}")
        
        # Check for NaN or infinite values
        if np.any(np.isnan(price_array)):
            raise InvalidDataError("Price data contains NaN values")
        
        if np.any(np.isinf(price_array)):
            raise InvalidDataError("Price data contains infinite values")
        
        # Check for negative prices
        if np.any(price_array < 0):
            raise InvalidDataError("Price data contains negative values")
        
        # Check minimum length
        if len(price_array) < min_length:
            raise InsufficientDataError(
                f"Need at least {min_length} data points for calculation, got {len(price_array)}",
                min_required=min_length,
                actual_count=len(price_array)
            )
        
        return price_array
    
    def _validate_period(self, period: int, max_period: int = None) -> int:
        """Validate period parameter"""
        if not isinstance(period, int):
            raise ValidationError("Period must be an integer")
        
        if period <= 0:
            raise ValidationError("Period must be greater than 0")
        
        if max_period and period > max_period:
            raise ValidationError(f"Period {period} cannot exceed data length {max_period}")
        
        return period
    
    def extract_prices(self, data: List[List[float]]) -> List[float]:
        """Extract closing prices from price data."""
        return [point[1] for point in data if len(point) >= 2]
    
    def convert_to_ohlc(self, price_data: List[List[float]], timeframe: str) -> List[Dict[str, Any]]:
        """Convert price data to OHLC format."""
        ohlc_data = []
        
        for point in price_data:
            if len(point) >= 2:
                timestamp, price = point[0], point[1]
                ohlc_data.append({
                    "timestamp": timestamp,
                    "open": price,
                    "high": price,
                    "low": price,
                    "close": price,
                    "volume": 0  # Volume not available in simple price data
                })
        
        return ohlc_data
    
    def extract_volume_data(self, data: List[List[float]]) -> List[Dict[str, Any]]:
        """Extract volume data from price history."""
        volume_data = []
        
        for point in data:
            if len(point) >= 3:
                timestamp, price, volume = point[0], point[1], point[2] if len(point) > 2 else 0
                volume_data.append({
                    "timestamp": timestamp,
                    "volume": volume
                })
        
        return volume_data
    
    def calculate_sma(self, prices: List[Union[float, int]], period: int) -> Dict[str, Any]:
        """Calculate Simple Moving Average with error handling"""
        try:
            # Validate inputs
            price_array = self._validate_price_data(prices, min_length=period)
            period = self._validate_period(period, max_period=len(price_array))
            
            # Calculate SMA
            sma_values = []
            for i in range(len(price_array)):
                if i >= period - 1:
                    try:
                        window_data = price_array[i - period + 1:i + 1]
                        window_avg = np.mean(window_data)
                        
                        # Check for mathematical errors
                        if np.isnan(window_avg):
                            raise ComputationError(
                                f"SMA calculation resulted in NaN at index {i}",
                                computation_type="simple_moving_average"
                            )
                        if np.isinf(window_avg):
                            raise ComputationError(
                                f"SMA calculation resulted in infinity at index {i}",
                                computation_type="simple_moving_average"
                            )
                            
                        sma_values.append(float(window_avg))
                    except (ZeroDivisionError, ArithmeticError) as e:
                        raise ComputationError(
                            f"Mathematical error in SMA calculation at index {i}: {str(e)}",
                            computation_type="simple_moving_average"
                        )
                else:
                    sma_values.append(None)  # Not enough data for this point
            
            # Log successful calculation
            valid_points = len([v for v in sma_values if v is not None])
            self.logger.info(f"Calculated SMA with period {period} for {len(price_array)} data points, {valid_points} valid")
            
            return {
                "values": sma_values,
                "period": period,
                "data_points": len(price_array),
                "valid_points": valid_points,
                "calculation_type": "simple_moving_average"
            }
            
        except (InvalidDataError, InsufficientDataError, ValidationError, ComputationError):
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error calculating SMA: {str(e)}", exc_info=True)
            raise ComputationError(
                f"SMA calculation failed unexpectedly: {str(e)}",
                computation_type="simple_moving_average"
            )
    
    def calculate_ema(self, prices: List[Union[float, int]], period: int) -> Dict[str, Any]:
        """Calculate Exponential Moving Average with error handling"""
        try:
            # Validate inputs
            price_array = self._validate_price_data(prices, min_length=period)
            period = self._validate_period(period, max_period=len(price_array))
            
            # Calculate EMA
            try:
                multiplier = 2.0 / (period + 1)
                if multiplier <= 0 or multiplier > 1:
                    raise ComputationError(
                        f"Invalid EMA multiplier calculated: {multiplier}",
                        computation_type="exponential_moving_average"
                    )
            except (ZeroDivisionError, ArithmeticError) as e:
                raise ComputationError(
                    f"Error calculating EMA multiplier: {str(e)}",
                    computation_type="exponential_moving_average"
                )
            
            ema_values = []
            
            # First EMA value is the SMA of the first 'period' values
            try:
                first_sma = np.mean(price_array[:period])
                if np.isnan(first_sma) or np.isinf(first_sma):
                    raise ComputationError(
                        "Initial SMA calculation for EMA resulted in invalid value",
                        computation_type="exponential_moving_average"
                    )
            except (ZeroDivisionError, ArithmeticError) as e:
                raise ComputationError(
                    f"Error calculating initial SMA for EMA: {str(e)}",
                    computation_type="exponential_moving_average"
                )
            
            ema_values.extend([None] * (period - 1))
            ema_values.append(float(first_sma))
            
            # Calculate subsequent EMA values
            for i in range(period, len(price_array)):
                try:
                    ema_value = (price_array[i] * multiplier) + (ema_values[i - 1] * (1 - multiplier))
                    
                    # Check for mathematical errors
                    if np.isnan(ema_value):
                        raise ComputationError(
                            f"EMA calculation resulted in NaN at index {i}",
                            computation_type="exponential_moving_average"
                        )
                    if np.isinf(ema_value):
                        raise ComputationError(
                            f"EMA calculation resulted in infinity at index {i}",
                            computation_type="exponential_moving_average"
                        )
                        
                    ema_values.append(float(ema_value))
                except (ZeroDivisionError, ArithmeticError) as e:
                    raise ComputationError(
                        f"Mathematical error in EMA calculation at index {i}: {str(e)}",
                        computation_type="exponential_moving_average"
                    )
            
            valid_points = len([v for v in ema_values if v is not None])
            self.logger.info(f"Calculated EMA with period {period} for {len(price_array)} data points, {valid_points} valid")
            
            return {
                "values": ema_values,
                "period": period,
                "multiplier": multiplier,
                "data_points": len(price_array),
                "valid_points": valid_points,
                "calculation_type": "exponential_moving_average"
            }
            
        except (InvalidDataError, InsufficientDataError, ValidationError, ComputationError):
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error calculating EMA: {str(e)}", exc_info=True)
            raise ComputationError(
                f"EMA calculation failed unexpectedly: {str(e)}",
                computation_type="exponential_moving_average"
            )
    
    def calculate_rsi(self, prices: List[Union[float, int]], period: int = 14) -> Dict[str, Any]:
        """Calculate Relative Strength Index with error handling"""
        try:
            # Validate inputs - need at least period + 1 for price changes
            price_array = self._validate_price_data(prices, min_length=period + 1)
            period = self._validate_period(period, max_period=len(price_array) - 1)
            
            # Calculate price changes
            price_changes = np.diff(price_array)
            
            if len(price_changes) == 0:
                raise InsufficientDataError("Need at least 2 price points to calculate RSI")
            
            # Separate gains and losses
            gains = np.where(price_changes > 0, price_changes, 0)
            losses = np.where(price_changes < 0, -price_changes, 0)
            
            rsi_values = [None] * period  # First 'period' values are None
            
            # Calculate initial average gain and loss
            avg_gain = np.mean(gains[:period])
            avg_loss = np.mean(losses[:period])
            
            # Calculate RSI for each subsequent point
            for i in range(period, len(price_changes)):
                # Update average gain and loss using smoothing
                avg_gain = ((avg_gain * (period - 1)) + gains[i]) / period
                avg_loss = ((avg_loss * (period - 1)) + losses[i]) / period
                
                # Calculate RSI
                if avg_loss == 0:
                    rsi = 100.0  # All gains, no losses
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100.0 - (100.0 / (1.0 + rs))
                
                rsi_values.append(float(rsi))
            
            self.logger.info(f"Calculated RSI with period {period} for {len(price_array)} data points")
            
            return {
                "values": rsi_values,
                "period": period,
                "data_points": len(price_array),
                "valid_points": len([v for v in rsi_values if v is not None])
            }
            
        except (InvalidDataError, InsufficientDataError):
            raise
        except Exception as e:
            self.logger.error(f"Error calculating RSI: {str(e)}", exc_info=True)
            raise InvalidDataError(f"RSI calculation failed: {str(e)}")
    
    def calculate_macd(self, prices: List[Union[float, int]], 
                      fast_period: int = 12, slow_period: int = 26, 
                      signal_period: int = 9) -> Dict[str, Any]:
        """Calculate MACD with error handling"""
        try:
            # Validate inputs
            min_length = slow_period + signal_period
            price_array = self._validate_price_data(prices, min_length=min_length)
            
            fast_period = self._validate_period(fast_period)
            slow_period = self._validate_period(slow_period)
            signal_period = self._validate_period(signal_period)
            
            if fast_period >= slow_period:
                raise InvalidDataError("Fast period must be less than slow period")
            
            # Calculate EMAs
            fast_ema = self.calculate_ema(prices, fast_period)["values"]
            slow_ema = self.calculate_ema(prices, slow_period)["values"]
            
            # Calculate MACD line
            macd_line = []
            for i in range(len(fast_ema)):
                if fast_ema[i] is not None and slow_ema[i] is not None:
                    macd_line.append(fast_ema[i] - slow_ema[i])
                else:
                    macd_line.append(None)
            
            # Calculate signal line (EMA of MACD line)
            # Remove None values for signal calculation
            macd_valid = [v for v in macd_line if v is not None]
            if len(macd_valid) < signal_period:
                raise InsufficientDataError(f"Insufficient MACD data for signal line: need {signal_period}, got {len(macd_valid)}")
            
            signal_ema = self.calculate_ema(macd_valid, signal_period)["values"]
            
            # Align signal line with MACD line (pad with None values)
            none_count = len([v for v in macd_line if v is None])
            signal_line = [None] * none_count + signal_ema
            
            # Calculate histogram
            histogram = []
            for i in range(len(macd_line)):
                if (macd_line[i] is not None and 
                    i < len(signal_line) and signal_line[i] is not None):
                    histogram.append(macd_line[i] - signal_line[i])
                else:
                    histogram.append(None)
            
            self.logger.info(f"Calculated MACD ({fast_period}, {slow_period}, {signal_period}) for {len(price_array)} data points")
            
            return {
                "macd_line": macd_line,
                "signal_line": signal_line,
                "histogram": histogram,
                "fast_period": fast_period,
                "slow_period": slow_period,
                "signal_period": signal_period,
                "data_points": len(price_array),
                "valid_points": len([v for v in macd_line if v is not None])
            }
            
        except (InvalidDataError, InsufficientDataError):
            raise
        except Exception as e:
            self.logger.error(f"Error calculating MACD: {str(e)}", exc_info=True)
            raise InvalidDataError(f"MACD calculation failed: {str(e)}")
    
    def calculate_bollinger_bands(self, prices: List[Union[float, int]], 
                                 period: int = 20, std_dev: float = 2.0) -> Dict[str, Any]:
        """Calculate Bollinger Bands with error handling"""
        try:
            # Validate inputs
            price_array = self._validate_price_data(prices, min_length=period)
            period = self._validate_period(period, max_period=len(price_array))
            
            if std_dev <= 0:
                raise InvalidDataError("Standard deviation multiplier must be positive")
            
            # Calculate middle band (SMA)
            sma_data = self.calculate_sma(prices, period)
            middle_band = sma_data["values"]
            
            # Calculate upper and lower bands
            upper_band = []
            lower_band = []
            
            for i in range(len(price_array)):
                if i >= period - 1:
                    # Calculate standard deviation for the window
                    window = price_array[i - period + 1:i + 1]
                    std = np.std(window, ddof=0)  # Population standard deviation
                    
                    if middle_band[i] is not None:
                        upper_band.append(middle_band[i] + (std_dev * std))
                        lower_band.append(middle_band[i] - (std_dev * std))
                    else:
                        upper_band.append(None)
                        lower_band.append(None)
                else:
                    upper_band.append(None)
                    lower_band.append(None)
            
            self.logger.info(f"Calculated Bollinger Bands (period={period}, std_dev={std_dev}) for {len(price_array)} data points")
            
            return {
                "upper_band": upper_band,
                "middle_band": middle_band,
                "lower_band": lower_band,
                "period": period,
                "std_dev": std_dev,
                "data_points": len(price_array),
                "valid_points": len([v for v in middle_band if v is not None])
            }
            
        except (InvalidDataError, InsufficientDataError):
            raise
        except Exception as e:
            self.logger.error(f"Error calculating Bollinger Bands: {str(e)}", exc_info=True)
            raise InvalidDataError(f"Bollinger Bands calculation failed: {str(e)}")
    
    def calculate_stochastic(self, highs: List[Union[float, int]], 
                           lows: List[Union[float, int]], 
                           closes: List[Union[float, int]], 
                           k_period: int = 14, d_period: int = 3) -> Dict[str, Any]:
        """Calculate Stochastic Oscillator with error handling"""
        try:
            # Validate inputs
            high_array = self._validate_price_data(highs, min_length=k_period)
            low_array = self._validate_price_data(lows, min_length=k_period)
            close_array = self._validate_price_data(closes, min_length=k_period)
            
            if not (len(high_array) == len(low_array) == len(close_array)):
                raise InvalidDataError("High, low, and close arrays must have the same length")
            
            # Validate that highs >= lows
            if np.any(high_array < low_array):
                raise InvalidDataError("High prices must be greater than or equal to low prices")
            
            k_period = self._validate_period(k_period, max_period=len(close_array))
            d_period = self._validate_period(d_period)
            
            # Calculate %K
            k_values = []
            for i in range(len(close_array)):
                if i >= k_period - 1:
                    # Get the highest high and lowest low in the period
                    period_highs = high_array[i - k_period + 1:i + 1]
                    period_lows = low_array[i - k_period + 1:i + 1]
                    
                    highest_high = np.max(period_highs)
                    lowest_low = np.min(period_lows)
                    
                    if highest_high == lowest_low:
                        # Avoid division by zero
                        k_value = 50.0
                    else:
                        k_value = ((close_array[i] - lowest_low) / (highest_high - lowest_low)) * 100.0
                    
                    k_values.append(float(k_value))
                else:
                    k_values.append(None)
            
            # Calculate %D (SMA of %K)
            k_valid = [v for v in k_values if v is not None]
            if len(k_valid) < d_period:
                d_values = [None] * len(k_values)
            else:
                d_sma = self.calculate_sma(k_valid, d_period)["values"]
                # Align with k_values
                none_count = len([v for v in k_values if v is None])
                d_values = [None] * none_count + d_sma
            
            self.logger.info(f"Calculated Stochastic (%K={k_period}, %D={d_period}) for {len(close_array)} data points")
            
            return {
                "k_values": k_values,
                "d_values": d_values,
                "k_period": k_period,
                "d_period": d_period,
                "data_points": len(close_array),
                "valid_points": len([v for v in k_values if v is not None])
            }
            
        except (InvalidDataError, InsufficientDataError):
            raise
        except Exception as e:
            self.logger.error(f"Error calculating Stochastic: {str(e)}", exc_info=True)
            raise InvalidDataError(f"Stochastic calculation failed: {str(e)}")
    
    def calculate_support_resistance(self, prices: List[Union[float, int]], 
                                   window: int = 10, min_touches: int = 2) -> Dict[str, Any]:
        """Calculate support and resistance levels with error handling"""
        try:
            # Validate inputs
            price_array = self._validate_price_data(prices, min_length=window * 2)
            window = self._validate_period(window, max_period=len(price_array) // 2)
            
            if min_touches < 2:
                raise InvalidDataError("Minimum touches must be at least 2")
            
            # Find local maxima and minima
            local_maxima = []
            local_minima = []
            
            for i in range(window, len(price_array) - window):
                window_data = price_array[i - window:i + window + 1]
                current_price = price_array[i]
                
                # Check if current price is local maximum
                if current_price == np.max(window_data):
                    local_maxima.append((i, current_price))
                
                # Check if current price is local minimum
                if current_price == np.min(window_data):
                    local_minima.append((i, current_price))
            
            # Cluster similar levels
            resistance_levels = self._cluster_levels([price for _, price in local_maxima], min_touches)
            support_levels = self._cluster_levels([price for _, price in local_minima], min_touches)
            
            self.logger.info(f"Calculated support/resistance levels for {len(price_array)} data points")
            
            return {
                "support_levels": support_levels,
                "resistance_levels": resistance_levels,
                "local_maxima": local_maxima,
                "local_minima": local_minima,
                "window": window,
                "min_touches": min_touches,
                "data_points": len(price_array)
            }
            
        except (InvalidDataError, InsufficientDataError):
            raise
        except Exception as e:
            self.logger.error(f"Error calculating support/resistance: {str(e)}", exc_info=True)
            raise InvalidDataError(f"Support/resistance calculation failed: {str(e)}")
    
    def _cluster_levels(self, levels: List[float], min_touches: int, 
                       tolerance_percent: float = 0.01) -> List[Dict[str, Any]]:
        """Cluster similar price levels"""
        if len(levels) < min_touches:
            return []
        
        levels = sorted(levels)
        clusters = []
        
        i = 0
        while i < len(levels):
            cluster = [levels[i]]
            base_level = levels[i]
            
            # Find all levels within tolerance
            j = i + 1
            while j < len(levels):
                if abs(levels[j] - base_level) / base_level <= tolerance_percent:
                    cluster.append(levels[j])
                    j += 1
                else:
                    break
            
            # Only keep clusters with minimum touches
            if len(cluster) >= min_touches:
                clusters.append({
                    "level": np.mean(cluster),
                    "touches": len(cluster),
                    "strength": len(cluster) / len(levels)
                })
            
            i = j
        
        return clusters
    
    def normalize_prices(self, data: List[List[float]]) -> List[Dict[str, Any]]:
        """Normalize prices to percentage change from first price."""
        if not data:
            return []
        
        prices = self.extract_prices(data)
        if not prices:
            return []
        
        first_price = prices[0]
        normalized = []
        
        for i, price in enumerate(prices):
            percentage_change = ((price - first_price) / first_price) * 100
            normalized.append({
                "timestamp": data[i][0] if i < len(data) else i,
                "value": percentage_change
            })
        
        return normalized
    
    def _calculate_ema_values(self, prices: List[float], period: int) -> List[float]:
        """Helper method to calculate EMA values."""
        if not prices or len(prices) < period:
            return []
        
        k = 2 / (period + 1)
        ema_values = []
        
        # Start with SMA
        ema = sum(prices[:period]) / period
        ema_values.append(ema)
        
        # Calculate EMA for remaining values
        for price in prices[period:]:
            ema = (price * k) + (ema * (1 - k))
            ema_values.append(ema)
        
        return ema_values 