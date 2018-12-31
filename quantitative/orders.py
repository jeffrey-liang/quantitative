#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .events import Event
from .securities import Security
import uuid
import abc


class Order(metaclass=abc.ABCMeta):

    def __init__(self):
        self.order_id = uuid.uuid4()

    def __eq__(self, other):
        return self.order_id == other.order_id

    def __repr__(self):
        return self.__class__.__name__


class MarketOrder(Order):
    '''
    Container for market order.
    '''

    __slots__ = ['creation_time', 'direction',
                 'security', 'shares', 'order_type']

    def __init__(self, creation_time, direction, security, shares,
                 time_condition='GTC', order_condition=None):

        assert(type(direction) == str)
        assert(type(shares) == int or float)
        assert(type(security) == Security)

        self.creation_time = creation_time
        self.direction = direction
        self.security = security
        self.shares = shares

        self.order_type = self.__class__.__name__
        self.time_condition = time_condition # GTC, AOK, ...
        self.order_condition = order_condition # Stop-loss, trailing, ...
        self.order_status = 'UNFILLED' # FILLED, PARTIAL, UNFILLED

        super().__init__()


class LimitOrder(Order):
    '''
    Container for limit order.
    '''

    __slots__ = ['creation_time', 'direction', 'security', 'price', 'shares',
                 'order_type']

    def __init__(self, creation_time, direction, security, price, shares,
                 time_condition='GTC', order_condition=None):

        assert(type(direction) == str)
        assert(type(price) == int or float)
        assert(type(shares) == int or float)
        assert(type(security) == Security)

        self.creation_time = creation_time
        self.direction = direction
        self.security = security
        self.price = price
        self.shares = shares

        self.order_type = self.__class__.__name__  # LimitOrder
        self.time_condition = time_condition  # GTC, AOK, ...
        self.order_condition = order_condition  # Stop-loss, trailing, ...
        self.order_status = 'UNFILLED'  # FILLED, PARTIAL, UNFILLED

        super().__init__()

