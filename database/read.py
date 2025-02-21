import psycopg2
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy import create_engine, text

class DatabaseReader:
    def __init__(self, dbname: str = "slingshot", user: str = "postgres", password: str = "24865", host: str = "localhost", port: str = "5432"):
        self.connection_params = {
            "dbname": dbname,
            "user": user,
            "password": password,
            "host": host,
            "port": port
        }
        # Create SQLAlchemy engine
        self.engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{dbname}')

    def connect(self):
        """Create and return a database connection"""
        try:
            return psycopg2.connect(**self.connection_params)
        except Exception as e:
            print(f"Error connecting to database: {str(e)}")
            return None

    def get_available_accounts(self) -> List[str]:
        """Get list of all available account numbers"""
        try:
            query = """
                SELECT DISTINCT account_number 
                FROM account_analysis 
                ORDER BY account_number
            """
            df = pd.read_sql_query(text(query), self.engine)
            accounts = df['account_number'].tolist()
            return ["All Accounts"] + [str(acc) for acc in accounts]
        except Exception as e:
            print(f"Error getting accounts: {str(e)}")
            return []

    def get_available_dates(self) -> List[str]:
        """Get list of all available dates"""
        try:
            query = """
                SELECT DISTINCT DATE(timestamp) as date
                FROM account_analysis
                ORDER BY date DESC
            """
            df = pd.read_sql_query(text(query), self.engine)
            return [str(date) for date in df['date']]
        except Exception as e:
            print(f"Error getting dates: {str(e)}")
            return []

    def get_overview_data(self, account: Optional[int], date: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Get basic and performance metrics for overview tab"""
        try:
            # Basic Metrics
            basic_cols = ['account_number', 'balance', 'equity', 'pnl', 'open_positions', 'total_deals']
            basic_query = f"""
                SELECT {', '.join(basic_cols)}
                FROM account_analysis
                WHERE DATE(timestamp) = :date
            """
            params = {'date': date}
            
            if account is not None:
                basic_query += " AND account_number = :account"
                params['account'] = account
                
            basic_query += " ORDER BY account_number"
            basic_df = pd.read_sql_query(text(basic_query), self.engine, params=params)

            # Performance Metrics
            perf_cols = ['account_number', 'win_rate', 'profit_factor', 'sharpe_ratio', 'sortino_ratio', 'calmar_ratio']
            perf_query = f"""
                SELECT {', '.join(perf_cols)}
                FROM account_analysis
                WHERE DATE(timestamp) = :date
            """
            
            if account is not None:
                perf_query += " AND account_number = :account"
                
            perf_query += " ORDER BY account_number"
            perf_df = pd.read_sql_query(text(perf_query), self.engine, params=params)

            return basic_df, perf_df
        except Exception as e:
            print(f"Error getting overview data: {str(e)}")
            return pd.DataFrame(), pd.DataFrame()

    def get_risk_data(self, account: Optional[int], date: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Get risk and advanced risk metrics for risk tab"""
        try:
            # Risk Metrics
            risk_cols = ['account_number', 'max_drawdown', 'avg_drawdown', 'max_drawdown_duration',
                       'var_95', 'es_95', 'risk_of_ruin', 'recovery_factor']
            risk_query = f"""
                SELECT {', '.join(risk_cols)}
                FROM account_analysis
                WHERE DATE(timestamp) = :date
            """
            params = {'date': date}
            
            if account is not None:
                risk_query += " AND account_number = :account"
                params['account'] = account
                
            risk_query += " ORDER BY account_number"
            risk_df = pd.read_sql_query(text(risk_query), self.engine, params=params)

            # Advanced Risk Metrics
            adv_risk_cols = ['account_number', 'var_99', 'es_99', 'tail_ratio', 'ulcer_index']
            adv_risk_query = f"""
                SELECT {', '.join(adv_risk_cols)}
                FROM account_analysis
                WHERE DATE(timestamp) = :date
            """
            
            if account is not None:
                adv_risk_query += " AND account_number = :account"
                
            adv_risk_query += " ORDER BY account_number"
            adv_risk_df = pd.read_sql_query(text(adv_risk_query), self.engine, params=params)

            return risk_df, adv_risk_df
        except Exception as e:
            print(f"Error getting risk data: {str(e)}")
            return pd.DataFrame(), pd.DataFrame()

    def get_forecast_data(self, account: Optional[int], date: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Get forecast scenarios and symbol forecasts for forecast tab"""
        try:
            # Forecast Scenarios
            scenarios_query = """
                SELECT account_number, scenario, forecast_balance, forecast_equity, 
                       balance_change_pct, equity_change_pct, forecast_pnl,
                       exposure_pct, risk_to_equity_pct, forecast_drawdown_pct,
                       forecast_risk_reward
                FROM forecast_scenarios
                WHERE DATE(timestamp) = :date
            """
            params = {'date': date}
            
            if account is not None:
                scenarios_query += " AND account_number = :account"
                params['account'] = account
                
            scenarios_query += " ORDER BY account_number, scenario"
            scenarios_df = pd.read_sql_query(text(scenarios_query), self.engine, params=params)

            # Symbol Forecasts
            symbols_query = """
                SELECT account_number, symbol, exposure, exposure_pct, current_profit,
                       current_profit_pct, positions, up_forecast,
                       up_change_pct, down_forecast, down_change_pct
                FROM symbol_forecasts
                WHERE DATE(timestamp) = :date
            """
            
            if account is not None:
                symbols_query += " AND account_number = :account"
                
            symbols_query += " ORDER BY account_number, symbol"
            symbols_df = pd.read_sql_query(text(symbols_query), self.engine, params=params)

            return scenarios_df, symbols_df
        except Exception as e:
            print(f"Error getting forecast data: {str(e)}")
            return pd.DataFrame(), pd.DataFrame()

    def get_symbol_statistics(self, account: Optional[int], date: str) -> pd.DataFrame:
        """Get symbol statistics"""
        try:
            query = """
                SELECT account_number, symbol, is_most_traded, is_profitable
                FROM symbol_statistics
                WHERE DATE(timestamp) = :date
            """
            params = {'date': date}
            
            if account is not None:
                query += " AND account_number = :account"
                params['account'] = account
                
            query += " ORDER BY account_number, symbol"
            return pd.read_sql_query(text(query), self.engine, params=params)
        except Exception as e:
            print(f"Error getting symbol statistics: {str(e)}")
            return pd.DataFrame()

    def get_historical_metrics(self, account: Optional[int], days: int = 30) -> pd.DataFrame:
        """Get historical metrics for an account"""
        try:
            query = """
                SELECT account_number, DATE(timestamp) as date,
                       balance, equity, pnl, win_rate,
                       max_drawdown, var_95, es_95
                FROM account_analysis
                WHERE timestamp >= CURRENT_DATE - interval ':days days'
            """
            params = {'days': days}
            
            if account is not None:
                query += " AND account_number = :account"
                params['account'] = account
                
            query += " ORDER BY account_number, timestamp"
            return pd.read_sql_query(text(query), self.engine, params=params)
        except Exception as e:
            print(f"Error getting historical metrics: {str(e)}")
            return pd.DataFrame()
