import pandas as pd
import numpy as np


class RSI:

    def __init__(self, period, source='close'):
        self.period = period
        self.source = source

    def rsi(self, df, col_name):
        df[col_name] = self.rsi_calc(df[self.source], self.period)
        return df

    @staticmethod
    def rsi_calc(series, n):
        '''
        https://stackoverflow.com/questions/20526414/relative-strength-index-in-python-pandas
        :param series: source column
        :param n: lookback
        :return: rsi index
        '''
        delta = series.diff()
        # Make the positive gains (up) and negative gains (down) Series
        up, down = delta.clip(lower=0), delta.clip(upper=0)
        # Calulate the SMA
        roll_up = up.rolling(n).mean()
        roll_down = down.abs().rolling(n).mean()

        # Calculate the RSI based on SMA
        RS = roll_up / roll_down
        RSI = 100.0 - (100.0 / (1.0 + RS))
        return RSI
