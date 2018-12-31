#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from securities import Security
from engine import BacktestEngine


class MyBacktest(BacktestEngine):

    def __init__(self):
        self.aapl = Security('AAPL')
        self.msft = Security('MSFT')
        self.market_data = pd.read_csv('../data_files/sample_qt_aapl_msft.csv',
                                       parse_dates=True, index_col=0)

        super().__init__(self.market_data, [self.aapl, self.msft])

        self.inital_cash = 1000
        self.counter = 0

        self.close_prices = {'AAPL': [], 'MSFT': []}

    def simple_moving_average(self, ticker, window=20):

        close_prices = self.close_prices[ticker]
        if len(close_prices) < window:
            return np.nan
        else:
            return np.sum(self.close_prices[ticker][-window:]) / window

    def at_tick(self):
        self.close_prices['AAPL'].append(self.aapl.last_sale_price)

    def trade_logic(self):

        if self.counter == 100:
            print(self.simple_moving_average('AAPL'))
            print(self.simple_moving_average('AAPL', window=40))

        self.counter += 1

backtest = MyBacktest()
backtest.run()
        # print(backtest.apple_close_prices)

        #arr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        # print(arr[-50:])
