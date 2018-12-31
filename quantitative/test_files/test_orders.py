#!/usr/bin/env python
# -*- coding: utf-8 -*-
from securities import Security
from orders import MarketOrder
from events import OrderEvent

s = Security('S')
mkt_order = MarketOrder('2018-01-01', 'BUY', s, 10)
mkt_order1 = MarketOrder('2018-01-01', 'BUY', s, 10)
'''
print(mkt_order.order_id)
mkt_order.shares = 100
print(mkt_order.order_id)
print(mkt_order)
print(mkt_order.order_type)

#print(mkt_order == mkt_order1)
'''

print(mkt_order.order_type == 'MarketOrder')
