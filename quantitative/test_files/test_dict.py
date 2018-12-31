#!/usr/bin/env python
# -*- coding: utf-8 -*-

from orders import MarketOrder
from securities import Security


unfilled_orders = []
s = Security('S')
mkt_order = MarketOrder('2017-01-01', 'BUY', s, 10)

unfilled_orders.append(mkt_order)
#mkt_order = MarketOrder('2017-01-02', 'SELL', s, 10)

unfilled_orders.remove(mkt_order)


