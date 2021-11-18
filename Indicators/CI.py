import pandas as pd
import numpy as np

class ChopIndex:

    def __init__(self, period):
        self.period = period

    def ci(self, df, col_name):
        df['tr1'] = df.high - df.low
        df['tr2'] = abs(df.high - df.close.shift(1))
        df['tr3'] = abs(df.low - df.close.shift(1))
        df['TR'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
        df['high_roll'] = df.high.rolling(self.period).max()
        df['low_roll'] = df.low.rolling(self.period).min()
        df['atr'] = df.TR.rolling(1).mean()
        df[col_name] = 100 * np.log10((df.atr.rolling(self.period).sum()) / (df.high_roll - df.low_roll)) / np.log10(
            self.period)
        return df
