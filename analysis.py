import numpy as np
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime, timedelta
from scipy import stats

def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """Calculate Sharpe ratio based on returns"""
    if not returns:
        return 0.0
    returns_array = np.array(returns)
    excess_returns = returns_array - risk_free_rate/252  # Daily risk-free rate
    if len(excess_returns) < 2:
        return 0.0
    return np.sqrt(252) * np.mean(excess_returns) / np.std(excess_returns, ddof=1) if np.std(excess_returns, ddof=1) != 0 else 0

def calculate_sortino_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """Calculate Sortino ratio using only negative returns for risk"""
    if not returns:
        return 0.0
    returns_array = np.array(returns)
    excess_returns = returns_array - risk_free_rate/252
    negative_returns = excess_returns[excess_returns < 0]
    if len(negative_returns) < 2:
        return 0.0
    downside_std = np.std(negative_returns, ddof=1) if len(negative_returns) > 0 else 1
    return np.sqrt(252) * np.mean(excess_returns) / downside_std if downside_std != 0 else 0

def calculate_max_drawdown(cumulative_returns: List[float]) -> Dict[str, float]:
    """Calculate drawdown statistics"""
    if not cumulative_returns:
        return {'max_dd': 0.0, 'avg_dd': 0.0, 'dd_duration': 0}
    
    running_max = cumulative_returns[0]
    drawdowns = []
    current_drawdown = []
    drawdown_durations = []
    current_duration = 0
    
    for ret in cumulative_returns:
        if ret > running_max:
            running_max = ret
            if current_drawdown:
                drawdowns.append(max(current_drawdown))
                drawdown_durations.append(current_duration)
                current_drawdown = []
                current_duration = 0
        else:
            dd = (running_max - ret) / running_max if running_max > 0 else 0
            current_drawdown.append(dd)
            current_duration += 1
    
    # Add the last drawdown if exists
    if current_drawdown:
        drawdowns.append(max(current_drawdown))
        drawdown_durations.append(current_duration)
    
    return {
        'max_dd': max(drawdowns) if drawdowns else 0.0,
        'avg_dd': np.mean(drawdowns) if drawdowns else 0.0,
        'dd_duration': max(drawdown_durations) if drawdown_durations else 0
    }

def calculate_var_es(returns: List[float], confidence_level: float = 0.95) -> Dict[str, float]:
    """Calculate Value at Risk and Expected Shortfall"""
    if not returns:
        return {'var': 0.0, 'es': 0.0}
    
    returns_array = np.array(returns)
    var = np.percentile(returns_array, (1 - confidence_level) * 100)
    es = np.mean(returns_array[returns_array < var])
    
    return {
        'var': abs(var),
        'es': abs(es) if not np.isnan(es) else 0.0
    }

