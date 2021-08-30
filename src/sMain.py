import numpy as np

from src.Banner import Banner
from src.Config import Config
from src.Core import Core

import os


class sMain:

    def train(self):
        print("1.个股参数确定")
        config = Config()
        for stock in config.myStock:
            if int(stock[4])<1 or int(stock[5])<4:
                core=Core()
                core.start=-1
                scale = 30  # 文本进度条宽度
                a = np.arange(3, scale, 1)
                tempProfit=-20
                for item in a:
                    t=item+1
                    a = '*' * t  # 字符串被复制的次数，"*"表示百分比所表达的信息
                    b = '.' * (scale - t)
                    c = (t / scale) * 100  # 输出对应进度条的百分比
                    z = 2 * item + 3
                    NewtonBuySall, profit, currentIndex = core.execute(stock[0], item, z,1)
                    ##print(str(item) + "\t" + str(z) + "\t" + str(profit))
                    if profit>tempProfit:
                        tempProfit=profit
                        stock[4] = item
                        stock[5] = z
                        config.newTrainValue()
                    print("\r{:^3.0f}%[{}->{}]{:^3.0f},{:^3.0f},{:^3.3f}".format(c, a, b,item,z,profit), end="",flush=True)  # dur用来记录打印文本进度条所消耗的时间
                print()


if __name__ == '__main__':
    currentPath = os.getcwd()
    print(currentPath)
    if not os.path.exists(currentPath + "\\temp\\"):
       os.makedirs(currentPath+"\\temp\\")
    banner=Banner()
    banner.bannerShow()
    smain=sMain()
    smain.train()
    core=Core()
    config=Config()
    # print("\033[1;32;40m 2.股票波段计算  \033[0m")
    print("2.股票波段计算")
    if len(config.myStock)>=1:
        core.start(config.myStock)
    else:
        print("没有待选股票~~~~~~")





