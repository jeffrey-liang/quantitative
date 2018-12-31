#!/usr/bin/env python
# -*- coding: utf-8 -*-

import queue
import abc
import numpy as np
import pandas as pd
import itertools
import datetime
from .portfolio import Portfolio
from .securities import Security
from .events import TradeEvent, QuoteEvent, MarketStatusEvent, OrderEvent
from .orders import MarketOrder, LimitOrder


class BacktestEngine(metaclass=abc.ABCMeta):

    def __init__(self, data=None, securities=None, record_history=False):
        '''User Settings'''
        self.inital_cash = 0
        self.include_commission = False
        self.broker = 'ib'
        self.market_open_time = '09:30:00.000000000'
        self.market_close_time = '16:00:00.000000000'
        self.verbose = True
        self.record_history = record_history

        '''Backtest Attributes'''
        self._market_status = None

        # Events queue
        self._events_queue = queue.PriorityQueue()

        # Priority Queue priorities
        self.QUOTE_TRADE_QUEUE_EVENT_PRIORITY = 3
        self.ORDER_EVENT_QUEUE_PRIORITY = 2
        self.MARGIN_CALL_EVENT_QUEUE_PRIORITY = 1

        self._portfolio = Portfolio()

        # Store orders than cannot be filled at time of creation
        self.unfilled_orders = {'AON': [], 'GTC': [], 'DAY': []}

        # Global backtest time
        self.simulation_time = None

        # Load security objects into securities_in_universe
        if securities is not None:
            self.securities_in_universe = {}

            for security in securities:
                security_name = security.ticker
                self.securities_in_universe[security_name] = security
                self._portfolio.securities_in_universe.append(security_name)

        else:
            raise RuntimeError('No securities in universe')

        # Load data into events queue
        if data is not None:
            first_time = '{} 09:30:00'
            # self.simulation_time = data.index[0]
            self.simulation_time = pd.Timestamp(
                first_time.format(data.index[0].date()))

            self._queue_data(data)

        else:
            raise RuntimeError('No data in backtest')

    ''' User Methods '''

    ''' Order Methods'''

    def create_limit_order(self, direction, security, shares, price,
                           time_condition='GTC', order_condition=None):
        '''
        Creates a limit order.

        Parameters:
        ----------
        direction: str
            BUY or SELL.

        security: securities.Security
            Security object.

        shares: float/int
            The amount of shares in order.

        price: float
            Price at which limit order is filled.

        time_condition: str
            Time constraint on the order. 
            options: 'GTC' (Good-Til-Cancelled), 'FOK' (Fill-or-Kill),
                     'AON' (All-or-None), 'IOC (Immediate-or-Cancel)'

        order_condition: str
            Order type of limit order. Not Implemented

        Returns:
        -------
        lmt_order: orders.LimitOrder
            Returns a limit order with specified parameters. Note that 
            this does not place the order.
        '''

        assert(type(direction) == str)
        assert(type(shares) == int or float)
        assert(type(price) == int or float)
        assert(type(security) == Security)

        lmt_order = LimitOrder(self.simulation_time, direction, security,
                               price, shares, time_condition, order_condition)

        return lmt_order

    def create_market_order(self, direction, security, shares,
                            time_condition='GTC', order_condition=None):
        '''
        Creates a market order.

        Parameters:
        ----------
        direction: str
            BUY or SELL.

        security: securities.Security
            Security object.

        shares: float/int
            The amount of shares in order.

        time_condition: str
            Time constraint on the order. 
            options: 'GTC' (Good-Til-Cancelled), 'FOK' (Fill-or-Kill),
                     'AON' (All-or-None), 'IOC (Immediate-or-Cancel)'

        order_condition: str
            Order type of limit order. Not Implemented

        Returns:
        -------
        mkt_order: orders.MarketOrder
            Returns a limit order with specified parameters.
        '''

        assert(type(direction) == str)
        assert(type(shares) == int or float)
        assert(type(security) == Security)

        mkt_order = MarketOrder(self.simulation_time, direction, security,
                                shares, time_condition, order_condition)

        return mkt_order

    def place_order(self, order):
        '''
        Sends order execution to backtest engine.

        Parameters:
        ----------
        order: orders.MarketOrder or order.LimitOrder
            Order with specified parameters to attempt to fill.

        Returns:
        -------
        None

        '''

        if (order.direction == 'SELL' and
                self.get_shares(order.security.ticker) < order.shares):

            if self.verbose:
                message = '[ERROR] Not enough shares to fill {} for {}'
                print(message.format(order, order.security.ticker))

        else:

            # Update time of order
            contract = OrderEvent(self.simulation_time, order)

            self._events_queue.put(
                (self.ORDER_EVENT_QUEUE_PRIORITY, contract))

        if self.verbose:
            if order.order_type == 'MarketOrder':
                message = '[ALERT]  {} {}-{} placed on {} for {} @ {} share(s).'
                print(message.format(order.direction, order.order_type,
                                     order.time_condition, self.simulation_time,
                                     order.security.ticker, order.shares))

            elif order.order_type == 'LimitOrder':
                message = '[ALERT]  {} {}-{} placed on {} for {} @ ${:.2f} x {} share(s).'
                print(message.format(order.direction, order.order_type,
                                     order.time_condition, self.simulation_time,
                                     order.security.ticker, order.price,
                                     order.shares))

    ''' User Portfolio Methods '''

    def add_cash(self, amount):
        '''
        Adds cash to backtest using modify_cash() from portfolio.

        Parameters:
        ----------
        amount: float/int
            The amount of cash to add.

        Returns:
        -------
        None

        '''

        if amount < 0:
            raise ValueError('Cash amount must be nonnegative.')

        old_cash_val = self.get_cash()

        self._portfolio.modify_cash(
            self.simulation_time, old_cash_val + amount)
        self._portfolio.add_transaction(self.simulation_time, cash=amount)

    def remove_cash(self, amount):
        '''
        Removes cash from backtest using modify_cash() from portfolio.

        Parameters:
        ----------
        amount: float/int
            The amount of cash to remove.

        Returns:
        -------
        None

        '''

        old_cash_val = self.get_cash()

        self._portfolio.modify_cash(
            self.simulation_time, old_cash_val - abs(amount))
        self._portfolio.add_transaction(self.simulation_time,
                                        cash=-abs(amount))

    def get_cash(self):
        '''
        Returns cash in backtest by calling get_cash() from portfolio.

        Parameters:
        ----------
        None

        Returns:
        -------
        self._portfolio.get_cash(self.simulation_time): float/int
            Current cash at global simulation time.
        '''

        return self._portfolio.get_cash(self.simulation_time)

    def get_portfolio_value(self):
        '''
        Returns portfolio value of backtest by calling get_portfolio_value()
        from portfolio.

        Parameters:
        ----------
        None

        Returns:
        -------
        self._portfolio.get_porfolio_value(self.simulation_time): float/int
            Portfolio value at global simulation time.
        '''

        return self._portfolio.get_porfolio_value(self.simulation_time)

    def get_total_investment_value(self):
        '''
        Returns total investment value of backtest by calling
        calculate_investment_total() from portfolio.

        Parameters:
        ----------
        None

        Returns:
        -------
        self._portfolio.calculate_investment_total(self.simulation_time): float/int
            Investment total at global simulation time.
        '''

        return self._portfolio.calculate_investment_total(self.simulation_time)

    def get_open_positions(self, ticker=None):
        '''
        Returns the open positions of the portfolio.

        Parameters:
        ----------
        ticker: str
            The open position of the ticker. If ticker is None, returns 
            the open positions of all the tickers in the portfolio.

        Returns:
        -------
        self._portfolio.open_positions: collections.namedtuple
            The open positions of the portfolio.

        '''
        if ticker is None:
            return self._portfolio.open_positions
        else:
            return self._portfolio.open_positions[ticker]

    def get_shares(self, ticker):
        '''
        Returns the number of shares of selected ticker in portfolio.

        Parameters:
        ----------
        ticker: str
            The ticker.

        Returns:
        -------
        shares: int
            The number of shares in portfolio of the ticker.

        '''
        try:
            return self._portfolio.open_positions[ticker].shares
        except KeyError as e:
            return 0

    def get_holdings(self):
        '''
        Returns the number of shares of each ticker of the portfolio. 
        

        Parameters:
        ----------
        None

        Returns:
        -------
        self._update_securities_history.holdings: dict
            The shares currently of each ticker in the portfolio.
            e.g. {'MSFT': 100, 'AAPL': 200}
        '''
        return self._portfolio.holdings

    def get_account_values(self):
        '''
        Returns the cash value, investment value and portfolio value of the 
        backtest.

        Parameters:
        ----------
        None

        Returns:
        -------
        self._portfolio.portfolio_value[self.simulation_time]: collections.namedtuple
            A namedtuple of the class value, investment value and portfolio value
            at the current backtest time.
                
        '''
        return self._portfolio.portfolio_value[self.simulation_time]

    def cancel_all_unfilled_orders(self):
        '''
        Cancel all unfilled orders.
        Parameters:
        ----------
        None

        Returns:
        -------
        None
        '''

        for order_type, orders in self.unfilled_orders.items():
            orders.clear()

    def cancel_unfilled_order(self, order):
        '''
        Cancel a specific order that has not been filled yet.

        Parameters:
        ----------
        order: orders.MarketOrder/orders.LimitOrder
            The unfilled order to be canceled.

        Returns:
        -------
        None
        '''
        try:
            self.unfilled_orders[order.time_condition].remove(order)
            if self.verbose:
                print('[UPDATE] Order canceled.')

        except ValueError:

            if self.verbose:
                print('[ALERT] Order not in unfilled orders')

    def get_market_status(self):
        '''
        Returns the market status: OPEN or CLOSE

        Parameters:
        ----------
        None

        Returns:
        -------
        self._market_status: str
            The market status.
        '''
        return self._market_status

    def get_transaction_log(self):
        '''
        Returns the transaction log of the backtest. The transaction log
        contains all cash, market transactions to the portfolio. 

        Parameters:
        ----------
        None

        Returns:
        -------
        self._portfolio.transaction_log: collections.namedtuple
            The transaction log.
        '''
        return self._portfolio.transaction_log

    def get_number_of_unfilled_orders(self):
        '''
        Returns the number of unfilled orders in the porfolio.

        Parameters:
        ----------
        None

        Returns:
        -------
        unfilled_orders: int
            The number of unfilled orders.
        '''
        
        unfilled_orders = 0

        for _, orders in self.unfilled_orders.items():
            if len(orders) != 0:
                unfilled_orders += 1

        return unfilled_orders

    def get_time(self):
        '''
        Returns the backtest time.

        Parameters:
        ----------
        None

        Returns:
        -------
        self.simulation_time: pd.Timestamp
            The current time of the backtest.

        '''
        return self.simulation_time

    ''' Backtest Methods '''

    def initialize_portfolio(self):
        '''
        Initialize the backtest portfolio by updating the cash and portfolio
        values of the porfolio class.

        '''

        # set initial cash, initialize portfolio starting values
        self._portfolio.modify_cash(self.simulation_time, self.inital_cash)
        self._portfolio.update_portfolio_values(self.simulation_time)

    def _queue_data(self, data):
        '''
        Queue the data into our backtest.

        Parameters:
        ----------
        data: pandas.DataFrame
            The Pandas DataFrame with the tick data. 

            Format:
            ------
            DATE_TIME,BID,BID_SIZE,ASK,ASK_SIZE,SEC,TYPE,SIZE,PRICE
            2017-11-10 09:46:32.278115304,83.79,1.0,83.81,2.0,MSFT,QUOTE,,
            2017-11-10 09:46:32.278133425,103.77,1.0,103.88,1.0,AAPL,QUOTE,,
            2017-11-10 09:46:32.278142489,103.77,1.0,103.88,1.0,AAPL,QUOTE,,
            2017-11-10 09:46:32.278175650,,,,,MSFT,TRADE,100.0,84.8
            2017-11-10 09:46:32.278182576,83.79,7.0,83.8,5.0,MSFT,QUOTE,,
            2017-11-10 09:46:32.278187841,,,,,AAPL,TRADE,100.0,103.8
            2017-11-10 09:46:32.278192693,83.79,3.0,83.81,4.0,MSFT,QUOTE,,
            2017-11-10 09:46:32.278221346,103.79,4.0,103.8,3.0,AAPL,QUOTE,,
            2017-11-10 09:46:32.278229858,83.72,1.0,83.81,2.0,MSFT,QUOTE,,
            2017-11-10 09:46:32.278235405,,,,,MSFT,TRADE,200.0,85.8

        '''
        time_format = '{} {}'

        first_time_in_data = data.index[0]
        first_market_open_time = pd.Timestamp(time_format.format(
            first_time_in_data.date(), self.market_open_time))

        first_market_open_event = MarketStatusEvent(
            first_market_open_time, market_status='OPEN')

        self._events_queue.put(
            (self.QUOTE_TRADE_QUEUE_EVENT_PRIORITY, first_market_open_event))

        market_status = 'OPEN'

        previous_time = first_market_open_time

        # Begin to queue data into priority queue.
        for row in data.itertuples(index=True):

            if (market_status == 'OPEN' and
                    row.Index.time() > pd.Timestamp(self.market_close_time).time()
                    or row.Index.date() > previous_time.date()):

                new_market_close_time = pd.Timestamp(
                    time_format.format(previous_time.date(), self.market_close_time))

                market_close_event = MarketStatusEvent(new_market_close_time,
                                                       market_status='CLOSE')

                # Add market close status 
                self._events_queue.put(
                    (self.QUOTE_TRADE_QUEUE_EVENT_PRIORITY, market_close_event))

                market_status = 'CLOSE'

            if (market_status == 'CLOSE' and
                    row.Index.time() > pd.Timestamp(self.market_open_time).time()):

                new_time = row.Index
                new_market_open_time = pd.Timestamp(
                    time_format.format(new_time.date(), self.market_open_time))

                market_open_event = MarketStatusEvent(new_market_open_time,
                                                      market_status='OPEN')

                self._events_queue.put(
                    (self.QUOTE_TRADE_QUEUE_EVENT_PRIORITY, market_open_event))

                market_status = 'OPEN'

            if row.TYPE == 'TRADE':
                new_event = TradeEvent(row.Index, row.SEC, row.PRICE, row.SIZE)

            elif row.TYPE == 'QUOTE':
                new_event = QuoteEvent(row.Index, row.SEC, row.BID, row.ASK,
                                       row.BID_SIZE, row.ASK_SIZE)

            self._events_queue.put(
                (self.QUOTE_TRADE_QUEUE_EVENT_PRIORITY, new_event))

            previous_time = row.Index

    def _update_securities_data(self, event):
        '''
        Update the security data from event data.
        '''

        security = self.securities_in_universe[event.ticker]

        if event.event_type == 'TradeEvent':
            security.last_sale_time = event.time
            security.last_sale_price = event.sale_price
            security.last_sale_size = event.sale_size

        elif event.event_type == 'QuoteEvent':
            security.time = event.time
            security.bid = event.bid
            security.ask = event.ask
            security.bid_size = event.bid_size
            security.ask_size = event.ask_size

    def _update_portfolio_values(self, time, cash, investment_value,
                                 portfolio_value):

        self.portfolio.modify_portfolio_value()

    def _update_portfolio_holdings(self, time):
        self._portfolio.update_portfolio_holdings(time)

    def _process_order(self, order_event):
        '''
        Handles when there is an order event.
        '''
        order = order_event.contract
        order_security = order.security

        if order.shares < 0:
            raise ValueError('Shares cannot be less than 0.')

        if np.isnan(order_security.ask) or np.isnan(order_security.bid):

            if order.time_condition == 'GTC' or order.time_condition == 'DAY':
                self.unfilled_orders[order.time_condition].append(order)

            elif order.time_condition == 'AON':
                if self.verbose:
                    message = '[UPDATE] {} {}-{} ({}: ${:.2f} x {} shares) could not be filled.'
                    print(message.format(order.direction, order.order_type,
                                         order.time_condition, order_security.ticker,
                                         order.price, order.shares))

        # Market Order
        # If there are enough shares
        elif (order.order_type == 'MarketOrder' and order.direction == 'BUY'
                and order_security.ask_size >= order.shares):

            self._fill_market_order(order)
            order.order_status = 'FILLED'

        elif (order.order_type == 'MarketOrder' and order.direction == 'SELL'
                and order_security.bid_size >= order.shares):

            self._fill_market_order(order)
            order.order_status = 'FILLED'

        # Not enough shares
        elif (order.order_type == 'MarketOrder' and order.direction == 'BUY'
                and order_security.ask_size < order.shares):

            if order.time_condition == 'GTC' or order.time_condition == 'DAY':
                # Good-Til-Canceled or Day Order

                difference_in_shares = order.shares - order_security.ask_size

                # Partial fill
                new_market_order = self.create_market_order(
                    order.direction, order.security,
                    order_security.ask_size,
                    time_condition=order.time_condition)

                self._fill_market_order(new_market_order)

                # Update old order with differences in shares
                order.shares = difference_in_shares
                order.order_status = 'PARTIAL'

                self.unfilled_orders[order.time_condition].append(order)

            elif order.time_condition == 'FOK':
                # Fill-Or-Kill
                if self.verbose:
                    message = '[UPDATE] {} {}-{} ({}: ${:.2f} x {} shares) could not be filled.'
                    print(message.format(order.direction, order.order_type,
                                         order.time_condition, order_security.ticker,
                                         order.price, order.shares))

            elif order.time_condition == 'AON':
                # All-Or-None
                self.unfilled_orders['AON'].append(order)

            elif order.time_condition == 'IOC':
                # Immediate-Or-Cancel
                new_market_order = MarketOrder(
                    self.simulation_time, order.direction, order_security,
                    order_security.ask_size, time_condition=order.time_condition)

                self._fill_market_order(new_market_order)

                order.order_status = 'PARTIAL'

        elif (order.order_type == 'MarketOrder' and order.direction == 'SELL'
                and order_security.bid_size < order.shares):

            if order.time_condition == 'GTC' or order.time_condition == 'DAY':
                # Good-Til-Canceled or Day order

                difference_in_shares = order.shares - order_security.bid_size

                # Partial fill
                new_market_order = MarketOrder(
                    self.simulation_time, order.direction, order_security,
                    order_security.bid_size, time_condition=order.time_condition)

                self._fill_market_order(new_market_order)

                order.shares = difference_in_shares

                self.unfilled_orders[order.time_condition].append(
                    order)

            elif order.time_condition == 'FOK':
                # Fill-Or-Kill
                if self.verbose:
                    message = '[UPDATE] {} {}-{} ({}: ${:.2f} x {} shares) could not be filled.'
                    print(message.format(order.direction, order.order_type,
                                         order.time_condition, order_security.ticker,
                                         order.price, order.shares))

            elif order.time_condition == 'AON':
                # All-Or-None
                self.unfilled_orders['AON'].append(order)

            elif order.time_condition == 'IOC':

                # Immediate-Or-Cancel
                new_market_order = MarketOrder(
                    self.simulation_time, order.direction, order_security,
                    order_security.bid_size, time_condition=order.time_condition)

                self._fill_market_order(new_market_order)
                order.order_status = 'PARTIAL'

        # Limit Order
        # Valid price, and enough shares avaliable in market
        elif (order.order_type == 'LimitOrder' and order.direction == 'BUY'
                and order_security.ask <= order.price and
                order_security.ask_size >= order.shares):

            self._fill_market_order(order)

        elif (order.order_type == 'LimitOrder' and order.direction == 'SELL'
                and order_security.bid >= order.price and
                order_security.bid_size >= order.shares):

            self._fill_market_order(order)

        # Valid price, but not enough shares avaliable in market
        elif (order.order_type == 'LimitOrder' and order.direction == 'BUY'
                and order_security.ask <= order.price and
                order_security.ask_size < order.shares):

            if order.time_condition == 'GTC' or order.time_condition == 'DAY':
                # Good-Til-Canceled

                difference_in_shares = order.shares - order_security.ask_size

                # Partial fill
                new_limit_order = LimitOrder(
                    self.simulation_time, order.direction, order_security,
                    order.price, order_security.ask_size,
                    time_condition=order.time_condition)

                self._fill_market_order(new_limit_order)

                order.shares = difference_in_shares

                self.unfilled_orders[order.time_condition].append(order)

            elif order.time_condition == 'FOK':
                # Fill-Or-Kill
                if self.verbose:
                    message = '[UPDATE] {} {}-{} ({}: ${:.2f} x {} shares) could not be filled. '\
                        'Not enough shares avaliable.'
                    print(message.format(order.direction, order.order_type,
                                         order.time_condition, order_security.ticker,
                                         order.price, order.shares))

            elif order.time_condition == 'AON':
                # All-Or-None
                self.unfilled_orders['AON'].append(order)

            elif order.time_condition == 'IOC':
                # Immediate-Or-Cancel
                assert(order_security.ask <= order.price)
                new_limit_order = LimitOrder(
                    self.simulation_time, order.direction, order_security,
                    order.price, order_security.ask_size,
                    time_condition=order.time_condition)

                self._fill_market_order(new_limit_order)

        # Valid price, but not enough shares avaliable in market
        elif (order.order_type == 'LimitOrder' and order.direction == 'SELL'
                and order_security.bid >= order.price and
                order_security.bid_size < order.shares):

            if order.time_condition == 'GTC' or order.time_condition == 'DAY':

                assert(order_security.bid >= order.price)
                # Good-Til-Canceled
                difference_in_shares = order.shares - order_security.bid_size

                # Partial fill
                new_limit_order = LimitOrder(
                    self.simulation_time, order.direction, order_security,
                    order.price, order_security.bid_size,
                    time_condition=order.time_condition)

                self._fill_market_order(new_limit_order)

                order.shares = difference_in_shares

                self.unfilled_orders[order.time_condition].append(order)
                order.order_status = 'PARTIAL'

            elif order.time_condition == 'FOK':
                # Fill-Or-Kill
                if self.verbose:
                    message = '[UPDATE] {} {}-{} ({}: ${:.2f} x {} shares) could not be filled. '\
                        'Not enough shares avaliable.'
                    print(message.format(order.direction, order.order_type,
                                         order.time_condition, order_security.ticker,
                                         order.price, order.shares))

            elif order.time_condition == 'AON':
                # All-Or-None
                self.unfilled_orders['AON'].append(order)

            elif order.order_type == 'IOC':
                # Immediate-Or-Cancel
                assert(order_security.bid <= order.price)

                new_limit_order = LimitOrder(
                    self.simulation_time, order.direction, order_security,
                    order.price, order_security.bid_size,
                    time_condition=order.time_condition)

                self._fill_market_order(new_limit_order)

        # Price not valid for limit order
        elif (order.order_type == 'LimitOrder' and order.direction == 'BUY' and
                order.price < order_security.ask):
            try:
                self.unfilled_orders[order.time_condition].append(order)

            except KeyError:
                if self.verbose:
                    message = '[UPDATE] {} {}-{} ({}: ${:.2f} x {} shares) could not be filled.'
                    print(message.format(order.direction, order.order_type,
                                         order.time_condition, order_security.ticker,
                                         order.price, order.shares))

            # Price not valid for limit order
        elif (order.order_type == 'LimitOrder' and order.direction == 'SELL' and
                order.price > order_security.bid):
            try:
                self.unfilled_orders[order.time_condition].append(order)

            except KeyError:
                # Fill-Or-Kill
                if self.verbose:
                    message = '[UPDATE] {} {}-{} ({}: ${:.2f} x {} shares) could not be filled.'
                    print(message.format(order.direction, order.order_type,
                                         order.time_condition, order_security.ticker,
                                         order.price, order.shares))

    def _query_unfilled_orders(self):

        unfilled_orders = [orders for _,
                           orders in self.unfilled_orders.items()]

        for order in itertools.chain(*unfilled_orders):

            order_security = order.security
            if order.order_type == 'MarketOrder' and order.direction == 'BUY':

                if np.isnan(order_security.ask) and order.time_condition != 'AON':
                    # self.unfilled_orders[order.order].append(order)
                    # self.unfilled_orders[order.time_condition].append(order)
                    pass

                elif order_security.ask_size >= order.shares:
                    self._fill_market_order(order)
                    self.unfilled_orders[order.time_condition].remove(order)

                elif order_security.ask_size < order.shares and order_security.ask_size != 0:

                    if order.time_condition != 'AON':
                        difference_in_shares = order.shares - order_security.ask_size

                        # Partial fill
                        new_mkt_order = MarketOrder(
                            self.simulation_time, order.direction,
                            order_security, order_security.ask_size,
                            time_condition=order.time_condition)

                        self._fill_market_order(new_mkt_order)

                        # Update order with remaining shares, keep in
                        # unfilled_orders list
                        order.shares = difference_in_shares

                    elif order.order_type == 'AON':
                        pass

            elif order.order_type == 'MarketOrder' and order.direction == 'SELL':

                if order_security.bid_size >= order.shares:
                    self._fill_market_order(order)
                    self.unfilled_orders[order.time_condition].remove(
                        order)

                elif order_security.bid_size < order.shares and order_security.bid_size != 0:

                    if order.time_condition != 'AON':
                        difference_in_shares = order.shares - order_security.bid_size

                        # Partial fill
                        new_mkt_order = MarketOrder(
                            self.simulation_time, order.direction,
                            order_security, order_security.bid_size,
                            time_condition=order.time_condition)

                        self._fill_market_order(new_mkt_order)

                        # Update order with remaining shares, keep in
                        # unfilled_orders list
                        order.shares = difference_in_shares
                        order.order_status = 'PARTIAL'

                    elif order.order_type == 'AON':
                        pass

            elif order.order_type == 'LimitOrder':

                if order.direction == 'BUY' and order_security.ask <= order.price:

                    if order_security.ask_size >= order.shares:

                        self._fill_market_order(order)
                        self.unfilled_orders[order.time_condition].remove(
                            order)

                    elif order_security.ask_size < order.shares and order_security.ask_size != 0:

                        if order.time_condition != 'AON':
                            difference_in_shares = order.shares - order_security.ask_size

                            # Partial fill
                            new_lmt_order = LimitOrder(
                                self.simulation_time, order.direction,
                                order_security, order.price,
                                order_security.ask_size,
                                time_condition=order.time_condition)

                            self._fill_market_order(new_lmt_order)

                            # Update order with remaining shares, keep in
                            # unfilled_orders list
                            order.shares = difference_in_shares

                        elif order.time_condition == 'AON':
                            pass

                elif order.direction == 'SELL' and order_security.bid >= order.price:
                    if order_security.bid_size >= order.shares:

                        self._fill_market_order(order)
                        self.unfilled_orders[order.time_condition].remove(
                            order)

                    elif order_security.ask_size < order.shares and order_security.ask_size != 0:

                        if order.time_condition != 'AON':
                            difference_in_shares = order.shares - order_security.bid_size

                            # Partial fill
                            new_lmt_order = LimitOrder(
                                self.simulation_time, order.direction,
                                order_security, order.price,
                                order_security.bid_size,
                                time_condition=order.time_condition)

                            self._fill_market_order(new_lmt_order)

                            # Update order with remaining shares, keep in
                            # unfilled_orders list
                            order.shares = difference_in_shares

                        elif order.time_condition == 'AON':
                            pass

    def _fill_market_order(self, order):
        '''
        Does not check if shares available, just checks if enough cash for buy
        orders.
        '''

        filled_successfully = False
        order_security = order.security
        # order_size = order.shares
        # order_direction = order.direction

        if order.direction == 'BUY':

            market_price = order_security.ask
            commission = self.calculate_commission(self.broker, market_price,
                                                   order.shares)

            order_cost = order.shares * market_price + commission

            if order_cost <= self.get_cash():

                try:
                    # if adding more shares, find avg price, and update positions
                    current_security_position = self._portfolio.open_positions[
                        order_security.ticker]
                    old_purchase_price = current_security_position.purchase_price
                    old_purchase_size = current_security_position.shares

                    avg_price = ((old_purchase_price * old_purchase_size) +
                                 (market_price * order.shares)) / (old_purchase_size + order.shares)

                    self._portfolio.modify_position(
                        order_security.ticker, purchase_price=avg_price,
                        shares=old_purchase_size + order.shares,
                        purchase_time=self.simulation_time,
                        market_price=market_price)

                # adding new shares
                except KeyError as e:
                    self._portfolio.add_position(
                        self.simulation_time, order_security.ticker,
                        market_price, order.shares)

                    self._update_portfolio_holdings(self.simulation_time)

                # print('fill order {}'.format(self.simulation_time))
                self.remove_cash(order_cost)

                self._portfolio.add_transaction(
                    self.simulation_time, cash=-order_cost)

                self._portfolio.add_transaction(
                    self.simulation_time, direction=order.direction,
                    ticker=order_security.ticker, price=market_price,
                    shares=order.shares, commission=commission)

                self._portfolio.update_portfolio_values(self.simulation_time)
                self._update_portfolio_holdings(self.simulation_time)

                # remove number of shares avaliable
                if order_security.ask_size - order.shares >= 0:
                    order_security.ask_size -= order.shares
                else:
                    order_security.ask_size = 0
                assert(order_security.ask_size >= 0)

                if self.verbose:
                    message = '[UPDATE] {} {}-{} for {} @ ${:.2f} x {:.0f} = ${:.2f} filled at {}.'

                    print(message.format(order.direction, order.order_type,
                                         order.time_condition, order_security.ticker,
                                         market_price, order.shares,
                                         order.shares * market_price,
                                         self.simulation_time))

                order_security.last_sale_price = market_price
                order_security.last_sale_size = order.shares
                order_security.last_sale_time = self.simulation_time
                filled_successfully = True

            else:
                if self.verbose:
                    message = '[WARNING] Not enough cash to fill {}-{} for {}. Order not filled.'
                    print(message.format(order.order_type, order.time_condition,
                                         order.security.ticker))

                order.order_status = 'UNFILLED'

        elif order.direction == 'SELL':
            market_price = order_security.bid
            commission = self.calculate_commission(self.broker, market_price,
                                                   order.shares)

            shares_in_account = self.get_shares(order_security.ticker)

            # selling some shares of ticker
            if order.shares < shares_in_account:
                difference = shares_in_account - order.shares

                self.add_cash((market_price * order.shares) - commission)

                # cash transaction
                self._portfolio.add_transaction(
                    self.simulation_time, cash=(market_price * order.shares))

                self._portfolio.modify_position(
                    ticker=order_security.ticker, time=self.simulation_time,
                    shares=difference, market_price=market_price)

                # order transaction
                self._portfolio.add_transaction(
                    self.simulation_time, direction=order.direction,
                    ticker=order_security.ticker, price=market_price,
                    shares=order.shares, commission=commission)

                self._portfolio.update_portfolio_values(self.simulation_time)
                self._update_portfolio_holdings(self.simulation_time)

            # selling all shares of ticker
            elif order.shares == shares_in_account:
                self._portfolio.remove_position(order_security.ticker)

                self.add_cash(
                    (market_price * order.shares) - commission)

                # cash transaction
                self._portfolio.add_transaction(
                    self.simulation_time, cash=(market_price * order.shares))

                # order transaction
                self._portfolio.add_transaction(
                    self.simulation_time, direction=order.direction,
                    ticker=order_security.ticker, price=market_price,
                    shares=order.shares, commission=commission)

                self._portfolio.update_portfolio_values(self.simulation_time)
                self._update_portfolio_holdings(self.simulation_time)

            # remove number of ask shares avaliable
            if order_security.bid_size - order.shares >= 0:
                order_security.bid_size -= order.shares
            else:
                order_security.bid_size = 0

            assert(order_security.bid_size >= 0)

            if self.verbose:
                message = '[UPDATE] {} {}-{} for {} @ ${:.2f} x {:.0f} = ${:.2f} filled at {}.'

                print(message.format(order.direction, order.order_type,
                                     order.time_condition, order_security.ticker,
                                     market_price, order.shares,
                                     order.shares * market_price,
                                     self.simulation_time))

            order_security.last_sale_price = market_price
            order_security.last_sale_size = order.shares
            order_security.last_sale_time = self.simulation_time

            filled_successfully = True

        return filled_successfully

    def calculate_commission(self, broker, price, shares):
        """
        Interactive brokers (CA) commission schedule.

        0.01 CAD per share
        Minimum per order is 1.00 CAD
        Maximum per order is 0.5% of trade value.

        Parameters:
        ----------
        broker: str
            The broker of the backtest.
        price: float
            The price of the security.
        shares: float/int
            The amount of shares in order.

        Returns:
        --------
        Commission: float
            The commission of the order.
        """
        if self.include_commission:

            COST_PER_SHARE = 0.01
            MIN_PER_ORDER_COST = 1.
            MAX_PER_ORDER_PERCENTAGE = 0.005

            interactive_brokers = ['interactive brokers', 'interactive', 'ib']

            if broker.lower() in interactive_brokers:
                contract_cost = price * shares
                commission = contract_cost * COST_PER_SHARE

                if commission <= MIN_PER_ORDER_COST:
                    return MIN_PER_ORDER_COST

                elif commission >= (contract_cost * MAX_PER_ORDER_PERCENTAGE):
                    return contract_cost * MAX_PER_ORDER_PERCENTAGE

                else:
                    return commission

            else:
                raise Exception(
                    'The broker \'{}\' is unavailable.'.format(self.broker))
            pass
        else:
            return 0

    def at_tick(self):
        '''
        User operations/computations at new tick event, before trade logic.
        '''
        pass

    def at_end_of_tick(self):
        pass

    @abc.abstractmethod
    def trade_logic(self):
        '''
        Trade logic.
        '''
        pass

    def run(self):
        '''
        Method to run the simulation. Order of execution:
        1. Update portfolio values 
        2. Get the next tick event
        3. Update security data based on information from tick event
        4. Call at_tick()
        5. Call trade_logic()
        6. Update portfolio values

        Parameters:
        ----------
        None

        Returns:
        -------
        result_account_values: pd.DataFrame
            Pandas DataFrame of portfolio value, cash value and investment 
            value at each tick of the backtest.

        '''
        if self.verbose:
            print('Backtest started...')
            start_time = datetime.datetime.now()

        self.initialize_portfolio()

        while not self._events_queue.empty():

            # Get next event from queue
            current_event = self._events_queue.get()

            tick_event_type = current_event[0]
            tick_event = current_event[1]

            ''' Update portfolio values before processing next tick '''

            previous_cash = self.get_cash()
            previous_investment_total = self.get_total_investment_value()

            self.simulation_time = tick_event.time

            self._portfolio.modify_cash(self.simulation_time, previous_cash)

            for ticker in self._portfolio.open_positions.keys():
                self._portfolio.modify_position(
                    ticker, time=self.simulation_time)

            self._portfolio.update_portfolio_values(self.simulation_time)

            '''Process next event tick'''

            # Quote or Trade Event
            if tick_event_type == self.QUOTE_TRADE_QUEUE_EVENT_PRIORITY:

                if tick_event.event_type == 'MarketStatusEvent':

                    self._market_status = tick_event.market_status

                    if tick_event.market_status == 'CLOSE':
                        self.unfilled_orders['DAY'].clear()

                # self._update_securities_data(tick_event)

                # Update prices for open positions
                elif tick_event.event_type == 'TradeEvent':

                    self._update_securities_data(tick_event)

                    try:
                        # if portfolio has shares of this security, update
                        #  portfolio value and investment values
                        self._portfolio.modify_position(
                            tick_event.ticker, time=self.simulation_time,
                            market_price=tick_event.sale_price)

                        self._portfolio.update_portfolio_values(
                            self.simulation_time)

                    except KeyError as e:
                        pass

                elif tick_event.event_type == 'QuoteEvent':
                    self._update_securities_data(tick_event)

                    self._query_unfilled_orders()

            # Order Event
            elif tick_event_type == self.ORDER_EVENT_QUEUE_PRIORITY:

                self._process_order(tick_event)

            elif current_event_type == self.MARGIN_CALL_EVENT_QUEUE_PRIORITY:
                pass

            self.at_tick()
            self.trade_logic()
            self.at_end_of_tick()

        if self.verbose:
            print('Backtest completed. Finished in {}'.format(
                datetime.datetime.now() - start_time))

        result_account_values = pd.DataFrame.from_dict(
            self._portfolio.portfolio_value, orient='index')

        result_account_values = result_account_values.astype('float64')

        return result_account_values
