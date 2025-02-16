from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict
from database.classes import (
    Trade, Account, OverviewMetrics, ProfitLossMetrics,
    SessionAnalysis, RiskMetrics, PortfolioMetrics,
    LongShortMetrics, AIMetrics, SequenceMetrics,
    SummaryMetrics, Direction
)
from .risk_calculator import RiskCalculator
from .profit_loss_calculator import ProfitLossCalculator
from .portfolio_calculator import PortfolioCalculator
from .ai_calculator import AICalculator
from .sequence_calculator import SequenceCalculator

class TradingAnalyzer:
    def __init__(self, trades: List[Trade], account: Account):
        self.trades = trades
        self.account = account
        self.trades_df = self._create_trades_dataframe()
        
        # Initialize specialized calculators
        self.risk_calculator = RiskCalculator(self.trades_df, account)
        self.profit_loss_calculator = ProfitLossCalculator(self.trades_df)
        self.portfolio_calculator = PortfolioCalculator(self.trades_df, account)
        self.ai_calculator = AICalculator(self.trades_df)
        self.sequence_calculator = SequenceCalculator(self.trades_df)
        
    def _create_trades_dataframe(self) -> pd.DataFrame:
        """Convert trades list to pandas DataFrame for easier analysis"""
        return pd.DataFrame([{
            'id': t.id,
            'symbol': t.symbol,
            'direction': t.direction.value,
            'open_time': t.open_time,
            'close_time': t.close_time,
            'open_price': t.open_price,
            'close_price': t.close_price,
            'volume': t.volume,
            'profit_loss': t.profit_loss,
            'swap': t.swap,
            'commission': t.commission,
            'take_profit': t.take_profit,
            'stop_loss': t.stop_loss,
            'status': t.status
        } for t in self.trades])
        
    def calculate_overview_metrics(self) -> OverviewMetrics:
        """Calculate overview tab metrics"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        open_trades = self.trades_df[self.trades_df['status'] == 'open']
        
        # Calculate daily PL
        today = datetime.now().date()
        daily_trades = closed_trades[
            closed_trades['close_time'].dt.date == today
        ]
        
        return OverviewMetrics(
            total_balance=self.account.balance,
            equity=self.account.equity,
            margin_used=self.account.margin,
            margin_level=self.account.margin_level,
            floating_pl=self.account.floating_pl,
            daily_pl=daily_trades['profit_loss'].sum(),
            open_positions=len(open_trades),
            active_orders=0,  # TODO: Implement orders tracking
            account_growth=self._calculate_account_growth(),
            growth_dates=self._get_growth_dates()
        )
        
    def calculate_profit_loss_metrics(self) -> ProfitLossMetrics:
        """Calculate profit and loss metrics"""
        return self.profit_loss_calculator.calculate_metrics()
        
    def calculate_risk_metrics(self) -> RiskMetrics:
        """Calculate risk management metrics"""
        return self.risk_calculator.calculate_metrics()
        
    def calculate_portfolio_metrics(self) -> PortfolioMetrics:
        """Calculate portfolio performance metrics"""
        return self.portfolio_calculator.calculate_metrics()
        
    def calculate_long_short_metrics(self) -> LongShortMetrics:
        """Calculate long/short analysis metrics"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        long_trades = closed_trades[closed_trades['direction'] == Direction.BUY.value]
        short_trades = closed_trades[closed_trades['direction'] == Direction.SELL.value]
        
        return LongShortMetrics(
            long_count=len(long_trades),
            long_percentage=len(long_trades) / len(closed_trades) if len(closed_trades) > 0 else 0,
            short_count=len(short_trades),
            short_percentage=len(short_trades) / len(closed_trades) if len(closed_trades) > 0 else 0,
            long_pl=long_trades['profit_loss'].sum(),
            short_pl=short_trades['profit_loss'].sum(),
            long_win_rate=len(long_trades[long_trades['profit_loss'] > 0]) / len(long_trades) 
                if len(long_trades) > 0 else 0,
            short_win_rate=len(short_trades[short_trades['profit_loss'] > 0]) / len(short_trades) 
                if len(short_trades) > 0 else 0,
            avg_long_profit=long_trades['profit_loss'].mean() if len(long_trades) > 0 else 0,
            avg_short_profit=short_trades['profit_loss'].mean() if len(short_trades) > 0 else 0
        )
        
    def calculate_ai_metrics(self) -> AIMetrics:
        """Calculate AI/ML metrics and predictions"""
        return self.ai_calculator.calculate_metrics()
        
    def calculate_sequence_metrics(self) -> SequenceMetrics:
        """Calculate trade sequence analysis metrics"""
        return self.sequence_calculator.calculate_metrics()
        
    def calculate_summary_metrics(self) -> SummaryMetrics:
        """Calculate summary tab overall metrics"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        winning_trades = closed_trades[closed_trades['profit_loss'] > 0]
        
        return SummaryMetrics(
            gross_profit=winning_trades['profit_loss'].sum(),
            gross_loss=closed_trades[closed_trades['profit_loss'] <= 0]['profit_loss'].sum(),
            net_profit=closed_trades['profit_loss'].sum(),
            total_trades=len(closed_trades),
            win_rate=len(winning_trades) / len(closed_trades) if len(closed_trades) > 0 else 0,
            profit_factor=self.risk_calculator._calculate_profit_factor(),
            expected_payoff=closed_trades['profit_loss'].mean(),
            absolute_drawdown=self.risk_calculator._calculate_max_drawdown(),
            maximal_drawdown=self.risk_calculator._calculate_max_drawdown(),
            relative_drawdown=self.risk_calculator._calculate_max_drawdown_percentage(),
            trades_per_day=self._calculate_trades_per_day(),
            avg_trade_length=self.sequence_calculator._calculate_avg_trade_duration(),
            trading_days=self._calculate_trading_days()
        )
        
    def _calculate_trades_per_day(self) -> float:
        """Calculate average number of trades per day"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        if len(closed_trades) < 2:
            return 0
            
        date_range = (closed_trades['close_time'].max() - 
                     closed_trades['open_time'].min()).days
        return len(closed_trades) / date_range if date_range > 0 else 0
        
    def _calculate_trading_days(self) -> int:
        """Calculate number of trading days"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        if len(closed_trades) == 0:
            return 0
            
        unique_days = closed_trades['close_time'].dt.date.nunique()
        return unique_days
        
    def _calculate_account_growth(self) -> List[float]:
        """Calculate account growth over time"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        if len(closed_trades) == 0:
            return []
            
        cumulative_pl = closed_trades.sort_values('close_time')['profit_loss'].cumsum()
        return (self.account.balance + cumulative_pl).tolist()
        
    def _get_growth_dates(self) -> List[datetime]:
        """Get dates corresponding to account growth points"""
        closed_trades = self.trades_df[self.trades_df['status'] == 'closed']
        if len(closed_trades) == 0:
            return []
            
        return closed_trades.sort_values('close_time')['close_time'].tolist()
