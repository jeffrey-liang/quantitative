#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2016 Jeffrey Liang

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from .portfolio import Portfolio
from .performance import Performance
import abc
import datetime as dt
import numpy as np


class Backtest(Portfolio, Performance, metaclass=abc.ABCMeta):
    """
    Base class of the backtest engine. Inherit this class to gain access to the
    backtest engine.
    """

    def __init__(self):

        super().__init__()

        self.start_time = 0
        self.end_time = 0
        self.time = 0
        self.next_time = 0
        self.custom_start_time = 0
        self.custom_end_time = 0
        self.data = {}
        self.securities = []
        self.use_adjusted_close = False
        self.verbose = False
        self.vectorize = False

    @abc.abstractclassmethod
    def trade_logic(self):
        """
        User must create a function named trade logic. This is where user
        implements their trading strategy.
        """
        pass

    def get_close(self, ticker):
        """
        Get the close of a security at the backtest time.

        Parameters:
        -----------
        ticker: str
                The security ticker name.

        Returns:
        --------
        float
                The current close price of the security.
        """

        if self.use_adjusted_close:

            return self.data[ticker].loc[self.time]['Adj Close'].item()
        else:

            return self.data[ticker].loc[self.time]['Close'].item()

    def get_open(self, ticker):
        """
        Get the open of a security at the backtest time.

        Parameters:
        -----------
        ticker: str
                The security ticker name.

        Returns:
        --------
        float
                The current open price of the security.
        """
        return self.data[ticker].loc[self.time]['Open'].item()

    def get_high(self, ticker):
        """
        Get the hight price of a security at the backtest time.

        Parameters:
        -----------
        ticker: str
                The security ticker name.

        Returns:
        --------
        float
                The current high price of the security.
        """
        return self.data[ticker].loc[self.time]['High'].item()

    def get_low(self, ticker):
        """
        Get the low price of a security at the backtest time.

        Parameters:
        -----------
        ticker: str
                The security ticker name.

        Returns:
        --------
        float
                The current low price of the security.
        """
        return self.data[ticker].loc[self.time]['Low'].item()

    def get_volume(self, ticker):
        """
        Get the volume of a security at the backtest time.

        Parameters:
        -----------
        ticker: str
                The security ticker name.

        Returns:
        --------
        float
                The current volume of the security.
        """
        return self.data[ticker].loc[self.time]['Volume'].item()

    def get_time(self):
        """
        Get the backtest time.

        Parameters:
        -----------
        None

        Returns:
        --------
        numpy.datetime64
                The backtest time.
        """
        return self.time

    def get_historical_data(self, ticker, start_time=None,
                            end_time=None, kind=None):
        """
        Get the historical data of a security up to the current backtest time.
        Parameters
        ----------
        ticker: str
                The security of the historical data requests.
        start_time: numpy.datetime64, optional
                The  start time of the historical data request.
        end_time: numpy.datetime64, optional
                The end time of the historical data request.
        kind: str
                The kind requested. i.e. 'Close', 'Open', 'High', 'Low',
                'Volume'.

        Returns
        -------
        data: pandas.core.frame.DataFrame
            Price and volume data.
        """

        if start_time is None and end_time is None:

            if kind is None:

                return self.data[ticker].loc[self.start_time: self.time]

            elif kind is not None:

                return self.data[ticker][kind].loc[
                    self.start_time: self.time]

        elif start_time is None and end_time is not None:

            if end_time > self.time:
                raise Exception(
                    'end_time cannot be later than current system time.')

            if kind is None:

                return self.data[ticker].loc[self.start_time: end_time]

            elif kind is not None:

                return self.data[ticker][kind].loc[
                    self.start_time: end_time]

        elif start_time is not None and end_time is None:

            if start_time > self.time:

                raise Exception(
                    'start_time cannot be later than current system time')

            if kind is None:

                return self.data[ticker].loc[start_time: self.end_time]

            elif kind is not None:

                return self.data[ticker][kind].loc[
                    start_time: self.end_time]

        elif start_time is not None and end_time is not None:

            if kind is None:

                return self.data[ticker].loc[start_time: end_time]

            elif kind is not None:

                return self.data[ticker][kind].loc[
                    start_time: end_time]

    def order_on_close(self, ticker, shares):
        """
        Invoke an order on the ticker's current close price. To buy on
        close, shares are positive (e.g. 10), to sell, shares are negative
        (e.g. -10).

        Parameters
        ----------
        ticker: str
                The security ticker name.
        shares: int
                The number of shares to purchase.

        Returns
        -------
        None

        Examples
        --------

        def trade_logic(self):
            if self.get_close('SPY') > 100:
                self.order_on_close('SPY', 10)

        def trade_logic(self):
            self.order_on_close('SPY', -10)
        """
        security_close_price = self.data[ticker]['Close'].loc[self.time]

        self.postiions(self.time, ticker, security_close_price, shares)

        if self.verbose:
            self.print_order(self.time, 'CLOSE', ticker, security_close_price,
                             shares, security_close_price * shares)

    def order_on_next_open(self, ticker, shares):
        """
        Invoke an order on the ticker's next open price. To buy on
        next open, shares are positive (e.g. 10), to sell, shares are negative
        (e.g. -10).

        Parameters
        ----------
        ticker: str
                The security ticker name.
        shares: int
                The number of shares to purchase.

        Returns
        -------
        None

        Examples
        --------

        def trade_logic(self):
            if self.get_open('SPY') > 100:
                self.order_on_open('SPY', 10)

        def trade_logic(self):
            self.order_on_open('SPY', -10)
        """
        security_open_price = self.data[ticker]['Open'].loc[self.next_time]

        self.postiions(self.next_time, ticker, security_open_price, shares)

        if self.verbose:
            self.print_order(self.next_time, 'OPEN', ticker,
                             security_open_price, shares,
                             security_open_price * shares)

    def get_data(self, data_feed):
        """
        Retrieve the data from user. User should not directly interact with
        this method. User loads data from .run()

        Parameters:
        -----------
        data_feed: dict
            The data must be in a dictionary structure with keys as the
            security name, and values as pandas.dataframe.

            The index of the data should be pandas.tseries.index.DatetimeIndex,
            and the indexes must match for more than one data file provided.

        Returns:
        --------
        None

        Example:
        --------
        import quantitative as qe
        import pandas as pd

        spy = pd.read_csv('spy.csv', parse_dates=True, index_col=0)
        bac = pd.read_csv('bac.csv', parse_dates=True, index_col=0)

        data = {'SPY': spy, 'BAC': bac}


        class MyStrategy(qe.Backtest):
            ....

        my_strat = MyStrategy()
        my_strat.run(data) # load data into .run()

        Notes:
        ------
        See run() method.
        """

        if isinstance(data_feed, dict):

            self.data = data_feed

            for security in list(data_feed.keys()):

                self.securities.append(security)

                # round decimals
                self.data[security] = self.data[security].round(2)

        else:
            raise Exception('Data not as dictionary.')

        self.check_if_index_is_chronological()

        first_sec_index = self.data[self.securities[0]].index

        for sec in self.securities:
            if np.array_equal(first_sec_index, self.data[sec].index):
                pass

            else:
                raise Exception('Indexes do not match for {} and {}'.format(
                    self.securities[0], sec))

    def set_times(self, start_time, end_time):
        """
        Set the 'global' times for the backtest and portfolio.

        Parameters:
        -----------
        start_time: pandas.tslib.Timestamp
            Start time of backtest.
        end_time: pandas.tslib.Timestamp
            End time of the backtest.

        Returns:
        --------
        None
        """
        if self.custom_start_time == 0 and self.custom_end_time == 0:
            self.start_time = start_time
            self.end_time = end_time

        elif self.custom_start_time != 0 and self.custom_end_time == 0:

            self.start_time = self.custom_start_time
            self.end_time = self.end_time

        elif self.custom_start_time == 0 and self.custom_end_time != 0:
            self.start_time = start_time
            self.end_time = self.custom_end_time

    def check_if_index_is_chronological(self):
        """
        Check if data is chronological, if false, format data to be
        chronological.
        """
        for security in self.securities:

            if self.data[security].index[0] > self.data[security].index[-1]:
                self.data[security] = self.data[security].iloc[::-1]

    def print_order(self, time, type_, ticker, price, shares, total):
        msg = '[{}] SIGNAL on {} {} @ ${}, {} share(s) Total: {}'
        print(msg.format(time, type_, ticker, price, shares, total))

    def print_simulation_start(self, t0, start_time, end_time):
        print(t0)
        print('Simulating between {} to {}'.format(start_time, end_time))
        print('Simulation started...')

    def print_simulation_end(self, t0, t1):
        print('Simulation successful. Finished in: {}'.format(t1 - t0))

    def set_cash_portfolio_times(self, time):
        """
        Set the time of the first entry in the portfolio cash, and value.
        User should not directly use this method.
        Parameters:
        -----------
        time: pandas.tslib.Timestamp
            The start time of the backtest.

        Returns:
        --------
        None
        """
        self.cash.index = [time]
        self.portfolio_value.index = [time]

    def run(self, data_feed):
        """
        Call this method to start the backtest.

        Parameters:
        -----------
        data_feed: dict
            The data feed used in the backtest.

        Returns:
        --------
        None

        Examples:
        ---------
        import quantitative as qe
        import pandas as pd

        # get the data
        spy = pd.read_csv('spy.csv', parse_dates=True, index_col=0)
        bac = pd.read_csv('bac.csv', parse_dates=True, index_col=0)

        data = {'SPY': spy, 'BAC': bac}

        class MyStrategy(qe.Backtest):

            def __init__(self):
                super().__init__():

                self.set_portfolio_cash = 10,000

            def trade_logic(self):
                ...

        my_strat = MyStrategy
        my_strat.run(data)
        """

        self.get_data(data_feed)

        self.set_times(self.data[self.securities[0]].index[0],
                       self.data[self.securities[0]].index[-1])

        self.set_cash_portfolio_times(self.start_time)

        timeline = np.array(
            self.data[self.securities[0]].index.to_pydatetime(),
            dtype=np.datetime64)

        t0 = dt.datetime.now()

        self.print_simulation_start(t0, self.start_time, self.end_time)

        for index in range(len(timeline)):
            self.time = timeline[index]

            try:
                self.next_time = timeline[index + 1]

            except IndexError:
                pass

            self.trade_logic()

        t1 = dt.datetime.now()

        self.ending_cash = self.get_cash()
        self.simulation_completed = True

        self.print_simulation_end(t0, t1)
