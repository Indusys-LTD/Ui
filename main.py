import json
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
from tabulate import tabulate
from analysis import analyze_account_data
from forecast import analyze_forecast, format_forecast_results
from database.write import write_results
import time
from typing import Dict, Any, List, Tuple
import pytz

def load_accounts() -> list:
    """Load account credentials from accounts.json"""
    with open('accounts.json', 'r') as f:
        data = json.load(f)
    return data['accounts']

def connect_account(login: int, password: str, server: str) -> bool:
    """Connect to MT5 account"""
    try:
        # Shutdown any existing connection
        mt5.shutdown()
        
        # Initialize connection
        if mt5.initialize(login=login, password=password, server=server):
            authorized = mt5.login(login=login, password=password, server=server)
            if not authorized:
                print(f"Failed to connect to account {login}")
                mt5.shutdown()
                return False
            return True
        else:
            print(f"initialize() failed for account {login}, error code: {mt5.last_error()}")
            return False
    except Exception as e:
        print(f"Error connecting to account {login}: {str(e)}")
        return False

def create_df_safely(data, default_columns=None):
    """Safely create DataFrame from MT5 data"""
    if data is None or len(data) == 0:
        if default_columns:
            return pd.DataFrame(columns=default_columns)
        return pd.DataFrame()
    
    try:
        # Try to create DataFrame with first row's keys
        df = pd.DataFrame(list(data), columns=data[0]._asdict().keys())
        print(f"Successfully created DataFrame with {len(df)} rows")
        return df
    except (AttributeError, IndexError) as e:
        print(f"Error creating DataFrame: {str(e)}")
        try:
            # Fallback: try to create DataFrame without specified columns
            df = pd.DataFrame(list(data))
            print(f"Created DataFrame using fallback method with {len(df)} rows")
            return df
        except Exception as e:
            print(f"Fallback DataFrame creation failed: {str(e)}")
            # If all else fails, return empty DataFrame
            if default_columns:
                return pd.DataFrame(columns=default_columns)
            return pd.DataFrame()

def get_account_data() -> Dict[str, Any]:
    """Get current account data and history"""
    try:
        account_info = mt5.account_info()
        if account_info is None:
            print(f"Failed to get account info. Error code: {mt5.last_error()}")
            return None
        
        # Default columns for each type of data
        deal_columns = ['ticket', 'order', 'time', 'type', 'entry', 'symbol', 'volume', 'price', 
                       'profit', 'swap', 'commission', 'magic', 'reason']
        position_columns = ['ticket', 'time', 'type', 'symbol', 'volume', 'price_open', 'sl', 'tp', 
                           'price_current', 'profit', 'magic']
        order_columns = ['ticket', 'time_setup', 'type', 'state', 'symbol', 'volume', 'price_open', 
                        'sl', 'tp', 'price_current', 'magic']
        
        # Get historical deals with timezone
        timezone = pytz.timezone("Etc/UTC")
        from_date = datetime.now(timezone) - timedelta(days=30)  # Last 30 days
        to_date = datetime.now(timezone)
        
        print(f"Requesting deals from {from_date} to {to_date}")
        deals = mt5.history_deals_get(from_date, to_date)
        if deals is None:
            print(f"No deals returned. Error code: {mt5.last_error()}")
        else:
            print(f"Retrieved {len(deals)} deals")
        deals_df = create_df_safely(deals, deal_columns)
        
        # Get historical orders
        orders_history = mt5.history_orders_get(from_date, to_date)
        if orders_history is None:
            print(f"No historical orders returned. Error code: {mt5.last_error()}")
        else:
            print(f"Retrieved {len(orders_history)} historical orders")
        
        # Get open positions
        positions = mt5.positions_get()
        if positions is None:
            print(f"No positions returned. Error code: {mt5.last_error()}")
        else:
            print(f"Retrieved {len(positions)} open positions")
        positions_df = create_df_safely(positions, position_columns)
        
        # Get pending orders
        orders = mt5.orders_get()
        if orders is None:
            print(f"No pending orders returned. Error code: {mt5.last_error()}")
        else:
            print(f"Retrieved {len(orders) if orders else 0} pending orders")
        orders_df = create_df_safely(orders, order_columns)
        
        # Convert time columns to datetime if they exist
        try:
            if 'time' in deals_df.columns and not deals_df.empty:
                deals_df['time'] = pd.to_datetime(deals_df['time'], unit='s')
            if 'time' in positions_df.columns and not positions_df.empty:
                positions_df['time'] = pd.to_datetime(positions_df['time'], unit='s')
            if 'time_setup' in orders_df.columns and not orders_df.empty:
                orders_df['time_setup'] = pd.to_datetime(orders_df['time_setup'], unit='s')
        except Exception as e:
            print(f"Error converting time columns: {str(e)}")
        
        return {
            'balance': float(account_info.balance) if hasattr(account_info, 'balance') else 0.0,
            'equity': float(account_info.equity) if hasattr(account_info, 'equity') else 0.0,
            'deals': deals_df,
            'positions': positions_df,
            'orders': orders_df
        }
    except Exception as e:
        print(f"Error getting account data: {str(e)}")
        return None

