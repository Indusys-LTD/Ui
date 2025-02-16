from .parameters import MagicNumbers, Sequence, PositionInfo, AccountStatistics, LogicSettings
import MetaTrader5 as mt5

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    PURPLE = '\033[95m'
    RESET = '\033[0m'

class OrderManager:
    def __init__(self, symbol: str, accountStatistics: AccountStatistics, logicInputs: LogicSettings):
        self.symbol = symbol
        self.accountStatistics = accountStatistics
        self.logicInputs = logicInputs
        self.Point = mt5.symbol_info(self.symbol).point

    def OpenPosition(self, sequence: Sequence) -> bool:
        opened = False
        if sequence.type == "Buy":
            magicNumber = MagicNumbers.BUY
            orderType = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(self.symbol).ask
        elif sequence.type == "Sell":
            magicNumber = MagicNumbers.SELL 
            orderType = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(self.symbol).bid
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": self.OptimizedLotSize(sequence),
            "type": orderType,
            "price": price,
            "deviation": 2,
            "magic": magicNumber,
            "type_filling": mt5.ORDER_FILLING_IOC,
            "tp": self.TakeProfit(sequence),
            "comment": sequence.id
        }

        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            if result.comment == "No money":
                print(f"{Colors.RED}No money: {self.symbol} | {request['price']} | Volume {request['volume']}{Colors.RESET}")
                opened = False
            else:
                print(f"OrderSend error: {result.comment if result else 'Unknown error'}")
                opened = False
        else:
            print(f"{Colors.GREEN}Opened {sequence.type} | {self.symbol} | {request['price']} | Volume {request['volume']}{Colors.RESET}")
            opened = True

        return opened

    def ModifyPositions(self, sequence: Sequence, sl: float, tp: float) -> bool:
        modified = False
        # normalise the tp and sl to the point size
        tp = round(tp / self.Point) * self.Point
        sl = round(sl / self.Point) * self.Point
        for position in sequence.positions:
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": position.ticketNumber,
                "symbol": self.symbol,
                "price": position.entryPrice,
                "tp": tp,
                "sl": sl,
                "type": position.type,
                "magic": position.magicNumber,
                "type_filling": mt5.ORDER_FILLING_IOC,
                "deviation": 20
            }
            result = mt5.order_send(request)
            if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = result.comment if result else 'Unknown error'
                print(f"Order modify error for position {position.ticketNumber}: {error_msg}")
                continue
            else:
                modified = True
                print(f"{Colors.PURPLE}Modified {sequence.type} | {self.symbol} | {request['price']} | Volume {position.volume}{Colors.RESET}")

        return modified

    def ClosePosition(self, position: PositionInfo) -> bool:
        closed = False
        if position.type == mt5.ORDER_TYPE_BUY:
            close_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(self.symbol).bid
        else:
            close_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(self.symbol).ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": position.volume,
            "type": close_type,
            "position": position.ticketNumber,
            "price": price,
            "deviation": 20,
            "magic": position.magicNumber,
            "type_filling": mt5.ORDER_FILLING_IOC
        }
        
        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            error_msg = result.comment if result else 'Unknown error'
            print(f"{Colors.RED}Order close error {error_msg}{Colors.RESET}")
            closed = False
        else:
            print(f"{Colors.YELLOW}Closed {position.type} | {self.symbol} | {request['price']} | Volume {request['volume']}{Colors.RESET}")
            closed = True

        return closed

    def OptimizedLotSize(self, sequence: Sequence) -> float:
        symbol_info = mt5.symbol_info(self.symbol)
        lot = symbol_info.volume_step
        OrderCount = len(sequence.positions)
        sequenceProfit = sequence.profit
        
        if OrderCount == 0:
            minLot = (self.accountStatistics.balance / self.logicInputs.base_Balance) * lot
            if minLot < lot:
                minLot = lot
            lot = round(minLot / lot) * lot
        else:
            targetProfit = (self.logicInputs.takeProfit_Points * self.Point) + abs(sequenceProfit)
            targetVolume = targetProfit / self.logicInputs.takeProfit_Points
            lot = round(targetVolume / lot) * lot
            if lot == sequence.lastPosition.volume:
                lot = lot +  symbol_info.volume_step
           
        if lot < symbol_info.volume_step:
            lot = symbol_info.volume_step

        lot = round(lot / symbol_info.volume_step) * symbol_info.volume_step
        return lot

    def TakeProfit(self, sequence: Sequence) -> float:
        tp = 0.0
        symbol_info = mt5.symbol_info_tick(self.symbol)
        
        if sequence.type == "Buy":
            tp = symbol_info.ask + (self.logicInputs.takeProfit_Points * self.Point)
        elif sequence.type == "Sell":
            tp = symbol_info.bid - (self.logicInputs.takeProfit_Points * self.Point)

        return tp
    