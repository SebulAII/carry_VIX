import backtrader
from backtrader import order
import numpy as np
import statistics as stats



class TestStrategy(backtrader.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.order = None
        self.volume = 100000
        # zmienne do ustalenia wielkości pozycji
        self.pip_av_days = 14
        # zmienne sterujące sygnałem otwarcia/zamknięcia
        self.alpha = 0.023882825238734987
        self.open_threshold = 0.9725866523243761
        self.close_threshold = 1.3107691833629984
        ############################
        self.base_es_volatility_period = 30
        self.n_days = 19 #okres do średniej zmienności w pipsach (z modułów zmienności dziennej)

        #lists
        self.zmiana_w_pipsach_1 = []
        self.zmiana_w_pipsach_2 = []
        self.zmiana_w_pipsach_1_wersja2 = []
        self.zmiana_w_pipsach_2_wersja2 = []
        self.zmiennosc = []
        self.es_volatility = []
        self.differencePips = []
        self.ticket = None
        self.ES_zmiany = []
        self.warmup = 42
        self.Len_average_es = self.warmup + 31
        self.max_module_period = 100
        self.profit = []
        self.holdingDateList = []
        self.dailyP_L_change = []
        self.value_USD_list = []

        self.returns = []

        #listy profitu z carry 
        self.pair1_carry = []
        self.pair2_carry = []
        
        
    def next(self):
        print(len(self))

        if len(self) >2:
            self.zmiana_w_pipsach_1.append(abs((self.datas[0].close[0] - self.datas[0].close[-1]) * 10000))  # AW
            self.zmiana_w_pipsach_2.append(abs((self.datas[1].close[0] - self.datas[1].close[-1]) * 10000))  # AX
            #wygładzanie wersja 2.0 / zmiana dzienności o 1 do góry potrzebne do kolumny BJ
            self.zmiana_w_pipsach_1_wersja2.append(abs((self.datas[0].close[-1] - self.datas[0].close[-2]) * 10000)) #AW    OK
            self.zmiana_w_pipsach_2_wersja2.append(abs((self.datas[1].close[-1] - self.datas[1].close[-2]) * 10000)) #AX    OK

        #suma zmian zmienności (kolumna BJ)
        #wygładzanie
            self.differencePips.append(self.zmiana_w_pipsach_1_wersja2[-1] - self.zmiana_w_pipsach_2_wersja2[-1]) #BJ
            if len(self) ==3:
                self.ES= self.differencePips[0] 
            if len(self) == 4:
                self.ES_zmiany.append(self.differencePips[-1] * self.alpha + self.ES * (1 - self.alpha)) #pierwszy input w liście od BM11
            if len(self) >= 5:
                self.ES_zmiany.append(self.differencePips[-1] * self.alpha + self.ES_zmiany[-1]  * (1 - self.alpha))

            if self.ticket is not None:
                cenka1 = self.datas[0].close[0]
                cenka2 = self.datas[1].close[0]
                self.Pair1Exposure = (self.buyValue - (self.cena1 * self.vol1open))/cenka1
                self.Pair2Exposure = (self.sellValue - (self.cena2 * self.vol2open))/cenka2
                self.holdingDateList.append(len(self))
                self.dailyP_L = ((self.vol1open * (cenka1 - self.openingPrice1))/cenka1) + ((self.vol2open * (cenka2 - self.openingPrice2))/cenka2)
                self.dailyP_L_change.append(self.dailyP_L)
                self.pair1_carry.append(self.datas[2].close[0] * self.Pair1Exposure)
                self.pair2_carry.append(self.datas[3].close[0] * self.Pair2Exposure)
                self.pair1_carry_sum = sum(self.pair1_carry)
                self.pair2_carry_sum = sum(self.pair2_carry)

            if self.ticket is None: 
                self.dailyP_L = 0
                self.value_USD_list.append(self.dailyP_L)
                self.dailyP_L_change.append(self.dailyP_L)
            
            if self.line.idx > self.warmup:
                #średnia wartość pipsa z X dni
                self.Pair1PipsValueCurrent = 1/np.array(self.datas[0].get(size=self.pip_av_days)) * self.volume *0.0001 #X
                self.Pair2PipsValueCurrent = 1/np.array(self.datas[1].get(size=self.pip_av_days)) * self.volume *0.0001 #Y
                
                #średnia zmienność pipsa z ostatnich Y dni
                # 1 PARA 
                ceny1 = np.array(self.datas[0].get(size=self.n_days+1))
                zmiana_ceny1 = abs(ceny1[1:] - ceny1[:-1]) #dzienna zmiana ceny       
                zmiana_w_pipsach1 = np.abs(zmiana_ceny1 * 10000) # dzienna zmiana ceny w pipsach kolumna AK
                srednia_zmiana_w_pipsach1 = np.mean(zmiana_w_pipsach1)
                srednia_zmiana_w_pipsach1_30d = np.mean(self.Pair1PipsValueCurrent[-30:]) #AF
                # 2 PARA
                ceny2 = np.array(self.datas[1].get(size=self.n_days+1))
                zmiana_ceny2 = abs(ceny2[1:] - ceny2[:-1]) #dzienna zmiana ceny 
                zmiana_w_pipsach2 = np.abs(zmiana_ceny2 * 10000) #dzienna zmiana ceny w pipsach  kolumna AL
                srednia_zmiana_w_pipsach2 = np.mean(zmiana_w_pipsach2)
                srednia_zmiana_w_pipsach2_30d = np.mean(self.Pair2PipsValueCurrent[-30:]) #AG
                
                #zmiana dzienna ceny w pipsach do kolumny BJ
                self.dailyPipDifference = (np.abs(zmiana_ceny1[:-1] * 10000)) - (np.abs(zmiana_ceny2[:-1] * 10000))
                #moduł zmienności w pipsach z ostatnich max 480 dni (AN bez mnożenia przez AG) 
                ceny_module1 = np.array(self.datas[0].get(size=len(self)-6)) 
                zmiana_ceny_module_1 = abs(ceny_module1[1:] - ceny_module1[:-1])
                srednia_zmiana_ceny_module_1 = np.abs(zmiana_ceny_module_1 * 10000) #AK
                module1 = np.mean(srednia_zmiana_ceny_module_1)

                 #moduł zmienności w pipsach z ostatnich max 480 dni (AN bez mnożenia przez AG) 
                ceny_module2 = np.array(self.datas[1].get(size=len(self)-1))
                zmiana_ceny_module_2 = abs(ceny_module2[1:] - ceny_module2[:-1])
                srednia_zmiana_ceny_module_2 = np.abs(zmiana_ceny_module_2 * 10000) #AL
                module2 = np.mean(srednia_zmiana_ceny_module_2)

                am = module1 * srednia_zmiana_w_pipsach1_30d #AM
                an = module2 * srednia_zmiana_w_pipsach2_30d #AN
                
                self.size1 = module2 / (module1 + module2) * self.volume
                self.size2 = module1 /(module1 + module2) * self.volume
                
                ao = an/am #usddkk
                ap = 1 #usdpln

                self.vol1 = 100000 * ao #usddkk
                self.vol2 = -100000 * ap #usdpln 

                # update listy: różnica w zmianach dziennych wartości par w pipsach
                self.zmiennosc.append(abs(self.zmiana_w_pipsach_1[-1] - self.zmiana_w_pipsach_2[-1]))
                
                if len(self) <= self.max_module_period:
                #średnia wygładzania od początku
                    all_smooth_av = sum(self.ES_zmiany)/ (len(self)-3)
                    self.cena1 = self.datas[0].close[0]
                    self.cena2 = self.datas[1].close[0]

                    if self.ticket is None and self.ES_zmiany[-1] < (all_smooth_av * self.open_threshold):
                        self.buyValue = self.cena1 * self.vol1
                        self.sellValue = self.cena2 * self.vol2
                        self.ticket = 1
                        self.vol1open = self.vol1 #wolumen otwarcia 1 pozycji
                        self.vol2open = self.vol2 #wolumen otwarcia 2 pozycji
                        self.openingPrice1 = self.datas[0].close[0]
                        self.openingPrice2 = self.datas[1].close[0]

                    if self.ticket is not None and self.ES_zmiany[-1] > (all_smooth_av * self.close_threshold):
                        self.ticket = None
                        self.closeBuyValue = self.cena1 * self.vol1open
                        self.closeSellValue = self.cena2 * self.vol2open
                        self.BuyProfit = (self.closeBuyValue - self.buyValue)/self.cena1
                        self.profit.append(self.BuyProfit)
                        self.SellProfit = (self.closeSellValue - self.sellValue)/ self.cena2
                        self.profit.append(self.SellProfit)
                        self.openingPrice1 = None
                        self.openingPrice2 = None


                if len(self) > self.max_module_period:
                    all_smooth_av = sum(self.ES_zmiany[-self.max_module_period:]) / self.max_module_period
                    self.cena1_1 = self.datas[0].close[0]
                    self.cena2_2 = self.datas[1].close[0]
                    if self.ticket is None and self.ES_zmiany[-1] < (all_smooth_av * self.open_threshold):
                        self.ticket = 1
                        self.buyValue = self.cena1_1 * self.vol1 #wartość otwarcia pozycji 1 
                        self.sellValue = self.cena2_2 * self.vol2 #wartość otwarcia pozycji 2 
                        self.vol1open = self.vol1 #wolumen otwarcia 1 pozycji
                        self.vol2open = self.vol2 #wolumen otwarcia 2 pozycji
                        self.value_USD = self.buyValue/self.cena1_1 + self.sellValue/self.cena2_2
                        self.openingPrice1 = self.datas[0].close[0]
                        self.openingPrice2 = self.datas[1].close[0]


                    if self.ticket is not None and self.ES_zmiany[-1] > (all_smooth_av * self.close_threshold):
                        self.ticket = None
                        self.closeBuyValue = self.cena1_1 * self.vol1open
                        self.closeSellValue = self.cena2_2 * self.vol2open
                        self.BuyProfit = (self.closeBuyValue - self.buyValue)/self.cena1_1
                        self.profit.append(self.BuyProfit)
                        self.SellProfit = (self.closeSellValue - self.sellValue)/ self.cena2_2
                        self.profit.append(self.SellProfit)
                        self.openingPrice1 = None
                        self.openingPrice2 = None
                
                #if len(self) == 541:
                #    self.log('0')

                #Sharpe Ratio
                if self.dailyP_L_change[-1] !=0:
                    self.returns.append(self.dailyP_L_change[-1] - self.dailyP_L_change[-2])

                    if self.returns[-1] != 0 and len(self.returns) > 1 and self.ticket is not None:
                        self.sharpe_ratio = sum(self.returns)/len(self) / stats.stdev(self.returns)
                        self.annualised_sharpe_ratio = self.sharpe_ratio*252**0.5
                
                    self.pair1PriceChange = self.datas[0].close[0] - self.datas[0].close[1]
                    self.pair2PriceChange = self.datas[1].close[0] - self.datas[1].close[1]