def calculate_risk_metrics(deals_df: pd.DataFrame, balance: float) -> Dict[str, Any]:
    """Calculate comprehensive risk metrics"""
    if deals_df.empty:
        return {
            'max_consecutive_losses': 0,
            'avg_loss_streak': 0,
            'var_95': 0.0,
            'es_95': 0.0,
            'var_99': 0.0,
            'es_99': 0.0,
            'profit_loss_ratio': 0.0,
            'recovery_factor': 0.0,
            'risk_of_ruin': 0.0,
            'tail_ratio': 0.0,
            'ulcer_index': 0.0
        }
    
    # Calculate consecutive losses
    deals_df['is_loss'] = deals_df['total_profit'] < 0
    loss_streaks = []
    current_streak = 0
    
    for is_loss in deals_df['is_loss']:
        if is_loss:
            current_streak += 1
        elif current_streak > 0:
            loss_streaks.append(current_streak)
            current_streak = 0
    
    if current_streak > 0:
        loss_streaks.append(current_streak)
    
    # Calculate daily returns for VaR and ES
    daily_returns = deals_df.groupby(deals_df['time'].dt.date)['total_profit'].sum() / balance
    
    # Calculate VaR and ES at different confidence levels
    var_es_95 = calculate_var_es(daily_returns.tolist(), 0.95)
    var_es_99 = calculate_var_es(daily_returns.tolist(), 0.99)
    
    # Calculate profit/loss ratio
    avg_profit = abs(deals_df[deals_df['total_profit'] > 0]['total_profit'].mean())
    avg_loss = abs(deals_df[deals_df['total_profit'] < 0]['total_profit'].mean())
    profit_loss_ratio = avg_profit / avg_loss if avg_loss != 0 else 0
    
    # Calculate tail ratio (absolute ratio of 95th percentile to 5th percentile)
    tail_ratio = abs(np.percentile(daily_returns, 95) / np.percentile(daily_returns, 5)) if np.percentile(daily_returns, 5) != 0 else 0
    
    # Calculate Ulcer Index (root mean square of drawdowns)
    cumulative_returns = (1 + daily_returns).cumprod()
    rolling_max = cumulative_returns.expanding().max()
    drawdowns = (cumulative_returns - rolling_max) / rolling_max
    ulcer_index = np.sqrt(np.mean(np.square(drawdowns)))
    
    # Calculate recovery factor
    total_return = deals_df['total_profit'].sum()
    max_dd = calculate_max_drawdown(cumulative_returns.tolist())['max_dd']
    recovery_factor = abs(total_return / max_dd) if max_dd != 0 else 0
    
    # Estimate risk of ruin (simplified)
    win_rate = len(deals_df[deals_df['total_profit'] > 0]) / len(deals_df)
    risk_of_ruin = (1 - win_rate) / win_rate if win_rate > 0 else 1
    
    return {
        'max_consecutive_losses': max(loss_streaks) if loss_streaks else 0,
        'avg_loss_streak': np.mean(loss_streaks) if loss_streaks else 0,
        'var_95': var_es_95['var'],
        'es_95': var_es_95['es'],
        'var_99': var_es_99['var'],
        'es_99': var_es_99['es'],
        'profit_loss_ratio': profit_loss_ratio,
        'recovery_factor': recovery_factor,
        'risk_of_ruin': min(risk_of_ruin, 1.0),  # Cap at 100%
        'tail_ratio': tail_ratio,
        'ulcer_index': ulcer_index
    }

