import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta
from database.classes import Trade, Account, PortfolioMetrics

class PortfolioCalculator:
    def __init__(self, trades_df: pd.DataFrame, account: Account):
        self.trades_df = trades_df
        self.account = account
        
    def calculate_metrics(self) -> PortfolioMetrics:
        """Calculate all portfolio-related metrics"""
        return PortfolioMetrics(
            total_value=self.account.equity,
            daily_pl=self._calculate_daily_pl(),
            monthly_pl=self._calculate_monthly_pl(),
            yearly_pl=self._calculate_yearly_pl(),
            allocation=self._calculate_allocation(),
            performance=self._calculate_symbol_performance(),
            correlation_matrix=self._calculate_correlation_matrix()
        )
        
    def _calculate_daily_pl(self) -> float:
        """Calculate daily profit/loss"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        today = datetime.now().date()
        daily_trades = closed_trades[closed_trades['close_time'].dt.date == today]
        return daily_trades['profit_loss'].sum()
        
    def _calculate_monthly_pl(self) -> float:
        """Calculate monthly profit/loss"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        current_month = datetime.now().replace(day=1)
        monthly_trades = closed_trades[
            closed_trades['close_time'].dt.to_period('M') == 
            pd.Period(current_month, freq='M')
        ]
        return monthly_trades['profit_loss'].sum()
        
    def _calculate_yearly_pl(self) -> float:
        """Calculate yearly profit/loss"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        current_year = datetime.now().year
        yearly_trades = closed_trades[
            closed_trades['close_time'].dt.year == current_year
        ]
        return yearly_trades['profit_loss'].sum()
        
    def _calculate_allocation(self) -> Dict[str, float]:
        """Calculate current portfolio allocation by symbol"""
        open_trades = self.trades_df[self.trades_df['status'] == 'open']
        
        # Calculate position values
        position_values = {}
        for symbol in open_trades['symbol'].unique():
            symbol_trades = open_trades[open_trades['symbol'] == symbol]
            position_value = (symbol_trades['volume'] * 
                            symbol_trades['open_price']).sum()
            position_values[symbol] = position_value
            
        # Convert to percentages
        total_value = sum(position_values.values())
        return {symbol: value/total_value * 100 if total_value > 0 else 0
                for symbol, value in position_values.items()}
        
    def _calculate_symbol_performance(self) -> Dict[str, float]:
        """Calculate performance by symbol"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        performance = {}
        
        for symbol in closed_trades['symbol'].unique():
            symbol_trades = closed_trades[closed_trades['symbol'] == symbol]
            initial_value = (symbol_trades.iloc[0]['volume'] * 
                           symbol_trades.iloc[0]['open_price'])
            final_value = initial_value + symbol_trades['profit_loss'].sum()
            performance[symbol] = ((final_value - initial_value) / 
                                 initial_value * 100) if initial_value > 0 else 0
                                 
        return performance
        
    def _calculate_correlation_matrix(self) -> Dict[str, Dict[str, float]]:
        """Calculate correlation matrix between symbols"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        
        # Create daily returns by symbol
        daily_returns = {}
        for symbol in closed_trades['symbol'].unique():
            symbol_trades = closed_trades[closed_trades['symbol'] == symbol]
            daily_returns[symbol] = symbol_trades.groupby(
                symbol_trades['close_time'].dt.date
            )['profit_loss'].sum()
            
        # Convert to DataFrame for correlation calculation
        returns_df = pd.DataFrame(daily_returns).fillna(0)
        corr_matrix = returns_df.corr().to_dict()
        
        # Convert to nested dictionary
        return {symbol: corr_matrix[symbol] for symbol in corr_matrix}
        
    def calculate_drawdown_by_symbol(self) -> Dict[str, float]:
        """Calculate maximum drawdown by symbol"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        drawdowns = {}
        
        for symbol in closed_trades['symbol'].unique():
            symbol_trades = closed_trades[closed_trades['symbol'] == symbol]
            cumulative = symbol_trades['profit_loss'].cumsum()
            rolling_max = cumulative.expanding().max()
            drawdown = ((rolling_max - cumulative) / rolling_max * 100
                       if len(rolling_max) > 0 else 0)
            drawdowns[symbol] = drawdown.max()
            
        return drawdowns
        
    def calculate_portfolio_beta(self, market_returns: pd.Series) -> float:
        """Calculate portfolio beta relative to market"""
        portfolio_returns = self.trades_df[
            self.trades_df['status'] == 'closed'
        ].groupby(
            self.trades_df['close_time'].dt.date
        )['profit_loss'].sum()
        
        # Align dates
        aligned_returns = pd.concat([portfolio_returns, market_returns], axis=1).dropna()
        
        if len(aligned_returns) < 2:
            return 0
            
        covariance = aligned_returns.cov().iloc[0, 1]
        market_variance = market_returns.var()
        
        return covariance / market_variance if market_variance != 0 else 0
        
    def calculate_portfolio_alpha(self, market_returns: pd.Series, 
                                risk_free_rate: float) -> float:
        """Calculate portfolio alpha (excess return)"""
        portfolio_returns = self.trades_df[
            self.trades_df['status'] == 'closed'
        ].groupby(
            self.trades_df['close_time'].dt.date
        )['profit_loss'].sum() / self.account.balance
        
        beta = self.calculate_portfolio_beta(market_returns)
        
        portfolio_return = portfolio_returns.mean() * 252  # Annualized
        market_return = market_returns.mean() * 252  # Annualized
        
        return portfolio_return - (risk_free_rate + beta * (market_return - risk_free_rate)) 