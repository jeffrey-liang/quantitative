#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import abc
from collections import namedtuple


class Portfolio(metaclass=abc.ABCMeta):

    def __init__(self):
        ''' Cash Attributes'''
        self.cash_in_account = {}

        self.cash_ledger = namedtuple('cash_ledger', ['time', 'cash'])

        '''Portfolio Value Attributes'''
        self.portfolio_value = {}

        self.current_portfolio_value = namedtuple('current_portfolio_value',
                                                  ['cash', 'investment_value',
                                                      'portfolio_value'])

        '''Transaction Log Attributes'''
        self.transaction_log = {}

        self.market_transaction = namedtuple('market_transaction',
                                             ['time', 'ticker',
                                              'price', 'shares', 'direction',
                                              'commission', 'sequence'])

        self.cash_transaction = namedtuple('cash_transaction',
                                           ['time', 'cash'])

        '''Open Positions Attributes'''
        self.open_positions = {}

        self.security_position = namedtuple('security_position',
                                            ['time', 'ticker', 'market_price',
                                                'shares', 'purchase_price',
                                                'purchase_time'])
        '''Holdings'''
        self.securities_in_universe = []
        self.holdings = {}

        ''' Security Sequence Attributes '''
        self.security_sequences = {}
        self.security_sequences_id = -1

        ''' User Settings '''
        self.initial_margin_requirement = 0.5
        self.maintenance_margin_requirement = 0.3
        self.reg_T_minimum_deposit = 2000

        self.broker = 'ib'
        self.include_commission = True

    ''' Cash in Account Methods '''

    def get_cash(self, time):
        '''
        Returns cash value at specific time.

        Parameters:
        ----------
        time: pd.Timestamp
            Time.

        Returns:
        -------
        self.cash_in_account[time].cash: float
            The cash value.
        '''
        assert(type(time) == pd.Timestamp)
        return self.cash_in_account[time].cash

    def modify_cash(self, time, amount):
        '''
        Overrides the cash value at specific time.

        Parameters:
        ----------
        time: pd.Timestamp
            Time.

        amount: float
            The new cash amount at the time.
        '''

        assert(type(time) == pd.Timestamp)
        ledger = self.cash_ledger(time, amount)
        self.cash_in_account[time] = ledger

    ''' Portfolio Value Methods '''

    def get_porfolio_value(self, time):
        assert(type(time) == pd.Timestamp)
        assert(self.portfolio_value[time].cash + self.portfolio_value[time].investment_value
               == self.portfolio_value[time].portfolio_value)
        return self.portfolio_value[time].portfolio_value

    def update_portfolio_values(self, time):
        assert(type(time) == pd.Timestamp)
        cash = self.get_cash(time)
        investment_total = self.calculate_investment_total(time)

        portfolio_val = cash + investment_total

        ledger = self.current_portfolio_value(
            cash, investment_total, portfolio_val)

        self.portfolio_value[time] = ledger

    ''' Holdings Modification Methods'''

    def update_portfolio_holdings(self, time):

        self.holdings.clear()
        total_investment_value = self.calculate_investment_total(time)

        for ticker, ledger in self.open_positions.items():
            self.holdings[ticker] = ((ledger.market_price * ledger.shares)
                                     / total_investment_value)

    '''Transaction Log Methods '''

    def add_transaction(self, time, **kwargs):

        assert(type(time) == pd.Timestamp)
        if time in self.transaction_log.keys():

            if 'cash' in kwargs.keys():
                kwargs['time'] = time

                self.transaction_log[time].append(
                    self.cash_transaction(**kwargs))

            else:
                ticker = kwargs['ticker']
                sequence = self.generate_sequence_for_transaction(ticker)

                kwargs['time'] = time
                kwargs['sequence'] = sequence

                ledger = self.market_transaction(**kwargs)

                self.transaction_log[time].append(ledger)

        else:
            if 'cash' in kwargs.keys():
                kwargs['time'] = time

                self.transaction_log[time] = [
                    self.cash_transaction(**kwargs)]

            else:
                ticker = kwargs['ticker']
                sequence = self.generate_sequence_for_transaction(ticker)

                kwargs['time'] = time
                kwargs['sequence'] = sequence

                ledger = self.market_transaction(**kwargs)

                self.transaction_log[time] = [ledger]

    def remove_transaction(self):
        pass

    def get_transaction(self, time):

        assert(type(time) == pd.Timestamp)
        transaction = self.transaction_log[time]

        if len(transaction) == 1:
            return transaction[0]

        else:
            return transaction

    def generate_sequence_for_transaction(self, ticker):

        if ticker in self.security_sequences.keys():
            return self.security_sequences[ticker]

        else:
            self.security_sequences_id += 1
            self.security_sequences[ticker] = self.security_sequences_id
            return self.security_sequences_id

    '''Open Position Methods '''

    def add_position(self, time, ticker, price, shares):

        assert(type(time) == pd.Timestamp)
        ledger = self.security_position(
            time, ticker, price, shares, price, time)
        self.open_positions[ticker] = ledger

    def modify_position(self, ticker, **kwargs):

        if 'time' in kwargs:
            assert(type(kwargs['time']) == pd.Timestamp)

        current_security_position = self.open_positions[ticker]
        new_position = current_security_position._replace(**kwargs)
        self.open_positions[ticker] = new_position

    def remove_position(self, ticker):

        del self.open_positions[ticker]

    def calculate_investment_total(self, time):

        total = 0
        for ticker, ledger in self.open_positions.items():
            assert(time == ledger.time)
            total += ledger.market_price * ledger.shares

        return total
