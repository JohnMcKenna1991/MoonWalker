from Backtester.BackTestBase import BackTestBase
from Indicators.MovingAverage import MovingAverage
from Indicators.RSI import RSI
from Indicators.ATR import ATR
from Indicators.CI import ChopIndex
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



class MoonPhaseDma(BackTestBase):

    def __init__(self, csv_path, date_col, timeframe,  entry_exit_conds, ma_1, ma_2,  rsi,  ci, atr):

        super().__init__(csv_path, date_col, 30)


        self.atr_long_target = entry_exit_conds.get('reward')
        self.atr_long_stop = entry_exit_conds.get('risk')
        self.atr_short_target = entry_exit_conds.get('reward')
        self.atr_short_stop = entry_exit_conds.get('risk')


        self.timeframe = timeframe


        self.ma_1 = ma_1
        self.ma_2 = ma_2

        self.rsi = rsi
        self.ci = ci

        self.atr = atr


    def open_long(self, price , atr):
        self.open_pos = True
        self.direction = 1
        self.entry_price = price
        self.target_price = price + atr * self.atr_long_target
        self.stop_price = price - atr * self.atr_long_stop
        self.returns_series.append(0)
        print(f'Opened a long trade at {self.entry_price}')

        print(f'Opened a long trade target  {self.target_price}')

        print(f'Opened a long trade stop at {self.stop_price}')

    def open_short(self, price, atr):
        self.open_pos = True
        self.direction = -1
        self.entry_price = price
        self.target_price = price - atr * self.atr_short_target
        self.stop_price = price + atr * self.atr_short_stop
        self.returns_series.append(0)
        print(f'Opened a short trade at {self.entry_price}')

        print(f'Opened a short trade target  {self.target_price}')

        print(f'Opened a short trade stop at {self.stop_price}')



    def generate_signals(self):
        df = self.dmgt.df
        df = MovingAverage(self.ma_1.get('period'), self.ma_1.get('source')).vwma(df, 'ma1')
        df = MovingAverage(self.ma_2.get('period'), self.ma_2.get('source')).lin_reg(df, 'ma2')
        df = ATR(self.atr.get('length')).atr(df, 'atr')
        # resamp = df.resample('D').last()
        # resamp = ChopIndex(self.ci.get('length')).ci(resamp, 'ci')
        # resamp = RSI(period=self.rsi.get('length')).rsi(resamp, 'rsi')
        df = ChopIndex(self.ci.get('length')).ci(df, 'ci')

        df = RSI(period=self.rsi.get('length')).rsi(df, 'rsi')
        # df = pd.merge(df, resamp[['ci', 'rsi']], how='outer', left_index=True, right_index=True)
        # df.fillna(method='ffill', inplace=True)

        df['longs'] = ((df.ma1 > df.ma2) & (df.ma1.shift(1) < df.ma2) & (df.rsi > self.rsi.get('long_min')) &
                        (df.rsi < self.rsi.get('long_max')) & (df.ci > self.ci.get('minci')) & (df.ci < self.ci.get('maxci')))*1

        df['shorts'] = ((df.ma1 < df.ma2) & (df.ma1.shift(1) > df.ma2) & (df.rsi > self.rsi.get('short_min')) &
                        (df.rsi < self.rsi.get('short_max')) & (df.ci > self.ci.get('minci')) & (df.ci < self.ci.get('maxci')))*-1

        df['entry'] = df.longs + df.shorts

        self.dmgt.df = df


    def switch_position_short_to_long(self, price, atr):
        self.close_position(price)

        self.open_long(price, atr)

        self.returns_series.remove(0)


    def switch_position_long_to_short(self, price, atr):

        self.close_position(price)
        self.open_short(price, atr)

        self.returns_series.remove(0)


    def run_backtest(self):
        # signals generated from child class
        self.generate_signals()

        # loop over dataframe
        for row in self.dmgt.df.itertuples():
            # if we get a long signal and do not have open position open a long
            if row.entry == 1 and self.open_pos is False:
                self.open_long(row.t_plus, row.atr)
            # if we get a short position and do not have open position open a sort
            elif row.entry == -1 and self.open_pos is False:
                self.open_short(row.t_plus, row.atr)
            # monitor open positions to see if any of the barriers have been touched, see function above
            elif row.entry == 1 and self.direction == -1:
                self.switch_position_short_to_long(row.t_plus, row.atr)

            elif row.entry == -1 and self.direction == 1:
                self.switch_position_long_to_short(row.t_plus, row.atr)

            elif self.open_pos:
                self.monitor_open_positions(row.close, row.Index)
            else:
                self.returns_series.append(0)

        self.dmgt.df['returns'] = self.returns_series
        self.returns_series = []








if __name__ == '__main__':
    ma_1 = {'type': 'vwma' , 'period': 69, 'source': 'low'}
    ma_2 = {'type': 'lin_reg' , 'period': 359, 'source': 'low'}

    rsi_params = {'length': 14, 'long_max': 75, 'long_min':30, 'short_max': 65, 'short_min': 45}
    chop_params = {'length': 14, 'maxci': 60, 'minci': 25}
    atr = {'length': 14}

    entry_exit_conds = {'risk': 25, 'reward': 15}

    csv_path = r"C:\Users\user\MoonWalkerBacktester\Data\BTCUSD_Bybit15min.csv"

    date_col = 'Date'

    strategy = MoonPhaseDma(csv_path=csv_path, date_col=date_col, timeframe='15', entry_exit_conds=entry_exit_conds,
                            ma_1=ma_1, ma_2=ma_2, rsi=rsi_params, ci=chop_params, atr=atr)

    strategy.run_backtest()
    strategy.dmgt.df.returns.cumsum().plot()
    plt.show()















