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
import pandas as pd
import numpy as np
import uuid


class Portfolio(object):

    def __init__(self):

        self.cash = 0
        self.open_positions = pd.DataFrame(columns=['Price', 'Shares',
                                                    'Total'])
        self.short_positions = pd.DataFrame(columns=['Price', 'Shares',
                                                     'Total'])
        self.portfolio_value = 0
        self.start_time = 0
        self.end_time = 0
        self.beginning_cash = 0
        self.ending_cash = 0
        self.total_margin_requirement_percentage = 1.25
        self.broker = 'ib'

        self.transaction_log = pd.DataFrame(columns=['Ticker', 'Price',
                                                     'Shares', 'Commission',
                                                     'Total', 'ID'])
        self.ticker_ids = {}
        self.include_commission = True
        self.asset_weights = {}
        self.simulation_completed = False

    def get_portfolio_value(self, show_all=True, freq='B'):

        if self.simulation_completed:

            # check if there is a value at the end, if not, add the last value
            # to the last time so we can resample and ffill
            if self.portfolio_value.index[-1] != self.end_time:
                self.portfolio_value.loc[
                    self.end_time] = self.portfolio_value['Value'][-1]

            self.portfolio_value = self.portfolio_value.resample(freq).ffill()
            if show_all:
                return self.portfolio_value

            else:
                return self.portfolio_value.iloc[-1]
        else:

            if show_all:
                return self.portfolio_value

            else:
                return self.portfolio_value.iloc[-1]

    def get_cash(self, show_all=False, freq='B'):

        if self.simulation_completed:

            if self.cash.index[-1] != self.end_time:
                self.cash.loc[self.end_time] = self.cash['Amount'][-1]

        self.cash = self.cash.resample(freq).ffill()

        if show_all:
            return np.round(self.cash, 2)

        else:
            return np.round(self.cash['Amount'][-1], 2)

    def modify_cash(self, amount, time):

        self.cash.loc[time] = self.cash.iloc[-1] + amount

    def modify_portfolio_value(self, time):
        self.portfolio_value.loc[time] = (
            self.get_cash() + self.open_positions['Total'].sum())

    def get_shares(self, ticker):

        try:
            return self.open_positions.loc[ticker]['Shares']

        except KeyError:
            raise Exception('Ticker: {} not in portfolio.'.format(ticker))

    def set_portfolio_cash(self, amount):
        '''User function'''
        self.cash = pd.DataFrame({'Amount': [amount]},
                                 index=[0])

        self.portfolio_value = pd.DataFrame({'Value': [amount]}, index=[0])

        self.beginning_cash = amount

    def add_cash(self, amount):
        """User function"""
        self.modify_cash(amount, self.system_time)

    def get_transactions_at(self, time):

        if isinstance(time, pd.Timestamp):
            return self.transaction_log.loc[time]

        else:
            raise Exception('Time not as datetime object.')

    def get_transaction_log(self):
        return self.transaction_log.drop(['ID'], axis=1)

    def calculate_asset_weights(self):

        total = self.open_positions['Total'].sum()

        for sec in self.open_positions.index:
            self.asset_weights[sec] = (self.open_positions.loc[
                                       sec]['Total'] / total)

    def get_asset_weights(self):
        self.calculate_asset_weights()

        return self.asset_weights

    def get_open_positions(self):
        return self.open_positions

    def get_portfolio_returns(self, log=True):

        if log:
            return np.log(self.portfolio_value / self.portfolio_value.shift(1))

        else:
            return self.portfolio_value.pct_change()

    def postiions(self, time, ticker, price, shares):
        '''Enter and exit trades'''
        if shares > 0:

            self.check_cash_condition(price, shares)

            contract_cost, commission = self.calculate_cost(price, shares)

            if ticker not in self.open_positions.index:
                ''' Entering long position, no shares in portfolio'''

                self.modify_cash(-(contract_cost + commission), time)

                self.add_to_transaction_log(time, ticker, price, shares,
                                            commission)

                self.open_positions.loc[
                    ticker] = price, shares, (price * shares)

                self.modify_portfolio_value(time)

            elif ticker in self.open_positions.index:

                if (shares + self.open_positions.loc[ticker]['Shares'] > 0):
                    ''' Add to existing position'''

                    self.modify_cash(-(contract_cost + commission), time)

                    self.add_to_transaction_log(time, ticker, price, shares,
                                                commission)

                    security_price = self.open_positions.loc[ticker]['Price']

                    price = (security_price + price) / 2.
                    shares = self.open_positions.loc[ticker]['Shares'] + shares
                    total = price * shares

                    self.open_positions.loc[ticker] = price, shares, total

                    self.modify_portfolio_value(time)

                elif (shares + self.open_positions.loc[ticker]['Shares'] == 0):
                    ''' exit short position'''

                    self.modify_cash(-(contract_cost + commission), time)

                    self.add_to_transaction_log(time, ticker, price, shares,
                                                commission)

                    self.remove_transaction_id(ticker)

                    self.open_positions = self.open_positions.drop(ticker)
                    self.short_positions = self.short_positions.drop(ticker)
                    self.modify_portfolio_value(time)

                elif (self.open_positions.loc[ticker]['Shares'] + shares > 0):
                    '''Short to long position'''
                    long_shares = (self.open_positions.loc[ticker]['Shares'] +
                                   shares)
                    portfolio_shares = self.open_positions.loc[
                        ticker]['Shares']

                    self.modify_cash(-(contract_cost + commission), time)

                    self.add_to_transaction_log(time, ticker, price, shares,
                                                commission)

                    self.short_positions = self.short_positions.drop(ticker)

                    total = price * long_shares

                    self.open_positions.loc[ticker] = price, long_shares, total
                    self.modify_portfolio_value(time)

                elif (self.open_positions.loc[ticker]['Shares'] + shares < 0):
                    '''reducing short position'''

                    self.modify_cash(-(contract_cost + commission), time)

                    self.add_to_transaction_log(time, ticker, price, shares,
                                                commission)

                    portfolio_price = self.open_positions.loc[ticker]['Price']
                    portfolio_shares = (self.open_positions.loc[
                                        ticker]['Shares'] + shares)
                    total = portfolio_price * portfolio_shares

                    self.open_positions.loc[
                        ticker] = portfolio_price, portfolio_shares, total

                    self.short_positions.loc[ticker]['Shares'] += shares
                    self.short_positions.loc[ticker][
                        'Total'] = self.open_positions.loc[ticker]['Total']
                    self.modify_portfolio_value(time)

        elif shares < 0:

            self.check_cash_condition(price, shares)

            contract_cost, commission = self.calculate_cost(price, shares)

            if ticker not in self.open_positions.index:
                '''Shorting position'''

                self.open_positions.loc[
                    ticker] = price, shares, (price * shares)

                self.modify_cash((contract_cost - commission), time)

                self.add_to_transaction_log(time, ticker, price, shares,
                                            commission)

                '''Add to short sell position ledger'''

                self.short_positions.loc[
                    ticker] = price, shares, (price * shares)
                self.modify_portfolio_value(time)

            elif ticker in self.open_positions.index:

                if (shares + self.open_positions.loc[ticker]['Shares'] == 0):
                    '''Exit  position'''

                    self.modify_cash((contract_cost - commission), time)

                    self.add_to_transaction_log(time, ticker, price, shares,
                                                commission)

                    self.remove_transaction_id(ticker)

                    self.open_positions = self.open_positions.drop(ticker)
                    self.modify_portfolio_value(time)

                elif (shares + self.open_positions.loc[ticker]['Shares'] > 0):
                    ''' off loading some shares, still long'''

                    self.modify_cash(-(contract_cost + commission), time)
                    self.add_to_transaction_log(time, ticker, price, shares,
                                                commission)

                    shares = self.open_positions.loc[ticker]['Shares'] + shares
                    self.open_positions.loc[
                        ticker] = price, shares, (shares * price)
                    self.modify_portfolio_value(time)

                elif (shares + self.open_positions.loc[ticker]['Shares'] < 0):
                    ''' Long to short position or add to short position'''

                    portfolio_shares = self.open_positions.loc[
                        ticker]['Shares']

                    shorted_shares = portfolio_shares + shares

                    self.modify_cash((contract_cost - commission), time)
                    self.add_to_transaction_log(time, ticker, price, shares,
                                                commission)

                    avg_price = ((self.open_positions.loc[
                                 ticker]['Price'] + price) / 2.)

                    shares = self.open_positions.loc[ticker]['Shares'] + shares

                    self.open_positions.loc[
                        ticker] = avg_price, shares, (avg_price * shares)

                    '''Add to short sell position ledger'''

                    self.short_positions.loc[
                        ticker] = price, shorted_shares, (price *
                                                          shorted_shares)
                    self.modify_portfolio_value(time)

    def check_cash_condition(self, price, shares):
        """ Check if enough cash in account"""
        contract_total = price * shares

        if shares >= 0:
            if self.get_cash() < contract_total:
                raise Exception('Not enough cash in portfolio.')

        elif shares < 0:
            total_margin_requirement = (
                self.total_margin_requirement_percentage *
                np.abs(contract_total))

            if self.get_cash() < total_margin_requirement:
                msg = (
                    'Trade does not meet total margin requirements. '
                    'Total margin required: {}, Cash in portfolio: {}'.format(
                        np.abs(total_margin_requirement), self.get_cash())
                )
                raise Exception(msg)

        return True

    def check_if_time_exist(self, time):

        if time in self.transaction_log.index:
            return True

        else:
            return False

    def calculate_cost(self, price, shares):
        '''Calculate cost of transaction '''

        contract_cost = np.abs(price * shares)

        commission = self.calculate_commission(
            self.broker, price, np.abs(shares))

        return contract_cost, commission

    def calculate_commission(self, broker, price, shares):
        '''
        Interactive brokers (CA) commission schedule.

        0.01 CAD per share
        Minimum per order is 1.00 CAD
        Maximum per order is 0.5% of trade value.
        '''
        if self.include_commission:

            COST_PER_SHARE = 0.01
            MIN_PER_ORDER_COST = 1.
            MAX_PER_ORDER_PERCENTAGE = 0.005

            interactive_brokers = ['interactive brokers', 'interactive', 'ib']

            if broker.lower() in interactive_brokers:
                trade_value = price * shares
                commission = trade_value * COST_PER_SHARE

                if commission <= MIN_PER_ORDER_COST:
                    return MIN_PER_ORDER_COST

                elif commission >= (trade_value * MAX_PER_ORDER_PERCENTAGE):
                    return trade_value * MAX_PER_ORDER_PERCENTAGE

                else:
                    return commission

            else:
                raise Exception(
                    'The broker \'{}\' is unavailable.'.format(self.broker))

        else:
            return 0

    def add_to_transaction_log(self, time, ticker, price, shares, commission):

        trans_id = self.generate_transaction_id(ticker)
        total = price * shares

        if self.check_if_time_exist(time) is False:
            self.transaction_log.loc[
                time] = ticker, price, shares, commission, total, trans_id

        elif self.check_if_time_exist(time):

            info = pd.DataFrame({'Ticker': [ticker],
                                 'Price': [price],
                                 'Shares': [shares],
                                 'Commission': [commission],
                                 'Total': [total],
                                 'ID': [trans_id]}, index=[time])

            self.transaction_log = self.transaction_log.append(info)[
                ['Ticker', 'Price', 'Shares', 'Commission', 'Total', 'ID']]

    def generate_transaction_id(self, ticker):

        if ticker not in self.ticker_ids:
            self.ticker_ids[ticker] = uuid.uuid4()

            return self.ticker_ids[ticker]

        elif ticker in self.ticker_ids:

            return self.ticker_ids[ticker]

    def remove_transaction_id(self, ticker):

        del self.ticker_ids[ticker]
