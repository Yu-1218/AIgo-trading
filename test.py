from AlgoAPI import AlgoAPIUtil, AlgoAPI_Backtest
from datetime import datetime, timedelta
import talib
import numpy

class AlgoEvent:
    def __init__(self):
        self.lasttradetime = datetime(2000,1,1)
        self.arr_close = numpy.array([])
        self.arr_MA = numpy.array([])
        self.MAperiod = 10
        
    def start(self, mEvt):
        self.myinstrument = mEvt['subscribeList'][0]
        self.evt = AlgoAPI_Backtest.AlgoEvtHandler(self, mEvt)
        self.evt.start()
        
    def on_bulkdatafeed(self, isSync, bd, ab):
        if bd[self.myinstrument]['timestamp'] > self.lasttradetime + timedelta(hours=24):
            self.lasttradetime = bd[self.myinstrument]['timestamp']
            lastprice = bd[self.myinstrument]['lastPrice']
            self.arr_close = numpy.append(self.arr_close, lastprice)
            if len(self.arr_close)> int(self.MAperiod):
                self.arr_close = self.arr_close[int(-self.MAperiod):]
            self.arr_MA = talib.SMA(self.arr_close, timeperiod=int(self.MAperiod))
            if not numpy.isnan(self.arr_MA[-10]):
                #send a buy order
                if numpy.var(self.arr_close) < self.arr_MA[-1]:
                    return 1
                #send a sell order
                else if numpy.var(self.arr_close) > self.arr_MA[-1]:
                    return -1
                #send a hold order
                else:
                    return 0
        pass

    def on_marketdatafeed(self, md, ab):
        pass

    def on_newsdatafeed(self, nd):
        pass

    def on_weatherdatafeed(self, wd):
        pass
    
    def on_econsdatafeed(self, ed):
        pass
        
    def on_orderfeed(self, of):
        pass

    def on_dailyPLfeed(self, pl):
        pass

    def on_openPositionfeed(self, op, oo, uo):
        pass
