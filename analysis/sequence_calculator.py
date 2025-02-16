import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta
from database.classes import Trade, SequenceMetrics

class SequenceCalculator:
    def __init__(self, trades_df: pd.DataFrame):
        self.trades_df = trades_df
        
    def calculate_metrics(self) -> SequenceMetrics:
        """Calculate all sequence-related metrics"""
        closed_trades = [Trade(**t) for t in 
                        self.trades_df[self.trades_df['status'] == 'closed'].to_dict('records')]
        
        return SequenceMetrics(
            trades=closed_trades,
            win_streak=self._calculate_win_streak(),
            loss_streak=self._calculate_loss_streak(),
            avg_trade_duration=self._calculate_avg_trade_duration(),
            time_distribution=self._calculate_time_distribution(),
            weekday_distribution=self._calculate_weekday_distribution(),
            volume_distribution=self._calculate_volume_distribution()
        )
        
    def _calculate_win_streak(self) -> int:
        """Calculate current winning streak"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        if len(closed_trades) == 0:
            return 0
            
        # Convert profits to 1s and losses to 0s
        wins = (closed_trades['profit_loss'] > 0).astype(int)
        
        # Count consecutive 1s from the end
        streak = 0
        for win in reversed(wins):
            if win:
                streak += 1
            else:
                break
        return streak
        
    def _calculate_loss_streak(self) -> int:
        """Calculate current losing streak"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        if len(closed_trades) == 0:
            return 0
            
        # Convert losses to 1s and profits to 0s
        losses = (closed_trades['profit_loss'] <= 0).astype(int)
        
        # Count consecutive 1s from the end
        streak = 0
        for loss in reversed(losses):
            if loss:
                streak += 1
            else:
                break
        return streak
        
    def _calculate_avg_trade_duration(self) -> float:
        """Calculate average trade duration in hours"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        if len(closed_trades) == 0:
            return 0.0
            
        durations = (closed_trades['close_time'] - 
                    closed_trades['open_time']).dt.total_seconds() / 3600
        return durations.mean()
        
    def _calculate_time_distribution(self) -> Dict[str, int]:
        """Calculate trade distribution by hour"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        if len(closed_trades) == 0:
            return {}
            
        hours = closed_trades['open_time'].dt.hour
        distribution = hours.value_counts().to_dict()
        return {str(hour): count for hour, count in distribution.items()}
        
    def _calculate_weekday_distribution(self) -> Dict[str, int]:
        """Calculate trade distribution by weekday"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        if len(closed_trades) == 0:
            return {}
            
        weekdays = closed_trades['open_time'].dt.day_name()
        return weekdays.value_counts().to_dict()
        
    def _calculate_volume_distribution(self) -> Dict[float, int]:
        """Calculate trade distribution by volume"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        if len(closed_trades) == 0:
            return {}
            
        # Create volume bins
        volumes = closed_trades['volume']
        bins = np.linspace(volumes.min(), volumes.max(), 10)
        labels = [f"{bins[i]:.2f}-{bins[i+1]:.2f}" for i in range(len(bins)-1)]
        
        distribution = pd.cut(volumes, bins=bins, labels=labels).value_counts()
        return {str(label): count for label, count in distribution.items()}
        
    def calculate_trade_clusters(self, time_window: timedelta = timedelta(hours=1)) -> List[List[Trade]]:
        """Find clusters of trades that occurred close together"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed'].sort_values('open_time')
        if len(closed_trades) < 2:
            return []
            
        clusters = []
        current_cluster = [closed_trades.iloc[0]]
        
        for i in range(1, len(closed_trades)):
            current_trade = closed_trades.iloc[i]
            previous_trade = closed_trades.iloc[i-1]
            
            if (current_trade['open_time'] - previous_trade['open_time']) <= time_window:
                current_cluster.append(current_trade)
            else:
                if len(current_cluster) > 1:
                    clusters.append([Trade(**t) for t in current_cluster])
                current_cluster = [current_trade]
                
        if len(current_cluster) > 1:
            clusters.append([Trade(**t) for t in current_cluster])
            
        return clusters
        
    def calculate_trade_patterns(self, window_size: int = 3) -> Dict[str, int]:
        """Identify common patterns in trade sequences"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        if len(closed_trades) < window_size:
            return {}
            
        # Create pattern strings (W for win, L for loss)
        patterns = []
        wins = (closed_trades['profit_loss'] > 0).astype(str).str.replace('True', 'W').replace('False', 'L')
        
        for i in range(len(wins) - window_size + 1):
            pattern = ''.join(wins.iloc[i:i+window_size])
            patterns.append(pattern)
            
        return pd.Series(patterns).value_counts().to_dict()
        
    def calculate_trade_timing_efficiency(self) -> Dict[str, float]:
        """Calculate efficiency metrics for trade timing"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        if len(closed_trades) == 0:
            return {}
            
        metrics = {}
        
        # Average profit by hour
        hourly_profits = closed_trades.groupby(closed_trades['open_time'].dt.hour)['profit_loss'].mean()
        metrics['best_hour'] = hourly_profits.idxmax()
        metrics['worst_hour'] = hourly_profits.idxmin()
        
        # Average profit by weekday
        daily_profits = closed_trades.groupby(closed_trades['open_time'].dt.day_name())['profit_loss'].mean()
        metrics['best_day'] = daily_profits.idxmax()
        metrics['worst_day'] = daily_profits.idxmin()
        
        # Time between trades analysis
        time_between = closed_trades['open_time'].diff()
        metrics['avg_time_between_trades'] = time_between.mean().total_seconds() / 3600
        metrics['min_time_between_trades'] = time_between.min().total_seconds() / 3600
        
        return metrics 