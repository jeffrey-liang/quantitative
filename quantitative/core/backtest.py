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
        pass

    def get_close(self, ticker):

        if self.use_adjusted_close:

            return self.data[ticker].loc[self.time]['Adj Close'].item()
        else:

            return self.data[ticker].loc[self.time]['Close'].item()

    def get_open(self, ticker):
        return self.data[ticker].loc[self.time]['Open'].item()

    def get_high(self, ticker):
        return self.data[ticker].loc[self.time]['High'].item()

    def get_low(self, ticker):
        return self.data[ticker].loc[self.time]['Low'].item()

    def get_volume(self, ticker):
        return self.data[ticker].loc[self.time]['Volume'].item()

    def get_time(self):
        return self.time

    def get_historical_data(self, ticker, start_time=None,
                            end_time=None, kind=None):

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
        security_close_price = self.data[ticker]['Close'].loc[self.time]

        self.postiions(self.time, ticker, security_close_price, shares)

        if self.verbose:
            self.print_order(self.time, 'CLOSE', ticker, security_close_price,
                             shares, security_close_price * shares)

    def order_on_next_open(self, ticker, shares):

        security_open_price = self.data[ticker]['Open'].loc[self.next_time]

        self.postiions(self.next_time, ticker, security_open_price, shares)

        if self.verbose:
            self.print_order(self.next_time, 'OPEN', ticker,
                             security_open_price, shares,
                             security_open_price * shares)

    def get_data(self, data_feed):
        """
        - Data must be ordered from earlist date to latest date.
        - Also assuming the data all start on the same date and
        end on the same date.
        - index is datetime object
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

        self.cash.index = [time]
        self.portfolio_value.index = [time]

    def run(self, data_feed):

        # if len(self.securities) != len(data_feed):
        #    raise Exception('List of securities not the same as data inputs.')

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
