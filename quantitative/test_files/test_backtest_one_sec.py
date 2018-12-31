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


class CheckTime(BacktestEngine):

    def __init__(self):
        self.aapl = Security('AAPL')
        self.msft = Security('MSFT')
        self.market_data = pd.read_csv('../data_files/test_data.csv',
                                       parse_dates=True, index_col=0)

        super().__init__(self.market_data, [self.aapl, self.msft])

        self.inital_cash = starting_cash
        self.include_commission = False
        self.verbose = False

        self.counter = 0

    def trade_logic(self):

        assert(self.get_time() == times[self.counter])
        self.counter += 1


check_time = CheckTime()
check_time.run()


class TestSecurities(BacktestEngine):

    def __init__(self):
        self.aapl = Security('AAPL')
        self.msft = Security('MSFT')
        self.market_data = pd.read_csv('../data_files/test_data.csv',
                                       parse_dates=True, index_col=0)

        super().__init__(self.market_data, [self.aapl, self.msft])

        self.inital_cash = starting_cash
        self.include_commission = False
        self.verbose = False

    def trade_logic(self):

        if self.get_time() == times[0]:
            assert(np.isnan(self.msft.ask) and np.isnan(self.msft.bid))
            assert(np.isnan(self.aapl.ask) and np.isnan(self.aapl.bid))

            assert(np.isnan(self.msft.ask_size)
                   and np.isnan(self.msft.bid_size))
            assert(np.isnan(self.msft.ask_size)
                   and np.isnan(self.msft.bid_size))

            assert(np.isnan(self.msft.last_sale_price))
            assert(np.isnan(self.msft.last_sale_size))
            assert(self.msft.last_sale_time == None)

            assert(np.isnan(self.aapl.last_sale_price))
            assert(np.isnan(self.aapl.last_sale_size))
            assert(self.aapl.last_sale_time == None)

        if self.get_time() == times[1]:
            assert(self.msft.ask == 83.81 and self.msft.bid == 83.79)
            assert(np.isnan(self.aapl.ask) and np.isnan(self.aapl.bid))

            assert(self.msft.ask_size == 2 and self.msft.bid_size == 1)
            assert(np.isnan(self.aapl.ask_size)
                   and np.isnan(self.aapl.bid_size))

            assert(np.isnan(self.msft.last_sale_price))
            assert(np.isnan(self.msft.last_sale_size))
            assert(self.msft.last_sale_time == None)

            assert(np.isnan(self.aapl.last_sale_price))
            assert(np.isnan(self.aapl.last_sale_size))
            assert(self.aapl.last_sale_time == None)

        if self.get_time() == times[2]:
            assert(self.msft.ask == 83.81 and self.msft.bid == 83.79)
            assert(self.aapl.ask == 103.88 and self.aapl.bid == 103.77)

            assert(self.msft.ask_size == 2 and self.msft.bid_size == 1)
            assert(self.aapl.ask_size == 1 and self.aapl.bid_size == 1)

            assert(np.isnan(self.msft.last_sale_price))
            assert(np.isnan(self.msft.last_sale_size))
            assert(self.msft.last_sale_time == None)

            assert(np.isnan(self.aapl.last_sale_price))
            assert(np.isnan(self.aapl.last_sale_size))
            assert(self.aapl.last_sale_time == None)

        if self.get_time() == times[3]:
            assert(self.msft.ask == 83.81 and self.msft.bid == 83.79)
            assert(self.aapl.ask == 103.88 and self.aapl.bid == 103.77)

            assert(self.msft.ask_size == 2 and self.msft.bid_size == 1)
            assert(self.aapl.ask_size == 1 and self.aapl.bid_size == 1)

            assert(np.isnan(self.msft.last_sale_price))
            assert(np.isnan(self.msft.last_sale_size))
            assert(self.msft.last_sale_time == None)

            assert(np.isnan(self.aapl.last_sale_price))
            assert(np.isnan(self.aapl.last_sale_size))
            assert(self.aapl.last_sale_time == None)

        if self.get_time() == times[4]:

            assert(self.msft.ask == 83.81 and self.msft.bid == 83.79)
            assert(self.aapl.ask == 103.88 and self.aapl.bid == 103.77)

            assert(self.msft.ask_size == 2 and self.msft.bid_size == 1)
            assert(self.aapl.ask_size == 1 and self.aapl.bid_size == 1)

            assert(self.msft.last_sale_price == 84.8)
            assert(self.msft.last_sale_size == 100)
            assert(self.msft.last_sale_time == times[4])

            assert(np.isnan(self.aapl.last_sale_price))
            assert(np.isnan(self.aapl.last_sale_size))
            assert(self.aapl.last_sale_time == None)

        if self.get_time() == times[5]:

            assert(self.msft.ask == 83.8 and self.msft.bid == 83.79)
            assert(self.aapl.ask == 103.88 and self.aapl.bid == 103.77)

            assert(self.msft.ask_size == 5 and self.msft.bid_size == 7)
            assert(self.aapl.ask_size == 1 and self.aapl.bid_size == 1)

            assert(self.msft.last_sale_price == 84.8)
            assert(self.msft.last_sale_size == 100)
            assert(self.msft.last_sale_time == times[4])

            assert(np.isnan(self.aapl.last_sale_price))
            assert(np.isnan(self.aapl.last_sale_size))
            assert(self.aapl.last_sale_time == None)

        if self.get_time() == times[6]:

            assert(self.msft.ask == 83.8 and self.msft.bid == 83.79)
            assert(self.aapl.ask == 103.88 and self.aapl.bid == 103.77)

            assert(self.msft.ask_size == 5 and self.msft.bid_size == 7)
            assert(self.aapl.ask_size == 1 and self.aapl.bid_size == 1)

            assert(self.msft.last_sale_price == 84.8)
            assert(self.msft.last_sale_size == 100)
            assert(self.msft.last_sale_time == times[4])

            assert(self.aapl.last_sale_price == 103.8)
            assert(self.aapl.last_sale_size == 100)
            assert(self.aapl.last_sale_time == times[6])

        if self.get_time() == times[7]:
            assert(self.msft.ask == 83.81 and self.msft.bid == 83.79)
            assert(self.aapl.ask == 103.88 and self.aapl.bid == 103.77)

            assert(self.msft.ask_size == 4 and self.msft.bid_size == 3)
            assert(self.aapl.ask_size == 1 and self.aapl.bid_size == 1)

            assert(self.msft.last_sale_price == 84.8)
            assert(self.msft.last_sale_size == 100)
            assert(self.msft.last_sale_time == times[4])

            assert(self.aapl.last_sale_price == 103.8)
            assert(self.aapl.last_sale_size == 100)
            assert(self.aapl.last_sale_time == times[6])

        if self.get_time() == times[8]:
            assert(self.msft.ask == 83.81 and self.msft.bid == 83.79)
            assert(self.aapl.ask == 103.88 and self.aapl.bid == 103.77)

            assert(self.msft.ask_size == 4 and self.msft.bid_size == 3)
            assert(self.aapl.ask_size == 1 and self.aapl.bid_size == 1)

            assert(self.msft.last_sale_price == 84.8)
            assert(self.msft.last_sale_size == 100)
            assert(self.msft.last_sale_time == times[4])

            assert(self.aapl.last_sale_price == 103.8)
            assert(self.aapl.last_sale_size == 100)
            assert(self.aapl.last_sale_time == times[6])

        if self.get_time() == times[9]:
            assert(self.msft.ask == 83.81 and self.msft.bid == 83.79)
            assert(self.aapl.ask == 103.88 and self.aapl.bid == 103.77)

            assert(self.msft.ask_size == 4 and self.msft.bid_size == 3)
            assert(self.aapl.ask_size == 1 and self.aapl.bid_size == 1)

            assert(self.msft.last_sale_price == 84.8)
            assert(self.msft.last_sale_size == 100)
            assert(self.msft.last_sale_time == times[4])

            assert(self.aapl.last_sale_price == 103.8)
            assert(self.aapl.last_sale_size == 100)
            assert(self.aapl.last_sale_time == times[6])

        if self.get_time() == times[10]:
            assert(self.msft.ask == 83.81 and self.msft.bid == 83.79)
            assert(self.aapl.ask == 103.8 and self.aapl.bid == 103.79)

            assert(self.msft.ask_size == 4 and self.msft.bid_size == 3)
            assert(self.aapl.ask_size == 3 and self.aapl.bid_size == 4)

            assert(self.msft.last_sale_price == 84.8)
            assert(self.msft.last_sale_size == 100)
            assert(self.msft.last_sale_time == times[4])

            assert(self.aapl.last_sale_price == 103.8)
            assert(self.aapl.last_sale_size == 100)
            assert(self.aapl.last_sale_time == times[6])

        if self.get_time() == times[11]:
            assert(self.msft.ask == 83.81 and self.msft.bid == 83.72)
            assert(self.aapl.ask == 103.8 and self.aapl.bid == 103.79)

            assert(self.msft.ask_size == 2 and self.msft.bid_size == 1)
            assert(self.aapl.ask_size == 3 and self.aapl.bid_size == 4)

            assert(self.msft.last_sale_price == 84.8)
            assert(self.msft.last_sale_size == 100)
            assert(self.msft.last_sale_time == times[4])

            assert(self.aapl.last_sale_price == 103.8)
            assert(self.aapl.last_sale_size == 100)
            assert(self.aapl.last_sale_time == times[6])

        if self.get_time() == times[12]:
            assert(self.msft.ask == 83.81 and self.msft.bid == 83.72)
            assert(self.aapl.ask == 103.8 and self.aapl.bid == 103.79)

            assert(self.msft.ask_size == 2 and self.msft.bid_size == 1)
            assert(self.aapl.ask_size == 3 and self.aapl.bid_size == 4)

            assert(self.msft.last_sale_price == 85.8)
            assert(self.msft.last_sale_size == 200)
            assert(self.msft.last_sale_time == times[12])

            assert(self.aapl.last_sale_price == 103.8)
            assert(self.aapl.last_sale_size == 100)
            assert(self.aapl.last_sale_time == times[6])


