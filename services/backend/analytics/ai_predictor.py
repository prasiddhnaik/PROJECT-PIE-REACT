"""
AI Predictor Module
==================

Machine Learning based market predictions:
- Nifty direction prediction
- Individual stock price prediction
- Pattern recognition using ML
- Sentiment analysis integration
- Risk assessment using AI
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta
import joblib
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class AIPredictor:
    """
    AI-powered market prediction system
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.is_trained = False
        
        # Model configurations
        self.classification_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        self.regression_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
    async def predict_nifty_direction(self, market_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Predict Nifty direction for next trading session
        
        Args:
            market_data: Dictionary containing market data
        
        Returns:
            Prediction with confidence and reasoning
        """
        try:
            # Get Nifty data
            nifty_data = market_data.get('^NSEI')
            if nifty_data is None or len(nifty_data) < 50:
                return {'error': 'Insufficient Nifty data'}
            
            # Prepare features
            features = self._prepare_nifty_features(nifty_data, market_data)
            
            if not self.is_trained:
                # Train model with historical data
                await self._train_nifty_model(nifty_data)
            
            # Make prediction
            prediction = self._predict_direction(features)
            
            # Generate reasoning
            reasoning = self._generate_nifty_reasoning(features, nifty_data)
            
            return {
                'prediction': prediction['direction'],
                'confidence': prediction['confidence'],
                'probability': {
                    'up': prediction['prob_up'],
                    'down': prediction['prob_down'],
                    'sideways': prediction['prob_sideways']
                },
                'target_range': prediction['target_range'],
                'reasoning': reasoning,
                'technical_factors': prediction['factors'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error predicting Nifty direction: {e}")
            return {'error': str(e)}
    
    async def predict_stock_price(self, symbol: str, stock_data: pd.DataFrame, 
                                 days_ahead: int = 1) -> Dict[str, Any]:
        """
        Predict individual stock price movement
        
        Args:
            symbol: Stock symbol
            stock_data: Historical stock data
            days_ahead: Number of days to predict ahead
        
        Returns:
            Price prediction with confidence intervals
        """
        try:
            if stock_data is None or len(stock_data) < 30:
                return {'error': 'Insufficient stock data'}
            
            # Prepare features for price prediction
            features = self._prepare_stock_features(stock_data)
            
            # Train or use existing model
            if symbol not in self.models:
                await self._train_stock_model(symbol, stock_data)
            
            # Make prediction
            prediction = self._predict_price(symbol, features, days_ahead)
            
            current_price = stock_data['Close'].iloc[-1]
            
            return {
                'symbol': symbol,
                'current_price': float(current_price),
                'predicted_price': prediction['price'],
                'price_change': prediction['change'],
                'price_change_percent': prediction['change_percent'],
                'confidence_interval': prediction['confidence_interval'],
                'prediction_quality': prediction['quality'],
                'days_ahead': days_ahead,
                'factors': prediction['factors'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error predicting price for {symbol}: {e}")
            return {'error': str(e)}
    
    async def analyze_pattern_strength(self, data: pd.DataFrame, pattern_type: str) -> Dict[str, Any]:
        """
        Use AI to analyze pattern strength and reliability
        
        Args:
            data: Stock/index data
            pattern_type: Type of pattern detected
        
        Returns:
            Pattern strength analysis
        """
        try:
            # Extract pattern features
            pattern_features = self._extract_pattern_features(data, pattern_type)
            
            # Calculate pattern strength using multiple indicators
            strength_score = self._calculate_pattern_strength(pattern_features)
            
            # Predict pattern success probability
            success_probability = self._predict_pattern_success(pattern_features)
            
            return {
                'pattern_type': pattern_type,
                'strength_score': strength_score,
                'success_probability': success_probability,
                'reliability': self._assess_reliability(strength_score, success_probability),
                'key_factors': pattern_features,
                'recommendation': self._generate_pattern_recommendation(strength_score, success_probability)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing pattern strength: {e}")
            return {'error': str(e)}
    
    async def predict_volatility(self, data: pd.DataFrame, days_ahead: int = 5) -> Dict[str, Any]:
        """
        Predict future volatility using AI
        
        Args:
            data: Historical data
            days_ahead: Days to predict ahead
        
        Returns:
            Volatility prediction
        """
        try:
            # Calculate historical volatility
            returns = data['Close'].pct_change().dropna()
            historical_vol = returns.rolling(window=20).std()
            
            # Prepare volatility features
            vol_features = self._prepare_volatility_features(data, returns)
            
            # Predict volatility
            predicted_vol = self._predict_vol(vol_features, days_ahead)
            
            current_vol = historical_vol.iloc[-1]
            
            return {
                'current_volatility': float(current_vol),
                'predicted_volatility': predicted_vol['value'],
                'volatility_trend': predicted_vol['trend'],
                'risk_assessment': predicted_vol['risk_level'],
                'confidence': predicted_vol['confidence'],
                'days_ahead': days_ahead
            }
            
        except Exception as e:
            logger.error(f"Error predicting volatility: {e}")
            return {'error': str(e)}
    
    def _prepare_nifty_features(self, nifty_data: pd.DataFrame, 
                               market_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Prepare features for Nifty prediction"""
        try:
            features = pd.DataFrame(index=nifty_data.index)
            
            # Price-based features
            features['close'] = nifty_data['Close']
            features['open'] = nifty_data['Open']
            features['high'] = nifty_data['High']
            features['low'] = nifty_data['Low']
            features['volume'] = nifty_data['Volume']
            
            # Technical indicators
            features['rsi'] = self._calculate_rsi(nifty_data['Close'])
            features['sma_20'] = nifty_data['Close'].rolling(window=20).mean()
            features['sma_50'] = nifty_data['Close'].rolling(window=50).mean()
            features['ema_12'] = nifty_data['Close'].ewm(span=12).mean()
            features['ema_26'] = nifty_data['Close'].ewm(span=26).mean()
            
            # MACD
            features['macd'] = features['ema_12'] - features['ema_26']
            features['macd_signal'] = features['macd'].ewm(span=9).mean()
            features['macd_histogram'] = features['macd'] - features['macd_signal']
            
            # Bollinger Bands
            bb_period = 20
            bb_std = features['close'].rolling(window=bb_period).std()
            features['bb_middle'] = features['close'].rolling(window=bb_period).mean()
            features['bb_upper'] = features['bb_middle'] + (bb_std * 2)
            features['bb_lower'] = features['bb_middle'] - (bb_std * 2)
            features['bb_position'] = (features['close'] - features['bb_lower']) / (features['bb_upper'] - features['bb_lower'])
            
            # Volume indicators
            features['volume_sma'] = features['volume'].rolling(window=20).mean()
            features['volume_ratio'] = features['volume'] / features['volume_sma']
            
            # Price action features
            features['price_change'] = features['close'].pct_change()
            features['high_low_ratio'] = (features['high'] - features['low']) / features['close']
            features['open_close_ratio'] = (features['close'] - features['open']) / features['open']
            
            # Lag features
            for lag in [1, 2, 3, 5]:
                features[f'close_lag_{lag}'] = features['close'].shift(lag)
                features[f'volume_lag_{lag}'] = features['volume'].shift(lag)
                features[f'rsi_lag_{lag}'] = features['rsi'].shift(lag)
            
            # Market breadth (if individual stock data available)
            if len(market_data) > 1:
                advancing = 0
                declining = 0
                for symbol, data in market_data.items():
                    if symbol != '^NSEI' and len(data) > 0:
                        if data['Close'].iloc[-1] > data['Close'].iloc[-2]:
                            advancing += 1
                        else:
                            declining += 1
                
                total = advancing + declining
                if total > 0:
                    features['advance_decline_ratio'] = advancing / total
                else:
                    features['advance_decline_ratio'] = 0.5
            
            # Drop NaN values and return recent data
            features = features.dropna()
            return features.tail(100)  # Last 100 days
            
        except Exception as e:
            logger.error(f"Error preparing Nifty features: {e}")
            return pd.DataFrame()
    
    def _prepare_stock_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for individual stock prediction"""
        try:
            features = pd.DataFrame(index=data.index)
            
            # Basic OHLCV
            features['open'] = data['Open']
            features['high'] = data['High']
            features['low'] = data['Low']
            features['close'] = data['Close']
            features['volume'] = data['Volume']
            
            # Technical indicators
            features['rsi'] = self._calculate_rsi(data['Close'])
            features['sma_10'] = data['Close'].rolling(window=10).mean()
            features['sma_20'] = data['Close'].rolling(window=20).mean()
            features['ema_12'] = data['Close'].ewm(span=12).mean()
            features['ema_26'] = data['Close'].ewm(span=26).mean()
            
            # Price momentum
            features['roc_5'] = data['Close'].pct_change(5)
            features['roc_10'] = data['Close'].pct_change(10)
            features['roc_20'] = data['Close'].pct_change(20)
            
            # Volatility
            features['volatility'] = data['Close'].rolling(window=10).std()
            features['atr'] = self._calculate_atr(data)
            
            # Volume analysis
            features['volume_sma'] = features['volume'].rolling(window=20).mean()
            features['volume_ratio'] = features['volume'] / features['volume_sma']
            
            # Price patterns
            features['higher_high'] = (data['High'] > data['High'].shift(1)).astype(int)
            features['higher_low'] = (data['Low'] > data['Low'].shift(1)).astype(int)
            features['inside_day'] = ((data['High'] < data['High'].shift(1)) & 
                                    (data['Low'] > data['Low'].shift(1))).astype(int)
            
            return features.dropna()
            
        except Exception as e:
            logger.error(f"Error preparing stock features: {e}")
            return pd.DataFrame()
    
    async def _train_nifty_model(self, nifty_data: pd.DataFrame):
        """Train Nifty direction prediction model"""
        try:
            # Prepare training data
            features = self._prepare_nifty_features(nifty_data, {'^NSEI': nifty_data})
            
            if len(features) < 50:
                logger.warning("Insufficient data for training")
                return
            
            # Create target variable (next day direction)
            features['next_close'] = features['close'].shift(-1)
            features['direction'] = np.where(
                features['next_close'] > features['close'], 1,  # Up
                np.where(features['next_close'] < features['close'], -1, 0)  # Down, Sideways
            )
            
            # Remove rows with NaN
            training_data = features.dropna()
            
            # Prepare features and target
            feature_cols = [col for col in training_data.columns 
                           if col not in ['next_close', 'direction']]
            X = training_data[feature_cols]
            y = training_data['direction']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            self.classification_model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = self.classification_model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Store model and scaler
            self.models['nifty_direction'] = self.classification_model
            self.scalers['nifty_direction'] = scaler
            self.feature_columns = feature_cols
            self.is_trained = True
            
            logger.info(f"Nifty model trained with accuracy: {accuracy:.3f}")
            
        except Exception as e:
            logger.error(f"Error training Nifty model: {e}")
    
    async def _train_stock_model(self, symbol: str, data: pd.DataFrame):
        """Train individual stock price prediction model"""
        try:
            features = self._prepare_stock_features(data)
            
            if len(features) < 30:
                logger.warning(f"Insufficient data for training {symbol}")
                return
            
            # Create target (next day price change)
            features['next_close'] = features['close'].shift(-1)
            features['price_change'] = (features['next_close'] - features['close']) / features['close']
            
            # Remove NaN
            training_data = features.dropna()
            
            # Prepare features and target
            feature_cols = [col for col in training_data.columns 
                           if col not in ['next_close', 'price_change']]
            X = training_data[feature_cols]
            y = training_data['price_change']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            
            # Train regression model
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            model.fit(X_train_scaled, y_train)
            
            # Store model
            self.models[f'{symbol}_price'] = model
            self.scalers[f'{symbol}_price'] = scaler
            
            logger.info(f"Stock model trained for {symbol}")
            
        except Exception as e:
            logger.error(f"Error training model for {symbol}: {e}")
    
    def _predict_direction(self, features: pd.DataFrame) -> Dict[str, Any]:
        """Predict market direction"""
        try:
            if 'nifty_direction' not in self.models:
                return self._default_prediction()
            
            # Get latest features
            latest_features = features.iloc[-1:][self.feature_columns]
            
            # Scale features
            scaler = self.scalers['nifty_direction']
            scaled_features = scaler.transform(latest_features)
            
            # Predict
            model = self.models['nifty_direction']
            prediction = model.predict(scaled_features)[0]
            probabilities = model.predict_proba(scaled_features)[0]
            
            # Map prediction
            direction_map = {1: 'UP', -1: 'DOWN', 0: 'SIDEWAYS'}
            predicted_direction = direction_map.get(prediction, 'SIDEWAYS')
            
            # Calculate confidence
            max_prob = max(probabilities)
            confidence = int(max_prob * 100)
            
            # Get current price for target calculation
            current_price = features['close'].iloc[-1]
            
            # Calculate target range
            if predicted_direction == 'UP':
                target_range = {
                    'low': current_price * 1.005,  # 0.5% up
                    'high': current_price * 1.02   # 2% up
                }
            elif predicted_direction == 'DOWN':
                target_range = {
                    'low': current_price * 0.98,   # 2% down
                    'high': current_price * 0.995  # 0.5% down
                }
            else:
                target_range = {
                    'low': current_price * 0.995,  # 0.5% range
                    'high': current_price * 1.005
                }
            
            return {
                'direction': predicted_direction,
                'confidence': confidence,
                'prob_up': float(probabilities[2]) if len(probabilities) > 2 else 0.33,
                'prob_down': float(probabilities[0]) if len(probabilities) > 0 else 0.33,
                'prob_sideways': float(probabilities[1]) if len(probabilities) > 1 else 0.34,
                'target_range': target_range,
                'factors': self._get_prediction_factors(features, model)
            }
            
        except Exception as e:
            logger.error(f"Error making direction prediction: {e}")
            return self._default_prediction()
    
    def _predict_price(self, symbol: str, features: pd.DataFrame, days_ahead: int) -> Dict[str, Any]:
        """Predict stock price"""
        try:
            model_key = f'{symbol}_price'
            if model_key not in self.models:
                return self._default_price_prediction(features)
            
            # Get latest features
            feature_cols = [col for col in features.columns if col not in ['next_close', 'price_change']]
            latest_features = features.iloc[-1:][feature_cols]
            
            # Scale and predict
            scaler = self.scalers[model_key]
            scaled_features = scaler.transform(latest_features)
            
            model = self.models[model_key]
            predicted_change = model.predict(scaled_features)[0]
            
            # Apply prediction for multiple days (compound effect)
            current_price = features['close'].iloc[-1]
            predicted_price = current_price * (1 + predicted_change) ** days_ahead
            
            # Calculate change
            change = predicted_price - current_price
            change_percent = (change / current_price) * 100
            
            # Calculate confidence interval (using model uncertainty)
            std_error = 0.02  # 2% standard error assumption
            confidence_interval = {
                'lower': predicted_price * (1 - std_error),
                'upper': predicted_price * (1 + std_error)
            }
            
            return {
                'price': float(predicted_price),
                'change': float(change),
                'change_percent': float(change_percent),
                'confidence_interval': confidence_interval,
                'quality': 'Good' if abs(change_percent) < 10 else 'Uncertain',
                'factors': self._get_price_factors(features)
            }
            
        except Exception as e:
            logger.error(f"Error predicting price for {symbol}: {e}")
            return self._default_price_prediction(features)
    
    def _default_prediction(self) -> Dict[str, Any]:
        """Default prediction when model is not available"""
        return {
            'direction': 'SIDEWAYS',
            'confidence': 50,
            'prob_up': 0.33,
            'prob_down': 0.33,
            'prob_sideways': 0.34,
            'target_range': {'low': 0, 'high': 0},
            'factors': ['Model not trained yet']
        }
    
    def _default_price_prediction(self, features: pd.DataFrame) -> Dict[str, Any]:
        """Default price prediction"""
        current_price = features['close'].iloc[-1]
        return {
            'price': float(current_price),
            'change': 0.0,
            'change_percent': 0.0,
            'confidence_interval': {'lower': current_price * 0.98, 'upper': current_price * 1.02},
            'quality': 'Uncertain',
            'factors': ['Model not trained yet']
        }
    
    def _generate_nifty_reasoning(self, features: pd.DataFrame, nifty_data: pd.DataFrame) -> List[str]:
        """Generate reasoning for Nifty prediction"""
        reasoning = []
        
        try:
            latest = features.iloc[-1]
            
            # RSI analysis
            if 'rsi' in latest:
                rsi = latest['rsi']
                if rsi < 30:
                    reasoning.append(f"RSI at {rsi:.1f} indicates oversold condition, potential reversal")
                elif rsi > 70:
                    reasoning.append(f"RSI at {rsi:.1f} indicates overbought condition, potential correction")
                else:
                    reasoning.append(f"RSI at {rsi:.1f} shows neutral momentum")
            
            # Moving average analysis
            if 'sma_20' in latest and 'sma_50' in latest:
                price = latest['close']
                sma20 = latest['sma_20']
                sma50 = latest['sma_50']
                
                if price > sma20 > sma50:
                    reasoning.append("Price above both 20-day and 50-day moving averages - bullish trend")
                elif price < sma20 < sma50:
                    reasoning.append("Price below both moving averages - bearish trend")
                else:
                    reasoning.append("Mixed signals from moving averages")
            
            # Volume analysis
            if 'volume_ratio' in latest:
                vol_ratio = latest['volume_ratio']
                if vol_ratio > 1.5:
                    reasoning.append(f"High volume ({vol_ratio:.1f}x average) supports the move")
                elif vol_ratio < 0.8:
                    reasoning.append(f"Low volume ({vol_ratio:.1f}x average) shows weak conviction")
            
            # MACD analysis
            if 'macd' in latest and 'macd_signal' in latest:
                macd = latest['macd']
                signal = latest['macd_signal']
                if macd > signal:
                    reasoning.append("MACD above signal line - bullish momentum")
                else:
                    reasoning.append("MACD below signal line - bearish momentum")
            
        except Exception as e:
            logger.error(f"Error generating reasoning: {e}")
            reasoning.append("Technical analysis in progress")
        
        return reasoning
    
    def _get_prediction_factors(self, features: pd.DataFrame, model) -> List[str]:
        """Get key factors influencing prediction"""
        try:
            # Get feature importance from model
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                feature_names = self.feature_columns
                
                # Get top 5 most important features
                top_indices = np.argsort(importances)[-5:][::-1]
                top_features = [feature_names[i] for i in top_indices]
                
                return [f"Key factor: {feature}" for feature in top_features]
            
        except Exception as e:
            logger.error(f"Error getting prediction factors: {e}")
        
        return ["RSI", "Moving Averages", "Volume", "MACD", "Price Action"]
    
    def _get_price_factors(self, features: pd.DataFrame) -> List[str]:
        """Get factors affecting price prediction"""
        factors = []
        
        try:
            latest = features.iloc[-1]
            
            # Momentum factors
            if 'roc_5' in latest:
                roc = latest['roc_5'] * 100
                if abs(roc) > 2:
                    factors.append(f"5-day momentum: {roc:.1f}%")
            
            # Volatility factors
            if 'volatility' in latest:
                vol = latest['volatility']
                avg_vol = features['volatility'].mean()
                if vol > avg_vol * 1.5:
                    factors.append("High volatility environment")
                elif vol < avg_vol * 0.5:
                    factors.append("Low volatility environment")
            
            # Volume factors
            if 'volume_ratio' in latest:
                vol_ratio = latest['volume_ratio']
                if vol_ratio > 2:
                    factors.append("Exceptional volume activity")
                elif vol_ratio > 1.5:
                    factors.append("Above average volume")
        
        except Exception as e:
            logger.error(f"Error getting price factors: {e}")
        
        return factors if factors else ["Price momentum", "Volume trends", "Technical indicators"]
    
    # Helper methods
    def _calculate_rsi(self, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate ATR"""
        high_low = data['High'] - data['Low']
        high_close = np.abs(data['High'] - data['Close'].shift())
        low_close = np.abs(data['Low'] - data['Close'].shift())
        
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        return true_range.rolling(window=period).mean()
    
    # Placeholder methods for advanced features
    def _extract_pattern_features(self, data: pd.DataFrame, pattern_type: str) -> Dict[str, float]:
        """Extract features for pattern analysis"""
        return {'volume_confirmation': 1.2, 'price_momentum': 0.8, 'duration': 5}
    
    def _calculate_pattern_strength(self, features: Dict[str, float]) -> float:
        """Calculate pattern strength score"""
        return 75.0  # Placeholder
    
    def _predict_pattern_success(self, features: Dict[str, float]) -> float:
        """Predict pattern success probability"""
        return 0.68  # Placeholder
    
    def _assess_reliability(self, strength: float, probability: float) -> str:
        """Assess pattern reliability"""
        if strength > 80 and probability > 0.7:
            return "High"
        elif strength > 60 and probability > 0.6:
            return "Medium"
        else:
            return "Low"
    
    def _generate_pattern_recommendation(self, strength: float, probability: float) -> str:
        """Generate pattern-based recommendation"""
        if strength > 75 and probability > 0.65:
            return "Strong signal - Consider position"
        elif strength > 60 and probability > 0.55:
            return "Moderate signal - Wait for confirmation"
        else:
            return "Weak signal - Avoid trade"
    
    def _prepare_volatility_features(self, data: pd.DataFrame, returns: pd.Series) -> pd.DataFrame:
        """Prepare features for volatility prediction"""
        features = pd.DataFrame(index=data.index)
        features['returns'] = returns
        features['abs_returns'] = np.abs(returns)
        features['volatility'] = returns.rolling(window=10).std()
        return features.dropna()
    
    def _predict_vol(self, features: pd.DataFrame, days_ahead: int) -> Dict[str, Any]:
        """Predict volatility"""
        current_vol = features['volatility'].iloc[-1]
        trend_vol = features['volatility'].rolling(window=5).mean().iloc[-1]
        
        if trend_vol > current_vol:
            trend = "Increasing"
            predicted_vol = current_vol * 1.1
        elif trend_vol < current_vol:
            trend = "Decreasing" 
            predicted_vol = current_vol * 0.9
        else:
            trend = "Stable"
            predicted_vol = current_vol
        
        return {
            'value': float(predicted_vol),
            'trend': trend,
            'risk_level': 'High' if predicted_vol > 0.02 else 'Medium' if predicted_vol > 0.01 else 'Low',
            'confidence': 70
        } 