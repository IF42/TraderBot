import numpy as np
import pandas as pd
import pandas_ta as ta
import enum


class Prediction(enum.Enum):
    WAIT = 0
    BUY  = 1
    SELL = 2


class TradeStatus(enum.Enum):
    NOTHING = 0
    SHORT   = 1
    LONG    = 2


class Symbol:
    """
    Container for historical data of given symbol with mathematical 
    analysis of the next step
    """
    def __init__(self, name, opens, highs, lows, closes):
        self.name   = name
        self.opens  = opens
        self.highs  = highs
        self.lows   = lows
        self.closes = closes
        self.status = TradeStatus.NOTHING

    def update_history(self, opens, highs, lows, closes):
        self.opens = self.opens[1:]
        self.highs = self.highs[1:]
        self.lows = self.lows[1:]
        self.closes = self.closes[1:]

        self.opens = np.append(self.opens, opens)
        self.highs = np.append(self.highs, highs)
        self.lows = np.append(self.lows, lows)
        self.closes = np.append(self.closes, closes)

    def update_trade_status(self, status):
        self.status = status

    def predict(self) -> Prediction:
        """
        t = talib.CDLDOJI(self.opens, self.highs, self.lows, self.closes)
        
        if t[-1] > 0:
            return Prediction.BUY
        elif t[-1] < 0:
            return Prediction.SELL
        else:
            return Prediction.WAIT

        """
        t = ta.rsi(close=pd.Series(self.closes), length = 3)
        
        if t.values[-1] > 80:
            return Prediction.BUY
        elif t.values[-1] < 20:
            return Prediction.SELL
        else:
            return Prediction.WAIT