test_sec = TestSecurities()
test_sec.run()


class SimpleBacktest(BacktestEngine):

    def __init__(self):
        self.aapl = Security('AAPL')
        self.msft = Security('MSFT')
        self.market_data = pd.read_csv('../data_files/test_data.csv',
                                       parse_dates=True, index_col=0)

        super().__init__(self.market_data, [self.aapl, self.msft])

        self.inital_cash = starting_cash
        self.include_commission = False
        self.verbose = False

    def trade_logic(self):
        pass


simple_backtest = SimpleBacktest()
result = simple_backtest.run()
# No trades, initalize account only
pd.testing.assert_frame_equal(result, test_df)

# Market Orders

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
            mkt_order = self.create_market_order('BUY', self.msft, 2, 'GTC')
            self.place_order(mkt_order)

        self.counter += 1

        assert_cash_investments_equal_portfolio_value(
            self.simulation_time, self.get_account_values())


test_buy_and_hold = TestBuyAndHold()
result = test_buy_and_hold.run()
test_df1 = test_df.copy()
test_df1.loc[times[1]:, 'cash'] = (10000 - (83.81 * 2))
test_df1.loc[times[1]:times[4], 'investment_value'] = (83.81 * 2)
test_df1.loc[times[4]:, 'investment_value'] = (84.8 * 2)
test_df1.loc[times[-1]:, 'investment_value'] = (85.8 * 2)
test_df1.loc[times[4]:, 'portfolio_value'] = 10000 + (84.8 - 83.81) * 2
test_df1.loc[times[-1]:, 'portfolio_value'] = 10000 + (85.8 - 83.81) * 2

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
            mkt_order = self.create_market_order('BUY', self.msft, 1, 'GTC')
            self.place_order(mkt_order)

        if self.counter == 3:
            mkt_order = self.create_market_order('SELL', self.msft, 1, 'GTC')
            self.place_order(mkt_order)

        self.counter += 1

        assert_cash_investments_equal_portfolio_value(
            self.simulation_time, self.get_account_values())


