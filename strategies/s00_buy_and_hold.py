from pyalgotrade import strategy, plotter
from pyalgotrade.barfeed import Frequency
from pyalgotrade.barfeed.csvfeed import GenericBarFeed
from pyalgotrade.bitstamp.broker import BacktestingBroker
from pyalgotrade.stratanalyzer import returns
import os


class BuyAndHoldStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, cash=10000):
        super(BuyAndHoldStrategy, self).__init__(feed, BacktestingBroker(cash, feed))

        self.__position = None
        self.__instrument = instrument

    def onEnterOk(self, position):
        exec_info = position.getEntryOrder().getExecutionInfo()
        self.info("BUY %s" % (str(exec_info)))

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        pass

    def onExitCanceled(self, position):
        pass

    def onBars(self, bars):
        bar = bars[self.__instrument]

        # Don't trade if volume is too low
        if bar.getVolume() < 100:
            return

        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:

            # Enter a buy market order for max shares possible. The order is good till canceled.
            # Ugly: using hardcoded Bitstamp fee 0.25%
            shares = self.getBroker().getCash(False) / bar.getPrice() * (1-0.0025)

            self.__position = self.enterLongLimit(self.__instrument, bar.getPrice(), shares, True)


def run_strategy():
    # Load the bar feed from the CSV file
    data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/btcusd_1h.csv')
    feed = GenericBarFeed(Frequency.HOUR)
    feed.addBarsFromCSV("BTC", data_path)

    # Evaluate the strategy with the feed's bars.
    strategy = BuyAndHoldStrategy(feed, "BTC")

    # Attach a returns analyzers to the strategy.
    returns_analyzer = returns.Returns()
    strategy.attachAnalyzer(returns_analyzer)

    # Attach the plotter to the strategy.
    plt = plotter.StrategyPlotter(strategy)
    # Plot the simple returns on each bar.
    plt.getOrCreateSubplot("returns").addDataSeries("Simple returns", returns_analyzer.getReturns())

    strategy.run()
    print("Final portfolio value: $%.2f" % strategy.getBroker().getEquity())

    plt.plot()


if __name__ == '__main__':
    run_strategy()
