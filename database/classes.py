from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum

@dataclass
class DatabaseMetrics:
    """Core database metrics"""
    size_gb: float
    table_count: int
    active_connections: int
    max_connections: int
    last_updated: datetime

@dataclass
class TableSpaceUsage:
    """Information about table space usage"""
    table_name: str
    size_mb: float
    index_size_mb: float
    total_size_mb: float
    row_count: int
    last_updated: datetime

@dataclass
class SlowQuery:
    """Information about slow-performing queries"""
    query_text: str
    duration_ms: float
    call_count: int
    rows_affected: int
    cache_hit_ratio: float
    last_execution: datetime

@dataclass
class CacheStatistics:
    """Cache performance metrics"""
    metric_name: str
    value_gb: float
    percentage: float
    last_updated: datetime

@dataclass
class IndexUsage:
    """Index usage statistics"""
    index_name: str
    table_name: str
    size_mb: float
    scan_count: int
    is_unused: bool
    last_updated: datetime

@dataclass
class DatabaseHealth:
    """Overall database health status"""
    metrics: DatabaseMetrics
    table_spaces: List[TableSpaceUsage]
    slow_queries: List[SlowQuery]
    cache_stats: List[CacheStatistics]
    index_usage: List[IndexUsage]
    last_check: datetime

# Enums for various types
class Direction(Enum):
    BUY = "Buy"
    SELL = "Sell"

class TimeFrame(Enum):
    M1 = "1 minute"
    M5 = "5 minutes"
    M15 = "15 minutes"
    M30 = "30 minutes"
    H1 = "1 hour"
    H4 = "4 hours"
    D1 = "1 day"
    W1 = "1 week"
    MN1 = "1 month"

@dataclass
class Trade:
    """Individual trade information"""
    id: int
    symbol: str
    direction: Direction
    open_time: datetime
    close_time: Optional[datetime]
    open_price: float
    close_price: Optional[float]
    volume: float
    profit_loss: Optional[float]
    swap: float
    commission: float
    take_profit: Optional[float]
    stop_loss: Optional[float]
    comment: str
    status: str

@dataclass
class Account:
    """Trading account information"""
    id: int
    login: str
    name: str
    balance: float
    equity: float
    margin: float
    margin_level: float
    floating_pl: float
    server: str
    max_positions: int
    max_volume: float

@dataclass
class OverviewMetrics:
    """Overview tab metrics"""
    total_balance: float
    equity: float
    margin_used: float
    margin_level: float
    floating_pl: float
    daily_pl: float
    open_positions: int
    active_orders: int
    account_growth: List[float]
    growth_dates: List[datetime]

@dataclass
class ProfitLossMetrics:
    """Profit & Loss tab metrics"""
    total_pl: float
    win_rate: float
    avg_trade: float
    profit_factor: float
    best_trade: float
    worst_trade: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    consecutive_wins: int
    consecutive_losses: int
    average_win: float
    average_loss: float
    risk_reward_ratio: float

@dataclass
class SessionAnalysis:
    """Market session analysis"""
    session: str
    total_pl: float
    win_rate: float
    avg_profit: float
    avg_loss: float
    net_trades: int
    profit_factor: float

@dataclass
class RiskMetrics:
    """Risk management metrics"""
    sharp_ratio: float
    max_drawdown: float
    max_drawdown_percentage: float
    profit_factor: float
    deposit_load: float
    recovery_factor: float
    trades_per_week: float
    risk_per_trade: float
    var_95: float  # Value at Risk (95% confidence)
    expected_shortfall: float

@dataclass
class PortfolioMetrics:
    """Portfolio performance metrics"""
    total_value: float
    daily_pl: float
    monthly_pl: float
    yearly_pl: float
    allocation: Dict[str, float]  # symbol -> allocation percentage
    performance: Dict[str, float]  # symbol -> performance percentage
    correlation_matrix: Dict[str, Dict[str, float]]  # symbol -> symbol -> correlation

@dataclass
class LongShortMetrics:
    """Long/Short analysis metrics"""
    long_count: int
    long_percentage: float
    short_count: int
    short_percentage: float
    long_pl: float
    short_pl: float
    long_win_rate: float
    short_win_rate: float
    avg_long_profit: float
    avg_short_profit: float

@dataclass
class AIMetrics:
    """AI/ML metrics and predictions"""
    model_accuracy: float
    prediction_confidence: float
    market_regime: str
    volatility_forecast: float
    trend_strength: float
    support_levels: List[float]
    resistance_levels: List[float]
    pattern_probability: Dict[str, float]
    feature_importance: Dict[str, float]

@dataclass
class SequenceMetrics:
    """Trade sequence analysis"""
    trades: List[Trade]
    win_streak: int
    loss_streak: int
    avg_trade_duration: float
    time_distribution: Dict[str, int]  # hour -> trade count
    weekday_distribution: Dict[str, int]  # weekday -> trade count
    volume_distribution: Dict[float, int]  # volume -> trade count

@dataclass
class SummaryMetrics:
    """Summary tab overall metrics"""
    gross_profit: float
    gross_loss: float
    net_profit: float
    total_trades: int
    win_rate: float
    profit_factor: float
    expected_payoff: float
    absolute_drawdown: float
    maximal_drawdown: float
    relative_drawdown: float
    trades_per_day: float
    avg_trade_length: float
    trading_days: int
