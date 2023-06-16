"""
TODO:
* Treat for bad bassword or user_id, better information is needed
* Logging of the internal operations for traded every symbol for further analysis
* Refactor the code to be cleaner
"""

import talib 
from XTBApi.api import Client, LOGGER
LOGGER.propagate = False
import numpy as np
import json
from getpass import getpass
import os
import enum
import datetime


class Prediction(enum.Enum):
  NOTHING = 0
  BUY     = 1
  SELL    = 2


class TradeStatus(enum.Enum):
  NOTHING = 0
  SHORT   = 1
  LONG    = 2


class Symbol:
    """
    Container for historical data of given symbol with mathematical 
    analysis of the next step
    """
    def __init__(self, name, history):
        self.name    = name
        self.history = history
        self.status  = TradeStatus.NOTHING

    def update_history(self, value):
        self.history = self.history[1:]
        self.history = np.append(self.history, value)

    def update_trade_status(self, status):
        self.status   = status

    def predict(self) -> Prediction:
        t = talib.RSI(self.history, timeperiod = 7)[-1]

        if t > 70:
            return Prediction.BUY
        elif t < 30:
            return Prediction.SELL
        else:
            return Prediction.NOTHING
    

class Trader:
    """
    Trader class represents connection with Broker. In this class 
    continuously readed current state of the market and 
    analyzed if to buy (short/long) or to sell
	TODO: initialize Symbol list with current open trades on trade server
    """

    def __init__(self, user_id, password, mode, traded_symbols):
        self.client = Client()
        self.client.login(user_id, password, mode)
        self.symbols = []

        for symbol in traded_symbols:
            history = list(map(lambda x: x["close"], self.client.get_lastn_candle_history(symbol, 60, 10)))
            self.symbols.append(Symbol(symbol, np.array(history)))

    def trade(self):
        step = 0

        while True:
            if(step == 0):
                step = 6

                for symbol in self.symbols:
                    # skip closed markets
                    if trader.client.check_if_market_open([symbol.name])[symbol.name] == False:
                        continue

                    close = self.client.get_lastn_candle_history(symbol.name, 60, 1)[0]["close"]
                    symbol.update_history(close)
                    prediction = symbol.predict()
                    print(f"{symbol.name}: {prediction}")

                    try:
                        if prediction == Prediction.BUY:
                            if symbol.status == TradeStatus.NOTHING:
                                """
                                BUY LONG
                                """
                                self.client.open_trade('buy', symbol.name, 0.8)
                                symbol.update_trade_status(TradeStatus.LONG)
                            elif symbol.status == TradeStatus.SHORT:
                                """
                                SELL SHORT
                                """
                                trades = trader.client.update_trades()
                                trade_id = list(filter(lambda r: r[0] == symbol.name, [(x[1].symbol, x[0]) for x in trades.items()]))[0][1]
                                self.client.close_trade(trade_id)
                                symbol.update_trade_status(TradeStatus.NOTHING)
                        elif prediction == Prediction.SELL:
                            if symbol.status == TradeStatus.NOTHING:
                                """
                                BUY SHORT
                                """
                                self.client.open_trade('sell', symbol.name, 0.8)
                                symbol.update_trade_status(TradeStatus.SHORT)
                            elif symbol.status == TradeStatus.LONG:
                                """
                                SELL LONG
                                """
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
    if(os.name == 'posix'):
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
    password = getpass("Password: ")
    clear_screen()    

    print("Trader bot is starting...")

    """
    Trader instance with trading loop
    TODO: treat login error 
    """
    trader = Trader(traded_symbols, cfg["ID"], password, cfg["mode"])
    trader.trade()    



