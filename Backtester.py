import matplotlib.pyplot as plt
import argparse
import numpy as np
import json
from getpass import getpass
from XTBApi.api import Client, LOGGER
import Symbol



LOGGER.propagate = False

history_test  = 50
history_valid = 300



class Backtester:
    def __init__(self, user_id, password, mode, test_symbol):
        self.client = Client()
        self.client.login(user_id, password, mode)
        candle_history = self.client.get_lastn_candle_history(test_symbol, 300, history_test+history_valid)
        
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


        for c in self.closes[:history_valid]:
            self.symbol.update_history(0, 0, 0, c)
            prediction = self.symbol.predict()

            if prediction == Symbol.Prediction.BUY:
                buy.append(1)
                sell.append(0)
            elif prediction == Symbol.Prediction.SELL:
                buy.append(0)
                sell.append(1)
            else:
                buy.append(0)
                sell.append(0)

        plt.plot(np.array(x), np.array(y))
        plt.scatter([x[i] for i in range(len(buy)) if buy[i] == 1], 
                                [y[i] for i in range(len(buy)) if buy[i] == 1], 
                                c='red', marker='o')
        plt.scatter([x[i] for i in range(len(sell)) if sell[i] == 1], 
                                [y[i] for i in range(len(sell)) if sell[i] == 1], 
                                c='blue', marker='o')

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

    password = getpass("Password: ")
    
    backtester = Backtester(cfg["ID"], password, cfg["mode"], args.backtest_symbol)
    backtester.test()

