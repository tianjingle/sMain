import json
import os

from src.Core import Core
from src.Industry import Industry
# 概念扫描
class HangYe:
    core=Core()
    industray=Industry()
    myBuy = []
    mySell = []
    # 板块文件地址
    BANKUAN_Buy_Sell_PATH = os.path.join(os.path.dirname(__file__), "industry_result.txt")

    def scan(self):
        bankuan=self.industray.get_bankuan_names()
        for item in bankuan:
            print(item)
            self.core.start=-1
            NewtonBuySall,profit,currentIndex=self.core.execute(item,5,15,0,False)
            if NewtonBuySall ==None:
                continue
            isToday = False
            caozuoHistory = sorted(NewtonBuySall, key=lambda x: x[0], reverse=True)
            flag = -1
            for mmzd in caozuoHistory[:3]:
                if mmzd[0] > currentIndex:
                    flag = mmzd[1]
                    isToday = True
                    if flag > 0:
                        operation = "买"
                        self.myBuy.append(item)
                    else:
                        operation = "卖"
                        self.mySell.append(item)
                if isToday == False and mmzd[0] == currentIndex:
                    flag = mmzd[1]
                    isToday = True
                    if flag > 0:
                        self.myBuy.append(item)
                        operation = "买"
                    else:
                        self.mySell.append(item)
                        operation = "卖"
                else:
                    isToday = False
            if isToday:
                print(item)
        with open(self.BANKUAN_Buy_Sell_PATH, "w") as f:
            f.write(json.dumps(dict(buy=self.myBuy,sell=self.mySell)))

    def getBuySellIndustry(self):
        with open(self.BANKUAN_Buy_Sell_PATH) as f:
            return json.load(f)["buy"]

HangYe().scan()
buy=HangYe().getBuySellIndustry()
print(buy)
