import psycopg2
from psycopg2 import sql
from typing import List

class DatabaseManager:
    def __init__(self, dbname: str = "slingshot", user: str = "postgres", password: str = "24865", host: str = "localhost", port: str = "5432"):
        self.connection_params = {
            "dbname": dbname,
            "user": user,
            "password": password,
            "host": host,
            "port": port
        }

    def create_database(self) -> None:
        """Create the database if it doesn't exist"""
        # Connect to default database to create new database
        conn_params = self.connection_params.copy()
        conn_params["dbname"] = "postgres"
        
        try:
            conn = psycopg2.connect(**conn_params)
            conn.autocommit = True
            cur = conn.cursor()
            
            # Check if database exists
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.connection_params["dbname"],))
            if not cur.fetchone():
                # Create database
                cur.execute(sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(self.connection_params["dbname"])
                ))
                print(f"Database {self.connection_params['dbname']} created successfully")
            else:
                print(f"Database {self.connection_params['dbname']} already exists")
                
        except Exception as e:
            print(f"Error creating database: {str(e)}")
        finally:
            if conn:
                conn.close()

    def create_tables(self) -> None:
        """Create all necessary tables"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            
            # Account Analysis Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS account_analysis (
                    id SERIAL PRIMARY KEY,
                    account_number BIGINT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    balance FLOAT,
                    equity FLOAT,
                    pnl FLOAT,
                    open_positions INTEGER,
                    total_deals INTEGER,
                    win_rate FLOAT,
                    profit_factor FLOAT,
                    sharpe_ratio FLOAT,
                    sortino_ratio FLOAT,
                    calmar_ratio FLOAT,
                    max_drawdown FLOAT,
                    avg_drawdown FLOAT,
                    max_drawdown_duration INTEGER,
                    var_95 FLOAT,
                    es_95 FLOAT,
                    risk_of_ruin FLOAT,
                    recovery_factor FLOAT,
                    avg_trade_profit FLOAT,
                    avg_trades_per_day FLOAT,
                    avg_position_size FLOAT,
                    max_consecutive_losses INTEGER,
                    avg_loss_streak FLOAT,
                    profit_loss_ratio FLOAT,
                    var_99 FLOAT,
                    es_99 FLOAT,
                    tail_ratio FLOAT,
                    ulcer_index FLOAT
                );

                CREATE UNIQUE INDEX IF NOT EXISTS idx_account_analysis_unique 
                ON account_analysis (account_number, CAST(timestamp AS DATE));
            """)

            # Symbol Statistics Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS symbol_statistics (
                    id SERIAL PRIMARY KEY,
                    account_number BIGINT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    symbol VARCHAR(20) NOT NULL,
                    is_most_traded BOOLEAN,
                    is_profitable BOOLEAN
                );

                CREATE UNIQUE INDEX IF NOT EXISTS idx_symbol_statistics_unique 
                ON symbol_statistics (account_number, symbol, CAST(timestamp AS DATE));
            """)

            # Forecast Scenarios Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS forecast_scenarios (
                    id SERIAL PRIMARY KEY,
                    account_number BIGINT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    scenario VARCHAR(10) NOT NULL,
                    forecast_balance FLOAT,
                    forecast_equity FLOAT,
                    balance_change_pct FLOAT,
                    equity_change_pct FLOAT,
                    forecast_pnl FLOAT,
                    exposure_pct FLOAT,
                    risk_to_equity_pct FLOAT,
                    forecast_drawdown_pct FLOAT,
                    forecast_risk_reward FLOAT
                );

                CREATE UNIQUE INDEX IF NOT EXISTS idx_forecast_scenarios_unique 
                ON forecast_scenarios (account_number, scenario, CAST(timestamp AS DATE));
            """)

            # Symbol Forecasts Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS symbol_forecasts (
                    id SERIAL PRIMARY KEY,
                    account_number BIGINT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    symbol VARCHAR(20) NOT NULL,
                    exposure FLOAT,
                    exposure_pct FLOAT,
                    current_profit FLOAT,
                    current_profit_pct FLOAT,
                    positions INTEGER,
                    up_forecast FLOAT,
                    up_change_pct FLOAT,
                    down_forecast FLOAT,
                    down_change_pct FLOAT
                );

                CREATE UNIQUE INDEX IF NOT EXISTS idx_symbol_forecasts_unique 
                ON symbol_forecasts (account_number, symbol, CAST(timestamp AS DATE));
            """)

            # Create additional indexes for better query performance
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_account_analysis_timestamp 
                ON account_analysis (timestamp);
                
                CREATE INDEX IF NOT EXISTS idx_symbol_stats_timestamp 
                ON symbol_statistics (timestamp);
                
                CREATE INDEX IF NOT EXISTS idx_forecast_scenarios_timestamp 
                ON forecast_scenarios (timestamp);
                
                CREATE INDEX IF NOT EXISTS idx_symbol_forecasts_timestamp 
                ON symbol_forecasts (timestamp);
            """)

            conn.commit()
            print("All tables and indexes created successfully")
            
        except Exception as e:
            print(f"Error creating tables: {str(e)}")
        finally:
            if conn:
                conn.close()

def setup_database():
    """Setup the database and create all necessary tables"""
    db_manager = DatabaseManager()
    db_manager.create_database()
    db_manager.create_tables()

if __name__ == "__main__":
    setup_database()
