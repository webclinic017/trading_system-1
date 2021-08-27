from datetime import datetime
import backtrader as bt
import pandas as pd
import quantstats

from strategies import SmaCross
from ib_commission import IBCommission

data = bt.feeds.YahooFinanceCSVData(
    dataname='./data/AAPL.csv',
    fromdate=datetime(2018, 1, 1),
    todate=datetime(2020, 12, 31),
)

cerebro = bt.Cerebro()
cerebro.adddata(data)
cerebro.addstrategy(SmaCross)

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

    quantstats.reports.html(returns, output='bt_smac.html', title='SMAC')
    cerebro.plot()