test_buy_and_sell = TestBuyAndSell()
result = test_buy_and_sell.run()

test_df2 = test_df.copy()
test_df2.loc[times[1], 'cash'] = (10000 - (83.81 * 1))
test_df2.loc[times[1], 'investment_value'] = (83.81 * 1)
test_df2.loc[times[2]:, 'cash'] = (10000 + (83.81 - 83.79))
test_df2.loc[times[2]:, 'portfolio_value'] = (10000 + (83.81 - 83.79))

pd.testing.assert_frame_equal(result, test_df2)


class TestOverBuy(BacktestEngine):
    # Not enough cash for order
    def __init__(self):
        self.aapl = Security('AAPL')
        self.msft = Security('MSFT')
        self.market_data = pd.read_csv('../data_files/test_data.csv',
                                       parse_dates=True, index_col=0)

        self.counter = 0

        super().__init__(self.market_data, [self.aapl, self.msft])

        self.inital_cash = 50
        self.include_commission = False
        self.verbose = False

    def trade_logic(self):

        if self.counter == 1:
            mkt_order = self.create_market_order('BUY', self.msft, 1, 'GTC')
            self.place_order(mkt_order)

        self.counter += 1

        assert(len(self.get_open_positions()) == 0)


test_over_buy = TestOverBuy()
test_over_buy.run()


