from dataclasses import dataclass, field
from typing import List

LOOK_BACK = 10     # The number of days to investigate
EVENTS_PERIOD = 10 # Seconds
ACCOUNT_INFO_UPDATE_INTERVAL = 60 # Seconds

class Trading_Timeframe:
    Min = 1
    Five_Min = 5
    Fifteen_Min = 15
    Thirty_Min = 30
    Hour = 60
    Two_Hour = 120
    Three_Hour = 180
    Four_Hour = 240
tradingPeriod = Trading_Timeframe.Min

maxEquityDrawdown = 30.0
maxDailyDrawdown = 60.0
minEquityPercent = 20.0

#--- Position Management
baseBalance = 3000
tpPoints = 80.0
minDeviationDistance = 80
deviationIncreaseFactor = 1.4


#--- Logic Settings
@dataclass
class LogicSettings:
    is_BotActivated: bool = True
    is_BuysActivated: bool = True
    is_SellsActivated: bool = True
    timeFrame: Trading_Timeframe = Trading_Timeframe.Hour
    drawdownMax_Equity: float = 0.0
    drawdownMax_Daily: float = 0.0
    drawdownMin_Equity: float = 0.0
    drawdownMin_Balance: float = 0.0  # Minimum balance drawdown threshold
    drawdownMin_Profit: float = 0.0  # Minimum profit drawdown threshold
    base_Balance: float = 0.0
    takeProfit_Points: float = 0.0
    max_Positions: int = 0
    min_DevDistance: float = 0.0
    dev_IncreaseFactor: float = 0.0

#--- Global Variables for Position Tracking
@dataclass
class MagicNumbers:
    BUY: int = 1231
    SELL: int = 1832

#--- Sequence Tracking
@dataclass
class PositionInfo:
    type: int = 0
    volume: float = 0.0
    profit: float = 0.0
    entryPrice: float = 0.0
    takeProfit: float = 0.0
    magicNumber: int = 0
    ticketNumber: int = 0
    entryTime: int = 0
    symbol: str = ""
    comment: str = ""

@dataclass
class Sequence:
    id: str = ""
    type: str = ""
    profit: float = 0.0
    volume: float = 0.0
    positions: List[PositionInfo] = field(default_factory=list)
    lastPosition: PositionInfo = field(default_factory=PositionInfo)

#--- Account Statistics
@dataclass
class AccountStatistics:
    accountNumber: int = 0
    accountName: str = ""
    currency: str = ""
    accountType: str = ""
    accountMode: int = 0
    server: str = ""
    deposit: float = 0.0
    balance: float = 0.0
    balancePercent: float = 0.0
    equity: float = 0.0
    equityPercent: float = 0.0
    profit: float = 0.0
    floatingProfit: float = 0.0


#--- Performance Metrics
@dataclass
class Metrics:
    Wins: int = 0
    WinPercent: float = 0.0
    Loosers: int = 0
    LoosePercent: float = 0.0
    MaxDrawdown: float = 0.0
    MaxDailyDrawdown: float = 0.0
    currDrawdown: float = 0.0
    ProfitFactor: float = 0.0
    SharpeRatio: float = 0.0
    AvgTradeProfit: float = 0.0
    RiskRewardRatio: float = 0.0
    TotalWinAmount: float = 0.0
    TotalLossAmount: float = 0.0
    AvgWinAmount: float = 0.0
    AvgLossAmount: float = 0.0

Symbols = [
    "EURUSD",
    "GBPUSD",
    "USDJPY"
]

class Account_Specific_Parameters:
    def __init__(self, symbol: str, tpPoints: float, maxPositions: int, 
                 minDeviationDistance: float, deviationIncreaseFactor: float):
        self.symbol = symbol
        self.tpPoints = tpPoints
        self.maxPositions = maxPositions
        self.minDeviationDistance = minDeviationDistance
        self.deviationIncreaseFactor = deviationIncreaseFactor

class Account_Info:
    def __init__(self, parameters: Account_Specific_Parameters, login: int, 
                 password: str, server: str, symbol: str):
        self.parameters = parameters
        self.login = login
        self.password = password
        self.server = server
        self.symbol = symbol


#--- Trade Info
@dataclass
class TradeInfo:
    ticketNumber: int = 0
    magicNumber: int = 0
    entryPrice: float = 0.0
    volume: float = 0.0
    profit: float = 0.0
    entryTime: int = 0

@dataclass
class Accounts_Data:
    login: int = 0
    balance: float = 0.0
    equity: float = 0.0
    floatingProfit: float = 0.0
    profit: float = 0.0
    max_Positions: int = 0
    open_buys: int = 0
    buys_profit: float = 0.0
    buys_volume: float = 0.0
    open_sells: int = 0
    sells_profit: float = 0.0
    sells_volume: float = 0.0
    open_positions: int = 0
    total_profit: float = 0.0
    total_volume: float = 0.0
    total_profit_percentage: float = 0.0
    total_volume_percentage: float = 0.0
    total_profit_percentage_percentage: float = 0.0
    total_volume_percentage_percentage: float = 0.0

