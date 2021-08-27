import backtrader as bt

# Create a subclass of Strategy to define the indicators and logic

class SmaCross(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict(
        pfast=10,  # period for the fast moving average
        pslow=30   # period for the slow moving average
    )

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.pfast)  # fast moving average
        sma2 = bt.ind.SMA(period=self.p.pslow)  # slow moving average
        self.crossover = bt.ind.CrossOver(sma1, sma2)  # crossover signal

    def next(self):
        if not self.position:  # not in the market
            if self.crossover > 0:  # if fast crosses slow to the upside
                self.buy()  # enter long

        elif self.crossover < 0:  # in the market & cross to the downside
            self.close()  # close long position


class Screener_SMA(bt.Analyzer):
    params = (('period', 20), ('devfactor', 2),)

    def start(self):
        self.bbands = {data: bt.indicators.BollingerBands(data, period=self.params.period, devfactor=self.params.devfactor)
                       for data in self.datas}

    def stop(self):
        self.rets['over'] = list()
        self.rets['under'] = list()

        for data, band in self.bbands.items():
            node = data._name, data.close[0], round(band.lines.bot[0], 2)
            if data > band.lines.bot:
                self.rets['over'].append(node)
            else:
                self.rets['under'].append(node)


class AverageTrueRange(bt.Strategy):

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')  # Print date and close

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low

    def next(self):
        range_total = 0
        for i in range(-13, 1):
            true_range = self.datahigh[i] - self.datalow[i]
            range_total += true_range
        ATR = range_total / 14

        self.log(f'Close: {self.dataclose[0]:.2f}, ATR: {ATR:.4f}')


class BtcSentiment(bt.Strategy):
    params = (('period', 10), ('devfactor', 1),)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def __init__(self):
        self.btc_price = self.datas[0].close
        self.google_sentiment = self.datas[1].close
        self.bbands = bt.indicators.BollingerBands(
            self.google_sentiment, period=self.params.period, devfactor=self.params.devfactor)

        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):
        # Check for open orders
        if self.order:
            return

        # Long signal
        if self.google_sentiment > self.bbands.lines.top[0]:
            # Check if we are in the market
            if not self.position:
                self.log(
                    f'Google Sentiment Value: {self.google_sentiment[0]:.2f}')
                self.log(f'Top band: {self.bbands.lines.top[0]:.2f}')
                # We are not in the market, we will open a trade
                self.log(f'***BUY CREATE {self.btc_price[0]:.2f}')
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        # Short signal
        elif self.google_sentiment < self.bbands.lines.bot[0]:
            # Check if we are in the market
            if not self.position:
                self.log(
                    f'Google Sentiment Value: {self.google_sentiment[0]:.2f}')
                self.log(f'Bottom band: {self.bbands.lines.bot[0]:.2f}')
                # We are not in the market, we will open a trade
                self.log(f'***SELL CREATE {self.btc_price[0]:.2f}')
                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

        # Neutral signal - close any open trades
        else:
            if self.position:
                # We are in the market, we will close the existing trade
                self.log(
                    f'Google Sentiment Value: {self.google_sentiment[0]:.2f}')
                self.log(f'Bottom band: {self.bbands.lines.bot[0]:.2f}')
                self.log(f'Top band: {self.bbands.lines.top[0]:.2f}')
                self.log(f'CLOSE CREATE {self.btc_price[0]:.2f}')
                self.order = self.close()


class EWMAC_Indicator(bt.Indicator):
    alias = ('EWMAC',)
    lines = ('ewmac',)
    plotinfo = dict(plotymargin=0.05, plotyhlines=[-20.0, 20.0])
    params = (
        # period for the fast Moving Average
        ('fast', 16),
        # period for the slow moving average
        ('slow', 16*4),
    )

    def __init__(self):
        ewma_fast = bt.indicators.EMA(period=self.params.fast)
        ewma_slow = bt.indicators.EMA(period=self.params.slow)
        ewmac_raw = ewma_fast - ewma_slow

        diff = self.data - self.data(-1)
        volatility_loopback = self.params.slow * 2
        stdev_returns = bt.indicators.StdDev(diff, period=volatility_loopback)
        ewmac_volatility_standardized = ewmac_raw / stdev_returns

        ewmac_volatility_standardized_abs_mean = bt.indicators.SMA(
            abs(ewmac_volatility_standardized), period=volatility_loopback)
        forecast_scalar = 10.0 / ewmac_volatility_standardized_abs_mean

        forecasts = ewmac_volatility_standardized * forecast_scalar

        # capped between -20.0 and 20.0
        forecasts = bt.Max(forecasts, -20.0)
        forecasts = bt.Min(forecasts, 20.0)

        self.lines.ewmac = forecasts


class EWMAC_Strategy(bt.Strategy):

    """EWMAC strategy form the book Systematic Trading."""
    alias = ('EWMAC',)

    params = (
        # period for the fast Moving Average
        ('fast', 16),
        # period for the slow moving average
        ('slow', 16*4),
    )

    def __init__(self):
        self.ewmac = EWMAC_Indicator(
            fast=self.params.fast, slow=self.params.slow)

        # Order variable will contain ongoing order details/status
        self.order = None

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        # Comment this line when running optimization
        print(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # An active Buy/Sell order has been submitted/accepted - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None

    def next(self):
        # Check for open orders
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # if we aren't in the market, look for a signal to open trades
            if self.ewmac > 5:
                self.buy()
        else:
            if self.ewmac < -5:
                self.sell()
