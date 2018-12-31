#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from scipy import stats

APPROX_BDAYS_PER_MONTH = 21
APPROX_BDAYS_PER_YEAR = 252
MONTHS_PER_YEAR = 12
WEEKS_PER_YEAR = 52
TOTAL_SECONDS_IN_A_DAY = 24 * 60 * 60.
TOTAL_SECONDS_IN_A_YEAR = TOTAL_SECONDS_IN_A_DAY * 365.24

ANNUALIZATION_FACTORS = {'daily': APPROX_BDAYS_PER_YEAR,
                         'weekly': WEEKS_PER_YEAR,
                         'monthly': MONTHS_PER_YEAR}


def annualized_return(start_equity, end_equity, hold_period, period=365):
    return ((1 + cumulative_return(start_equity, end_equity)) ** (period / hold_period) - 1)


def cumulative_return(start_equity, end_equity):
    return (end_equity - start_equity) / start_equity


def drawdown(array):
    pass


def downside_risk():
    pass


def information_ratio():
    pass


def sharpe_ratio(returns, risk_free):

    if isinstance(returns, (pd.Series, pd.DataFrame)):
        returns = returns.values

    if isinstance(risk_free, (pd.Series, pd.DataFrame)):
        risk_free = risk_free.values

    return np.mean(returns - risk_free) / np.std(returns - risk_free)


def sortino_ratio(annualized_returns, target_return, downside_risk):
    # return (annualized_returns - target_return) / downside_risk
    pass


def skew(returns):
    return stats.skew(returns)


def kurtosis(returns):
    return stats.kurtosis(returns)


def value_at_risk(returns, percentile=.05):
    return np.percentile(np.sort(returns, percentile * 100))
