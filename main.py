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
        self.keywordList = ["increase", "up", "improve"]
        
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
            #send a buy order
            self.evt.consoleLog(self.arr_MA[-1])
            if not numpy.isnan(self.arr_MA[-1]) and not numpy.isnan(self.arr_MA[-2]):
                if self.arr_MA[-1]>self.arr_MA[-2]:
                    BuySignalMA = 1
                else:
                    BuySignalMA = -1
            self.test_sendorder(BuySignalMA,0,0)

    def on_marketdatafeed(self, md, ab):
        pass

    def on_newsdatafeed(self, nd):
        if nd.lang=="en" and nd.category=="AMERICAS":
            cnt = sum(1 for word in self.keywordList if word in nd.text)
            # check if News content contains all desired keywords
            if cnt==len(self.keywordList):
                BuySignalNews = 1
            else:
                BuySignalNews = -1
        self.test_sendorder(0,BuySignalNews,0)
                
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
        elif weather == "Rain":
            weather_sig = -1
        else:
            weather_sig = 0
        if coulds > badclouds:
            clouds_sig = 1
        elif coulds < goodclouds:
            clouds_sig = -1
        else:
            clouds_sig = 0
        if (temp_sig + weather_sig + clouds_sig)/3 > 0:
            BuySignalWeather = 1
        else:
            #send sell signal or hold
            BuySignalWeather = -1
        self.test_sendorder(0,0,BuySignalWeather)

    
    def on_econsdatafeed(self, ed):
        pass
        
    def on_orderfeed(self, of):
        pass

    def on_dailyPLfeed(self, pl):
        pass

    def on_openPositionfeed(self, op, oo, uo):
        
        pass

    def test_sendorder(self):
        orderObj = AlgoAPIUtil.OrderObject()
        orderObj.instrument = self.myinstrument
        orderObj.openclose = 'open'
        self.evt.consoleLog(self.BuySignalMA)
        total_signal = 0.4*self.BuySignalMA + 0.3*self.BuySignalWeather + 0.3*self.BuySignalNews
        if total_signal > 0:
            orderObj.buysell = 1
        else:
            orderObj.buysell = -1
        orderObj.ordertype = 0
        orderObj.volume = total_signal
        self.evt.sendOrder(orderObj)
