#!/usr/bin/env python
# -*- coding: utf-8 -*-
pmport numpy as np
import pandas as pd
import quantitative as qe


class Test_Buy_Sell(qe.Backtest):

    def __init__(self):

        super().__init__()

        self.set_portfolio_cash(10000)

    def trade_logic(self):

        if self.time == np.datetime64('2015-09-02'):

            self.order_on_close('SPY', 10)

        if self.time == np.datetime64('2015-09-10'):
            self.order_on_close('SPY', -10)


spy = pd.read_csv('test_data_files/spy_test.csv', parse_dates=True,
                  index_col=0)

data = {'SPY': spy}

Test = Test_Buy_Sell()
Test.run(data)

# print(Test.get_portfolio_value())


def test_portfolio_value():
    pv = pd.DataFrame({'Value': np.zeros(11)},
                      index=pd.date_range(start='2015-09-02', end='2015-09-16',
                                          freq='B'))
    pv.loc['2015-09-02':'2015-09-09'] = 9990.23
    pv.loc['2015-09-10': '2015-09-16'] = 9984.84

    pd.util.testing.assert_frame_equal(Test.get_portfolio_value(), pv)

test_portfolio_value()