#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
    cagr = (np.power((end_val / beg_val), (1 / years))) - 1

    return cagr.round(decimals)


def sharpe_ratio(asset_returns, risk_free_rate=.05, period='daily'):

    excess_returns = np.mean(asset_returns - risk_free_rate)

    sigma_of_asset = np.std(asset_returns)

    sr = (excess_returns / sigma_of_asset) * \
        np.sqrt(ANNUALIZATION_FACTORS[period])

    return sr


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

    dd_array = array.copy()

    # convert data into pct. change
    dd_array['Pct. Change'] = dd_array[target].pct_change()

    # since first row is NaN, if the second row is downwards,
    # set replace NaN with 0.
    if dd_array['Pct. Change'].ix[1] < 0:
        dd_array['Pct. Change'].ix[0] = 0

    t0_dd = []
    t1_dd = []

    for i in range(len(dd_array['Pct. Change'])):

        time = dd_array['Pct. Change'].index[i]

        try:

            if (dd_array['Pct. Change'][i] > 0 and
                    dd_array['Pct. Change'][i + 1] < 0):
                t0_dd.append(time)

            if (dd_array['Pct. Change'][i] == 0 and
                    dd_array['Pct. Change'][i + 1] < 0):
                t0_dd.append(time)

            if (dd_array['Pct. Change'][i] < 0 and
                    dd_array['Pct. Change'][i + 1] > 0):
                t1_dd.append(time)

            if (dd_array['Pct. Change'][i] == 0 and
                    dd_array['Pct. Change'][i + 1] > 0):
                t1_dd.append(time)

        except IndexError:
            pass

    # if uneven list, the last drawdown does not go up
    # when data ends, "assume" end of data is end of drawdown
    # to continue drawdown
    if len(t0_dd) != len(t1_dd):
        t1_dd.append(dd_array['Pct. Change'].index[-1])

    dd = pd.DataFrame({'From': t0_dd,
                       'To': t1_dd})

    dd['Length'] = dd['To'] - dd['From']
    dd['DD'] = np.round((dd_array[target].loc[dd['From']].values /
                         dd_array[target].loc[dd['To']].values) - 1, 2)

    dd['Cost'] = (dd_array[target].loc[dd['To']].values -
                  dd_array[target].loc[dd['From']].values)
    return dd


def plot_drawdown(array, target='Value', figsize=(15, 5)):

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