def save_symbol_statistics(account_data: Dict[str, Any], account_number: int):
    """Save symbol statistics to CSV safely"""
    try:
        if not account_data.get('most_traded_symbols'):
            print(f"No symbol statistics available for account {account_number}")
            return
        
        # Get the lists
        most_traded = account_data['most_traded_symbols']
        profitable = account_data['profitable_symbols']
        
        # Create lists of equal length
        max_length = max(len(most_traded), len(profitable))
        most_traded_padded = most_traded + [''] * (max_length - len(most_traded))
        profitable_padded = profitable + [''] * (max_length - len(profitable))
        
        # Create DataFrame
        symbol_df = pd.DataFrame({
            'Most Traded Symbols': most_traded_padded,
            'Profitable Symbols': profitable_padded
        })
        
        # Save to CSV
        filename = f"symbols_account_{account_number}.csv"
        symbol_df.to_csv(filename, index=False)
        print(f"Symbol statistics saved to '{filename}'")
    except Exception as e:
        print(f"Error saving symbol statistics for account {account_number}: {str(e)}")

def main():
    try:
        accounts = load_accounts()
        results = []
        forecast_scenarios = []
        forecast_symbols = []
        
        for account in accounts:
            if account['server'] == 'MetaQuotes-Demo':  # Only process MetaQuotes demo accounts
                print(f"\nProcessing account {account['login']}...")
                
                if connect_account(account['login'], account['password'], account['server']):
                    try:
                        print(f"Connected to account {account['login']}")
                        account_data = get_account_data()
                        if account_data:
                            print(f"Retrieved data for account {account['login']}:")
                            print(f"Deals: {len(account_data['deals'])} rows")
                            print(f"Positions: {len(account_data['positions'])} rows")
                            print(f"Orders: {len(account_data['orders'])} rows")
                            
                            # Regular analysis
                            metrics = analyze_account_data(
                                account_data['deals'],
                                account_data['positions'],
                                account_data['orders'],
                                account_data['balance'],
                                account_data['equity']
                            )
                            metrics['account'] = account['login']
                            results.append(metrics)
                            
                            # Forecast analysis
                            forecast_data = analyze_forecast(
                                account_data['positions'],
                                {'balance': account_data['balance'], 'equity': account_data['equity']}
                            )
                            
                            # Format forecast results
                            scenarios_df, symbols_df = format_forecast_results(account['login'], forecast_data)
                            forecast_scenarios.append(scenarios_df)
                            forecast_symbols.append(symbols_df)
                            
                            print(f"Successfully processed account {account['login']}")
                    except Exception as e:
                        print(f"Error processing account {account['login']}: {str(e)}")
                    finally:
                        mt5.shutdown()
                
                time.sleep(1)  # Small delay between accounts
        
        if results:
            # Regular analysis display
            df = pd.DataFrame(results)
            
            # Round numeric columns with default values if columns don't exist
            rounding_dict = {
                'balance': 2,
                'equity': 2,
                'pnl': 2,
                'win_rate': 2,
                'profit_factor': 2,
                'sharpe_ratio': 3,
                'sortino_ratio': 3,
                'calmar_ratio': 3,
                'max_drawdown': 4,
                'avg_drawdown': 4,
                'risk_reward_ratio': 2,
                'avg_trade_profit': 2,
                'avg_trades_per_day': 2,
                'avg_position_size': 3,
                'var_95': 4,
                'es_95': 4,
                'var_99': 4,
                'es_99': 4,
                'profit_loss_ratio': 2,
                'recovery_factor': 2,
                'risk_of_ruin': 4,
                'tail_ratio': 2,
                'ulcer_index': 4
            }
            
            # Round existing columns
            for col, decimals in rounding_dict.items():
                if col in df.columns:
                    df[col] = df[col].round(decimals)
            
            # Convert drawdown values to percentage
            percentage_columns = ['max_drawdown', 'avg_drawdown', 'var_95', 'es_95', 
                                'var_99', 'es_99', 'risk_of_ruin']
            for col in percentage_columns:
                if col in df.columns:
                    df[col] = df[col] * 100
            
            # Define column groups with safe column selection
            def safe_columns(df: pd.DataFrame, columns: List[str]) -> List[str]:
                """Return only columns that exist in the DataFrame"""
                return [col for col in columns if col in df.columns]
            
            # Basic metrics columns
            basic_cols = safe_columns(df, [
                'account', 'balance', 'equity', 'pnl', 'open_positions', 'total_deals'
            ])
            
            # Performance metrics columns
            performance_cols = safe_columns(df, [
                'account', 'win_rate', 'profit_factor', 'sharpe_ratio', 
                'sortino_ratio', 'calmar_ratio'
            ])
            
            # Risk metrics columns
            risk_cols = safe_columns(df, [
                'account', 'max_drawdown', 'avg_drawdown', 'max_drawdown_duration',
                'var_95', 'es_95', 'risk_of_ruin', 'recovery_factor'
            ])
            
            # Trading metrics columns
            trading_cols = safe_columns(df, [
                'account', 'avg_trade_profit', 'avg_trades_per_day', 'avg_position_size',
                'max_consecutive_losses', 'avg_loss_streak', 'profit_loss_ratio'
            ])
            
            # Advanced risk metrics columns
            advanced_cols = safe_columns(df, [
                'account', 'var_99', 'es_99', 'tail_ratio', 'ulcer_index'
            ])
            
            # Create tables only if columns exist
            if len(basic_cols) > 1:  # More than just 'account'
                print("\nBasic Metrics:")
                print(tabulate(df[basic_cols], headers='keys', tablefmt='grid', showindex=False))
            
            if len(performance_cols) > 1:
                print("\nPerformance Metrics:")
                print(tabulate(df[performance_cols], headers='keys', tablefmt='grid', showindex=False))
            
            if len(risk_cols) > 1:
                print("\nRisk Metrics:")
                print(tabulate(df[risk_cols], headers='keys', tablefmt='grid', showindex=False))
            
            if len(trading_cols) > 1:
                print("\nTrading Activity Metrics:")
                print(tabulate(df[trading_cols], headers='keys', tablefmt='grid', showindex=False))
            
            if len(advanced_cols) > 1:
                print("\nAdvanced Risk Metrics:")
                print(tabulate(df[advanced_cols], headers='keys', tablefmt='grid', showindex=False))
            
            # Combine forecast results
            all_scenarios = pd.concat(forecast_scenarios, ignore_index=True)
            all_symbols = pd.concat(forecast_symbols, ignore_index=True)
            
            # Round forecast scenario values
            scenario_rounding = {
                'forecast_balance': 2,
                'forecast_equity': 2,
                'balance_change_%': 2,
                'equity_change_%': 2,
                'forecast_pnl': 2,
                'exposure_%': 2,
                'risk_to_equity_%': 2,
                'forecast_drawdown_%': 2,
                'forecast_risk_reward': 3
            }
            
            for col, decimals in scenario_rounding.items():
                if col in all_scenarios.columns:
                    all_scenarios[col] = all_scenarios[col].round(decimals)
            
            # Round symbol forecast values
            symbol_rounding = {
                'exposure': 3,
                'exposure_%': 2,
                'current_profit': 2,
                'current_profit_%': 2,
                'up_forecast': 2,
                'down_forecast': 2,
                'up_change_%': 2,
                'down_change_%': 2
            }
            
            for col, decimals in symbol_rounding.items():
                if col in all_symbols.columns:
                    all_symbols[col] = all_symbols[col].round(decimals)
            
            # Split forecast scenarios into two tables for better readability
            scenario_basic = all_scenarios[['account', 'scenario', 'forecast_balance', 
                                         'forecast_equity', 'forecast_pnl']]
            
            scenario_risk = all_scenarios[['account', 'scenario', 'balance_change_%', 
                                        'equity_change_%', 'exposure_%', 'risk_to_equity_%',
                                        'forecast_drawdown_%', 'forecast_risk_reward']]
            
            # Split symbol forecasts into two tables
            symbol_basic = all_symbols[['account', 'symbol', 'exposure', 'exposure_%',
                                         'positions', 'current_profit', 'current_profit_%']]
            
            symbol_forecast = all_symbols[['account', 'symbol', 'up_forecast', 'up_change_%',
                                            'down_forecast', 'down_change_%']]
            
            print("\nForecast Scenarios - Basic Metrics (1000 points movement):")
            print(tabulate(scenario_basic, headers='keys', tablefmt='grid', showindex=False))
            
            print("\nForecast Scenarios - Risk Metrics (%):")
            print(tabulate(scenario_risk, headers='keys', tablefmt='grid', showindex=False))
            
            print("\nSymbol-Specific Current State:")
            print(tabulate(symbol_basic, headers='keys', tablefmt='grid', showindex=False))
            
            print("\nSymbol-Specific Forecast Changes:")
            print(tabulate(symbol_forecast, headers='keys', tablefmt='grid', showindex=False))
            
            # Write results to database
            try:
                print("\nWriting results to database...")
                write_results(results, all_scenarios, all_symbols)
                print("Database update completed successfully")
            except Exception as e:
                print(f"Error writing to database: {str(e)}")
            
            # Save to CSV files (as backup)
            try:
                df.to_csv('account_analysis_results.csv', index=False)
                all_scenarios.to_csv('forecast_scenarios.csv', index=False)
                all_symbols.to_csv('forecast_symbols.csv', index=False)
                print("\nResults have also been saved to CSV files as backup")
            except Exception as e:
                print(f"Error saving to CSV files: {str(e)}")
            
            # Save symbol statistics for each account
            for account_data in results:
                save_symbol_statistics(account_data, account_data['account'])
        else:
            print("No results to display")
            
    except Exception as e:
        print(f"Error in main execution: {str(e)}")
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    main()
