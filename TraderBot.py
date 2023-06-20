"""
TODO:
* Treat for bad password or user_id, better information is needed
* Logging of the internal operations for traded every symbol for further analysis
* Refactor the code to be cleaner
* Reaction to network disconnect
* budget control for prevent trials for too expansive transactions
* add time stamp to output 
* add more trading strategies
* improve performace in time and order synchronization with server
* add initial prompt where is summari of open trades
"""

import pandas as pd
from XTBApi.api import Client, LOGGER
import numpy as np
import json
from getpass import getpass
import os
import enum
import datetime
import time
import argparse
from Symbol import Symbol, Prediction, TradeStatus

LOGGER.propagate = False


__version__   = "0.4.0"
__prog_name__ = "TraderBot" 



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

        trades = self.client.update_trades()

        for symbol in traded_symbols:
            candle_history = self.client.get_lastn_candle_history(symbol, 900, 100)
            
            closes = list(map(lambda x: x["close"], candle_history))
            opens  = list(map(lambda x: x["open"], candle_history))
            highs  = list(map(lambda x: x["high"], candle_history))
            lows   = list(map(lambda x: x["low"], candle_history))

            self.symbols.append(
                    Symbol(symbol
                           , np.array(opens)
                           , np.array(highs)
                           , np.array(lows)
                           , np.array(closes)))

    def trade(self):
        while True:
            for symbol in self.symbols:
                # skip closed markets
                if not trader.client.check_if_market_open([symbol.name])[symbol.name]:
                    continue

                candle_history = self.client.get_lastn_candle_history(symbol.name, 900, 1)
                time_stamp = candle_history[0]["timestamp"]
                
                if symbol.time_stamp == time_stamp:
                    continue

                symbol.time_stamp = time_stamp

                closes = candle_history[0]["close"]
                opens  = candle_history[0]["open"]
                highs  = candle_history[0]["high"]
                lows   = candle_history[0]["low"]

                symbol.update_history(opens, highs, lows, closes)

                prediction = symbol.predict()
                print(f"{symbol.name}: {prediction}", flush=True)

                trades = [x[1] for x in self.client.update_trades().items()]
                symbol_trades = list(filter(lambda x: x.symbol == symbol.name, trades))
                
                try:
                    if symbol_trades == []:
                        if prediction == Prediction.BUY:
                            # BUY LONG
                            print("buy")
                            self.client.open_trade('buy', symbol.name, 0.2)
                        elif prediction == Prediction.SELL:
                            # BUY SHORT
                            print("sell")
                            self.client.open_trade('sell', symbol.name, 0.2)
                    else:
                        for symbol_trade in symbol_trades:
                            if prediction == Prediction.BUY and symbol_trade.mode == "sell":
                                # SELL SHORT
                                self.client.close_trade(symbol_trade.order_id)
                            elif prediction == Prediction.SELL and symbol_trade.mode == "buy":
                                # SELL LONG
                                self.client.close_trade(symbol_trade.order_id)

                except Exception as e:
                    print(f"An exception occurred: {str(e)}")
                
            time.sleep(10)
        


def clear_screen():
    if os.name == 'posix':
        os.system("clear")
    else:
        os.system("clear")


if __name__ == "__main__":
    """
    Command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=f"{__prog_name__} {__version__}")
    args = parser.parse_args()

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
    trader = Trader(cfg["ID"], password, cfg["mode"], traded_symbols)
    trader.trade()    





