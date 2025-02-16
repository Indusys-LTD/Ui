import pandas as pd
import numpy as np
from typing import Dict, List
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from database.classes import AIMetrics

class AICalculator:
    def __init__(self, trades_df: pd.DataFrame):
        self.trades_df = trades_df
        self.model = None
        self.X = None
        self.y = None
        self._prepare_features()
        
    def _prepare_features(self):
        """Prepare features for ML analysis"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed'].copy()
        
        if len(closed_trades) < 2:
            return
            
        # Create features
        closed_trades['hour'] = closed_trades['open_time'].dt.hour
        closed_trades['day_of_week'] = closed_trades['open_time'].dt.dayofweek
        closed_trades['trade_duration'] = (closed_trades['close_time'] - 
                                         closed_trades['open_time']).dt.total_seconds() / 3600
        closed_trades['volume_normalized'] = (closed_trades['volume'] - 
                                            closed_trades['volume'].mean()) / closed_trades['volume'].std()
        
        # Previous trade features
        closed_trades['prev_profit'] = closed_trades['profit_loss'].shift(1)
        closed_trades['prev_duration'] = closed_trades['trade_duration'].shift(1)
        
        # Target variable
        closed_trades['return'] = closed_trades['profit_loss'] / (closed_trades['volume'] * 
                                                                 closed_trades['open_price'])
        
        # Drop rows with NaN values
        closed_trades = closed_trades.dropna()
        
        if len(closed_trades) < 2:
            return
            
        # Features for ML model
        feature_columns = ['hour', 'day_of_week', 'trade_duration', 'volume_normalized',
                          'prev_profit', 'prev_duration']
        
        self.X = closed_trades[feature_columns]
        self.y = closed_trades['return']
        
        # Train the model
        self._train_model()
        
    def _train_model(self):
        """Train the ML model"""
        if self.X is None or len(self.X) < 2:
            return
            
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(self.X, self.y)
        
    def calculate_metrics(self) -> AIMetrics:
        """Calculate all AI-related metrics"""
        if self.model is None:
            return AIMetrics(
                model_accuracy=0.0,
                prediction_confidence=0.0,
                market_regime=self._determine_market_regime(),
                volatility_forecast=self._forecast_volatility(),
                trend_strength=self._calculate_trend_strength(),
                support_levels=self._calculate_support_levels(),
                resistance_levels=self._calculate_resistance_levels(),
                pattern_probability=self._calculate_pattern_probabilities(),
                feature_importance={}
            )
            
        return AIMetrics(
            model_accuracy=self._calculate_model_accuracy(),
            prediction_confidence=self._calculate_prediction_confidence(),
            market_regime=self._determine_market_regime(),
            volatility_forecast=self._forecast_volatility(),
            trend_strength=self._calculate_trend_strength(),
            support_levels=self._calculate_support_levels(),
            resistance_levels=self._calculate_resistance_levels(),
            pattern_probability=self._calculate_pattern_probabilities(),
            feature_importance=self._calculate_feature_importance()
        )
        
    def _calculate_model_accuracy(self) -> float:
        """Calculate model accuracy using out-of-sample predictions"""
        if self.model is None or self.X is None or len(self.X) < 2:
            return 0.0
            
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )
        
        self.model.fit(X_train, y_train)
        return self.model.score(X_test, y_test)
        
    def _calculate_prediction_confidence(self) -> float:
        """Calculate prediction confidence based on model variance"""
        if self.model is None or self.X is None or len(self.X) < 2:
            return 0.0
            
        # Use the variance of predictions from individual trees as confidence measure
        predictions = np.array([tree.predict(self.X) for tree in self.model.estimators_])
        confidence = 1 - np.std(predictions, axis=0).mean()
        return max(0.0, min(1.0, confidence))
        
    def _determine_market_regime(self) -> str:
        """Determine current market regime (trending, ranging, volatile)"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        if len(closed_trades) < 10:
            return "Unknown"
            
        # Calculate returns
        returns = closed_trades['profit_loss'].tail(10) / (closed_trades['volume'] * 
                                                          closed_trades['open_price']).tail(10)
        
        volatility = returns.std()
        trend = abs(returns.mean()) / volatility if volatility > 0 else 0
        
        if volatility > 0.02:  # High volatility threshold
            return "Volatile"
        elif trend > 0.5:  # Strong trend threshold
            return "Trending"
        else:
            return "Ranging"
            
    def _forecast_volatility(self) -> float:
        """Forecast volatility using EWMA"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        if len(closed_trades) < 2:
            return 0.0
            
        returns = closed_trades['profit_loss'] / (closed_trades['volume'] * 
                                                closed_trades['open_price'])
        return returns.ewm(span=20).std().iloc[-1]
        
    def _calculate_trend_strength(self) -> float:
        """Calculate trend strength using ADX-like measure"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        if len(closed_trades) < 14:  # Minimum periods for ADX
            return 0.0
            
        # Calculate directional movement
        price_changes = closed_trades['close_price'].diff()
        pos_dm = (price_changes > 0).astype(float) * price_changes
        neg_dm = (price_changes < 0).astype(float) * -price_changes
        
        # Calculate trend strength (simplified ADX)
        dm_sum = pos_dm + neg_dm
        di_diff = abs(pos_dm.sum() - neg_dm.sum())
        
        return (di_diff / dm_sum.sum() * 100) if dm_sum.sum() > 0 else 0.0
        
    def _calculate_support_levels(self) -> List[float]:
        """Calculate potential support levels using price clusters"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        if len(closed_trades) < 10:
            return []
            
        prices = closed_trades['close_price'].values
        # Use kernel density estimation to find price clusters
        kde = np.histogram(prices, bins='auto')[1]
        # Return the 3 strongest support levels
        return sorted(kde[:3])
        
    def _calculate_resistance_levels(self) -> List[float]:
        """Calculate potential resistance levels using price clusters"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        if len(closed_trades) < 10:
            return []
            
        prices = closed_trades['close_price'].values
        # Use kernel density estimation to find price clusters
        kde = np.histogram(prices, bins='auto')[1]
        # Return the 3 strongest resistance levels
        return sorted(kde[-3:])
        
    def _calculate_pattern_probabilities(self) -> Dict[str, float]:
        """Calculate probabilities of various price patterns"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        if len(closed_trades) < 10:
            return {}
            
        patterns = {
            'trend_continuation': 0.0,
            'trend_reversal': 0.0,
            'breakout': 0.0,
            'range_bound': 0.0
        }
        
        # Calculate pattern probabilities based on recent price action
        returns = closed_trades['profit_loss'].tail(10) / (closed_trades['volume'] * 
                                                          closed_trades['open_price']).tail(10)
        volatility = returns.std()
        trend = returns.mean()
        
        # Simple pattern probability calculations
        patterns['trend_continuation'] = abs(trend) / volatility if volatility > 0 else 0
        patterns['trend_reversal'] = 1 - patterns['trend_continuation']
        patterns['breakout'] = volatility * 2  # Higher volatility suggests breakout
        patterns['range_bound'] = 1 - patterns['breakout']
        
        # Normalize probabilities
        total = sum(patterns.values())
        return {k: v/total for k, v in patterns.items()} if total > 0 else patterns
        
    def _calculate_feature_importance(self) -> Dict[str, float]:
        """Calculate feature importance from the ML model"""
        if self.model is None or self.X is None:
            return {}
            
        importance = self.model.feature_importances_
        return dict(zip(self.X.columns, importance)) 