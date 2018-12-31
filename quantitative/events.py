#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc


class Event(metaclass=abc.ABCMeta):

    def __init__(self, event_index):

        self.event_type = self.__class__.__name__
        self.event_index = event_index

    def __repr__(self):
        return self.event_type

    def __gt__(self, other):
        return self.event_index > other.event_index

    def __eq__(self, other):
        return self.event_index == other.event_index

    def __ne__(self, other):
        return self.event_index != other.event_index


class TradeEvent(Event):
    '''
    Contains information about the trade data of a security.
    '''

    __slots__ = ['time', 'ticker', 'sale_price', 'sale_size']

    def __init__(self, time, ticker, sale_price, sale_size):

        self.time = time
        self.ticker = ticker
        self.sale_price = sale_price
        self.sale_size = sale_size

        super().__init__(self.time)

    def __repr__(self):
        return 'TradeEvent: {}, {}'.format(self.time, self.ticker)


class QuoteEvent(Event):
    '''
    Contains information about the quote data of a security.
    '''

    __slots__ = ['time', 'ticker', 'bid', 'ask', 'bid_size', 'ask_size']

    def __init__(self, time, ticker, bid, ask, bid_size, ask_size):

        self.time = time
        self.ticker = ticker
        self.bid = bid
        self.ask = ask
        self.bid_size = bid_size
        self.ask_size = ask_size

        super().__init__(self.time)

    def __repr__(self):
        return 'QuoteEvent: {}, {}'.format(self.time, self.ticker)


class MarketStatusEvent(Event):
    '''
    Contains information about the market status.
    '''

    __slots__ = ['market_status']

    def __init__(self, time, market_status):

        self.time = time
        self.market_status = market_status

        super().__init__(self.time)

    def __repr__(self):
        return 'MarketStatus: {}, {}'.format(self.time, self.market_status)


class OrderEvent(Event):
    '''
    Contains information about an order that was queued.
    '''

    __slots__ = ['time', 'contract']

    def __init__(self, time, contract):

        self.time = time
        self.contract = contract

        super().__init__(self.time)

    def __repr__(self):
        return 'OrderEvent: {}, {}'.format(self.time, self.contract)
