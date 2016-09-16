#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
from portfolio import Portfolio


def test(time0, ticker0, price0, shares0, commission0,
         time1, ticker1, price1, shares1, commission1):

    p = Portfolio()
    p.start_time = pd.Timestamp('2016-01-01')
    p.set_portfolio_cash(100000.00)

    p.postiions(time0, ticker0, price0, shares0)
    p.postiions(time1, ticker1, price1, shares1)

    test_df = pd.DataFrame({'Ticker': [ticker0, ticker1],
                            'Price': [price0, price1],
                            'Shares': [shares0, shares1],
                            'Commission': [commission0, commission1],
                            'Total': [price0 * shares0, price1 * shares1]},
                           index=[time0, time1])

    portfolio_df = p.transaction_log.drop('ID', axis=1)
    test_df = test_df[['Ticker', 'Price', 'Shares', 'Commission', 'Total']]

    return pd.util.testing.assert_frame_equal(portfolio_df, test_df)


test(pd.Timestamp('2016-01-01'), 'MSFT', 100., 100., 50.,
     pd.Timestamp('2016-01-02'), 'AAPL', 100., 100., 50.)

test(pd.Timestamp('2016-01-01'), 'MSFT', 100., 100., 50.,
     pd.Timestamp('2016-01-01'), 'AAPL', 100., 100., 50.)

test(pd.Timestamp('2016-01-01'), 'MSFT', 100., 100., 50.,
     pd.Timestamp('2016-01-01'), 'AAPL', 100., -100., 50.)

test(pd.Timestamp('2016-01-01'), 'MSFT', 100., -100., 50.,
     pd.Timestamp('2016-01-02'), 'MSFT', 100., 100., 50.)


test(pd.Timestamp('2016-01-01'), 'MSFT', 100., -100., 50.,
     pd.Timestamp('2016-01-02'), 'MSFT', 100., -100., 50.)

