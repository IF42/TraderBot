"""
TODO:
* Treat for bad password or user_id, better information is needed
* Logging of the internal operations for traded every symbol for further analysis
* Refactor the code to be cleaner
* Add version signature with with output into command line
* Reaction to network disconnect
* budget control for prevent trials for too expansive transactions
* synchronize witch trading server time
* add time stamp to output 
* add more trading strategies
"""


import talib 
from XTBApi.api import Client, LOGGER
import numpy as np
import json
from getpass import getpass
import os
import enum
import datetime
import time


LOGGER.propagate = False


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
        t = talib.RSI(self.closes, timeperiod = 14)[-1]

        if t > 70:
            return Prediction.BUY
        elif t < 30:
            return Prediction.SELL
        else:
            return Prediction.NOTHING
        """
        
        t = talib.CDLDOJI(self.opens, self.highs, self.lows, self.closes)
        
        if t[-1] > 0:
            return Prediction.BUY
        elif t[-1] < 0:
            return Prediction.SELL
        else:
            return Prediction.WAIT


class Trader:
    """
    Trader class represents connection with Broker. In this class 
    continuously read current state of the market and
    analyzed if to buy (short/long) or to sell
    TODO: initialize Symbol list with current open trades on trade server
    """

    def __init__(self, user_id, password, mode, traded_symbols):
        self.client = Client()
        self.client.login(user_id, password, mode)
        self.symbols = []

        for symbol in traded_symbols:
            candle_history = self.client.get_lastn_candle_history(symbol, 60, 60)
            
            closes = list(map(lambda x: x["close"], candle_history))
            opens  = list(map(lambda x: x["open"], candle_history))
            highs  = list(map(lambda x: x["high"], candle_history))
            lows   = list(map(lambda x: x["low"], candle_history))

            self.symbols.append(Symbol(symbol, np.array(opens), np.array(highs), np.array(lows), np.array(closes)))

    def trade(self):
        step = 0

        while True:
            if step == 0:
                step = 6

                for symbol in self.symbols:
                    # skip closed markets
                    if not trader.client.check_if_market_open([symbol.name])[symbol.name]:
                        continue

                    candle_history = self.client.get_lastn_candle_history(symbol.name, 60, 1)
                    
                    closes = list(map(lambda x: x["close"], candle_history))
                    opens  = list(map(lambda x: x["open"], candle_history))
                    highs  = list(map(lambda x: x["high"], candle_history))
                    lows   = list(map(lambda x: x["low"], candle_history))

                    symbol.update_history(opens, highs, lows, closes)

                    prediction = symbol.predict()
                    print(f"{symbol.name}: {prediction}")

                    try:
                        if prediction == Prediction.BUY:
                            if symbol.status == TradeStatus.NOTHING:
                                # BUY LONG
                                self.client.open_trade('buy', symbol.name, 0.2)
                                symbol.update_trade_status(TradeStatus.LONG)
                            elif symbol.status == TradeStatus.SHORT:
                                # SELL SHORT
                                trades = trader.client.update_trades()
                                trade_id = list(filter(lambda r: r[0] == symbol.name, [(x[1].symbol, x[0]) for x in trades.items()]))[0][1]
                                self.client.close_trade(trade_id)
                                symbol.update_trade_status(TradeStatus.NOTHING)
                        elif prediction == Prediction.SELL:
                            if symbol.status == TradeStatus.NOTHING:
                                # BUY SHORT
                                self.client.open_trade('sell', symbol.name, 0.2)
                                symbol.update_trade_status(TradeStatus.SHORT)
                            elif symbol.status == TradeStatus.LONG:
                                # SELL LONG
                                trades = trader.client.update_trades()
                                trade_id = list(filter(lambda r: r[0] == symbol.name, [(x[1].symbol, x[0]) for x in trades.items()]))[0][1]
                                self.client.close_trade(trade_id)
                                symbol.update_trade_status(TradeStatus.NOTHING)
                    except Exception as e:
                        print(f"An exception occurred: {str(e)}")
            else:
                step -= 1
                self.client.ping()

            time.sleep(10)


def clear_screen():
    if os.name == 'posix':
        os.system("clear")
    else:
        os.system("cls")


if __name__ == "__main__":
    """
    Loading of configuration file
    TODO: what to do if the file is not presented?
    """
    cfg_file = open('config.json')
    cfg = json.load(cfg_file)    

    traded_symbols = np.array(cfg["symbols"])
    
    """
    Loading of login password from command line
    """
    password = "4xl74fx0.H" #getpass("Password: ")
    clear_screen()    

    print("Trader bot is starting...")

    """
    Trader instance with trading loop
    TODO: treat login error 
    """
    trader = Trader(cfg["ID"], password, cfg["mode"], traded_symbols)
    trader.trade()    



