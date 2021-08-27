import os, sys
lib_path = os.path.abspath('../commission')
sys.path.append(lib_path)

from datetime import datetime
import backtrader as bt
import pandas as pd
import quantstats

from tech_strategies import EWMAC_Indicator, EWMAC_Strategy
from ib_commission import IBCommission

data_feed = bt.feeds.YahooFinanceCSVData(
    dataname='../data/ticker/AAPL.csv',
    fromdate=datetime(2016, 1, 1),
    todate=datetime(2020, 12, 31),
)

cerebro = bt.Cerebro()
cerebro.addstrategy(EWMAC_Strategy, fast=32, slow=64)
cerebro.adddata(data_feed)

cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')

cerebro.broker.setcash(10000)
start_portfolio_value = cerebro.broker.getvalue()
cerebro.broker.addcommissioninfo(IBCommission())
cerebro.addsizer(bt.sizers.FixedSize, stake=100)


if __name__ == '__main__':
    results = cerebro.run()
    end_portfolio_value = cerebro.broker.getvalue()

    strat = results[0]
    pnl = end_portfolio_value - start_portfolio_value

    print(f'Starting Portfolio Value: {start_portfolio_value:2f}')
    print(f'Final Portfolio Value: {end_portfolio_value:2f}')
    print(f'PnL: {pnl:.2f}')

    portfolio_stats = strat.analyzers.getbyname('PyFolio')
    returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
    returns.index = returns.index.tz_convert(None)

    quantstats.reports.html(returns, benchmark="SPY", output='ewmac_ts.html', title='EWMAC')
    cerebro.plot()