class TestSellOrderMultipleTries(BacktestEngine):
    # Buy order filled in one try
    # Sell order filled completely in two tries
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
            mkt_order = self.create_market_order('BUY', self.msft, 2, 'GTC')
            self.place_order(mkt_order)

        if self.counter == 2:
            # check if shares are reduced after order was filled
            assert(self.msft.ask_size == 0)

        if self.counter == 3:
            mkt_order = self.create_market_order('SELL', self.msft, 2, 'GTC')
            self.place_order(mkt_order)

        if self.counter == 4:
            assert(self.msft.bid_size == 0)

        if self.counter == 5:
            assert(self.msft.bid_size == 0)

        self.counter += 1

        assert_cash_investments_equal_portfolio_value(
            self.simulation_time, self.get_account_values())


test_sell_order_multi_tries = TestSellOrderMultipleTries()
result = test_sell_order_multi_tries.run()

test_df3 = test_df.copy()
test_df3.loc[times[1], 'cash'] = (10000 - (83.81 * 2))
test_df3.loc[times[1], 'investment_value'] = (83.81 * 2)
test_df3.loc[times[2:5], 'cash'] = (10000 - (83.81 * 2) + (83.79 * 1))
test_df3.loc[times[2:4], 'investment_value'] = (83.79 * 1)
test_df3.loc[times[2:4], 'portfolio_value'] = (10000 - (83.81 * 2)) + 83.79 * 2
test_df3.loc[times[4], 'investment_value'] = (84.8)
test_df3.loc[times[4], 'portfolio_value'] = (
    10000 - (83.81 * 2) + (83.79 * 1) + 84.8)
test_df3.loc[times[5]:, 'cash'] = (10000 - (83.81 * 2) + (83.79 * 1)) + 83.79
test_df3.loc[times[5]:, 'investment_value'] = 0
test_df3.loc[times[5]:, 'portfolio_value'] = (
    10000 - (83.81 * 2) + (83.79 * 1)) + 83.79

pd.testing.assert_frame_equal(result, test_df3)


