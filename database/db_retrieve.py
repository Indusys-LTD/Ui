import psycopg2
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from .classes import (
    DatabaseMetrics, TableSpaceUsage, SlowQuery,
    CacheStatistics, IndexUsage, DatabaseHealth,
    Trade, Account, Direction, TimeFrame,
    OverviewMetrics, ProfitLossMetrics, SessionAnalysis,
    RiskMetrics, PortfolioMetrics, LongShortMetrics,
    AIMetrics, SequenceMetrics, SummaryMetrics
)

class DatabaseConnection:
    def __init__(self, host: str, port: int, dbname: str, user: str, password: str):
        self.connection_params = {
            'host': host,
            'port': port,
            'dbname': dbname,
            'user': user,
            'password': password
        }
        self.conn = None
        
    def connect(self) -> None:
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
        except psycopg2.Error as e:
            raise Exception(f"Failed to connect to database: {str(e)}")
            
    def disconnect(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()
            
    def get_database_metrics(self) -> DatabaseMetrics:
        """Retrieve core database metrics"""
        query = """
            SELECT
                pg_database_size(current_database()) / (1024 * 1024 * 1024.0) as size_gb,
                (SELECT count(*) FROM information_schema.tables) as table_count,
                (SELECT count(*) FROM pg_stat_activity) as active_connections,
                current_setting('max_connections')::int as max_connections
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            size_gb, table_count, active_connections, max_connections = cur.fetchone()
            return DatabaseMetrics(
                size_gb=size_gb,
                table_count=table_count,
                active_connections=active_connections,
                max_connections=max_connections,
                last_updated=datetime.now()
            )
            
    def get_table_space_usage(self) -> List[TableSpaceUsage]:
        """Retrieve table space usage information"""
        query = """
            SELECT
                relname as table_name,
                pg_total_relation_size(relid) / (1024 * 1024.0) as total_size_mb,
                pg_indexes_size(relid) / (1024 * 1024.0) as index_size_mb,
                (pg_total_relation_size(relid) - pg_indexes_size(relid)) / (1024 * 1024.0) as table_size_mb,
                n_live_tup as row_count
            FROM pg_stat_user_tables
            ORDER BY pg_total_relation_size(relid) DESC
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            return [
                TableSpaceUsage(
                    table_name=row[0],
                    size_mb=row[3],
                    index_size_mb=row[2],
                    total_size_mb=row[1],
                    row_count=row[4],
                    last_updated=datetime.now()
                )
                for row in cur.fetchall()
            ]
            
    def get_slow_queries(self) -> List[SlowQuery]:
        """Retrieve information about slow queries"""
        query = """
            SELECT
                query,
                mean_exec_time as duration_ms,
                calls as call_count,
                rows as rows_affected,
                shared_blks_hit::float / nullif(shared_blks_hit + shared_blks_read, 0) as cache_hit_ratio,
                last_call as last_execution
            FROM pg_stat_statements
            WHERE mean_exec_time > 1000  -- queries taking more than 1 second
            ORDER BY mean_exec_time DESC
            LIMIT 10
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            return [
                SlowQuery(
                    query_text=row[0],
                    duration_ms=row[1],
                    call_count=row[2],
                    rows_affected=row[3],
                    cache_hit_ratio=row[4] or 0.0,
                    last_execution=row[5]
                )
                for row in cur.fetchall()
            ]
            
    def get_cache_statistics(self) -> List[CacheStatistics]:
        """Retrieve cache performance metrics"""
        query = """
            SELECT
                'buffer_cache' as metric_name,
                pg_size_bytes(current_setting('shared_buffers')) / (1024 * 1024 * 1024.0) as value_gb,
                (SELECT
                    sum(heap_blks_hit) * 100.0 / 
                    nullif(sum(heap_blks_hit) + sum(heap_blks_read), 0)
                FROM pg_statio_user_tables) as hit_ratio
            UNION ALL
            SELECT
                'query_cache' as metric_name,
                pg_size_bytes(current_setting('work_mem')) / (1024 * 1024 * 1024.0) as value_gb,
                (SELECT
                    sum(idx_blks_hit) * 100.0 /
                    nullif(sum(idx_blks_hit) + sum(idx_blks_read), 0)
                FROM pg_statio_user_indexes) as hit_ratio
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            return [
                CacheStatistics(
                    metric_name=row[0],
                    value_gb=row[1],
                    percentage=row[2] or 0.0,
                    last_updated=datetime.now()
                )
                for row in cur.fetchall()
            ]
            
    def get_index_usage(self) -> List[IndexUsage]:
        """Retrieve index usage statistics"""
        query = """
            SELECT
                i.indexrelname as index_name,
                t.relname as table_name,
                pg_relation_size(i.indexrelid) / (1024 * 1024.0) as size_mb,
                s.idx_scan as scan_count,
                s.idx_scan = 0 as is_unused
            FROM pg_stat_user_indexes s
            JOIN pg_index i ON s.indexrelid = i.indexrelid
            JOIN pg_class t ON i.indrelid = t.oid
            WHERE NOT i.indisunique AND NOT i.indisprimary
            ORDER BY pg_relation_size(i.indexrelid) DESC
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            return [
                IndexUsage(
                    index_name=row[0],
                    table_name=row[1],
                    size_mb=row[2],
                    scan_count=row[3],
                    is_unused=row[4],
                    last_updated=datetime.now()
                )
                for row in cur.fetchall()
            ]
            
    def get_database_health(self) -> DatabaseHealth:
        """Retrieve overall database health information"""
        return DatabaseHealth(
            metrics=self.get_database_metrics(),
            table_spaces=self.get_table_space_usage(),
            slow_queries=self.get_slow_queries(),
            cache_stats=self.get_cache_statistics(),
            index_usage=self.get_index_usage(),
            last_check=datetime.now()
        )

    def get_account(self, account_id: int) -> Account:
        """Retrieve account information"""
        query = """
            SELECT 
                id, login, name, balance, equity, margin,
                margin_level, floating_pl, server,
                max_positions, max_volume
            FROM accounts
            WHERE id = %s
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (account_id,))
            row = cur.fetchone()
            if not row:
                raise Exception(f"Account {account_id} not found")
            return Account(*row)

    def get_trades(self, account_id: int, start_date: datetime, end_date: datetime) -> List[Trade]:
        """Retrieve trades for a specific account within date range"""
        query = """
            SELECT 
                id, symbol, direction, open_time, close_time,
                open_price, close_price, volume, profit_loss,
                swap, commission, take_profit, stop_loss,
                comment, status
            FROM trades
            WHERE account_id = %s
            AND open_time BETWEEN %s AND %s
            ORDER BY open_time DESC
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (account_id, start_date, end_date))
            return [
                Trade(
                    id=row[0],
                    symbol=row[1],
                    direction=Direction(row[2]),
                    open_time=row[3],
                    close_time=row[4],
                    open_price=row[5],
                    close_price=row[6],
                    volume=row[7],
                    profit_loss=row[8],
                    swap=row[9],
                    commission=row[10],
                    take_profit=row[11],
                    stop_loss=row[12],
                    comment=row[13],
                    status=row[14]
                )
                for row in cur.fetchall()
            ]

    def get_overview_metrics(self, account_id: int) -> OverviewMetrics:
        """Retrieve overview metrics for an account"""
        query = """
            WITH daily_balance AS (
                SELECT date_trunc('day', time) as date, 
                       last(balance, time) as balance
                FROM account_snapshots
                WHERE account_id = %s
                GROUP BY date_trunc('day', time)
                ORDER BY date
            )
            SELECT 
                a.balance as total_balance,
                a.equity,
                a.margin as margin_used,
                a.margin_level,
                a.floating_pl,
                (a.equity - lag(a.equity, 1) OVER (ORDER BY time)) as daily_pl,
                (SELECT count(*) FROM trades WHERE account_id = %s AND close_time IS NULL) as open_positions,
                (SELECT count(*) FROM orders WHERE account_id = %s AND status = 'active') as active_orders,
                array_agg(db.balance ORDER BY db.date) as growth_values,
                array_agg(db.date ORDER BY db.date) as growth_dates
            FROM account_snapshots a
            JOIN daily_balance db ON a.account_id = %s
            WHERE a.account_id = %s
            AND a.time = (SELECT max(time) FROM account_snapshots WHERE account_id = %s)
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (account_id,) * 6)
            row = cur.fetchone()
            return OverviewMetrics(
                total_balance=row[0],
                equity=row[1],
                margin_used=row[2],
                margin_level=row[3],
                floating_pl=row[4],
                daily_pl=row[5] or 0,
                open_positions=row[6],
                active_orders=row[7],
                account_growth=row[8],
                growth_dates=row[9]
            )

    def get_profit_loss_metrics(self, account_id: int, start_date: datetime, end_date: datetime) -> ProfitLossMetrics:
        """Retrieve profit/loss metrics for an account"""
        query = """
            WITH trade_stats AS (
                SELECT 
                    sum(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as winning_trades,
                    count(*) as total_trades,
                    sum(CASE WHEN profit_loss > 0 THEN profit_loss ELSE 0 END) as total_profit,
                    sum(CASE WHEN profit_loss < 0 THEN profit_loss ELSE 0 END) as total_loss,
                    max(profit_loss) as best_trade,
                    min(profit_loss) as worst_trade,
                    avg(CASE WHEN profit_loss > 0 THEN profit_loss END) as avg_win,
                    avg(CASE WHEN profit_loss < 0 THEN profit_loss END) as avg_loss
                FROM trades
                WHERE account_id = %s
                AND open_time BETWEEN %s AND %s
                AND close_time IS NOT NULL
            )
            SELECT *,
                   CASE WHEN total_trades > 0 
                        THEN winning_trades::float / total_trades 
                        ELSE 0 
                   END as win_rate,
                   CASE WHEN total_loss != 0 
                        THEN abs(total_profit / total_loss)
                        ELSE 0
                   END as profit_factor
            FROM trade_stats
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (account_id, start_date, end_date))
            row = cur.fetchone()
            
            # Get consecutive wins/losses
            streak_query = """
                SELECT 
                    max(win_streak) as max_win_streak,
                    max(loss_streak) as max_loss_streak
                FROM (
                    SELECT 
                        sum(CASE WHEN profit_loss > 0 
                            THEN 1 ELSE 0 END) OVER (ORDER BY close_time) as win_streak,
                        sum(CASE WHEN profit_loss < 0 
                            THEN 1 ELSE 0 END) OVER (ORDER BY close_time) as loss_streak
                    FROM trades
                    WHERE account_id = %s
                    AND close_time BETWEEN %s AND %s
                ) streaks
            """
            cur.execute(streak_query, (account_id, start_date, end_date))
            streak_row = cur.fetchone()
            
            return ProfitLossMetrics(
                total_pl=row[2] + row[3],  # total_profit + total_loss
                win_rate=row[8],
                avg_trade=(row[2] + row[3]) / row[1] if row[1] > 0 else 0,
                profit_factor=row[9],
                best_trade=row[4],
                worst_trade=row[5],
                total_trades=row[1],
                winning_trades=row[0],
                losing_trades=row[1] - row[0],
                consecutive_wins=streak_row[0],
                consecutive_losses=streak_row[1],
                average_win=row[6] or 0,
                average_loss=row[7] or 0,
                risk_reward_ratio=abs(row[6] / row[7]) if row[7] else 0
            )

    def get_session_analysis(self, account_id: int, start_date: datetime, end_date: datetime) -> List[SessionAnalysis]:
        """Retrieve session analysis metrics"""
        query = """
            WITH session_trades AS (
                SELECT 
                    CASE 
                        WHEN EXTRACT(HOUR FROM open_time) BETWEEN 0 AND 7 THEN 'Asian'
                        WHEN EXTRACT(HOUR FROM open_time) BETWEEN 8 AND 15 THEN 'European'
                        ELSE 'American'
                    END as session,
                    sum(profit_loss) as total_pl,
                    count(*) as total_trades,
                    sum(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as winning_trades,
                    avg(CASE WHEN profit_loss > 0 THEN profit_loss END) as avg_profit,
                    avg(CASE WHEN profit_loss < 0 THEN profit_loss END) as avg_loss,
                    sum(CASE WHEN profit_loss > 0 THEN profit_loss ELSE 0 END) as total_profit,
                    sum(CASE WHEN profit_loss < 0 THEN profit_loss ELSE 0 END) as total_loss
                FROM trades
                WHERE account_id = %s
                AND open_time BETWEEN %s AND %s
                GROUP BY session
            )
            SELECT 
                session,
                total_pl,
                winning_trades::float / total_trades as win_rate,
                avg_profit,
                avg_loss,
                total_trades,
                CASE WHEN total_loss != 0 
                     THEN abs(total_profit / total_loss)
                     ELSE 0 
                END as profit_factor
            FROM session_trades
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (account_id, start_date, end_date))
            return [
                SessionAnalysis(
                    session=row[0],
                    total_pl=row[1],
                    win_rate=row[2],
                    avg_profit=row[3] or 0,
                    avg_loss=row[4] or 0,
                    net_trades=row[5],
                    profit_factor=row[6]
                )
                for row in cur.fetchall()
            ]

    def get_risk_metrics(self, account_id: int, start_date: datetime, end_date: datetime) -> RiskMetrics:
        """Retrieve risk management metrics"""
        query = """
            WITH daily_returns AS (
                SELECT 
                    date_trunc('day', close_time) as date,
                    sum(profit_loss) / lag(balance) OVER (ORDER BY date_trunc('day', close_time)) as daily_return,
                    max(balance) as balance
                FROM trades t
                JOIN account_snapshots a ON t.account_id = a.account_id 
                    AND date_trunc('day', t.close_time) = date_trunc('day', a.time)
                WHERE t.account_id = %s
                AND t.close_time BETWEEN %s AND %s
                GROUP BY date_trunc('day', close_time)
            ),
            drawdown AS (
                SELECT 
                    max(balance) OVER (ORDER BY time) - balance as drawdown_amount,
                    (max(balance) OVER (ORDER BY time) - balance) / max(balance) OVER (ORDER BY time) as drawdown_percentage
                FROM account_snapshots
                WHERE account_id = %s
                AND time BETWEEN %s AND %s
            )
            SELECT 
                (avg(daily_return) / stddev(daily_return)) * sqrt(252) as sharp_ratio,
                max(drawdown_amount) as max_drawdown,
                max(drawdown_percentage) as max_drawdown_percentage,
                (SELECT abs(sum(CASE WHEN profit_loss > 0 THEN profit_loss ELSE 0 END) / 
                        NULLIF(sum(CASE WHEN profit_loss < 0 THEN profit_loss ELSE 0 END), 0))
                 FROM trades 
                 WHERE account_id = %s
                 AND close_time BETWEEN %s AND %s) as profit_factor,
                (SELECT count(*) / extract(epoch from %s - %s) * 604800
                 FROM trades
                 WHERE account_id = %s
                 AND close_time BETWEEN %s AND %s) as trades_per_week
            FROM daily_returns
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (account_id, start_date, end_date) * 3 + (start_date, end_date))
            row = cur.fetchone()
            
            # Calculate VaR and Expected Shortfall
            returns_query = """
                SELECT profit_loss / balance as return
                FROM trades t
                JOIN account_snapshots a ON t.account_id = a.account_id 
                    AND date_trunc('day', t.close_time) = date_trunc('day', a.time)
                WHERE t.account_id = %s
                AND t.close_time BETWEEN %s AND %s
                ORDER BY return
            """
            cur.execute(returns_query, (account_id, start_date, end_date))
            returns = [r[0] for r in cur.fetchall()]
            
            var_95 = sorted(returns)[int(len(returns) * 0.05)] if returns else 0
            expected_shortfall = sum(r for r in returns if r <= var_95) / (len(returns) * 0.05) if returns else 0
            
            return RiskMetrics(
                sharp_ratio=row[0] or 0,
                max_drawdown=row[1] or 0,
                max_drawdown_percentage=row[2] or 0,
                profit_factor=row[3] or 0,
                deposit_load=0,  # Calculated separately
                recovery_factor=0,  # Calculated separately
                trades_per_week=row[4] or 0,
                risk_per_trade=0,  # Calculated separately
                var_95=var_95,
                expected_shortfall=expected_shortfall
            )

    def get_portfolio_metrics(self, account_id: int) -> PortfolioMetrics:
        """Retrieve portfolio metrics"""
        query = """
            WITH symbol_stats AS (
                SELECT 
                    symbol,
                    sum(profit_loss) as total_pl,
                    count(*) as trade_count,
                    sum(volume * open_price) / sum(sum(volume * open_price)) OVER () as allocation
                FROM trades
                WHERE account_id = %s
                GROUP BY symbol
            ),
            daily_returns AS (
                SELECT 
                    symbol,
                    date_trunc('day', close_time) as date,
                    sum(profit_loss) / lag(sum(volume * open_price)) OVER (PARTITION BY symbol ORDER BY date_trunc('day', close_time)) as return
                FROM trades
                WHERE account_id = %s
                GROUP BY symbol, date_trunc('day', close_time)
            )
            SELECT 
                s1.symbol,
                s2.symbol,
                corr(r1.return, r2.return) as correlation
            FROM symbol_stats s1
            CROSS JOIN symbol_stats s2
            JOIN daily_returns r1 ON s1.symbol = r1.symbol
            JOIN daily_returns r2 ON s2.symbol = r2.symbol AND r1.date = r2.date
            GROUP BY s1.symbol, s2.symbol
        """
        with self.conn.cursor() as cur:
            # Get current portfolio value and P/L
            value_query = """
                SELECT 
                    balance + floating_pl as total_value,
                    (SELECT sum(profit_loss) 
                     FROM trades 
                     WHERE account_id = %s 
                     AND close_time >= current_date) as daily_pl,
                    (SELECT sum(profit_loss)
                     FROM trades
                     WHERE account_id = %s
                     AND close_time >= date_trunc('month', current_date)) as monthly_pl,
                    (SELECT sum(profit_loss)
                     FROM trades
                     WHERE account_id = %s
                     AND close_time >= date_trunc('year', current_date)) as yearly_pl
                FROM account_snapshots
                WHERE account_id = %s
                ORDER BY time DESC
                LIMIT 1
            """
            cur.execute(value_query, (account_id,) * 4)
            value_row = cur.fetchone()
            
            # Get symbol allocations and performance
            cur.execute("""
                SELECT 
                    symbol,
                    sum(volume * open_price) / (SELECT balance FROM account_snapshots WHERE account_id = %s ORDER BY time DESC LIMIT 1) as allocation,
                    sum(profit_loss) / sum(volume * open_price) as performance
                FROM trades
                WHERE account_id = %s
                GROUP BY symbol
            """, (account_id, account_id))
            
            allocation = {}
            performance = {}
            for row in cur.fetchall():
                allocation[row[0]] = row[1]
                performance[row[0]] = row[2]
            
            # Get correlation matrix
            cur.execute(query, (account_id, account_id))
            correlation_matrix = {}
            for row in cur.fetchall():
                if row[0] not in correlation_matrix:
                    correlation_matrix[row[0]] = {}
                correlation_matrix[row[0]][row[1]] = row[2] or 0
            
            return PortfolioMetrics(
                total_value=value_row[0],
                daily_pl=value_row[1] or 0,
                monthly_pl=value_row[2] or 0,
                yearly_pl=value_row[3] or 0,
                allocation=allocation,
                performance=performance,
                correlation_matrix=correlation_matrix
            )

    def get_long_short_metrics(self, account_id: int, start_date: datetime, end_date: datetime) -> LongShortMetrics:
        """Retrieve long/short analysis metrics"""
        query = """
            WITH direction_stats AS (
                SELECT 
                    direction,
                    count(*) as trade_count,
                    sum(profit_loss) as total_pl,
                    sum(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END)::float / count(*) as win_rate,
                    avg(CASE WHEN profit_loss > 0 THEN profit_loss ELSE 0 END) as avg_profit
                FROM trades
                WHERE account_id = %s
                AND close_time BETWEEN %s AND %s
                GROUP BY direction
            )
            SELECT *
            FROM direction_stats
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (account_id, start_date, end_date))
            rows = cur.fetchall()
            
            long_stats = next((r for r in rows if r[0] == Direction.BUY.value), None)
            short_stats = next((r for r in rows if r[0] == Direction.SELL.value), None)
            
            total_trades = sum(r[1] for r in rows)
            
            return LongShortMetrics(
                long_count=long_stats[1] if long_stats else 0,
                long_percentage=long_stats[1] / total_trades * 100 if long_stats and total_trades > 0 else 0,
                short_count=short_stats[1] if short_stats else 0,
                short_percentage=short_stats[1] / total_trades * 100 if short_stats and total_trades > 0 else 0,
                long_pl=long_stats[2] if long_stats else 0,
                short_pl=short_stats[2] if short_stats else 0,
                long_win_rate=long_stats[3] if long_stats else 0,
                short_win_rate=short_stats[3] if short_stats else 0,
                avg_long_profit=long_stats[4] if long_stats else 0,
                avg_short_profit=short_stats[4] if short_stats else 0
            )

    def get_sequence_metrics(self, account_id: int, start_date: datetime, end_date: datetime) -> SequenceMetrics:
        """Retrieve trade sequence metrics"""
        # Get trades
        trades = self.get_trades(account_id, start_date, end_date)
        
        # Calculate streaks
        current_streak = 0
        max_win_streak = 0
        max_loss_streak = 0
        
        for trade in trades:
            if trade.profit_loss and trade.profit_loss > 0:
                if current_streak > 0:
                    current_streak += 1
                else:
                    current_streak = 1
                max_win_streak = max(max_win_streak, current_streak)
            elif trade.profit_loss and trade.profit_loss < 0:
                if current_streak < 0:
                    current_streak -= 1
                else:
                    current_streak = -1
                max_loss_streak = max(max_loss_streak, abs(current_streak))
        
        # Calculate distributions
        time_dist = {}
        weekday_dist = {}
        volume_dist = {}
        
        for trade in trades:
            # Hour distribution
            hour = trade.open_time.hour
            time_dist[hour] = time_dist.get(hour, 0) + 1
            
            # Weekday distribution
            weekday = trade.open_time.strftime('%A')
            weekday_dist[weekday] = weekday_dist.get(weekday, 0) + 1
            
            # Volume distribution
            volume_dist[trade.volume] = volume_dist.get(trade.volume, 0) + 1
        
        # Calculate average trade duration
        durations = []
        for trade in trades:
            if trade.close_time:
                duration = (trade.close_time - trade.open_time).total_seconds() / 3600  # hours
                durations.append(duration)
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return SequenceMetrics(
            trades=trades,
            win_streak=max_win_streak,
            loss_streak=max_loss_streak,
            avg_trade_duration=avg_duration,
            time_distribution=time_dist,
            weekday_distribution=weekday_dist,
            volume_distribution=volume_dist
        )

    def get_summary_metrics(self, account_id: int, start_date: datetime, end_date: datetime) -> SummaryMetrics:
        """Retrieve summary metrics"""
        query = """
            WITH trade_stats AS (
                SELECT 
                    sum(CASE WHEN profit_loss > 0 THEN profit_loss ELSE 0 END) as gross_profit,
                    sum(CASE WHEN profit_loss < 0 THEN profit_loss ELSE 0 END) as gross_loss,
                    count(*) as total_trades,
                    sum(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END)::float / count(*) as win_rate,
                    sum(CASE WHEN profit_loss > 0 THEN profit_loss ELSE 0 END) / 
                        nullif(abs(sum(CASE WHEN profit_loss < 0 THEN profit_loss ELSE 0 END)), 0) as profit_factor,
                    avg(profit_loss) as expected_payoff,
                    extract(epoch from avg(close_time - open_time))/3600 as avg_trade_length,
                    count(DISTINCT date_trunc('day', close_time)) as trading_days
                FROM trades
                WHERE account_id = %s
                AND close_time BETWEEN %s AND %s
            ),
            drawdown AS (
                SELECT 
                    max(balance) OVER (ORDER BY time) - balance as drawdown_amount,
                    (max(balance) OVER (ORDER BY time) - balance) / max(balance) OVER (ORDER BY time) as drawdown_percentage
                FROM account_snapshots
                WHERE account_id = %s
                AND time BETWEEN %s AND %s
            )
            SELECT 
                ts.*,
                max(d.drawdown_amount) as absolute_drawdown,
                max(d.drawdown_percentage) as relative_drawdown
            FROM trade_stats ts
            CROSS JOIN drawdown d
            GROUP BY 
                ts.gross_profit, ts.gross_loss, ts.total_trades, ts.win_rate,
                ts.profit_factor, ts.expected_payoff, ts.avg_trade_length, ts.trading_days
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (account_id, start_date, end_date) * 2)
            row = cur.fetchone()
            
            return SummaryMetrics(
                gross_profit=row[0] or 0,
                gross_loss=row[1] or 0,
                net_profit=(row[0] or 0) + (row[1] or 0),
                total_trades=row[2],
                win_rate=row[3] or 0,
                profit_factor=row[4] or 0,
                expected_payoff=row[5] or 0,
                absolute_drawdown=row[9] or 0,
                maximal_drawdown=row[9] or 0,  # Same as absolute for now
                relative_drawdown=row[10] or 0,
                trades_per_day=row[2] / row[7] if row[7] > 0 else 0,
                avg_trade_length=row[6] or 0,
                trading_days=row[7]
            )
