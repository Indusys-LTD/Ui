import pandas as pd
import numpy as np
from typing import List
from database.classes import Trade, Account, RiskMetrics

class RiskCalculator:
    def __init__(self, trades_df: pd.DataFrame, account: Account):
        self.trades_df = trades_df
        self.account = account
        
    def calculate_metrics(self) -> RiskMetrics:
        """Calculate all risk-related metrics"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        returns = closed_trades['profit_loss'] / self.account.balance
        
        return RiskMetrics(
            sharp_ratio=self._calculate_sharpe_ratio(returns),
            max_drawdown=self._calculate_max_drawdown(),
            max_drawdown_percentage=self._calculate_max_drawdown_percentage(),
            profit_factor=self._calculate_profit_factor(),
            deposit_load=self._calculate_deposit_load(),
            recovery_factor=self._calculate_recovery_factor(),
            trades_per_week=self._calculate_trades_per_week(),
            risk_per_trade=self._calculate_risk_per_trade(),
            var_95=self._calculate_var_95(returns),
            expected_shortfall=self._calculate_expected_shortfall(returns)
        )
        
    def _calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculate Sharpe ratio using daily returns"""
        if len(returns) < 2:
            return 0
        return (returns.mean() / returns.std()) * np.sqrt(252)  # Annualized
        
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown in absolute terms"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        cumulative = closed_trades['profit_loss'].cumsum()
        rolling_max = cumulative.expanding().max()
        drawdowns = rolling_max - cumulative
        return drawdowns.max()
        
    def _calculate_max_drawdown_percentage(self) -> float:
        """Calculate maximum drawdown as a percentage"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        cumulative = self.account.balance + closed_trades['profit_loss'].cumsum()
        rolling_max = cumulative.expanding().max()
        drawdowns = (rolling_max - cumulative) / rolling_max * 100
        return drawdowns.max()
        
    def _calculate_profit_factor(self) -> float:
        """Calculate profit factor (gross profit / gross loss)"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        gross_profit = closed_trades[closed_trades['profit_loss'] > 0]['profit_loss'].sum()
        gross_loss = abs(closed_trades[closed_trades['profit_loss'] <= 0]['profit_loss'].sum())
        return gross_profit / gross_loss if gross_loss != 0 else float('inf')
        
    def _calculate_deposit_load(self) -> float:
        """Calculate deposit load (margin used / equity)"""
        return (self.account.margin / self.account.equity * 100) if self.account.equity != 0 else 0
        
    def _calculate_recovery_factor(self) -> float:
        """Calculate recovery factor (net profit / max drawdown)"""
        max_dd = self._calculate_max_drawdown()
        if max_dd == 0:
            return float('inf')
        net_profit = self.trades_df[self.trades_df['status'] == 'closed']['profit_loss'].sum()
        return net_profit / max_dd
        
    def _calculate_trades_per_week(self) -> float:
        """Calculate average number of trades per week"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        if len(closed_trades) < 2:
            return 0
            
        date_range = (closed_trades['close_time'].max() - 
                     closed_trades['open_time'].min()).days / 7
        return len(closed_trades) / date_range if date_range > 0 else 0
        
    def _calculate_risk_per_trade(self) -> float:
        """Calculate average risk per trade based on stop loss"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        risk_amounts = closed_trades.apply(lambda x: 
            abs(x['open_price'] - x['stop_loss']) * x['volume'] 
            if x['stop_loss'] is not None else 0, axis=1)
        return risk_amounts.mean()
        
    def _calculate_var_95(self, returns: pd.Series) -> float:
        """Calculate Value at Risk (95% confidence)"""
        if len(returns) < 2:
            return 0
        return np.percentile(returns, 5)  # 95% VaR is the 5th percentile of returns
        
    def _calculate_expected_shortfall(self, returns: pd.Series) -> float:
        """Calculate Expected Shortfall (Average loss beyond VaR)"""
        if len(returns) < 2:
            return 0
        var_95 = self._calculate_var_95(returns)
        return returns[returns <= var_95].mean() 