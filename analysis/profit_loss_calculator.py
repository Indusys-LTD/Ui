import pandas as pd
import numpy as np
from typing import List
from database.classes import Trade, ProfitLossMetrics

class ProfitLossCalculator:
    def __init__(self, trades_df: pd.DataFrame):
        self.trades_df = trades_df
        
    def calculate_metrics(self) -> ProfitLossMetrics:
        """Calculate all profit/loss related metrics"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        winning_trades = closed_trades[closed_trades['profit_loss'] > 0]
        losing_trades = closed_trades[closed_trades['profit_loss'] <= 0]
        
        return ProfitLossMetrics(
            total_pl=closed_trades['profit_loss'].sum(),
            win_rate=len(winning_trades) / len(closed_trades) if len(closed_trades) > 0 else 0,
            avg_trade=closed_trades['profit_loss'].mean(),
            profit_factor=self._calculate_profit_factor(winning_trades, losing_trades),
            best_trade=closed_trades['profit_loss'].max(),
            worst_trade=closed_trades['profit_loss'].min(),
            total_trades=len(closed_trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            consecutive_wins=self._calculate_consecutive_wins(),
            consecutive_losses=self._calculate_consecutive_losses(),
            average_win=winning_trades['profit_loss'].mean() if len(winning_trades) > 0 else 0,
            average_loss=abs(losing_trades['profit_loss'].mean()) if len(losing_trades) > 0 else 0,
            risk_reward_ratio=self._calculate_risk_reward_ratio(winning_trades, losing_trades)
        )
        
    def _calculate_profit_factor(self, winning_trades: pd.DataFrame, 
                               losing_trades: pd.DataFrame) -> float:
        """Calculate profit factor (gross profit / gross loss)"""
        gross_profit = winning_trades['profit_loss'].sum()
        gross_loss = abs(losing_trades['profit_loss'].sum())
        return gross_profit / gross_loss if gross_loss != 0 else float('inf')
        
    def _calculate_consecutive_wins(self) -> int:
        """Calculate maximum consecutive winning trades"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        wins = (closed_trades['profit_loss'] > 0).astype(int)
        return self._max_consecutive(wins)
        
    def _calculate_consecutive_losses(self) -> int:
        """Calculate maximum consecutive losing trades"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        losses = (closed_trades['profit_loss'] <= 0).astype(int)
        return self._max_consecutive(losses)
        
    def _max_consecutive(self, series: pd.Series) -> int:
        """Helper function to calculate maximum consecutive occurrences"""
        if len(series) == 0:
            return 0
        # Convert to string of 0s and 1s
        s = series.astype(str).str.cat()
        # Find longest sequence of 1s
        return max(len(x) for x in s.split('0')) if '1' in s else 0
        
    def _calculate_risk_reward_ratio(self, winning_trades: pd.DataFrame, 
                                   losing_trades: pd.DataFrame) -> float:
        """Calculate risk/reward ratio"""
        avg_win = winning_trades['profit_loss'].mean() if len(winning_trades) > 0 else 0
        avg_loss = abs(losing_trades['profit_loss'].mean()) if len(losing_trades) > 0 else 0
        return avg_win / avg_loss if avg_loss != 0 else float('inf')
        
    def calculate_daily_pl(self) -> pd.Series:
        """Calculate daily profit/loss"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        return closed_trades.groupby(closed_trades['close_time'].dt.date)['profit_loss'].sum()
        
    def calculate_monthly_pl(self) -> pd.Series:
        """Calculate monthly profit/loss"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        return closed_trades.groupby(closed_trades['close_time'].dt.to_period('M'))['profit_loss'].sum()
        
    def calculate_symbol_pl(self) -> pd.Series:
        """Calculate profit/loss by symbol"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        return closed_trades.groupby('symbol')['profit_loss'].sum()
        
    def calculate_win_rate_by_symbol(self) -> pd.Series:
        """Calculate win rate by symbol"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        wins_by_symbol = closed_trades[closed_trades['profit_loss'] > 0].groupby('symbol').size()
        total_by_symbol = closed_trades.groupby('symbol').size()
        return wins_by_symbol / total_by_symbol
        
    def calculate_average_trade_duration(self) -> pd.Timedelta:
        """Calculate average trade duration"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        durations = closed_trades['close_time'] - closed_trades['open_time']
        return durations.mean()
        
    def calculate_profit_distribution(self, bins: int = 50) -> tuple:
        """Calculate profit distribution for histogram"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        return np.histogram(closed_trades['profit_loss'], bins=bins) 