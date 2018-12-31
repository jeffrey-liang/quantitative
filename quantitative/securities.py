#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd


class Security(object):
    '''
    Container for security information.
    '''

    __slots__ = ['ticker', 'time', 'bid', 'ask', 'bid_size', 'ask_size',
                 'last_sale_time', 'last_sale_size', 'last_sale_price',
                 '_history']

    def __init__(self, ticker, time=None, bid=np.nan, ask=np.nan,
                 bid_size=np.nan, ask_size=np.nan, last_sale_time=None,
                 last_sale_price=np.nan, last_sale_size=np.nan):

        self.ticker = ticker

        self.time = time
        self.bid = bid
        self.ask = ask
        self.bid_size = bid_size
        self.ask_size = ask_size

        self.last_sale_time = last_sale_time
        self.last_sale_price = last_sale_price
        self.last_sale_size = last_sale_size

        self._history = None

    def __repr__(self):

        if self.time is not None:
            message = 'Security({}, {}, {}, {}, {}, {})'
            return message.format(self.ticker, self.time, self.bid, self.ask,
                                  self.bid_size, self.ask_size)
        else:
            return 'Security({})'.format(self.ticker)

    def __str__(self):
        if self.time is not None:
            message = '[Security] {}, {}'
            return message.format(self.ticker, self.time)
        else:
            return '[Security] {}'.format(self.ticker)

    def summary(self):
        summary = pd.Series([self.time, self.ticker, self.bid,
                             self.ask, self.bid_size, self.ask_size,
                             self.last_sale_time, self.last_sale_price,
                             self.last_sale_size],
                            index=['Time', 'Ticker', 'Bid', 'Ask',
                                   'Bid Size', 'Ask Size', 'Last Sale Time',
                                   'Last Sale Price', 'Last Sale Size'])
        return summary
