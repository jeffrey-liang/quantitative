#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
from portfolio import Portfolio


def test(price0, shares0, price1, shares1, cash0, cash1):
    p = Portfolio()
    p.start_time = pd.Timestamp('2016-01-01')
    p.set_portfolio_cash(100000.00)

    p.postiions(pd.Timestamp('2016-01-02'), 'AAPL', price0, shares0)
    p.postiions(pd.Timestamp('2016-01-03'), 'AAPL', price1, shares1)

    correct_cash = pd.DataFrame({'Amount': [100000.0, cash0, cash1]},
                                index=[pd.Timestamp('2016-01-01'),
                                       pd.Timestamp('2016-01-02'),
                                       pd.Timestamp('2016-01-03')])

    pd.util.testing.assert_frame_equal(correct_cash, p.get_cash(show_all=True))


test(100, 100, 110, -100, 89950., 100895.)
test(100, 100, 90, -100, 89950., 98905.)
test(100, 100, 100, 100, 89950., 79900.)
test(100, -100, 100, -100, 109950., 119900.)
test(100, -100, 90, 100, 109950., 100905.)
test(100, -100, 110, 100, 109950., 98895.)
test(100, 100, 100, -100, 89950., 99900.)
