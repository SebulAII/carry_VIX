import backtrader as bt
import datetime
from CarryBacktest import TestStrategy
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
                    #self.datas[0].datetime.datetime(),
                    #self.datas[0].close[0],
                    #self.datas[1].close[0],
                    #self.datas[2].close[0],
                    #self.datas[3].close[0],                 
                    #self.strategy.broker.getvalue(),
                    #self.strategy.broker.getcash(),
                    #self.strategy.Pair1Exposure,
                    #self.strategy.Pair2Exposure,
                    #self.strategy.sum,
                    len(self),
                    #self.strategy.holdingDate,
                    #self.strategy.dailyP_L,
                    #self.strategy.dailyP_L_change_day_by_day,
                    #self.strategy.sumPair1Swap,
                    #self.strategy.priceChangeSum,
                    #self.strategy.vol1open,
                    #self.strategy.vol2open,
                    #self.strategy.pair1_carry_sum,
                    #self.strategy.pair2_carry_sum,
                    self.strategy.swapsSum,
                    self.strategy.test_daily_change_summary_report, ## dobry
                    #self.strategy.test_swap_priceChange,
                    #self.strategy.ticket
                ]
            )
        except:
            pass

    def get_analysis(self):
        return self.rets

instruments = ['USDDKK wyrownane ceny', 'USDPLN wyrownane ceny', 'USDDKK wyrownane swapy', 'USDPLN wyrownane swapy']
for instrument in instruments:
    datapath = '%s.csv' % instrument
    # Create a Data Feed
    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2005, 1, 3),
        todate=datetime.datetime(2022, 11, 2),
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
df.to_csv('TEST DO DODANIA 2.csv')
#b = Bokeh(style='bar', scheme=Tradimo())
#cerebro.plot(b)

#print('Sharpe Ratio:', cerebro.run().analyzers.DD.get_analysis())