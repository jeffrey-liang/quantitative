#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from quantitative import Security, BacktestEngine, MarketOrder
'''
from securities import Security
from orders import MarketOrder
from engine import BacktestEngine
'''
starting_cash = 10000.0


times = ['2017-11-10 09:30:00.000000000',  '2017-11-10 09:46:32.278115304',
         '2017-11-10 09:46:32.278133425', '2017-11-10 09:46:32.278142489',
         '2017-11-10 09:46:32.278175650', '2017-11-10 09:46:32.278182576',
         '2017-11-10 09:46:32.278187841', '2017-11-10 09:46:32.278192693',
         '2017-11-10 16:00:00.000000000', '2017-12-10 09:30:00.000000000',
         '2017-12-10 09:46:32.278221346', '2017-12-10 09:46:32.278229858',
         '2017-12-10 09:46:32.278235405']

times = [pd.Timestamp(time) for time in times]


class TestBuyAndHold(BacktestEngine):

    def __init__(self):
        self.aapl = Security('AAPL')
        self.msft = Security('MSFT')
        self.market_data = pd.read_csv('../../data_files/test_data.csv',
                                       parse_dates=True, index_col=0)

        self.counter = 0

        super().__init__(self.market_data, [
              self.aapl, self.msft], record_history=True)

        self.inital_cash = starting_cash
        self.include_commission = False
        self.verbose = True

    def trade_logic(self):

        if self.counter == 8:
            mkt_order = self.create_market_order('BUY', self.msft, 2, 'GTC')
            self.place_order(mkt_order)

        print(self.get_account_values())

        self.counter += 1


test_buy_and_hold=TestBuyAndHold()
result=test_buy_and_hold.run()
