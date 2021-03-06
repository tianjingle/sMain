import numpy as np

from src.Banner import Banner
from src.Config import Config
from src.Core import Core

import os

from src.HangYe import HangYe
from src.Industry import Industry
from src.IndustryCore import IndustryCore


class sMain:

    def train(self):
        print("1.个股参数计算 ")
        config = Config()
        for stock in config.myStock:
            if int(stock[4])<1 or int(stock[5])<4:
                core=Core()
                core.start=-1
                scale = 24  # 文本进度条宽度
                a = np.arange(3, scale, 1)
                tempProfit=-20
                trainTemp=[]
                for item in a:
                    temp=[]
                    temp.append(item)
                    temp.append(2 * item + 3)
                    trainTemp.append(temp)

                    temp=[]
                    temp.append(item)
                    temp.append(2 * item + 2)
                    trainTemp.append(temp)

                    temp=[]
                    temp.append(item)
                    temp.append(2 * item + 1)
                    trainTemp.append(temp)

                    temp=[]
                    temp.append(item)
                    temp.append(2 * item)
                    trainTemp.append(temp)

                    temp=[]
                    temp.append(item)
                    temp.append(2 * item-1)
                    trainTemp.append(temp)

                    temp=[]
                    temp.append(item)
                    temp.append(2 * item-2)
                    trainTemp.append(temp)

                    temp=[]
                    temp.append(item)
                    temp.append(2 * item-3)
                    trainTemp.append(temp)

                scale=len(trainTemp)
                for k in range(len(trainTemp)):
                    item=trainTemp[k][0]
                    t=k+1
                    a = '*' * t  # 字符串被复制的次数，"*"表示百分比所表达的信息
                    b = '.' * (scale - t)
                    c = (t / scale) * 100  # 输出对应进度条的百分比
                    z = trainTemp[k][1]
                    NewtonBuySall, profit, currentIndex = core.execute(stock[0], item, z,1)
                    ##print(str(item) + "\t" + str(z) + "\t" + str(profit))
                    if profit>tempProfit:
                        tempProfit=profit
                        stock[4] = item
                        stock[5] = z
                        config.newTrainValue()
                    print("\r{:^3.0f}%[{}->{}]{:^3.0f},{:^3.0f},{:^3.3f}".format(c, a, b,item,z,profit), end="",flush=True)  # dur用来记录打印文本进度条所消耗的时间
        # print("\033[1;32;40m 1.配置文件规整  \033[0m")


    def start(self):
        # cur_path = os.path.abspath(os.path.dirname(__file__))
        cur_path="C:\zMain-pic"
        tempDir=cur_path+"/temp/"
        if os.path.exists(tempDir)==False:
            os.makedirs(tempDir)
        banner=Banner()
        banner.bannerShow()
        smain=sMain()
        smain.train()
        core=Core()
        config=Config()
        print("2.股票波段计算")
        core.start(config.myStock)

    def doParseCode(self,tt):
        name=""+tt
        if name.startswith("00") or name.startswith("200") or name.startswith("300"):
            return "sz."+name
        return "sh."+tt

    def concept(self):
        # 行业扫描
        HangYe().scan()
        self.getHangyeStock()

    def getHangyeStock(self):
        f = "C:\\Users\\Administrator\\PycharmProjects\\sMain\\src\\IndustryStockResult.txt"

        with open(f, "w") as file:  # 只需要将之前的”w"改为“a"即可，代表追加内容
            industry=Industry()
            industryCore=IndustryCore()
            #获取买入的概念信息
            buyIndustry=HangYe().getBuySellIndustry()
            for itme in buyIndustry:
                #板块成员的code
                itme=itme.replace("@","")
                codes=industry.get_bankuan_members(itme)
                print(codes)
                for one in codes:
                    realcode=self.doParseCode(one)
                    print(realcode)
                    ok,type=industryCore.startA(realcode)
                    if ok:
                        if type!='':
                            one=type+one+"</font>"
                        print(one+"\tshould buy")
                        file.write(one+ "\n")
                        file.flush()

# sMain().getHangyeStock()






