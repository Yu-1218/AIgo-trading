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
        self.BuySignalNews = 0
        self.BuySignalWeather = 0
        self.BuySignalMA = 0
        
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
                    self.BuySignalMA = 1
                #send a sell order
                else if numpy.var(self.arr_close) > self.arr_MA[-1]:
                    self.BuySignalMA = -1
                #send a hold order
                else:
                    self.BuySignalMA =  0

    def on_marketdatafeed(self, md, ab):
        pass

    def on_newsdatafeed(self, nd):
        pass

    def on_weatherdatafeed(self, wd):
        city = wd.city #how to choose a specific city, say HK
        temp = wd.temperature
        normal = 65.5 #nomal and comfortable temp in HK
        weather = wd.weather
        clouds = wd.clouds
        goodcoulds = 10
        badclouds = 80
        if temp < normal + 5 and temp > normal + 5: #compute temp signal
            temp_sig =  1
        else:
            temp_sig = -1
        if weather == "Clear":
            weather_sig = 1
        else if weather == "Rain":
            weather_sig = -1
        else:
            weather_sig = 0
        if coulds > badclouds:
            clouds_sig = 1
        else if coulds < goodclouds:
            clouds_sig = -1
        else:
            clouds_sig = 0
        if (temp_sig + weather_sig + clouds_sig)/3 > 0:
            #send buy signal
        else:
            #send sell signal or hold

    
    def on_econsdatafeed(self, ed):
        pass
        
    def on_orderfeed(self, of):
        pass

    def on_dailyPLfeed(self, pl):
        pass

    def on_openPositionfeed(self, op, oo, uo):
        pass
