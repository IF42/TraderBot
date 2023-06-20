import numpy as np
import pandas as pd
import enum
from sklearn.cluster import KMeans



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

        X = pd.DataFrame({
            'Open': opens
            , 'High': highs
            , 'Low': lows
            , 'Close': closes})

        X_normalized = (X - X.mean()) / X.std()

        self.kmeans = KMeans(n_clusters=2, n_init=10)
        self.kmeans.fit(X_normalized)
        

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
        X = pd.DataFrame({
            'Open': self.opens
            , 'High': self.highs
            , 'Low': self.lows
            , 'Close': self.closes})

        X_normalized = (X - X.mean()) / X.std()
        new_cluster_labels = self.kmeans.predict(X_normalized)

        cluster_counts = np.bincount(new_cluster_labels)
        most_common_cluster = np.argmax(cluster_counts)
    
        
        sell_signals = np.where(new_cluster_labels == most_common_cluster, 1, 0)
        buy_signals = np.where(new_cluster_labels != most_common_cluster, 1, 0)
        
        if buy_signals[-1] == 1 and sell_signals[-1] == 1:
            return Prediction.WAIT
        elif buy_signals[-1] == 1:
            return Prediction.BUY
        elif sell_signals[-1] == 1:
           return Prediction.SELL
        else:
            return Prediction.WAIT
    

