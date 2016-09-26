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
from .metrics import (CAGR, sharpe_ratio, drawdowns, volatility, max_drawdown)
from dateutil.relativedelta import relativedelta
import pandas as pd


class Performance(object):

    def __init__(self):
        super().__init__()

    def CAGR(self, decimals=5):
        return CAGR(self.beginning_cash, self.ending_cash,
                    relativedelta(self.end_time, self.start_time).years,
                    decimals)

    def sharpe_ratio(self, risk_free_rate=.05, period='daily', decimals=3):
        return sharpe_ratio(self.portfolio_value.pct_change().dropna().values,
                            decimals=decimals)

    def wins(self):

        tl = self.transaction_log.groupby(['ID', 'Ticker']).sum()

        return tl[tl['Total'] >= 0].shape[0]

    def losses(self):
        tl = self.transaction_log.groupby(['ID', 'Ticker']).sum()

        return tl[tl['Total'] < 0].shape[0]

    def total_completed_trades(self):
        tl = self.transaction_log.groupby(['ID', 'Ticker']).sum()

        return tl.shape[0]

    def win_percentage(self):
        return self.wins() / self.total_completed_trades()

    def largest_profit(self):
        tl = self.transaction_log.groupby(['ID', 'Ticker']).sum()

        return tl['Total'].max()

    def largest_loss(self):
        tl = self.transaction_log.groupby(['ID', 'Ticker']).sum()

        return tl['Total'].min()

    def drawdowns(self, target='Value'):
        return drawdowns(self.get_portfolio_value(),
                         target=target)

    def max_drawdown(self, target='Value'):

        return max_drawdown(self.get_portfolio_value())

    def volatility(self):
        return volatility(self.get_portfolio_value())

    def profit_loss(self):
        tl = self.transaction_log.copy()
        tl = tl.groupby(['ID', 'Ticker']).sum()

        tl.index = tl.index.droplevel(level=0)
        return tl['Total']

    def summary(self):

        summary = pd.Series([self.CAGR(),
                             self.sharpe_ratio(),
                             self.win_percentage(),
                             self.max_drawdown()['DD'].values[0],
                             self.volatility()['Value']],

                            index=['CAGR',
                                   'Sharpe Ratio',
                                   'Win Pct.',
                                   'Max Drawdown',
                                   'Volatility'])

        return summary.round(5)
