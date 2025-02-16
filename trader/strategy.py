import MetaTrader5 as mt5
from datetime import datetime, timedelta
import time
import numpy as np
import random
from .parameters import (MagicNumbers, PositionInfo, Sequence, Metrics, 
                      AccountStatistics, LogicSettings, Trading_Timeframe,
                      baseBalance, Account_Info)
from .order_manager import OrderManager
from analysis.analysis import SequenceAnalysis

class Strategy:
    def __init__(self, account_info: Account_Info):
        self.account_info = account_info
        self.symbol = account_info.symbol
        self.is_running = True
        self.buySequence = Sequence(type="Buy")
        self.sellSequence = Sequence(type="Sell")
        self.accountStatistics = AccountStatistics()
        self.performanceMetrics = Metrics()
        self.last_timer_check = datetime.now()
        self.consecutive_losses = 0  # Add consecutive losses tracking
        
        # Initialize components
        self.logicInputs = LogicSettings()
                
        # Initialize point value
        self.Point = mt5.symbol_info(self.symbol).point
        
        # Initialize parameters
        self.InitParameters()
        
        # Initialize order manager
        self.orderManager = OrderManager(self.symbol, self.accountStatistics, self.logicInputs)
        self.sequenceAnalysis = SequenceAnalysis()
        
    def InitParameters(self):
        """Initialize strategy parameters using values from parameters.py"""
        self.logicInputs.is_BotActivated = True
        self.logicInputs.is_BuysActivated = True
        self.logicInputs.is_SellsActivated = True
        
        # Set values from account_info parameters
        self.logicInputs.base_Balance = baseBalance
        self.logicInputs.takeProfit_Points = self.account_info.parameters.tpPoints
        self.logicInputs.max_Positions = self.account_info.parameters.maxPositions
        self.logicInputs.min_DevDistance = self.account_info.parameters.minDeviationDistance
        self.logicInputs.dev_IncreaseFactor = self.account_info.parameters.deviationIncreaseFactor
        self.logicInputs.timeFrame = Trading_Timeframe.Three_Hour
        
        return True

    def Run(self) -> dict:
        """Main update method called by the dashboard"""
        cycle_time = 10
        if not self.is_running:
            return self.get_stats()
            
        try:
            # Run for 20 seconds
            start_time = time.time()
            while time.time() - start_time < cycle_time:
                # Update account info
                self.AccountInfo()
                
                # Update sequences
                self.UpdateSequenceTracking(self.buySequence)
                self.UpdateSequenceTracking(self.sellSequence)
                
                # Process sequences
                if len(self.buySequence.positions) > 0:
                    self.CheckSequence(self.buySequence)
                    self.UpdateSequenceTracking(self.buySequence)
                    self.CheckModify(self.buySequence)
                    self.UpdateSequenceTracking(self.buySequence)
                    self.CheckTrailingStop(self.buySequence)
                    self.UpdateSequenceTracking(self.buySequence)
                    self.CheckClose(self.buySequence)
                else:
                    # Initialize the sequence
                    self.buySequence.id = self.GenerateSequenceIdentifier(self.buySequence)
                    self.orderManager.OpenPosition(self.buySequence)

                if len(self.sellSequence.positions) > 0:
                    self.CheckSequence(self.sellSequence)
                    self.UpdateSequenceTracking(self.sellSequence)
                    self.CheckModify(self.sellSequence)
                    self.UpdateSequenceTracking(self.sellSequence)
                    self.CheckTrailingStop(self.sellSequence)
                    self.UpdateSequenceTracking(self.sellSequence)
                    self.CheckClose(self.sellSequence)
                else:
                    # Initialize the sequence
                    self.sellSequence.id = self.GenerateSequenceIdentifier(self.sellSequence)
                    self.orderManager.OpenPosition(self.sellSequence)

                time.sleep(2)

            self.sequenceAnalysis.Run_Assessment()
        except Exception as e:
            print(f"Error in strategy update: {str(e)}")
            return

    def CheckSequence(self, sequence: Sequence):
        try:
            reason = ""
            # If the sequence is profitable, return False
            if(sequence.profit > 0):
                return
            else:
                reason = "\n========== Sequence Position Updating =========="
                reason += "\nProfit: " + str(sequence.profit)

            if (len(sequence.positions) > self.logicInputs.max_Positions):
                print(f"Sequence has too many positions: {len(sequence.positions)}/{self.logicInputs.max_Positions}")
                return
            else:
                reason += f"\nPositions: {len(sequence.positions)}/{self.logicInputs.max_Positions}"

            # If the price deviation is less than the deviation points, return False
            symbol_info = mt5.symbol_info_tick(self.symbol)
            currentPricePrice = symbol_info.bid if sequence.type == "Buy" else symbol_info.ask
            entryPrice = sequence.lastPosition.entryPrice
            price_deviation = abs(currentPricePrice - entryPrice)/self.Point
            ref_deviation = self.GetDeviation(sequence)
            if(price_deviation < ref_deviation):
                return
            else:
                reason = "\nPrice Deviation: " + str(price_deviation)

            # If the time difference is less than the time difference points, return False
            entryTime = sequence.lastPosition.entryTime
            current_time = mt5.symbol_info_tick(self.symbol).time
            timeDifference = abs(current_time - entryTime)
            ref_time = self.GetTimeDifference(sequence)
            if(timeDifference < ref_time):
                return
            else:
                reason = "\nTime Difference: " + str(timeDifference)

            # Open a position since all conditions are met
            result = self.orderManager.OpenPosition(sequence)
            if(result==True):
                print(reason)
                self.UpdateSequenceTracking(sequence)
                self.CheckModify(sequence)
                      
        except Exception as e:
            print(f"Error in check sequence: {str(e)}")
            return False
        
    def GenerateSequenceIdentifier(self, sequence: Sequence) -> str:
        """
        Generate a 31-character unique identifier for a sequence.
        Format: YYMMDDHHMMTNNN (15 chars) + Random Hash (2 chars)
        """
        # Generate a timestamp (YYMMDDHHMM)
        start_time = datetime.now().strftime("%y%m%d%H%M")  # 10 chars

        # Sequence type: "B" for Buy, "S" for Sell
        sequence_type = "B" if sequence.type == "Buy" else "S"  # 1 char

        # Sequence number: Fixed 3-digit format (001-999)
        sequence_number = f"{random.randint(1, 999):03d}"  # 3 chars

        # Generate a random hash (to reach 31 characters)
        random_hash = f"{random.randint(10, 99)}"  # 2 chars

        # Construct the final 31-character identifier
        sequence_identifier = f"{start_time}{sequence_type}{sequence_number}{random_hash}"

        return sequence_identifier
    
    def GetTimeDifference(self, sequence: Sequence) -> int:
        # Get a randon timeframe between -30 and 30 minutes (I hour range)
        random_time = random.randint(-30, 30)
        time = (self.logicInputs.timeFrame + random_time) * 60
        return time
    
    def GetDeviation(self, sequence: Sequence) -> float:
        deviation_factor = self.logicInputs.dev_IncreaseFactor
        # Get a random deviation factor between 1.3 and 1.5
        random_deviation = random.uniform(1.3, 1.5)
        deviation_factor = random_deviation
        deviation = self.logicInputs.min_DevDistance * pow(deviation_factor, float(len(sequence.positions)))
        return deviation
    
    def CheckModify(self, sequence: Sequence):
        # Check if all positions in a sequence have the same take profit,
        # If they do not, modify them to have same take profit as the last position
        take_profit = sequence.lastPosition.takeProfit
        if(take_profit == 0.0):
            take_profit = sequence.lastPosition.entryPrice + (self.logicInputs.takeProfit_Points * self.Point)

        for position in sequence.positions:
            position_tp = position.takeProfit
            if position_tp == 0.0:
                if self.orderManager.ModifyPositions(sequence, sl=0.0, tp= take_profit):
                    reason = "\n========== Take Profit Assigned =========="
                    reason += "\nAssigned Take Profit: " + str(take_profit)
                    print(reason)
            if position_tp != take_profit:
                if self.orderManager.ModifyPositions(sequence, sl=0.0, tp= take_profit):
                    reason = "\n========== Take Profit Modified =========="
                    reason += "\nOld Take Profit: " + str(position_tp)
                    reason += "\nNew Take Profit: " + str(take_profit)
                    print(reason)
    
    def CheckClose(self, sequence: Sequence):
        # Check if a sequence is profitable, if so, close all positions in that sequence
        # Calculate profitability using 10 pips so that different volumes can have different profit thresholds
        profit_threshold = 30 * self.Point * sequence.lastPosition.volume
        if sequence.profit > profit_threshold:
            for position in sequence.positions:
                self.orderManager.ClosePosition(position)

    def CheckTrailingStop(self, sequence: Sequence):
        # Check if a sequence is profitable, if so, close all positions in that sequence
        # Calculate profitability using 10 pips so that different volumes can have different profit thresholds
        profit_threshold = 30 * 1.5 * self.Point * sequence.lastPosition.volume
        trailing_stop_points = 20
        if sequence.profit > profit_threshold:
            # Calculate the trailing stop
            if sequence.type == "Buy":
                current_price = mt5.symbol_info_tick(self.symbol).bid
                trailing_stop = current_price - (trailing_stop_points * self.Point)
                new_tp = sequence.lastPosition.takeProfit + (trailing_stop_points * self.Point)
            else:
                current_price = mt5.symbol_info_tick(self.symbol).ask
                trailing_stop = current_price + (trailing_stop_points * self.Point)
                new_tp = sequence.lastPosition.takeProfit - (trailing_stop_points * self.Point)

            self.orderManager.ModifyPositions(sequence, sl=trailing_stop, tp=new_tp)

    def UpdateSequenceTracking(self, sequence: Sequence):
        self.GetTradeHistory()
        if sequence.type == "Buy":
            positionType = mt5.ORDER_TYPE_BUY
            magicNumber = MagicNumbers.BUY
        elif sequence.type == "Sell":
            positionType = mt5.ORDER_TYPE_SELL
            magicNumber = MagicNumbers.SELL

        sequence.profit = 0
        sequence.volume = 0
        sequence.positions = []
        string_id = ""
        positions = mt5.positions_get(symbol=self.symbol)
        if positions is not None:
            for position in positions:
                if position.magic == magicNumber:
                    posInfo = PositionInfo()
                    posInfo.type = position.type
                    posInfo.profit = position.profit
                    posInfo.volume = position.volume
                    posInfo.entryPrice = position.price_open
                    posInfo.takeProfit = position.tp
                    posInfo.magicNumber = position.magic
                    posInfo.ticketNumber = position.ticket
                    posInfo.entryTime = position.time
                    posInfo.symbol = position.symbol
                    posInfo.comment = position.comment
                    if len(posInfo.comment) == 16:
                        string_id = posInfo.comment
                    sequence.positions.append(posInfo)
                    sequence.profit += posInfo.profit
                    sequence.volume += posInfo.volume

        sequence.lastPosition = self.GetLastOrder(positionType)
        sequence.id = string_id

        return sequence

    def GetTradeHistory(self) -> bool:
        try:
            from_date = datetime(2020,1,1)
            to_date = datetime.now()
            deals = mt5.history_deals_get(from_date, to_date, group="*"+self.symbol+"*")
            if deals is None:
                error_code = mt5.last_error()
                print(f"History deals get failed. Error code={error_code}")
                return False
                
            for deal in deals:
                if deal.entry == mt5.DEAL_ENTRY_IN:  # Only process entry deals
                    if deal.profit > 0:
                        self.performanceMetrics.Wins += 1
                        self.performanceMetrics.TotalWinAmount += deal.profit
                    elif deal.profit < 0:
                        self.performanceMetrics.Loosers += 1
                        self.performanceMetrics.TotalLossAmount += abs(deal.profit)
                        
            return True
        except Exception as e:
            print(f"Error in GetTradeHistory: {str(e)}")
            return False

    def GetLastOrder(self, Type: int) -> PositionInfo:
        try:
            lastPosition = PositionInfo()
            magic = MagicNumbers.BUY if Type == mt5.ORDER_TYPE_BUY else MagicNumbers.SELL

            positions = mt5.positions_get(symbol=self.symbol)
            if positions is not None:
                for position in positions:
                    if position.type == Type and position.magic == magic:
                        lastPosition.ticketNumber = position.ticket
                        lastPosition.magicNumber = position.magic
                        lastPosition.entryPrice = position.price_open
                        lastPosition.volume = position.volume
                        lastPosition.entryTime = position.time
                        lastPosition.profit = position.profit
                        lastPosition.takeProfit = position.tp
                        lastPosition.symbol = position.symbol
                        return lastPosition

            # If no open positions, check history
            current_time = mt5.symbol_info_tick(self.symbol).time
            from_time = current_time - 7 * 24 * 60 * 60  # 7 days lookback
            
            orders = mt5.history_orders_get(from_date=from_time, to_date=current_time, group=f"{self.symbol}*")
            if orders is not None:
                for order in reversed(orders):
                    if order.type == Type and order.magic == magic:
                        lastPosition.ticketNumber = order.ticket
                        lastPosition.magicNumber = order.magic
                        lastPosition.entryPrice = order.price_open
                        lastPosition.volume = order.volume_initial
                        lastPosition.entryTime = order.time_setup
                        lastPosition.profit = 0  # Can't get profit from order history
                        lastPosition.takeProfit = order.tp
                        lastPosition.symbol = order.symbol
                        return lastPosition

            return lastPosition
            
        except Exception as e:
            print(f"Error in GetLastOrder: {str(e)}")
            return PositionInfo()

    def AccountInfo(self) -> bool:
        try:
            account = mt5.account_info()
            if account is None:
                print("Failed to get account info")
                return False

            self.accountStatistics.balance = account.balance
            self.accountStatistics.equity = account.equity
            self.accountStatistics.floatingProfit = account.profit
            
            total_trades = self.performanceMetrics.Wins + self.performanceMetrics.Loosers
            if total_trades > 0:
                self.UpdatePerformanceMetrics(total_trades)

            return True
        except Exception as e:
            print(f"Error in AccountInfo: {str(e)}")
            return False


    def UpdatePerformanceMetrics(self, total_trades: int):
        self.accountStatistics.balancePercent = (self.accountStatistics.balance / self.accountStatistics.deposit) * 100 if self.accountStatistics.deposit != 0 else 0
        self.accountStatistics.equityPercent = (self.accountStatistics.equity / self.accountStatistics.balance) * 100 if self.accountStatistics.balance != 0 else 0
        self.accountStatistics.profit = self.accountStatistics.balance - self.accountStatistics.deposit

        self.performanceMetrics.WinPercent = (self.performanceMetrics.Wins / total_trades) * 100
        self.performanceMetrics.LoosePercent = 100 - self.performanceMetrics.WinPercent

        self.performanceMetrics.ProfitFactor = self.performanceMetrics.TotalWinAmount / self.performanceMetrics.TotalLossAmount if self.performanceMetrics.TotalLossAmount > 0 else 0
        self.performanceMetrics.AvgTradeProfit = self.accountStatistics.profit / total_trades
        self.performanceMetrics.AvgWinAmount = self.performanceMetrics.TotalWinAmount / self.performanceMetrics.Wins if self.performanceMetrics.Wins > 0 else 0

        self.performanceMetrics.AvgLossAmount = self.performanceMetrics.TotalLossAmount / self.performanceMetrics.Loosers if self.performanceMetrics.Loosers > 0 else 1
        self.performanceMetrics.RiskRewardRatio = abs(self.performanceMetrics.AvgWinAmount / self.performanceMetrics.AvgLossAmount) if self.performanceMetrics.AvgLossAmount != 0 else 0
        self.performanceMetrics.currDrawdown = (self.accountStatistics.balance - self.accountStatistics.equity) / self.accountStatistics.balance if self.accountStatistics.balance != 0 else 0

        # Update consecutive losses based on the last trade
        if self.performanceMetrics.TotalLossAmount > 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0

        if self.performanceMetrics.currDrawdown > self.performanceMetrics.MaxDrawdown:
            self.performanceMetrics.MaxDrawdown = self.performanceMetrics.currDrawdown
            print(f"New maximum drawdown recorded: {self.performanceMetrics.MaxDrawdown:.2f}%") 