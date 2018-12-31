#!/usr/bin/env python
# -*- coding: utf-8 -*-

from orders import MarketOrder
from securities import Security
from events import OrderEvent
from collections import namedtuple

s = Security('S')
mkt_order = MarketOrder('2017-01-01', 'BUY', s, 10)
event = OrderEvent('2017-01-01', mkt_order)

print(event.contract)




