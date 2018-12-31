#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from securities import Security
from orders import MarketOrder
from engine import BacktestEngine

market_data = pd.read_csv('../data_files/test_data.csv',
                          parse_dates=True, index_col=0)
starting_cash = 10000.0

times = ['2017-11-10 09:30:00.000000000',  '2017-11-10 09:46:32.278115304',
         '2017-11-10 09:46:32.278133425', '2017-11-10 09:46:32.278142489',
         '2017-11-10 09:46:32.278175650', '2017-11-10 09:46:32.278182576',
         '2017-11-10 09:46:32.278187841', '2017-11-10 09:46:32.278192693',
         '2017-11-10 16:00:00.000000000', '2017-11-11 09:30:00.000000000',
         '2017-11-11 09:46:32.278221346', '2017-11-11 09:46:32.278229858',
         '2017-11-11 09:46:32.278235405']

times = [pd.Timestamp(time) for time in times]

cash = np.ones((1, len(times))) * starting_cash
portfolio_value = cash
investment_value = np.zeros((1, len(times)))

test_df = pd.DataFrame({'cash': cash.flatten(),
                        'investment_value': investment_value.flatten(),
                        'portfolio_value': portfolio_value.flatten()},
                       index=pd.to_datetime(times), dtype='float64')


def assert_account_values(time, actual, desired):

    print(actual.cash, desired.loc[time].cash)

    assert(actual.cash == desired.loc[time].cash)
    assert(actual.portfolio_value == desired.loc[time].portfolio_value)
    assert(actual.investment_value == desired.loc[time].investment_value)


def assert_cash_investments_equal_portfolio_value(time, account_vals):

    assert(account_vals.cash + account_vals.investment_value ==
           account_vals.portfolio_value)


class TestBuyAndHold(BacktestEngine):

    def __init__(self):
        self.aapl = Security('AAPL')
        self.msft = Security('MSFT')
        self.market_data = pd.read_csv('../data_files/test_data.csv',
                                       parse_dates=True, index_col=0)

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
                'BUY', self.aapl, 2, 103.88, 'GTC')
            self.place_order(lmt_order)

        #print(self.counter, self.msft.last_sale_price, self.aapl.last_sale_price)

        self.counter += 1

        assert_cash_investments_equal_portfolio_value(
            self.simulation_time, self.get_account_values())


test_buy_and_hold = TestBuyAndHold()
result = test_buy_and_hold.run()

test_df1 = test_df.copy()

test_df1.loc[times[1], 'cash'] = (10000 - (83.81 * 2))
test_df1.loc[times[1], 'investment_value'] = 83.81 * 2
test_df1.loc[times[2], 'cash'] = (10000 - (83.81 * 2)) - (103.88)
test_df1.loc[times[2], 'investment_value'] = 83.81 * 2 + 103.88
test_df1.loc[times[3]:, 'cash'] = (10000 - (83.81 * 2)) - (103.88 * 2)
test_df1.loc[times[3], 'investment_value'] = 83.81 * 2 + 103.88 * 2
test_df1.loc[times[4:6], 'investment_value'] = 84.8 * 2 + 103.88 * 2
test_df1.loc[times[4:6], 'portfolio_value'] = ((10000 - (83.81 * 2)) - (103.88 * 2) +
                                               84.8 * 2 + 103.88 * 2)
test_df1.loc[times[6:-1], 'investment_value'] = 84.8 * 2 + 103.8 * 2
test_df1.loc[times[6:-1], 'portfolio_value'] = ((10000 - (83.81 * 2)) - (103.88 * 2) +
                                                84.8 * 2 + 103.8 * 2)
test_df1.loc[times[-1], 'investment_value'] = 85.8 * 2 + 103.8 * 2
test_df1.loc[times[-1], 'portfolio_value'] = ((10000 - (83.81 * 2)) - (103.88 * 2) +
                                              85.8 * 2 + 103.8 * 2)

pd.testing.assert_frame_equal(result, test_df1)

class TestBuyAndSell(BacktestEngine):
    def __init__(self):
        self.aapl = Security('AAPL')
        self.msft = Security('MSFT')
        self.market_data = pd.read_csv('../data_files/test_data.csv',
                                       parse_dates=True, index_col=0)

        self.counter = 0

        super().__init__(self.market_data, [self.aapl, self.msft])

        self.inital_cash = starting_cash
        self.include_commission = False
        self.verbose = False

    def trade_logic(self):

        if self.counter == 1:
            lmt_order = self.create_limit_order(
                'BUY', self.msft, 1, 83.81, 'GTC')
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

        #print(self.get_holdings())

        assert_cash_investments_equal_portfolio_value(
            self.simulation_time, self.get_account_values())


test_buy_and_sell = TestBuyAndSell()
result = test_buy_and_sell.run()

test_df2 = test_df.copy()
test_df2.loc[times[1], 'cash'] = starting_cash - 83.81
test_df2.loc[times[1], 'investment_value'] = 83.81

test_df2.loc[times[2:4], 'cash'] = starting_cash - 83.81 - 103.88
test_df2.loc[times[2:4], 'investment_value'] = 83.81 + 103.88

test_df2.loc[times[4:6], 'cash'] = starting_cash - 83.81 - 103.88 + 83.79
test_df2.loc[times[4:6], 'investment_value'] = 103.88
test_df2.loc[times[4:6], 'portfolio_value'] = starting_cash - (83.81 - 83.79)

test_df2.loc[times[6:10], 'cash'] = starting_cash - 83.81 - 103.88 + 83.79
test_df2.loc[times[6:10], 'investment_value'] =  103.80
test_df2.loc[times[6:10], 'portfolio_value'] = (starting_cash - (83.81 - 83.79) -
                                               (103.88 - 103.8))


test_df2.loc[times[-3:], 'cash'] = (starting_cash - 83.81 - 103.88 +
                                    83.79 + 103.79)
test_df2.loc[times[-3:], 'investment_value'] = 0
test_df2.loc[times[-3:], 'portfolio_value'] = (starting_cash - (83.81 - 83.79)
                                               - (103.88 - 103.79))
pd.testing.assert_frame_equal(result, test_df2)
