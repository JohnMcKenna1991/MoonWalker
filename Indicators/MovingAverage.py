import pandas as pd
import numpy as np


class MovingAverage:

    def __init__(self, period, source='close'):
        self.period = period
        self.source = source

    @staticmethod
    def rolling_tt(series, n):
        '''

        :param series: close price for eth/btc in pandas series
        :param n: lookahead from constructor
        :return: prediction for close_{+n}
        '''

        y = series.values.reshape(-1, 1)
        t = np.arange(len(y))
        X = np.c_[np.ones_like(y), t]
        betas = np.linalg.inv(X.T @ X) @ X.T @ y
        new_vals = np.array([1, t[-1] + n])
        pred = new_vals @ betas  # beta0 + beta1 * t[-1]+n + beta2 * (t[-1]+n)**2
        return pred

    def lin_reg(self, df, col_name):
        '''
        moving average by linear regression
        :param df: data frame with historical data
        :param col_name: name to output the simple moving average too
        :return: dataframe with new column
        '''
        df[col_name] = df[self.source].rolling(self.period).apply(self.rolling_tt,
                                                                  args=(self.period,), raw=False)

        return df

    def sma(self, df, col_name):
        '''

        :param df: data frame with historical data
        :param col_name: name to output the simple moving average too
        :return: dataframe with new column
        '''
        df[col_name] = df[self.source].rolling(self.period).mean()
        return df

    def vwma(self, df, col_name):
        '''
        volume weighted moving average
        :param df: data frame with historical data
        :param col_name: name to output the simple moving average too
        :return: dataframe with new column
        '''
        df['vxp'] = (df[self.source] * df.volume).rolling(20).mean()
        df['vol_avg'] = df.volume.rolling(20).mean()
        df[col_name] = df.vxp / df.vol_avg
        return df

    def ewma(self, df, col_name, span):
        '''
        exponentially weighted moving average

        :param df: data frame with historical data
        :param col_name: name to output the simple moving average too
        :param span: span of the moving average
        :return: dataframe with new column
        '''
        df[col_name] = df[self.source].ewm(span=span, adjust=False).mean()
        return df

    def wma(self, df, col_name):
        '''
        weighted moving average
        :param df: data frame with historical data
        :param col_name: name to output the simple moving average too
        :return: dataframe with new column
        '''
        df[col_name] = df[self.source].rolling(self.period).apply(
            lambda x: ((np.arange(self.period) + 1) * x).sum() / (np.arange(self.period) + 1).sum(),
            raw=True)
        return df

    def hull_helper(self, s, period):
        '''
        helper to calculate weighted MAs for hull moving average
        :param s: series with source column
        :param period: period of moving average
        :return:
        '''
        return s.rolling(period).apply(lambda x: ((np.arange(period) + 1) * x).sum() / (np.arange(period) + 1).sum(),
                                       raw=True)

    def hull(self, df, col_name):
        '''

        :param df:  data frame with historical data
        :param col_name: name to output the simple moving average to
        :return: dataframe with new column
        '''
        df[col_name] = self.hull_helper(
            self.hull_helper(df[self.source], self.period // 2) * 2 - self.hull_helper(df[self.source], self.period)
            , int(np.sqrt(self.period)))
        return df
