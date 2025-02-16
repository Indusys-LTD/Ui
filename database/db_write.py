from typing import Dict, List, Any
import sqlite3
from datetime import datetime
from database.classes import (
    Trade, Account, OverviewMetrics, ProfitLossMetrics,
    SessionAnalysis, RiskMetrics, PortfolioMetrics,
    LongShortMetrics, AIMetrics, SequenceMetrics,
    SummaryMetrics
)

class DatabaseWriter:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.setup_database()
        
    def setup_database(self):
        """Create necessary tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create tables for each metric type
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY,
                    login TEXT NOT NULL,
                    name TEXT,
                    balance REAL,
                    equity REAL,
                    margin REAL,
                    margin_level REAL,
                    floating_pl REAL,
                    server TEXT,
                    max_positions INTEGER,
                    max_volume REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY,
                    account_id INTEGER,
                    symbol TEXT,
                    direction TEXT,
                    open_time DATETIME,
                    close_time DATETIME,
                    open_price REAL,
                    close_price REAL,
                    volume REAL,
                    profit_loss REAL,
                    swap REAL,
                    commission REAL,
                    take_profit REAL,
                    stop_loss REAL,
                    comment TEXT,
                    status TEXT,
                    FOREIGN KEY(account_id) REFERENCES accounts(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS overview_metrics (
                    id INTEGER PRIMARY KEY,
                    account_id INTEGER,
                    total_balance REAL,
                    equity REAL,
                    margin_used REAL,
                    margin_level REAL,
                    floating_pl REAL,
                    daily_pl REAL,
                    open_positions INTEGER,
                    active_orders INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(account_id) REFERENCES accounts(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profit_loss_metrics (
                    id INTEGER PRIMARY KEY,
                    account_id INTEGER,
                    total_pl REAL,
                    win_rate REAL,
                    avg_trade REAL,
                    profit_factor REAL,
                    best_trade REAL,
                    worst_trade REAL,
                    total_trades INTEGER,
                    winning_trades INTEGER,
                    losing_trades INTEGER,
                    consecutive_wins INTEGER,
                    consecutive_losses INTEGER,
                    average_win REAL,
                    average_loss REAL,
                    risk_reward_ratio REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(account_id) REFERENCES accounts(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS risk_metrics (
                    id INTEGER PRIMARY KEY,
                    account_id INTEGER,
                    sharp_ratio REAL,
                    max_drawdown REAL,
                    max_drawdown_percentage REAL,
                    profit_factor REAL,
                    deposit_load REAL,
                    recovery_factor REAL,
                    trades_per_week REAL,
                    risk_per_trade REAL,
                    var_95 REAL,
                    expected_shortfall REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(account_id) REFERENCES accounts(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_metrics (
                    id INTEGER PRIMARY KEY,
                    account_id INTEGER,
                    total_value REAL,
                    daily_pl REAL,
                    monthly_pl REAL,
                    yearly_pl REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(account_id) REFERENCES accounts(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_allocation (
                    id INTEGER PRIMARY KEY,
                    portfolio_metric_id INTEGER,
                    symbol TEXT,
                    allocation REAL,
                    performance REAL,
                    FOREIGN KEY(portfolio_metric_id) REFERENCES portfolio_metrics(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS long_short_metrics (
                    id INTEGER PRIMARY KEY,
                    account_id INTEGER,
                    long_count INTEGER,
                    long_percentage REAL,
                    short_count INTEGER,
                    short_percentage REAL,
                    long_pl REAL,
                    short_pl REAL,
                    long_win_rate REAL,
                    short_win_rate REAL,
                    avg_long_profit REAL,
                    avg_short_profit REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(account_id) REFERENCES accounts(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_metrics (
                    id INTEGER PRIMARY KEY,
                    account_id INTEGER,
                    model_accuracy REAL,
                    prediction_confidence REAL,
                    market_regime TEXT,
                    volatility_forecast REAL,
                    trend_strength REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(account_id) REFERENCES accounts(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_levels (
                    id INTEGER PRIMARY KEY,
                    ai_metric_id INTEGER,
                    level_type TEXT,
                    value REAL,
                    FOREIGN KEY(ai_metric_id) REFERENCES ai_metrics(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sequence_metrics (
                    id INTEGER PRIMARY KEY,
                    account_id INTEGER,
                    win_streak INTEGER,
                    loss_streak INTEGER,
                    avg_trade_duration REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(account_id) REFERENCES accounts(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS summary_metrics (
                    id INTEGER PRIMARY KEY,
                    account_id INTEGER,
                    gross_profit REAL,
                    gross_loss REAL,
                    net_profit REAL,
                    total_trades INTEGER,
                    win_rate REAL,
                    profit_factor REAL,
                    expected_payoff REAL,
                    absolute_drawdown REAL,
                    maximal_drawdown REAL,
                    relative_drawdown REAL,
                    trades_per_day REAL,
                    avg_trade_length REAL,
                    trading_days INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(account_id) REFERENCES accounts(id)
                )
            """)
            
            conn.commit()
            
    def write_account(self, account: Account) -> int:
        """Write account data and return the account_id"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO accounts (
                    login, name, balance, equity, margin, margin_level,
                    floating_pl, server, max_positions, max_volume
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account.login, account.name, account.balance, account.equity,
                account.margin, account.margin_level, account.floating_pl,
                account.server, account.max_positions, account.max_volume
            ))
            return cursor.lastrowid
            
    def write_trades(self, trades: List[Trade], account_id: int):
        """Write trade data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for trade in trades:
                cursor.execute("""
                    INSERT INTO trades (
                        account_id, symbol, direction, open_time, close_time,
                        open_price, close_price, volume, profit_loss, swap,
                        commission, take_profit, stop_loss, comment, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    account_id, trade.symbol, trade.direction.value,
                    trade.open_time, trade.close_time, trade.open_price,
                    trade.close_price, trade.volume, trade.profit_loss,
                    trade.swap, trade.commission, trade.take_profit,
                    trade.stop_loss, trade.comment, trade.status
                ))
            conn.commit()
            
    def write_overview_metrics(self, metrics: OverviewMetrics, account_id: int):
        """Write overview metrics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO overview_metrics (
                    account_id, total_balance, equity, margin_used,
                    margin_level, floating_pl, daily_pl, open_positions,
                    active_orders
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account_id, metrics.total_balance, metrics.equity,
                metrics.margin_used, metrics.margin_level, metrics.floating_pl,
                metrics.daily_pl, metrics.open_positions, metrics.active_orders
            ))
            conn.commit()
            
    def write_profit_loss_metrics(self, metrics: ProfitLossMetrics, account_id: int):
        """Write profit/loss metrics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO profit_loss_metrics (
                    account_id, total_pl, win_rate, avg_trade, profit_factor,
                    best_trade, worst_trade, total_trades, winning_trades,
                    losing_trades, consecutive_wins, consecutive_losses,
                    average_win, average_loss, risk_reward_ratio
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account_id, metrics.total_pl, metrics.win_rate, metrics.avg_trade,
                metrics.profit_factor, metrics.best_trade, metrics.worst_trade,
                metrics.total_trades, metrics.winning_trades, metrics.losing_trades,
                metrics.consecutive_wins, metrics.consecutive_losses,
                metrics.average_win, metrics.average_loss, metrics.risk_reward_ratio
            ))
            conn.commit()
            
    def write_risk_metrics(self, metrics: RiskMetrics, account_id: int):
        """Write risk metrics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO risk_metrics (
                    account_id, sharp_ratio, max_drawdown, max_drawdown_percentage,
                    profit_factor, deposit_load, recovery_factor, trades_per_week,
                    risk_per_trade, var_95, expected_shortfall
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account_id, metrics.sharp_ratio, metrics.max_drawdown,
                metrics.max_drawdown_percentage, metrics.profit_factor,
                metrics.deposit_load, metrics.recovery_factor,
                metrics.trades_per_week, metrics.risk_per_trade,
                metrics.var_95, metrics.expected_shortfall
            ))
            conn.commit()
            
    def write_portfolio_metrics(self, metrics: PortfolioMetrics, account_id: int):
        """Write portfolio metrics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO portfolio_metrics (
                    account_id, total_value, daily_pl, monthly_pl, yearly_pl
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                account_id, metrics.total_value, metrics.daily_pl,
                metrics.monthly_pl, metrics.yearly_pl
            ))
            portfolio_id = cursor.lastrowid
            
            # Write allocation and performance data
            for symbol in metrics.allocation:
                cursor.execute("""
                    INSERT INTO portfolio_allocation (
                        portfolio_metric_id, symbol, allocation, performance
                    ) VALUES (?, ?, ?, ?)
                """, (
                    portfolio_id, symbol, metrics.allocation[symbol],
                    metrics.performance[symbol]
                ))
            conn.commit()
            
    def write_long_short_metrics(self, metrics: LongShortMetrics, account_id: int):
        """Write long/short metrics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO long_short_metrics (
                    account_id, long_count, long_percentage, short_count,
                    short_percentage, long_pl, short_pl, long_win_rate,
                    short_win_rate, avg_long_profit, avg_short_profit
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account_id, metrics.long_count, metrics.long_percentage,
                metrics.short_count, metrics.short_percentage, metrics.long_pl,
                metrics.short_pl, metrics.long_win_rate, metrics.short_win_rate,
                metrics.avg_long_profit, metrics.avg_short_profit
            ))
            conn.commit()
            
    def write_ai_metrics(self, metrics: AIMetrics, account_id: int):
        """Write AI metrics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ai_metrics (
                    account_id, model_accuracy, prediction_confidence,
                    market_regime, volatility_forecast, trend_strength
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                account_id, metrics.model_accuracy, metrics.prediction_confidence,
                metrics.market_regime, metrics.volatility_forecast,
                metrics.trend_strength
            ))
            ai_metric_id = cursor.lastrowid
            
            # Write support and resistance levels
            for level in metrics.support_levels:
                cursor.execute("""
                    INSERT INTO ai_levels (ai_metric_id, level_type, value)
                    VALUES (?, 'support', ?)
                """, (ai_metric_id, level))
                
            for level in metrics.resistance_levels:
                cursor.execute("""
                    INSERT INTO ai_levels (ai_metric_id, level_type, value)
                    VALUES (?, 'resistance', ?)
                """, (ai_metric_id, level))
            conn.commit()
            
    def write_sequence_metrics(self, metrics: SequenceMetrics, account_id: int):
        """Write sequence metrics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sequence_metrics (
                    account_id, win_streak, loss_streak, avg_trade_duration
                ) VALUES (?, ?, ?, ?)
            """, (
                account_id, metrics.win_streak, metrics.loss_streak,
                metrics.avg_trade_duration
            ))
            conn.commit()
            
    def write_summary_metrics(self, metrics: SummaryMetrics, account_id: int):
        """Write summary metrics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO summary_metrics (
                    account_id, gross_profit, gross_loss, net_profit,
                    total_trades, win_rate, profit_factor, expected_payoff,
                    absolute_drawdown, maximal_drawdown, relative_drawdown,
                    trades_per_day, avg_trade_length, trading_days
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account_id, metrics.gross_profit, metrics.gross_loss,
                metrics.net_profit, metrics.total_trades, metrics.win_rate,
                metrics.profit_factor, metrics.expected_payoff,
                metrics.absolute_drawdown, metrics.maximal_drawdown,
                metrics.relative_drawdown, metrics.trades_per_day,
                metrics.avg_trade_length, metrics.trading_days
            ))
            conn.commit()
            
    def write_all_metrics(self, account: Account, trades: List[Trade], metrics: Dict[str, Any]):
        """Write all metrics to the database"""
        account_id = self.write_account(account)
        self.write_trades(trades, account_id)
        
        if 'overview' in metrics:
            self.write_overview_metrics(metrics['overview'], account_id)
        if 'profit_loss' in metrics:
            self.write_profit_loss_metrics(metrics['profit_loss'], account_id)
        if 'risk' in metrics:
            self.write_risk_metrics(metrics['risk'], account_id)
        if 'portfolio' in metrics:
            self.write_portfolio_metrics(metrics['portfolio'], account_id)
        if 'long_short' in metrics:
            self.write_long_short_metrics(metrics['long_short'], account_id)
        if 'ai' in metrics:
            self.write_ai_metrics(metrics['ai'], account_id)
        if 'sequence' in metrics:
            self.write_sequence_metrics(metrics['sequence'], account_id)
        if 'summary' in metrics:
            self.write_summary_metrics(metrics['summary'], account_id)