def analyze_account_data(deals: pd.DataFrame, positions: pd.DataFrame, orders: pd.DataFrame, 
                        balance: float, equity: float) -> Dict[str, Any]:
    """Analyze trading data and return key metrics"""
    
    # Initialize metrics
    metrics = {
        'balance': balance,
        'equity': equity,
        'open_positions': len(positions[positions['type'] <= 1]) if not positions.empty else 0,
        'total_deals': len(deals),
        'pnl': 0.0,
        'sharpe_ratio': 0.0,
        'sortino_ratio': 0.0,
        'win_rate': 0.0,
        'profit_factor': 0.0,
        'max_drawdown': 0.0,
        'avg_drawdown': 0.0,
        'max_drawdown_duration': 0,
        'avg_trade_profit': 0.0,
        'avg_win_profit': 0.0,
        'avg_loss_profit': 0.0,
        'largest_win': 0.0,
        'largest_loss': 0.0,
        'avg_trades_per_day': 0.0,
        'avg_holding_time_minutes': 0.0,
        'avg_position_size': 0.0,
        'risk_reward_ratio': 0.0,
        'most_traded_symbols': [],
        'profitable_symbols': [],
        'calmar_ratio': 0.0
    }
    
    # Calculate metrics if we have deals
    if not deals.empty:
        # Calculate total PnL including swaps and commission
        deals['total_profit'] = deals['profit'] + deals['swap'] + deals['commission']
        metrics['pnl'] = deals['total_profit'].sum()
        
        # Profitability metrics
        profitable_deals = deals[deals['total_profit'] > 0]
        losing_deals = deals[deals['total_profit'] < 0]
        
        metrics['win_rate'] = (len(profitable_deals) / len(deals) * 100) if len(deals) > 0 else 0
        metrics['profit_factor'] = (abs(profitable_deals['total_profit'].sum()) / 
                                  abs(losing_deals['total_profit'].sum())) if len(losing_deals) > 0 else 0
        
        # Average profits
        metrics['avg_trade_profit'] = deals['total_profit'].mean()
        metrics['avg_win_profit'] = profitable_deals['total_profit'].mean() if len(profitable_deals) > 0 else 0
        metrics['avg_loss_profit'] = losing_deals['total_profit'].mean() if len(losing_deals) > 0 else 0
        metrics['largest_win'] = profitable_deals['total_profit'].max() if len(profitable_deals) > 0 else 0
        metrics['largest_loss'] = losing_deals['total_profit'].min() if len(losing_deals) > 0 else 0
        
        # Risk-reward ratio
        avg_win = abs(metrics['avg_win_profit'])
        avg_loss = abs(metrics['avg_loss_profit'])
        metrics['risk_reward_ratio'] = avg_win / avg_loss if avg_loss != 0 else 0
        
        # Calculate daily returns and drawdown
        deals_sorted = deals.sort_values('time')
        daily_pnl = deals_sorted.groupby(deals_sorted['time'].dt.date)['total_profit'].sum()
        
        # Calculate daily returns relative to previous day's balance
        daily_returns = []
        cumulative_returns = []
        running_balance = balance - daily_pnl.sum()  # Start with current balance minus all PnL
        
        for day_pnl in daily_pnl:
            if running_balance > 0:
                daily_return = day_pnl / running_balance
                daily_returns.append(daily_return)
                running_balance += day_pnl
                cumulative_returns.append(running_balance)
        
        if daily_returns:
            metrics['sharpe_ratio'] = calculate_sharpe_ratio(daily_returns)
            metrics['sortino_ratio'] = calculate_sortino_ratio(daily_returns)
            
            # Calculate drawdown statistics
            dd_stats = calculate_max_drawdown(cumulative_returns)
            metrics['max_drawdown'] = dd_stats['max_dd']
            metrics['avg_drawdown'] = dd_stats['avg_dd']
            metrics['max_drawdown_duration'] = dd_stats['dd_duration']
            
            # Calmar ratio
            if metrics['max_drawdown'] > 0:
                annual_return = np.mean(daily_returns) * 252
                metrics['calmar_ratio'] = annual_return / metrics['max_drawdown']
        
        # Trading activity metrics
        if len(deals) > 1:
            date_range = (deals_sorted['time'].max() - deals_sorted['time'].min()).days + 1
            metrics['avg_trades_per_day'] = len(deals) / date_range if date_range > 0 else 0
        
        # Position metrics
        metrics['avg_position_size'] = deals['volume'].mean()
        
        # Symbol analysis
        symbol_stats = deals.groupby('symbol').agg({
            'total_profit': 'sum',
            'ticket': 'count'
        }).sort_values('ticket', ascending=False)
        
        metrics['most_traded_symbols'] = symbol_stats.head(5).index.tolist()
        profitable_symbols = symbol_stats[symbol_stats['total_profit'] > 0].index.tolist()
        metrics['profitable_symbols'] = profitable_symbols[:5]  # Top 5 profitable symbols
        
        # Add risk metrics
        risk_metrics = calculate_risk_metrics(deals, balance)
        metrics.update(risk_metrics)
        
        # Print detailed analysis
        print(f"\nDetailed Analysis for Account:")
        print(f"Total PnL: {metrics['pnl']:.2f}")
        print(f"Number of trades: {len(deals)}")
        print(f"Win rate: {metrics['win_rate']:.2f}%")
        print(f"Profit factor: {metrics['profit_factor']:.2f}")
        print(f"Sharpe ratio: {metrics['sharpe_ratio']:.3f}")
        print(f"Sortino ratio: {metrics['sortino_ratio']:.3f}")
        print(f"Maximum drawdown: {metrics['max_drawdown']*100:.2f}%")
        print(f"Average drawdown: {metrics['avg_drawdown']*100:.2f}%")
        print(f"Max drawdown duration: {metrics['max_drawdown_duration']} days")
        print(f"Risk-reward ratio: {metrics['risk_reward_ratio']:.2f}")
        print(f"Value at Risk (95%): {metrics['var_95']*100:.2f}%")
        print(f"Expected Shortfall (95%): {metrics['es_95']*100:.2f}%")
        print(f"Maximum consecutive losses: {metrics['max_consecutive_losses']}")
        print(f"Recovery factor: {metrics['recovery_factor']:.2f}")
        print(f"Risk of ruin: {metrics['risk_of_ruin']*100:.2f}%")
        print(f"Ulcer index: {metrics['ulcer_index']:.4f}")
        print(f"Average trade profit: {metrics['avg_trade_profit']:.2f}")
        print(f"Average trades per day: {metrics['avg_trades_per_day']:.2f}")
        print(f"Most traded symbols: {', '.join(metrics['most_traded_symbols'])}")
        print(f"Most profitable symbols: {', '.join(metrics['profitable_symbols'])}")
        
    return metrics
