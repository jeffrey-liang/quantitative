#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pandas as pd
from securities import Security
from orders import MarketOrder
from engine import BacktestEngine

market_data = pd.read_csv('../data_files/test_data.csv',
                          parse_dates=True, index_col=0)
times = market_data.index

class BuySingleSecurity(BacktestEngine):

    def __init__(self):
        self.aapl = Security('AAPL')
        self.msft = Security('MSFT')
        self.market_data = market_data

        super().__init__(self.market_data, [self.aapl, self.msft])

        self.inital_cash = 10000
        self.include_commission = False

        self.counter = 0

    def trade_logic(self):

        if self.counter == 1:
            mkt_order = self.create_market_order('BUY', self.msft, 3, 'GTC')
            self.place_order(mkt_order)

        self.counter += 1


backtest = BuySingleSecurity()
result = backtest.run()
print(result)
print(result.loc[times[0]].cash)
