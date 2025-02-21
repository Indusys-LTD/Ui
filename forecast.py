import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ForecastScenario:
    direction: str  # 'up' or 'down'
    balance: float
    equity: float
    pnl: float
    drawdown: float
    risk_reward: float
    balance_change_pct: float
    equity_change_pct: float
    exposure_pct: float
    risk_to_equity_pct: float

class PositionForecast:
    def __init__(self, position_data: Dict[str, Any], point_value: float = 0.0001):
        self.symbol = position_data['symbol']
        self.type = position_data['type']  # 0 for buy, 1 for sell
        self.volume = float(position_data['volume'])
        self.price_open = float(position_data['price_open'])
        self.price_current = float(position_data['price_current'])
        self.profit = float(position_data['profit'])
        self.point_value = point_value
        self.points_movement = 1000  # Number of points to simulate movement

    def calculate_pip_value(self) -> float:
        """Calculate the value of one pip for this position"""
        # This is a simplified calculation, might need adjustment based on specific symbols
        return self.volume * self.point_value * 10000  # Standard lot = 100,000 units

    def forecast_profit(self, direction: str) -> float:
        """Calculate forecasted profit based on price movement direction"""
        pip_value = self.calculate_pip_value()
        movement = self.points_movement if direction == 'up' else -self.points_movement
        
        # For buy positions
        if self.type == 0:
            return self.profit + (movement * pip_value)
        # For sell positions
        else:
            return self.profit - (movement * pip_value)

def calculate_percentage_metrics(current: float, forecast: float) -> float:
    """Calculate percentage change between current and forecast values"""
    if current == 0:
        return 0.0
    return ((forecast - current) / abs(current)) * 100

def analyze_forecast(positions: pd.DataFrame, account_metrics: Dict[str, float]) -> Dict[str, Any]:
    """Analyze potential outcomes based on price movements"""
    if positions.empty:
        return {
            'scenarios': {},
            'symbol_forecasts': {}
        }

    initial_balance = account_metrics['balance']
    initial_equity = account_metrics['equity']
    
    # Group positions by symbol
    symbol_groups = positions.groupby('symbol')
    symbol_forecasts = {}
    total_up_pnl = 0
    total_down_pnl = 0
    
    # Calculate total position exposure
    total_exposure = positions['volume'].sum() * 100000  # Approximate exposure in base currency

    for symbol, positions_group in symbol_groups:
        symbol_exposure = positions_group['volume'].sum() * 100000
        current_profit = positions_group['profit'].sum()
        
        symbol_forecasts[symbol] = {
            'current_exposure': positions_group['volume'].sum(),
            'exposure_pct': (symbol_exposure / initial_equity * 100) if initial_equity > 0 else 0,
            'current_profit': current_profit,
            'current_profit_pct': (current_profit / initial_equity * 100) if initial_equity > 0 else 0,
            'positions': len(positions_group),
            'scenarios': {}
        }

        # Calculate forecasts for each direction
        for direction in ['up', 'down']:
            total_forecast_profit = 0
            for _, pos in positions_group.iterrows():
                position = PositionForecast(pos)
                forecast_profit = position.forecast_profit(direction)
                total_forecast_profit += forecast_profit

            pnl_change = total_forecast_profit - current_profit
            symbol_forecasts[symbol]['scenarios'][direction] = {
                'forecast_profit': total_forecast_profit,
                'forecast_pnl_change': pnl_change,
                'forecast_profit_pct': (total_forecast_profit / initial_equity * 100) if initial_equity > 0 else 0,
                'pnl_change_pct': calculate_percentage_metrics(current_profit, total_forecast_profit)
            }

            if direction == 'up':
                total_up_pnl += total_forecast_profit
            else:
                total_down_pnl += total_forecast_profit

    # Calculate overall scenarios
    scenarios = {
        'up': ForecastScenario(
            direction='up',
            balance=initial_balance + total_up_pnl,
            equity=initial_equity + total_up_pnl,
            pnl=total_up_pnl,
            drawdown=abs(min(0, total_up_pnl) / initial_balance) if initial_balance > 0 else 0,
            risk_reward=abs(total_up_pnl / initial_balance) if initial_balance > 0 else 0,
            balance_change_pct=calculate_percentage_metrics(initial_balance, initial_balance + total_up_pnl),
            equity_change_pct=calculate_percentage_metrics(initial_equity, initial_equity + total_up_pnl),
            exposure_pct=(total_exposure / initial_equity * 100) if initial_equity > 0 else 0,
            risk_to_equity_pct=(abs(total_down_pnl) / initial_equity * 100) if initial_equity > 0 else 0
        ),
        'down': ForecastScenario(
            direction='down',
            balance=initial_balance + total_down_pnl,
            equity=initial_equity + total_down_pnl,
            pnl=total_down_pnl,
            drawdown=abs(min(0, total_down_pnl) / initial_balance) if initial_balance > 0 else 0,
            risk_reward=abs(total_down_pnl / initial_balance) if initial_balance > 0 else 0,
            balance_change_pct=calculate_percentage_metrics(initial_balance, initial_balance + total_down_pnl),
            equity_change_pct=calculate_percentage_metrics(initial_equity, initial_equity + total_down_pnl),
            exposure_pct=(total_exposure / initial_equity * 100) if initial_equity > 0 else 0,
            risk_to_equity_pct=(abs(total_up_pnl) / initial_equity * 100) if initial_equity > 0 else 0
        )
    }

    return {
        'scenarios': scenarios,
        'symbol_forecasts': symbol_forecasts
    }

def format_forecast_results(account_number: int, forecast_data: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Format forecast results into DataFrames for display"""
    # Overall scenarios DataFrame
    scenarios = forecast_data['scenarios']
    scenarios_data = []
    for direction, scenario in scenarios.items():
        scenarios_data.append({
            'account': account_number,
            'scenario': direction,
            'forecast_balance': scenario.balance,
            'forecast_equity': scenario.equity,
            'balance_change_%': scenario.balance_change_pct,
            'equity_change_%': scenario.equity_change_pct,
            'forecast_pnl': scenario.pnl,
            'exposure_%': scenario.exposure_pct,
            'risk_to_equity_%': scenario.risk_to_equity_pct,
            'forecast_drawdown_%': scenario.drawdown * 100,
            'forecast_risk_reward': scenario.risk_reward
        })
    scenarios_df = pd.DataFrame(scenarios_data)

    # Symbol-specific forecasts DataFrame
    symbol_data = []
    for symbol, data in forecast_data['symbol_forecasts'].items():
        symbol_data.append({
            'account': account_number,
            'symbol': symbol,
            'exposure': data['current_exposure'],
            'exposure_%': data['exposure_pct'],
            'current_profit': data['current_profit'],
            'current_profit_%': data['current_profit_pct'],
            'positions': data['positions'],
            'up_forecast': data['scenarios']['up']['forecast_profit'],
            'up_change_%': data['scenarios']['up']['pnl_change_pct'],
            'down_forecast': data['scenarios']['down']['forecast_profit'],
            'down_change_%': data['scenarios']['down']['pnl_change_pct']
        })
    symbols_df = pd.DataFrame(symbol_data)

    return scenarios_df, symbols_df 