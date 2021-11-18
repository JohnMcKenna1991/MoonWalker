import pandas as pd
import numpy as np

class ATR:
    def __init__(self, period):
        self.period = period

    def atr(self, df, col_name):
        '''
        https://www.investopedia.com/terms/a/atr.asp#:~:text=The%20average%20true%20range%20(ATR)%20is%20a%20market%20volatility%20indicator,to%20all%20types%20of%20securities.
        :param df: pandas df with open , high , low columns
        :param col_name: name of column to output
        :return: df with atr column
        '''
        df['H-L'] = df.high - df.low
        df['H-C'] = abs(df.high -df.close)
        df['L-C'] = abs(df.low - df.close)
        df['TR'] = df[['H-L', 'H-C', 'L-C']].max(axis=1)
        df[col_name] = df.TR.rolling(self.period).mean()
        return df




