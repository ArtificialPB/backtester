import os

from pyalgotrade import strategy, plotter
from pyalgotrade.barfeed import Frequency
from pyalgotrade.barfeed.csvfeed import GenericBarFeed
from pyalgotrade.bitstamp.broker import BacktestingBroker
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.technical import ma


class SmaCrossStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, sma_period=50, cash=10000):
        super(SmaCrossStrategy, self).__init__(feed, BacktestingBroker(cash, feed))

        self.__position = None
        self.__instrument = instrument
        self.__sma = ma.SMA(feed[instrument].getPriceDataSeries(), sma_period)

    def onEnterOk(self, position):
        exec_info = position.getEntryOrder().getExecutionInfo()
        self.info("BUY %s" % (str(exec_info)))

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        exec_info = position.getExitOrder().getExecutionInfo()
        self.info("SELL %s" % (str(exec_info)))
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def onBars(self, bars):
        # Wait for enough bars to be available to calculate a SMA.
        if self.__sma[-1] is None:
            return

        bar = bars[self.__instrument]

        # Don't trade if volume is too low
        if bar.getVolume() < 100:
            return

        # Open a position when no position yet opened
        if self.__position is None:
            if bar.getPrice() > self.__sma[-1]:
                # Enter a buy market order for max shares possible. The order is good till canceled.
                # Ugly: using hardcoded Bitstamp fee 0.25%
                shares = self.getBroker().getCash(False) / bar.getPrice() * (1-0.0025)

                # Skip if trade_size < 5USD (min Bitstamp trade)
                trade_size = bar.getPrice() * max(shares, bar.getVolume())
                # self.debug('Trade size %s shares (BTC)' % trade_size)

                self.__position = self.enterLongLimit(self.__instrument, bar.getPrice(), shares, True)
        # Check if we have to exit the position.
        elif bar.getPrice() < self.__sma[-1] and not self.__position.exitActive():
            # Sometimes there is too litle volume to close the position and we get an Exception
            # Very ugly hack, should solve it with Broker throwing better exceptions, not general Exception
            try:
                self.__position.exitLimit(bar.getPrice())
            except Exception:
                self.warning("Not enough volume to close the position. Trying later.")

    def get_sma(self):
        return self.__sma


def run_strategy(sma_period):
    # Load the bar feed from the CSV file
    data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/btcusd_1h.csv')
    feed = GenericBarFeed(Frequency.HOUR)
    feed.addBarsFromCSV("BTC", data_path)

    # Evaluate the strategy with the feed's bars.
    strategy = SmaCrossStrategy(feed, "BTC", sma_period=sma_period)

    # Attach a returns analyzers to the strategy.
    returns_analyzer = returns.Returns()
    strategy.attachAnalyzer(returns_analyzer)

    # Attach the plotter to the strategy.
    plt = plotter.StrategyPlotter(strategy)
    # Include the SMA in the instrument's subplot to get it displayed along with the closing prices.
    plt.getInstrumentSubplot("BTC").addDataSeries("SMA", strategy.get_sma())
    # Plot the simple returns on each bar.
    plt.getOrCreateSubplot("returns").addDataSeries("Simple returns", returns_analyzer.getReturns())

    strategy.run()
    print("Final portfolio value: $%.2f" % strategy.getBroker().getEquity())

    plt.plot()


if __name__ == '__main__':
    run_strategy(150)
