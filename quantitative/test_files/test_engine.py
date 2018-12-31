#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
from securities import Security
from orders import MarketOrder
from engine import BacktestEngine


market_data = pd.read_csv('../data_files/test_data.csv',
                          parse_dates=True, index_col=0)


class TestFunctions(BacktestEngine):

    def __init__(self):
        self.aapl = Security('AAPL')
        self.msft = Security('MSFT')
        self.market_data = pd.read_csv('../data_files/test_data.csv',
                                       parse_dates=True, index_col=0)

        super().__init__(self.market_data, [self.aapl, self.msft])

        self.inital_cash = 10000
        self.include_commission = False

    def at_tick(self):
        pass

    def trade_logic(self):

        lmt_order = self.create_limit_order('BUY', self.msft, 10, 100)

test_funcs = TestFunctions()
test_funcs.run()
#test_funcs.create_limit_order('BUY', self.msft, 10, 100)

for ticker, security in test_funcs.securities_in_universe.items():
    print(security)