class TestBuyOrderMultipleTries(BacktestEngine):
    # Buy order filled in two tries
    # Sell order filled completely in one try
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
            mkt_order = self.create_market_order('BUY', self.msft, 3, 'GTC')
            self.place_order(mkt_order)

        if self.counter == 2:
            assert(self.msft.ask_size == 0)

        if self.counter == 3:
            assert(self.msft.ask_size == 0)
            assert(self.get_shares('MSFT') == 2)

        if self.counter == 4:
            assert(self.msft.ask_size == 0)

        if self.counter == 5:
            assert(self.msft.ask_size == 0)
            assert(self.msft.last_sale_price == 84.8)

        if self.counter == 6:
            assert(self.msft.ask_size == 4)
            assert(self.msft.last_sale_price == 83.8)
            assert(self.get_shares('MSFT') == 3)

        if self.counter == 7:
            mkt_order = self.create_market_order('SELL', self.msft, 3, 'GTC')
            self.place_order(mkt_order)

        if self.counter == 8:
            assert(self.get_shares('MSFT') == 0)

        assert(self.get_shares('AAPL') == 0)
        self.counter += 1
        assert_cash_investments_equal_portfolio_value(
            self.simulation_time, self.get_account_values())


test_buy_order_multi_tries = TestBuyOrderMultipleTries()
result = test_buy_order_multi_tries.run()

test_df4 = test_df.copy()
test_df4.loc[times[1:5], 'cash'] = starting_cash - (83.81 * 2)
test_df4.loc[times[1:4], 'investment_value'] = (83.81 * 2)
test_df4.loc[times[4], 'investment_value'] = (84.8 * 2)
test_df4.loc[times[4], 'portfolio_value'] = (
    starting_cash + (84.8 * 2 - 83.81 * 2))
test_df4.loc[times[5], 'cash'] = starting_cash - (83.81 * 2) - 83.8
test_df4.loc[times[5], 'investment_value'] = (83.8 * 3)
test_df4.loc[times[5], 'portfolio_value'] = (
    (starting_cash - (83.81 * 2) - 83.8) + (83.8 * 3))
test_df4.loc[times[6:], 'cash'] = (
    starting_cash - (83.81 * 2) - 83.8 + (83.79 * 3))
test_df4.loc[times[6:], 'portfolio_value'] = (
    starting_cash - (83.81 * 2) - 83.8 + (83.79 * 3))

pd.testing.assert_frame_equal(result, test_df4)


class BuyMoreShares(BacktestEngine):

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
            mkt_order = self.create_market_order('BUY', self.msft, 2, 'GTC')
            self.place_order(mkt_order)

        if self.counter == 2:
            assert(self.get_shares('MSFT') == 2)

        if self.counter == 6:
            mkt_order = self.create_market_order('BUY', self.msft, 2, 'GTC')
            self.place_order(mkt_order)

        if self.counter == 7:
            assert(self.get_shares('MSFT') == 4)

        self.counter += 1


buy_more_shares = BuyMoreShares()
result = buy_more_shares.run()

test_df5 = test_df.copy()
test_df5.loc[times[1:5], 'cash'] = starting_cash - 83.81 * 2
test_df5.loc[times[1:4], 'investment_value'] = 83.81 * 2
test_df5.loc[times[4], 'investment_value'] = 84.8 * 2
test_df5.loc[times[4], 'portfolio_value'] = starting_cash + (84.8 - 83.81) * 2
test_df5.loc[times[5:], 'cash'] = starting_cash - 83.81 * 2 - 83.8 * 2
test_df5.loc[times[5:], 'investment_value'] = 4 * 83.8
test_df5.loc[times[5:-1], 'portfolio_value'] = (
    starting_cash - 83.81 * 2 - 83.8 * 2 + (83.8 * 4))
