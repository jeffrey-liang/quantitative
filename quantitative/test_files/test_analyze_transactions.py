#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from securities import Security
from orders import MarketOrder
from engine import BacktestEngine
from collections import namedtuple
from utils import parse_transaction_log, trade_details, trades_summary

market_data = pd.read_csv('../data_files/test_data.csv',
                          parse_dates=True, index_col=0)
starting_cash = 10000.0


class TestBuyAndSell(BacktestEngine):
    def __init__(self):
        self.aapl = Security('AAPL')
        self.msft = Security('MSFT')
        self.market_data = market_data

        self.counter = 0

        super().__init__(self.market_data, [self.aapl, self.msft])

        self.inital_cash = starting_cash
        self.include_commission = False
        self.verbose = False

    def trade_logic(self):

        if self.counter == 1:
            lmt_order = self.create_limit_order(
                'BUY', self.msft, 2, 83.81, 'GTC')
            self.place_order(lmt_order)

        if self.counter == 3:
            lmt_order = self.create_limit_order(
                'BUY', self.aapl, 1, 103.88, 'GTC')
            self.place_order(lmt_order)

        if self.counter == 6:
            lmt_order = self.create_limit_order(
                'SELL', self.msft, 1, 83.78, 'GTC')
            self.place_order(lmt_order)

        if self.counter == 7:
            lmt_order = self.create_limit_order(
                'SELL', self.aapl, 1, 103.78, 'GTC')
            self.place_order(lmt_order)

        self.counter += 1

        # print(self.get_holdings())


test_buy_and_sell = TestBuyAndSell()
result = test_buy_and_sell.run()
trans_log = test_buy_and_sell.get_transaction_log()
'''
cash_trans = []
market_trans = []
for key, lists in trans_log.items():
    for item in lists:
        if type(item).__name__ == 'cash_transaction':
            cash_trans.append(item)

        if type(item).__name__ == 'market_transaction':
            market_trans.append(item)

cash_trans = pd.DataFrame.from_dict(cash_trans)
cash_trans = cash_trans.set_index('time')
market_trans = pd.DataFrame.from_dict(market_trans)
market_trans = market_trans.set_index('time')
'''

cash, mkt = parse_transaction_log(trans_log)
# print(mkt)
#mkt['total'] = mkt[mkt['direction'] == 'SELL']
#mkt['total'] = mkt[['price', 'shares']][mkt['direction'] == 'SELL']
#print(mkt)
'''
mkt['total'] = 0

mask = mkt['direction'] == 'SELL'

mkt.loc[mask, 'total'] = mkt['price'] * mkt['shares'] - mkt['commission']
mkt.loc[~mask, 'total'] = -mkt['price'] * mkt['shares'] + mkt['commission']
# print(mkt)
groups = mkt.groupby(['ticker', 'sequence']).sum()

print(len(groups[groups['total'] > 0]))
print(len(groups[groups['total'] < 0]))
'''
#print(group_trades(mkt))
#print(trade_details(mkt, sequence_id=1))
print(trades_summary(mkt, 'AAPL'))

