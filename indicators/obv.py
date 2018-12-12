from pyalgotrade import technical

"""
Indicator calculations are done in a class that extends technical.EventWindow, which (by default) accepts float values.
If we want to pass any other value type, we must set it in "dtype" parameter when calling constructor of super class.

"""


class OBVEventWindow(technical.EventWindow):
    def __init__(self, period):
        assert (period > 0)
        # To accept values other than float, we must set "dtype" to "object"
        super(OBVEventWindow, self).__init__(period, dtype=object)
        self.__value = None
        self.__price = None

    def onNewValue(self, dateTime, value):
        if len(self.getValues()) > 0:
            assert (self.getValues()[0] is not None)

        super(OBVEventWindow, self).onNewValue(dateTime, value)

        if value is not None and self.windowFull():
            if self.__value is None:
                self.__value = 0
                self.__price = value.getClose()
            else:
                currPrice = value.getClose()
                if currPrice > self.__price:
                    self.__value += value.getVolume()
                elif currPrice < self.__price:
                    self.__value -= value.getVolume()
                self.__price = currPrice

    def getValue(self):
        return self.__value


class OBV(technical.EventBasedFilter):
    def __init__(self, dataSeries, period, maxLen=None):
        super(OBV, self).__init__(dataSeries, OBVEventWindow(period), maxLen)