test_df5.loc[times[-1], 'investment_value'] = 4 * 85.8
test_df5.loc[times[-1], 'portfolio_value'] = (
    starting_cash - 83.81 * 2 - 83.8 * 2 + (85.8 * 4))

pd.testing.assert_frame_equal(result, test_df5)


class SellMoreShares(BacktestEngine):

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
        if self.counter == 6:
            mkt_order = self.create_market_order('BUY', self.msft, 4, 'GTC')
            self.place_order(mkt_order)

        if self.counter == 8:
            mkt_order = self.create_market_order('SELL', self.msft, 2, 'GTC')
            self.place_order(mkt_order)

        if self.counter == 12:
            mkt_order = self.create_market_order('SELL', self.msft, 2, 'GTC')
            self.place_order(mkt_order)

        self.counter += 1


sell_more_shares = SellMoreShares()
result = sell_more_shares.run()

test_df6 = test_df.copy()
test_df6.loc[times[6], 'cash'] = starting_cash - 83.8 * 4
test_df6.loc[times[6], 'investment_value'] = 83.8 * 4
test_df6.loc[times[7:10], 'cash'] = starting_cash - (83.8 * 4) + (83.79 * 2)
test_df6.loc[times[7:10], 'investment_value'] = 83.79 * 2
test_df6.loc[times[7:10], 'portfolio_value'] = (
    (starting_cash - 83.8 * 4) + 83.79 * 4)
test_df6.loc[times[10], 'cash'] = (starting_cash -
                                   (83.8 * 4) + (83.79 * 2) + 83.79)
test_df6.loc[times[10], 'investment_value'] = 83.79
test_df6.loc[times[7:11], 'portfolio_value'] = (
    starting_cash - (83.8 * 4) + (83.79 * 2) + 83.79 * 2)
test_df6.loc[times[11:13], 'cash'] = (starting_cash -
                                      (83.8 * 4) + (83.79 * 2) + 83.79 + 83.72)
test_df6.loc[times[11:13], 'portfolio_value'] = (
    starting_cash - 83.8 * 4 + 83.79 * 3 + 83.72)
pd.testing.assert_frame_equal(result, test_df6)


class TestBuyAndHoldAON(BacktestEngine):

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
            mkt_order = self.create_market_order('BUY', self.msft, 2, 'AON')
            self.place_order(mkt_order)

        if self.counter == 5:
            mkt_order = self.create_market_order('BUY', self.msft, 10, 'AON')
            self.place_order(mkt_order)

        self.counter += 1

        assert_cash_investments_equal_portfolio_value(
            self.simulation_time, self.get_account_values())


test_buy_and_hold_AON = TestBuyAndHoldAON()
result = test_buy_and_hold_AON.run()

pd.testing.assert_frame_equal(result, test_df1)


class TestBuyAndSellAON(BacktestEngine):

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
            mkt_order = self.create_market_order('BUY', self.msft, 1, 'AON')
            self.place_order(mkt_order)

        if self.counter == 3:
            mkt_order = self.create_market_order('SELL', self.msft, 1, 'AON')
            self.place_order(mkt_order)

        if self.counter == 5:
            mkt_order = self.create_market_order('BUY', self.msft, 10, 'AON')

        self.counter += 1

        assert_cash_investments_equal_portfolio_value(
            self.simulation_time, self.get_account_values())


test_buy_and_sell_AON = TestBuyAndSellAON()
result = test_buy_and_sell_AON.run()

pd.testing.assert_frame_equal(result, test_df2)


class TestBuyAndHoldIOC(BacktestEngine):

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
            mkt_order = self.create_market_order('BUY', self.msft, 3, 'IOC')
            self.place_order(mkt_order)

        self.counter += 1

        assert_cash_investments_equal_portfolio_value(
            self.simulation_time, self.get_account_values())


test_buy_and_hold_IOC = TestBuyAndHoldIOC()
result = test_buy_and_hold_IOC.run()
pd.testing.assert_frame_equal(result, test_df1)


