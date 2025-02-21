import psycopg2
from psycopg2 import sql
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime

class DatabaseWriter:
    def __init__(self, dbname: str = "slingshot", user: str = "postgres", password: str = "24865", host: str = "localhost", port: str = "5432"):
        self.connection_params = {
            "dbname": dbname,
            "user": user,
            "password": password,
            "host": host,
            "port": port
        }

    def connect(self):
        """Create and return a database connection"""
        return psycopg2.connect(**self.connection_params)

    def write_account_analysis(self, analysis_data: Dict[str, Any]) -> None:
        """Write or update account analysis results in database"""
        try:
            conn = self.connect()
            cur = conn.cursor()

            # Map 'account' to 'account_number' if it exists
            if 'account' in analysis_data:
                analysis_data['account_number'] = analysis_data['account']

            # Prepare the SQL query
            columns = [
                'account_number', 'balance', 'equity', 'pnl', 'open_positions',
                'total_deals', 'win_rate', 'profit_factor', 'sharpe_ratio',
                'sortino_ratio', 'calmar_ratio', 'max_drawdown', 'avg_drawdown',
                'max_drawdown_duration', 'var_95', 'es_95', 'risk_of_ruin',
                'recovery_factor', 'avg_trade_profit', 'avg_trades_per_day',
                'avg_position_size', 'max_consecutive_losses', 'avg_loss_streak',
                'profit_loss_ratio', 'var_99', 'es_99', 'tail_ratio', 'ulcer_index'
            ]

            # Extract values in the same order as columns
            values = [analysis_data.get(col, None) for col in columns]

            # Create the UPDATE part of the UPSERT
            update_parts = [f"{col} = EXCLUDED.{col}" for col in columns if col != 'account_number']
            update_statement = ', '.join(update_parts)

            # UPSERT query
            placeholders = ', '.join(['%s'] * len(columns))
            query = f"""
                INSERT INTO account_analysis ({', '.join(columns)})
                VALUES ({placeholders})
                ON CONFLICT (account_number, DATE(timestamp))
                DO UPDATE SET
                    {update_statement},
                    timestamp = CURRENT_TIMESTAMP
            """

            cur.execute(query, values)
            conn.commit()
            print(f"Account analysis data updated for account {analysis_data.get('account_number')}")

        except Exception as e:
            print(f"Error writing account analysis: {str(e)}")
            print(f"Analysis data: {analysis_data}")
        finally:
            if conn:
                conn.close()

    def write_symbol_statistics(self, account_number: int, most_traded: List[str], profitable: List[str]) -> None:
        """Write or update symbol statistics in database"""
        try:
            conn = self.connect()
            cur = conn.cursor()

            # First, delete old records for this account for the current day
            cur.execute("""
                DELETE FROM symbol_statistics 
                WHERE account_number = %s 
                AND DATE(timestamp) = CURRENT_DATE
            """, (account_number,))

            # Then insert new records
            all_symbols = set(most_traded + profitable)
            for symbol in all_symbols:
                values = (
                    account_number,
                    symbol,
                    symbol in most_traded,
                    symbol in profitable
                )
                
                query = """
                    INSERT INTO symbol_statistics (account_number, symbol, is_most_traded, is_profitable)
                    VALUES (%s, %s, %s, %s)
                """
                
                cur.execute(query, values)
            
            conn.commit()
            print(f"Symbol statistics updated for account {account_number}")

        except Exception as e:
            print(f"Error writing symbol statistics: {str(e)}")
        finally:
            if conn:
                conn.close()

    def write_forecast_scenarios(self, scenarios_df: pd.DataFrame) -> None:
        """Write or update forecast scenarios in database"""
        try:
            conn = self.connect()
            cur = conn.cursor()

            for _, row in scenarios_df.iterrows():
                values = (
                    int(row['account']),
                    row['scenario'],
                    row['forecast_balance'],
                    row['forecast_equity'],
                    row['balance_change_%'],
                    row['equity_change_%'],
                    row['forecast_pnl'],
                    row['exposure_%'],
                    row['risk_to_equity_%'],
                    row['forecast_drawdown_%'],
                    row['forecast_risk_reward']
                )
                
                query = """
                    INSERT INTO forecast_scenarios (
                        account_number, scenario, forecast_balance, forecast_equity,
                        balance_change_pct, equity_change_pct, forecast_pnl,
                        exposure_pct, risk_to_equity_pct, forecast_drawdown_pct,
                        forecast_risk_reward
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (account_number, scenario, DATE(timestamp))
                    DO UPDATE SET
                        forecast_balance = EXCLUDED.forecast_balance,
                        forecast_equity = EXCLUDED.forecast_equity,
                        balance_change_pct = EXCLUDED.balance_change_pct,
                        equity_change_pct = EXCLUDED.equity_change_pct,
                        forecast_pnl = EXCLUDED.forecast_pnl,
                        exposure_pct = EXCLUDED.exposure_pct,
                        risk_to_equity_pct = EXCLUDED.risk_to_equity_pct,
                        forecast_drawdown_pct = EXCLUDED.forecast_drawdown_pct,
                        forecast_risk_reward = EXCLUDED.forecast_risk_reward,
                        timestamp = CURRENT_TIMESTAMP
                """
                
                cur.execute(query, values)
            
            conn.commit()
            print("Forecast scenarios updated in database")

        except Exception as e:
            print(f"Error writing forecast scenarios: {str(e)}")
            print(f"Last row attempted: {values}")
        finally:
            if conn:
                conn.close()

    def write_symbol_forecasts(self, symbols_df: pd.DataFrame) -> None:
        """Write or update symbol forecasts in database"""
        try:
            conn = self.connect()
            cur = conn.cursor()

            for _, row in symbols_df.iterrows():
                values = (
                    int(row['account']),
                    row['symbol'],
                    row['exposure'],
                    row['exposure_%'],
                    row['current_profit'],
                    row['current_profit_%'],
                    row['positions'],
                    row['up_forecast'],
                    row['up_change_%'],
                    row['down_forecast'],
                    row['down_change_%']
                )
                
                query = """
                    INSERT INTO symbol_forecasts (
                        account_number, symbol, exposure, exposure_pct,
                        current_profit, current_profit_pct, positions,
                        up_forecast, up_change_pct, down_forecast, down_change_pct
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (account_number, symbol, DATE(timestamp))
                    DO UPDATE SET
                        exposure = EXCLUDED.exposure,
                        exposure_pct = EXCLUDED.exposure_pct,
                        current_profit = EXCLUDED.current_profit,
                        current_profit_pct = EXCLUDED.current_profit_pct,
                        positions = EXCLUDED.positions,
                        up_forecast = EXCLUDED.up_forecast,
                        up_change_pct = EXCLUDED.up_change_pct,
                        down_forecast = EXCLUDED.down_forecast,
                        down_change_pct = EXCLUDED.down_change_pct,
                        timestamp = CURRENT_TIMESTAMP
                """
                
                cur.execute(query, values)
            
            conn.commit()
            print("Symbol forecasts updated in database")

        except Exception as e:
            print(f"Error writing symbol forecasts: {str(e)}")
            print(f"Last row attempted: {values}")
        finally:
            if conn:
                conn.close()

def write_results(analysis_results: List[Dict[str, Any]], 
                 forecast_scenarios: pd.DataFrame,
                 forecast_symbols: pd.DataFrame) -> None:
    """Write or update all results in database"""
    writer = DatabaseWriter()
    
    try:
        # Write analysis results for each account
        for result in analysis_results:
            # Ensure account number is properly set
            if 'account' in result and 'account_number' not in result:
                result['account_number'] = result['account']
            
            writer.write_account_analysis(result)
            
            # Write symbol statistics if available
            if 'most_traded_symbols' in result and 'profitable_symbols' in result:
                writer.write_symbol_statistics(
                    int(result['account_number']),
                    result['most_traded_symbols'],
                    result['profitable_symbols']
                )
        
        # Write forecast results
        writer.write_forecast_scenarios(forecast_scenarios)
        writer.write_symbol_forecasts(forecast_symbols)
        
        print("All results updated in database successfully")
        
    except Exception as e:
        print(f"Error writing results to database: {str(e)}")
