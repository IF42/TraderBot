import matplotlib.pyplot as plt
import argparse
import numpy as np
import json
from getpass import getpass
from XTBApi.api import Client, LOGGER
import Symbol



LOGGER.propagate = False

history_test  = 100
history_valid = 500



class Backtester:
    def __init__(self, user_id, password, mode, test_symbol):
        self.client = Client()
        self.client.login(user_id, password, mode)
        candle_history = self.client.get_lastn_candle_history(test_symbol, 15*60, history_test+history_valid)
        
        self.opens  = list(map(lambda x: x["open"], candle_history))
        self.highs  = list(map(lambda x: x["high"], candle_history))
        self.lows   = list(map(lambda x: x["low"], candle_history))
        self.closes = list(map(lambda x: x["close"], candle_history))

        self.symbol = Symbol.Symbol(test_symbol
                              , np.array(self.opens[history_test:])
                              , np.array(self.highs[history_test:])
                              , np.array(self.lows[history_test:])
                              , np.array(self.closes[history_test:]))

    def test(self):
        x = range(len(self.closes))
        y = self.closes
        buy = [0 for _ in range(history_test)]
        sell = [0 for _ in range(history_test)]

        for o,h,l,c in zip(self.opens[:history_valid], self.highs[:history_valid], self.lows[:history_valid], self.closes[:history_valid]):
            self.symbol.update_history(o, h, l, c)
            prediction = self.symbol.predict()
            
            if prediction == Symbol.Prediction.BUY:
                if self.symbol.status == Symbol.TradeStatus.NOTHING:
                    self.symbol.status = Symbol.TradeStatus.LONG
                else:
                    self.symbol.status = Symbol.TradeStatus.NOTHING
            elif prediction == Symbol.Prediction.SELL:
                if self.symbol.status == Symbol.TradeStatus.NOTHING:
                    self.symbol.status = Symbol.TradeStatus.SHORT
                else:
                    self.symbol.status = Symbol.TradeStatus.NOTHING

            if prediction == Symbol.Prediction.BUY:
                buy.append(1)
                sell.append(0)
            elif prediction == Symbol.Prediction.SELL:
                buy.append(0)
                sell.append(1)
            else:
                buy.append(0)
                sell.append(0)

        plt.plot(np.array(x), np.array(y), label=self.symbol.name)
        plt.scatter([x[i] for i in range(len(buy)) if buy[i] == 1], 
                                [y[i] for i in range(len(buy)) if buy[i] == 1], 
                                c='green', marker='o', label="buy")
        plt.scatter([x[i] for i in range(len(sell)) if sell[i] == 1], 
                                [y[i] for i in range(len(sell)) if sell[i] == 1], 
                                c='red', marker='o', label="sell")

        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-T', required=True, dest='backtest_symbol', help='Backtesting')

    args = parser.parse_args()

    """
    Loading of configuration file
    TODO: what to do if the file is not presented?
    """
    cfg_file = open('config.json')
    cfg = json.load(cfg_file)    

    password = "4xl74fx0.H" #getpass("Password: ")
    
    backtester = Backtester(cfg["ID"], password, cfg["mode"], args.backtest_symbol)
    backtester.test()