class TestBuyAndSellIOC(BacktestEngine):

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
            mkt_order = self.create_market_order('BUY', self.msft, 2, 'IOC')
            self.place_order(mkt_order)

        if self.counter == 3:
            mkt_order = self.create_market_order('SELL', self.msft, 2, 'IOC')
            self.place_order(mkt_order)

        self.counter += 1
        for _, order in self.unfilled_orders.items():
            assert(len(order) == 0)

        assert_cash_investments_equal_portfolio_value(
            self.simulation_time, self.get_account_values())


test_buy_and_sell_IOC = TestBuyAndSellIOC()
result = test_buy_and_sell_IOC.run()

test_df7 = test_df.copy()
test_df7.loc[times[1], 'cash'] = starting_cash - 83.81 * 2
test_df7.loc[times[1], 'investment_value'] = 83.81 * 2
test_df7.loc[times[2:], 'cash'] = starting_cash - 83.81 * 2 + 83.79
test_df7.loc[times[2:4], 'investment_value'] = 83.79
test_df7.loc[times[2:4], 'portfolio_value'] = (83.79 +
                                               starting_cash - 83.81 * 2 + 83.79)
test_df7.loc[times[4:], 'investment_value'] = 84.8
test_df7.loc[times[4:-1], 'portfolio_value'] = (83.79 +
                                                starting_cash - 83.81 * 2 + 84.8)
test_df7.loc[times[-1], 'investment_value'] = 85.8
test_df7.loc[times[-1], 'portfolio_value'] = (83.79 +
                                              starting_cash - 83.81 * 2 + 85.8)

pd.testing.assert_frame_equal(result, test_df7)


class TestBuyAndHoldFOK(BacktestEngine):

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
            mkt_order = self.create_market_order('BUY', self.msft, 2, 'FOK')
            self.place_order(mkt_order)

        if self.counter == 5:
            mkt_order = self.create_market_order('BUY', self.msft, 10, 'FOK')
            self.place_order(mkt_order)

        self.counter += 1

        assert_cash_investments_equal_portfolio_value(
            self.simulation_time, self.get_account_values())


test_buy_and_hold_FOK = TestBuyAndHoldFOK()
result = test_buy_and_hold_FOK.run()
pd.testing.assert_frame_equal(result, test_df1)


class TestBuyAndSellFOK(BacktestEngine):

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
            mkt_order = self.create_market_order('BUY', self.msft, 1, 'FOK')
            self.place_order(mkt_order)

        if self.counter == 3:
            mkt_order = self.create_market_order('SELL', self.msft, 1, 'FOK')
            self.place_order(mkt_order)

        self.counter += 1
        for _, order in self.unfilled_orders.items():
            assert(len(order) == 0)

        assert_cash_investments_equal_portfolio_value(
            self.simulation_time, self.get_account_values())


test_buy_and_sell_FOK = TestBuyAndSellFOK()
result = test_buy_and_sell_FOK.run()
pd.testing.assert_frame_equal(result, test_df2)


class TestBuyAndFailToSellFOK(BacktestEngine):

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
            mkt_order = self.create_market_order('BUY', self.msft, 2, 'FOK')
            self.place_order(mkt_order)

        if self.counter == 3:
            mkt_order = self.create_market_order('SELL', self.msft, 2, 'FOK')
            self.place_order(mkt_order)

        self.counter += 1
        for _, order in self.unfilled_orders.items():
            assert(len(order) == 0)

        assert_cash_investments_equal_portfolio_value(
            self.simulation_time, self.get_account_values())


test_buy_and_fail_to_sell_FOK = TestBuyAndFailToSellFOK()
result = test_buy_and_fail_to_sell_FOK.run()
pd.testing.assert_frame_equal(result, test_df1)

# Limit Orders


