import backtrader as bt
import datetime
from strategiesTestowa2 import TestStrategy
import matplotlib
import itertools 
from backtrader_plotting import Bokeh
from backtrader_plotting.schemes import Tradimo
import pandas as pd


cerebro = bt.Cerebro()

cerebro.broker.set_cash(1000000)

class BarAnalysis(bt.analyzers.Analyzer):

    def start(self):
        self.rets = list()

    def next(self):
        try:
            self.rets.append(
                [
                    self.datas[0].datetime.datetime(),
                    #self.datas[0].open[0],
                    self.datas[0].close[0],
                    #self.datas[1].open[0],
                    self.datas[1].close[0],
                    self.datas[2].close[0],
                    self.strategy.getposition(data = self.datas[0]).size,
                    self.strategy.getposition(data = self.datas[1]).size,                    
                    #self.strategy.broker.getvalue(),
                    #self.strategy.broker.getcash(),
                    self.strategy.Pair1Exposure,
                    self.strategy.Pair2Exposure,
                    #self.strategy.sum,
                    len(self),
                    #self.strategy.holdingDate,
                    #self.strategy.dailyP_L,
                    #self.strategy.dailyP_L_change_day_by_day,
                    #self.strategy.sumPair1Swap,
                    #self.strategy.priceChangeSum,
                    #self.strategy.pair1_carry_sum,
                    #self.strategy.pair2_carry_sum
                ]
            )
        except:
            pass

    def get_analysis(self):
        return self.rets

instruments = ['NOK', 'PLN', 'Swapy USDDKK', 'Swapy USDPLN']
for instrument in instruments:
    datapath = '%s.csv' % instrument
    # Create a Data Feed
    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2006, 1, 3),
        todate=datetime.datetime(2020, 3, 24),
        reverse=False,
        dtformat="%Y-%m-%d",
        openinterest=-1,
        )

    cerebro.adddata(data, name=instrument)


print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

cerebro.addstrategy (TestStrategy)
#cerebro.run()

print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())




cerebro.addanalyzer(BarAnalysis, _name="bar_data")
strat = cerebro.run()
bar_data_res = strat[0].analyzers.bar_data.get_analysis()
df = pd.DataFrame(bar_data_res)
print(df)
df.to_csv('test.csv')
#b = Bokeh(style='bar', scheme=Tradimo())
#cerebro.plot(b)

#print('Sharpe Ratio:', cerebro.run().analyzers.DD.get_analysis())