#!/usr/bin/env python
# -*- coding: utf-8 -*-

from portfolio import Portfolio
import pandas as pd

time = [pd.Timestamp('2017-01-01 09:30:00'),
        pd.Timestamp('2017-01-01 09:31:00'),
        pd.Timestamp('2017-01-01 09:32:00')]

portfolio = Portfolio()

'''Cash'''

'''Add cash'''
portfolio.modify_cash(time[0], 1000)
assert(portfolio.get_cash(time[0]) == 1000)

'''Update portfolio value, then get portfolio value'''
portfolio.update_portfolio_values(time[0])
assert(portfolio.get_porfolio_value(time[0]) == 1000)

'''Removing cash'''
old_cash_value = portfolio.get_cash(time[0])
portfolio.modify_cash(time[0], old_cash_value - 400)
assert(portfolio.get_cash(time[0]) == 600)

'''Out of bound indexing'''

try:
    portfolio.get_porfolio_value(time[2])
except KeyError:
    pass

try:
    portfolio.get_cash(time[2])
except KeyError:
    pass

''' Positions'''

'''Add position'''
portfolio.add_position(time[0], 'AAA', 100.00, 10)
position = portfolio.open_positions['AAA']
assert(position.time == time[0])
assert(position.ticker == 'AAA')
assert(position.market_price == 100.00)
assert(position.shares == 10)
assert(position.purchase_price == 100.00)
assert(position.purchase_time == time[0])

'''Modify position'''
# Updated market price
portfolio.modify_position('AAA', time=time[1], market_price=110.00)
position = portfolio.open_positions['AAA']
assert(position.market_price == 110.00)
assert(position.time == time[1])
assert(position.purchase_time == time[0])
assert(position.shares == 10)

# Remove position
portfolio.remove_position('AAA')
assert(len(portfolio.open_positions) == 0)

# Remove nonexistant position
try:
    portfolio.remove_position('BBB')
except KeyError:
    pass

'''Add multiple positions'''
portfolio.add_position(time[0], 'AAA', 100.00, 10)
portfolio.add_position(time[0], 'BBB', 20.00, 5)

assert(len(portfolio.open_positions) == 2)

'''Calculate investment total'''
assert(portfolio.calulate_investment_total(time[0]) == 1100)

''' Transactions '''

# Cash transaction
portfolio.add_transaction(time[0], cash=1000)
transaction = portfolio.transaction_log[time[0]][0]
assert(transaction.cash == 1000)
assert(transaction.time == time[0])

# Adding multiple cash transactions at same time
portfolio.add_transaction(time[0], cash=1000)
assert(len(portfolio.transaction_log[time[0]]) == 2)