class TestBuyAndHoldLmt(BacktestEngine):

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

        if self.counter == 2:
            lmt_order = self.create_limit_order('BUY', self.msft, 2, 80, 'GTC')
            self.place_order(lmt_order)

        self.counter += 1

        assert_cash_investments_equal_portfolio_value(
            self.simulation_time, self.get_account_values())


test_buy_and_hold_lmt = TestBuyAndHoldLmt()
result = test_buy_and_hold_lmt.run()

pd.testing.assert_frame_equal(result, test_df1)


class TestBuyAndSellLmt(BacktestEngine):
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
                'SELL', self.msft, 2, 90, 'GTC')
            self.place_order(lmt_order)

        if self.counter == 4:
            assert(len(self.unfilled_orders['GTC']) == 1)
            lmt_order = self.create_limit_order(
                'SELL', self.msft, 2, 80, 'GTC')
            self.place_order(lmt_order)

        self.counter += 1

        assert_cash_investments_equal_portfolio_value(
            self.simulation_time, self.get_account_values())


test_buy_and_sell_lmt = TestBuyAndSellLmt()
result = test_buy_and_sell_lmt.run()

pd.testing.assert_frame_equal(result, test_df3)


class TestBuyLmtFOK(BacktestEngine):

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
                'BUY', self.msft, 2, 83.81, 'FOK')
            self.place_order(lmt_order)

        if self.counter == 3:
            lmt_order = self.create_limit_order(
                'SELL', self.msft, 2, 90, 'FOK')
            self.place_order(lmt_order)

        if self.counter == 4:
            lmt_order = self.create_limit_order(
                'SELL', self.msft, 2, 80, 'FOK')
            self.place_order(lmt_order)

        self.counter += 1

        assert_cash_investments_equal_portfolio_value(
            self.simulation_time, self.get_account_values())


test_buy_lmt_FOK = TestBuyLmtFOK()
result = test_buy_lmt_FOK.run()
pd.testing.assert_frame_equal(result, test_df1)


class TestBuyAndSellLmtFOK(BacktestEngine):

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
                'BUY', self.msft, 2, 83.81, 'FOK')
            self.place_order(lmt_order)

        if self.counter == 3:
            lmt_order = self.create_limit_order(
                'SELL', self.msft, 2, 90, 'FOK')
            self.place_order(lmt_order)

        if self.counter == 7:
            lmt_order = self.create_limit_order(
                'SELL', self.msft, 2, 80, 'FOK')
            self.place_order(lmt_order)

        self.counter += 1

        assert_cash_investments_equal_portfolio_value(
            self.simulation_time, self.get_account_values())


test_buy_and_sell_lmt_FOK = TestBuyAndSellLmtFOK()
result = test_buy_and_sell_lmt_FOK.run()
test_df8 = test_df.copy()
test_df8.loc[times[1:5], 'cash'] = starting_cash - 83.81 * 2
test_df8.loc[times[1:4], 'investment_value'] = 83.81 * 2
test_df8.loc[times[4], 'investment_value'] = 84.8 * 2
test_df8.loc[times[4], 'portfolio_value'] = starting_cash + (84.8 - 83.81) * 2
test_df8.loc[times[5:], 'cash'] = starting_cash + (83.79 - 83.81) * 2
test_df8.loc[times[5:], 'portfolio_value'] = starting_cash + \
    (83.79 - 83.81) * 2

pd.testing.assert_frame_equal(result, test_df8)


class TestBuyAndSellLmtIOC(BacktestEngine):
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
                'BUY', self.msft, 3, 83.81, 'IOC')
            self.place_order(lmt_order)

        self.counter += 1

        if self.counter == 7:
            lmt_order = self.create_limit_order(
                'SELL', self.msft, 2, 80, 'IOC')
            self.place_order(lmt_order)
            #print(self.msft.ask, self.msft.ask_size)


test_buy_and_sell_lmt_IOC = TestBuyAndSellLmtIOC()
result = test_buy_and_sell_lmt_IOC.run()

pd.testing.assert_frame_equal(result, test_df8)

