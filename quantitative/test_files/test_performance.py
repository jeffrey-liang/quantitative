#!/usr/bin/env python
# -*- coding: utf-8 -*-
from engine import BacktestEngine
from securities import Security
from performance import cumulative_return, annualized_return, sharpe_ratio
from utils import log_returns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

import warnings
warnings.filterwarnings("ignore")

import empyrical as ep

#with warnings.catch_warnings():
#    warnings.filterwarnings("ignore", category=DeprecationWarning)

backtest_results = pd.read_csv('../data_files/backtest_results.csv',
        index_col=0, parse_dates=True)
start = backtest_results.iloc[0]
end = backtest_results.iloc[-1]

# print(backtest_results)
# print(cumulative_return(start.portfolio_value, end.portfolio_value))
# print(annualized_return(start.portfolio_value, end.portfolio_value, 2*365))

prices = pd.read_csv('../data_files/prices.csv', index_col=0)
#print(np.log(prices.iloc[1] / prices.iloc[0]))
#print(np.log(prices.shift(-1) / prices))
#print(np.log(prices.shift(-1) / prices))

log_returns = log_returns(prices)

#print(sharpe_ratio(log_returns, 0))

#print(ep.sharpe_ratio(log_returns))
print(ep.annual_volatility(log_returns))
