from typing import Dict, List, Optional, Tuple
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import numpy as np
from .parameters import (
    AccountStatistics, LogicSettings, PositionInfo, 
    Sequence, maxEquityDrawdown, maxDailyDrawdown, minEquityPercent
)

class ValidationResult:
    def __init__(self, is_valid: bool, message: str = ""):
        self.is_valid = is_valid
        self.message = message

class TradingValidator:
    def __init__(self, account_stats: AccountStatistics, logic_settings: LogicSettings):
        self.account_stats = account_stats
        self.logic_settings = logic_settings
        self.min_equity_percent = minEquityPercent
        self.max_equity_drawdown = maxEquityDrawdown
        self.max_daily_drawdown = maxDailyDrawdown
        
        # Additional risk parameters
        self.max_positions_per_symbol = 5
        self.max_daily_trades = 20
        self.min_risk_reward_ratio = 1.5
        self.max_correlation_threshold = 0.7
        self.max_spread_multiplier = 1.5
        self.volatility_threshold = 0.002  # 0.2% price movement
        
        # Market condition parameters
        self.min_daily_volume = 1000
        self.max_spread_percent = 0.1  # 0.1% of price
        self.min_market_activity = 100  # minimum trades per hour
    
    def validate_account_conditions(self) -> ValidationResult:
        """
        Validate account conditions including:
        - Equity level
        - Drawdown limits
        - Account balance requirements
        """
        try:
            # Check if account info is available
            account = mt5.account_info()
            if account is None:
                return ValidationResult(False, "Failed to get account information")
            
            # Check equity percentage
            equity_percent = (account.equity / account.balance * 100 
                            if account.balance != 0 else 0)
            if equity_percent < self.min_equity_percent:
                return ValidationResult(
                    False,
                    f"Equity percentage ({equity_percent:.2f}%) below minimum required ({self.min_equity_percent}%)"
                )
            
            # Check equity drawdown
            equity_drawdown = ((account.balance - account.equity) / account.balance * 100 
                             if account.balance != 0 else 0)
            if equity_drawdown > self.max_equity_drawdown:
                return ValidationResult(
                    False,
                    f"Equity drawdown ({equity_drawdown:.2f}%) exceeds maximum allowed ({self.max_equity_drawdown}%)"
                )
            
            # Check daily drawdown
            daily_drawdown = self._calculate_daily_drawdown()
            if daily_drawdown > self.max_daily_drawdown:
                return ValidationResult(
                    False,
                    f"Daily drawdown ({daily_drawdown:.2f}%) exceeds maximum allowed ({self.max_daily_drawdown}%)"
                )
            
            return ValidationResult(True, "Account conditions validated successfully")
            
        except Exception as e:
            return ValidationResult(False, f"Account validation error: {str(e)}")
    
    def validate_order_parameters(self, 
                                symbol: str,
                                order_type: int,
                                volume: float,
                                price: float,
                                sl: float,
                                tp: float) -> ValidationResult:
        """
        Validate order parameters including:
        - Symbol validity
        - Volume limits
        - Price validity
        - Stop loss and take profit levels
        """
        try:
            # Check symbol
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return ValidationResult(False, f"Invalid symbol: {symbol}")
            
            # Validate volume
            if volume < symbol_info.volume_min or volume > symbol_info.volume_max:
                return ValidationResult(
                    False,
                    f"Volume {volume} outside allowed range [{symbol_info.volume_min}, {symbol_info.volume_max}]"
                )
            
            # Check if volume is multiple of step
            if volume % symbol_info.volume_step != 0:
                return ValidationResult(
                    False,
                    f"Volume {volume} not multiple of step size {symbol_info.volume_step}"
                )
            
            # Validate price levels
            if not self._validate_price_levels(symbol_info, order_type, price, sl, tp):
                return ValidationResult(False, "Invalid price levels")
            
            return ValidationResult(True, "Order parameters validated successfully")
            
        except Exception as e:
            return ValidationResult(False, f"Order parameter validation error: {str(e)}")
    
    def validate_sequence(self, sequence: Sequence) -> ValidationResult:
        """
        Validate trading sequence including:
        - Position count
        - Total volume
        - Sequence profitability
        - Time between positions
        """
        try:
            # Check position count
            if len(sequence.positions) >= self.logic_settings.max_Positions:
                return ValidationResult(
                    False,
                    f"Maximum positions ({self.logic_settings.max_Positions}) reached for sequence"
                )
            
            # Validate total volume
            total_volume = sum(pos.volume for pos in sequence.positions)
            if total_volume > self._get_max_allowed_volume():
                return ValidationResult(
                    False,
                    f"Total sequence volume ({total_volume}) exceeds maximum allowed"
                )
            
            # Check time between positions
            if len(sequence.positions) > 0:
                last_position_time = sequence.lastPosition.entryTime
                current_time = mt5.symbol_info_tick(sequence.positions[0].symbol).time
                time_diff = current_time - last_position_time
                
                if time_diff < self.logic_settings.timeFrame * 60:
                    return ValidationResult(
                        False,
                        "Minimum time between positions not met"
                    )
            
            return ValidationResult(True, "Sequence validated successfully")
            
        except Exception as e:
            return ValidationResult(False, f"Sequence validation error: {str(e)}")
    
    def validate_risk_parameters(self, 
                               new_position_volume: float,
                               sequence: Sequence) -> ValidationResult:
        """
        Validate risk management parameters including:
        - Position sizing
        - Risk per trade
        - Total risk exposure
        """
        try:
            account = mt5.account_info()
            if account is None:
                return ValidationResult(False, "Failed to get account information")
            
            # Calculate risk per trade
            risk_per_trade = (new_position_volume * sequence.lastPosition.entryPrice * 0.01 
                            if sequence.lastPosition else 0)
            max_risk_amount = account.balance * 0.02  # 2% risk per trade
            
            if risk_per_trade > max_risk_amount:
                return ValidationResult(
                    False,
                    f"Risk per trade ({risk_per_trade:.2f}) exceeds maximum allowed ({max_risk_amount:.2f})"
                )
            
            # Calculate total risk exposure
            total_risk = sum(pos.volume * pos.entryPrice * 0.01 for pos in sequence.positions)
            max_total_risk = account.balance * 0.06  # 6% total risk
            
            if total_risk > max_total_risk:
                return ValidationResult(
                    False,
                    f"Total risk exposure ({total_risk:.2f}) exceeds maximum allowed ({max_total_risk:.2f})"
                )
            
            return ValidationResult(True, "Risk parameters validated successfully")
            
        except Exception as e:
            return ValidationResult(False, f"Risk validation error: {str(e)}")
    
    def _calculate_daily_drawdown(self) -> float:
        """Calculate the current day's drawdown percentage"""
        try:
            today = datetime.now().date()
            today_start = int(datetime.combine(today, datetime.min.time()).timestamp())
            
            # Get today's deals
            deals = mt5.history_deals_get(today_start, int(datetime.now().timestamp()))
            if deals is None:
                return 0.0
            
            # Calculate daily profit/loss
            daily_pnl = sum(deal.profit for deal in deals)
            
            # Get starting balance
            account = mt5.account_info()
            if account is None:
                return 0.0
            
            starting_balance = account.balance - daily_pnl
            if starting_balance == 0:
                return 0.0
            
            return abs(daily_pnl / starting_balance * 100)
            
        except Exception:
            return 0.0
    
    def _validate_price_levels(self, 
                             symbol_info: mt5.SymbolInfo,
                             order_type: int,
                             price: float,
                             sl: float,
                             tp: float) -> bool:
        """Validate price, stop loss, and take profit levels"""
        try:
            tick = mt5.symbol_info_tick(symbol_info.name)
            if tick is None:
                return False
            
            # Get minimum stop level in points
            min_stop_level = symbol_info.point * symbol_info.trade_stops_level
            
            if order_type == mt5.ORDER_TYPE_BUY:
                if sl > 0 and price - sl < min_stop_level:
                    return False
                if tp > 0 and tp - price < min_stop_level:
                    return False
            elif order_type == mt5.ORDER_TYPE_SELL:
                if sl > 0 and sl - price < min_stop_level:
                    return False
                if tp > 0 and price - tp < min_stop_level:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _get_max_allowed_volume(self) -> float:
        """Calculate maximum allowed volume based on account equity"""
        try:
            account = mt5.account_info()
            if account is None:
                return 0.0
            
            # Use a conservative approach: 1 standard lot per $10,000 equity
            max_volume = account.equity / 100000  # 1.0 lot = 100,000 units
            return max_volume
            
        except Exception:
            return 0.0

    def validate_market_conditions(self, symbol: str) -> ValidationResult:
        """
        Validate market conditions including:
        - Spread levels
        - Volume conditions
        - Market activity
        - Volatility
        - Trading session status
        """
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return ValidationResult(False, f"Invalid symbol: {symbol}")
            
            # Check if market is open
            if not symbol_info.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL:
                return ValidationResult(False, "Market is closed or not available for trading")
            
            # Get current tick
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                return ValidationResult(False, "Unable to get current market data")
            
            # Check spread
            current_spread = (tick.ask - tick.bid) / tick.bid * 100
            if current_spread > self.max_spread_percent:
                return ValidationResult(
                    False,
                    f"Spread ({current_spread:.3f}%) exceeds maximum allowed ({self.max_spread_percent}%)"
                )
            
            # Check volume
            if tick.volume < self.min_daily_volume:
                return ValidationResult(
                    False,
                    f"Volume ({tick.volume}) below minimum required ({self.min_daily_volume})"
                )
            
            # Check volatility
            volatility = self._calculate_volatility(symbol)
            if volatility > self.volatility_threshold:
                return ValidationResult(
                    False,
                    f"Market volatility ({volatility:.4f}) exceeds threshold ({self.volatility_threshold})"
                )
            
            # Check market activity
            activity = self._check_market_activity(symbol)
            if activity < self.min_market_activity:
                return ValidationResult(
                    False,
                    f"Market activity ({activity}) below minimum required ({self.min_market_activity})"
                )
            
            return ValidationResult(True, "Market conditions validated successfully")
            
        except Exception as e:
            return ValidationResult(False, f"Market condition validation error: {str(e)}")
    
    def validate_position_correlation(self, symbol: str, sequence: Sequence) -> ValidationResult:
        """
        Validate position correlation with existing positions:
        - Check correlation with other symbols
        - Validate exposure to correlated assets
        """
        try:
            if not sequence.positions:
                return ValidationResult(True, "No existing positions to check correlation")
            
            # Get current positions for correlation check
            positions = mt5.positions_get()
            if positions is None:
                return ValidationResult(True, "No positions to check correlation")
            
            # Get unique symbols from current positions
            position_symbols = set(pos.symbol for pos in positions)
            
            # Calculate correlation if we have other positions
            if len(position_symbols) > 0:
                correlation = self._calculate_symbol_correlation(symbol, position_symbols)
                if correlation > self.max_correlation_threshold:
                    return ValidationResult(
                        False,
                        f"High correlation ({correlation:.2f}) with existing positions"
                    )
            
            return ValidationResult(True, "Position correlation validated successfully")
            
        except Exception as e:
            return ValidationResult(False, f"Correlation validation error: {str(e)}")
    
    def validate_advanced_risk(self, symbol: str, sequence: Sequence) -> ValidationResult:
        """
        Advanced risk validation including:
        - Daily trade count
        - Risk/Reward ratio
        - Position concentration
        - Maximum loss limits
        """
        try:
            # Check daily trade count
            daily_trades = self._get_daily_trade_count()
            if daily_trades >= self.max_daily_trades:
                return ValidationResult(
                    False,
                    f"Maximum daily trades ({self.max_daily_trades}) reached"
                )
            
            # Check symbol position count
            symbol_positions = len([pos for pos in sequence.positions if pos.symbol == symbol])
            if symbol_positions >= self.max_positions_per_symbol:
                return ValidationResult(
                    False,
                    f"Maximum positions ({self.max_positions_per_symbol}) for {symbol} reached"
                )
            
            # Validate risk/reward ratio if sequence has positions
            if sequence.positions:
                rr_ratio = self._calculate_risk_reward_ratio(sequence)
                if rr_ratio < self.min_risk_reward_ratio:
                    return ValidationResult(
                        False,
                        f"Risk/Reward ratio ({rr_ratio:.2f}) below minimum ({self.min_risk_reward_ratio})"
                    )
            
            # Check maximum loss limit
            if sequence.profit < -(self.account_stats.balance * 0.02):  # 2% max loss per sequence
                return ValidationResult(
                    False,
                    "Sequence loss exceeds maximum allowed"
                )
            
            return ValidationResult(True, "Advanced risk parameters validated successfully")
            
        except Exception as e:
            return ValidationResult(False, f"Advanced risk validation error: {str(e)}")
    
    def _calculate_volatility(self, symbol: str, period: int = 20) -> float:
        """Calculate current market volatility"""
        try:
            # Get recent prices
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, period)
            if rates is None or len(rates) < period:
                return 0.0
            
            # Calculate price changes
            prices = np.array([rate[4] for rate in rates])  # Close prices
            returns = np.diff(np.log(prices))
            
            # Calculate volatility (standard deviation of returns)
            return np.std(returns)
            
        except Exception:
            return 0.0
    
    def _check_market_activity(self, symbol: str) -> int:
        """Check market activity level"""
        try:
            # Get last hour's trades
            current_time = datetime.now()
            from_time = current_time - timedelta(hours=1)
            
            # Get trades in the last hour
            trades = mt5.copy_ticks_from(symbol, from_time, 100000, mt5.COPY_TICKS_ALL)
            if trades is None:
                return 0
            
            return len(trades)
            
        except Exception:
            return 0
    
    def _calculate_symbol_correlation(self, symbol: str, other_symbols: set) -> float:
        """Calculate correlation between symbol and other positions"""
        try:
            # Get recent prices for all symbols
            period = 100
            symbol_prices = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, period)
            if symbol_prices is None:
                return 0.0
            
            symbol_returns = np.diff(np.log([rate[4] for rate in symbol_prices]))
            max_correlation = 0.0
            
            for other_symbol in other_symbols:
                if other_symbol == symbol:
                    continue
                    
                other_prices = mt5.copy_rates_from_pos(other_symbol, mt5.TIMEFRAME_M1, 0, period)
                if other_prices is None:
                    continue
                
                other_returns = np.diff(np.log([rate[4] for rate in other_prices]))
                if len(other_returns) == len(symbol_returns):
                    correlation = abs(np.corrcoef(symbol_returns, other_returns)[0, 1])
                    max_correlation = max(max_correlation, correlation)
            
            return max_correlation
            
        except Exception:
            return 0.0
    
    def _get_daily_trade_count(self) -> int:
        """Get number of trades executed today"""
        try:
            today = datetime.now().date()
            today_start = int(datetime.combine(today, datetime.min.time()).timestamp())
            
            deals = mt5.history_deals_get(today_start, int(datetime.now().timestamp()))
            if deals is None:
                return 0
            
            return len(deals)
            
        except Exception:
            return 0
    
    def _calculate_risk_reward_ratio(self, sequence: Sequence) -> float:
        """Calculate risk/reward ratio for the sequence"""
        try:
            if not sequence.positions:
                return 0.0
            
            # Calculate average entry price
            avg_entry = sum(pos.entryPrice * pos.volume for pos in sequence.positions) / sum(pos.volume for pos in sequence.positions)
            
            # Get current market price
            symbol = sequence.positions[0].symbol
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                return 0.0
            
            current_price = tick.bid if sequence.type == "Buy" else tick.ask
            
            # Calculate potential reward and risk
            if sequence.type == "Buy":
                reward = current_price - avg_entry
                risk = avg_entry - min(pos.entryPrice for pos in sequence.positions)
            else:
                reward = avg_entry - current_price
                risk = max(pos.entryPrice for pos in sequence.positions) - avg_entry
            
            return reward / risk if risk > 0 else 0.0
            
        except Exception:
            return 0.0
