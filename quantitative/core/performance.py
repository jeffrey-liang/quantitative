from .metrics import *
from dateutil.relativedelta import relativedelta


class Performance(object):

    def __init__(self):
        super().__init__()

    def CAGR(self, decimals=5):
        return CAGR(self.beginning_cash, self.ending_cash,
                    relativedelta(self.end_time, self.start_time).years,
                    decimals)

    def sharpe_ratio(self, risk_free_rate=.05, period='daily'):
        return sharpe_ratio(self.portfolio_value.values)

    def wins(self):

        tl = self.transaction_log.groupby(['ID', 'Ticker']).sum()

        return tl[tl['Total'] >= 0].shape[0]

    def losses(self):
        tl = self.transaction_log.groupby(['ID', 'Ticker']).sum()

        return tl[tl['Total'] < 0].shape[0]

    def total_completed_trades(self):
        tl = self.transaction_log.groupby(['ID', 'Ticker']).sum()

        return tl.shape[0]

    def win_percentage(self):
        return self.wins() / self.total_completed_trades()

    def largest_profit(self):
        tl = self.transaction_log.groupby(['ID', 'Ticker']).sum()

        return tl['Total'].max()

    def largest_loss(self):
        tl = self.transaction_log.groupby(['ID', 'Ticker']).sum()

        return tl['Total'].min()

    def drawdowns(self, target='Value'):
        return drawdowns(self.get_portfolio_value(),
                         target=target)
