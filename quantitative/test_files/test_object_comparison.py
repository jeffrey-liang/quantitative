#!/usr/bin/env python
# -*- coding: utf-8 -*-

from events import Event
from orders import Order

e = Event('2018-01-01')
o = Order(10)
o1 = Order(10)
print(o1 == o)

