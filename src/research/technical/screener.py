import datetime
import backtrader as bt
from strategies import *
import yfinance as yf

# Instantiate Cerebro engine
cerebro = bt.Cerebro()

# Add CSV data for all tickers to Cerebro
instruments = ['TSLA', 'AAPL', 'GE', 'GRPN']
start = '2016-01-01'
end = '2017-10-30'
for ticker in instruments:
	data = bt.feeds.PandasData(
		dataname=yf.download(ticker, start, end)
	)
	cerebro.adddata(data)

# Add analyzer for screener
cerebro.addanalyzer(Screener_SMA)

if __name__ == '__main__':
	# Run Cerebro Engine
	cerebro.run(runonce=False, stdstats=False, writer=True)
