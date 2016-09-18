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
import numpy as np
import pandas as pd

APPROX_BDAYS_PER_MONTH = 21
APPROX_BDAYS_PER_YEAR = 252
MONTHS_PER_YEAR = 12
WEEKS_PER_YEAR = 52
TOTAL_SECONDS_IN_A_DAY = 24 * 60 * 60.
TOTAL_SECONDS_IN_A_YEAR = TOTAL_SECONDS_IN_A_DAY * 365.24

ANNUALIZATION_FACTORS = {'daily': APPROX_BDAYS_PER_YEAR,
                         'weekly': WEEKS_PER_YEAR,
                         'monthly': MONTHS_PER_YEAR}


def CAGR(beg_val, end_val, years, decimals=5):
    try:
        cagr = (np.power((end_val / beg_val), (1 / years))) - 1

        return cagr.round(decimals)

    except ZeroDivisionError:
        years = 1

        cagr = (np.power((end_val / beg_val), (1 / years))) - 1

        return cagr.round(decimals)


def sharpe_ratio(asset_returns, risk_free_rate=.05, period='daily',
                 decimals=3):

    excess_returns = np.mean(asset_returns - risk_free_rate)

    sigma_of_asset = np.std(asset_returns)

    sr = (excess_returns / sigma_of_asset) * \
        np.sqrt(ANNUALIZATION_FACTORS[period])

    return np.round(sr, decimals)


def rate_of_return(array):

    if isinstance(array, pd.DataFrame):

        if array.iloc[0] == 0:
            raise ZeroDivisionError

        return ((array.iloc[-1] - array.iloc[0]) / array.iloc[0]).item()

    if isinstance(array, pd.Series):

        if array.iloc[0] == 0:
            raise ZeroDivisionError

        return (array.iloc[-1] - array.iloc[0]) / array.iloc[0]

    else:
        if array[0] == 0:
            raise ZeroDivisionError

        return (array[-1] - array[0]) / array[0]


def alpha():
    pass


def sortino_ratio():
    pass


def information_ratio():
    pass


def VAR(returns, percentile=.05):

    percentile = percentile * 100

    returns = np.sort(returns)

    if isinstance(returns, np.ndarray):
        return np.round(np.percentile(returns, percentile), 2)

    else:
        return np.round(np.percentile(returns.values, percentile), 2)


def expected_shortfall():
    pass


def max_drawdown(array):

    dd = drawdowns(array)

    return dd[dd['Length'] == dd['Length'].max()]


def drawdowns(array, target='Value'):

    if not isinstance(array, pd.DataFrame):
        raise Exception('Array must be a pandas dataframe.')

    drawdown_down_times = []
    drawdown_up_times = []

    in_drawdown_period = False

    array = array.copy()
    array['Pct. Change'] = array[target].pct_change()

    if array['Pct. Change'].ix[1] < 0:
        drawdown_down_times.append(array['Pct. Change'].index[0])

        in_drawdown_period = True

    for i in range(1, len(array['Pct. Change'])):

        time = array['Pct. Change'].index[i - 1]

        if in_drawdown_period:

            if array['Pct. Change'][i] > 0:
                drawdown_up_times.append(time)

                in_drawdown_period = False

        elif not in_drawdown_period:

            if array['Pct. Change'][i] < 0:

                drawdown_down_times.append(time)

                in_drawdown_period = True

    if in_drawdown_period:
        drawdown_up_times.append(array['Pct. Change'].index[-1])

    drawdown_df = pd.DataFrame({'From': drawdown_down_times,
                                'To': drawdown_up_times})

    drawdown_df['Length'] = drawdown_df['To'] - drawdown_df['From']

    drawdown_df['DD'] = ((array[target].loc[drawdown_df['From']].values /
                          array[target].loc[drawdown_df['To']].values) - 1).round(5)

    drawdown_df['Cost'] = (array[target].loc[drawdown_df['To']].values -
                           array[target].loc[drawdown_df['From']].values).round(2)

    return drawdown_df


def plot_drawdowns(array, target='Value', figsize=(15, 5)):

    import matplotlib.pyplot as plt

    dd_array = array
    fig, ax = plt.subplots(1, figsize=figsize)

    ax.plot(dd_array[target], c='k')
    ax.set_title('Drawdowns')

    dd = drawdowns(dd_array, target)

    for _, row in dd.iterrows():
        ax.axvspan(row['From'], row['To'], alpha=.2)


def drawdown_summary(array):
    # max drawdown
    # average length
    # count of lengths
    pass


def volatility(array):
    return np.std(array)


def consecutive_wins():
    pass


def consecutive_losses():
    pass


def risk_adj_roc():
    pass


def beta(returns, market_returns):

    matrix = np.vstack((returns, market_returns))

    return np.cov(matrix)[0][1] / np.std(market_returns)


def profit_loss(returns):

    pass
