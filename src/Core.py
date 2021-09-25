import os


import matplotlib.pyplot as plt
from matplotlib.pylab import date2num
import matplotlib.ticker as ticker  # 用于日期刻度定制
import baostock as bs
import pandas as pd
import numpy as np
import datetime
from matplotlib import colors as mcolors  # 用于颜色转换成渲染时顶点需要的颜色格式
from matplotlib.collections import LineCollection, PolyCollection  # 用于绘制直线集合和多边形集合
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import talib




from src.Config import Config

#线性回归
from scipy.optimize import leastsq
import time

from src.ChipCalculate import ChipCalculate

class Core:
    stackCode="sz.000918"
    isIndex=False
    window=80
    totalRmb=1000000
    baseRmb=totalRmb
    handTotal=0
    buysell=[]
    myRmb=[]
    #线性回归横坐标
    XI=[]
    #线性回归纵坐标
    YI=[]
    erChengPrice=[]
    Kflag=[]
    erjieK=[]
    KlineBuySellFlag=[]
    downlimit=-100
    date_tickers=[]
    priceJJJ=0
    result=None
    start=-1
    currentPrice=0
    startRmb=0
    def date_to_num(self,dates):
        num_time = []
        for date in dates:
            date_time = datetime.datetime.strptime(date,'%Y-%m-%d')
            num_date = date2num(date_time)
            num_time.append(num_date)
        return num_time

    # 绘制蜡烛图
    def format_date(self,x, pos=None):
        # 日期格式化函数，根据天数索引取出日期值
        return '' if x < 0 or x > len(self.date_tickers) - 1 else self.date_tickers[int(x)]


    ##需要拟合的函数func :指定函数的形状 k= 0.42116973935 b= -8.28830260655
    def func(self,p, x):
        k, b = p
        return k * x + b


    ##偏差函数：x,y都是列表:这里的x,y更上面的Xi,Yi中是一一对应的
    def error(self,p, x, y):
        return self.func(p, x) - y


    def everyErChengPrice(self,sourceResult,step):
        # k,b的初始值，可以任意设定,经过几次试验，发现p0的值会影响cost的值：Para[1]
        Kflag=[]
        p0=[1,20]
        #最前的7天都不计算
        count=len(sourceResult)
        if count-step<0:
            return
        for i in range(count):
            temp=[]
            ktemp=[]
            myStart=i
            myEnd=i+step
            if myEnd>count:
                break
            XI=sourceResult.values[myStart:myEnd][:,0]
            YI=sourceResult['tprice'][myStart:myEnd]
            # 把error函数中除了p0以外的参数打包到args中(使用要求)
            Para = leastsq(self.error, p0, args=(XI, YI))
            # 读取结果
            k, b = Para[0]
            temp.append(XI)
            temp.append(k * XI + b)
            self.erChengPrice.append(temp)
            #回归的变化率
            ktemp.append(myEnd)
            ktemp.append(k)
            Kflag.append(ktemp)
        return Kflag


    def everyErChengPriceForArray(self,sourceX,sourceY,step):
        # k,b的初始值，可以任意设定,经过几次试验，发现p0的值会影响cost的值：Para[1]
        Kflag=[]
        p0=[1,20]
        #最前的7天都不计算
        count=len(sourceX)
        if count-step<0:
            return
        for i in range(count):
            temp=[]
            ktemp=[]
            myStart=i
            myEnd=i+step
            if myEnd>count:
                break
            XI=sourceX[myStart:myEnd]
            YI=sourceY[myStart:myEnd]
            # 把error函数中除了p0以外的参数打包到args中(使用要求)
            Para = leastsq(self.error, p0, args=(XI, YI))
            # 读取结果
            k, b = Para[0]
            temp.append(XI)
            temp.append(k * XI + b)
            self.erChengPrice.append(temp)
            #回归的变化率
            ktemp.append(myEnd)
            ktemp.append(k)
            Kflag.append(ktemp)
        return Kflag

    def doubleErJie(self,yijieList,step):
        erjieK=[]
        # k,b的初始值，可以任意设定,经过几次试验，发现p0的值会影响cost的值：Para[1]
        p0 = [1, 20]
        # 最前的7天都不计算
        count = len(yijieList)
        if count - step < 0:
            return
        for i in range(count):
            ktemp = []
            myEnd = i + step
            if myEnd > count:
                break
            tempX=[]
            tempY=[]
            for j in range(step):
                tempX.append(yijieList[i+j][0])
                tempY.append(yijieList[i+j][1])
            # 把error函数中除了p0以外的参数打包到args中(使用要求)
            Para = leastsq(self.error, p0, args=(np.array(tempX), np.array(tempY)))
            # 读取结果
            k, b = Para[0]
            # 回归的变化率
            ktemp.append(myEnd)
            ktemp.append(k*5)
            ktemp.append(0)
            erjieK.append(ktemp)
        return erjieK

    def init(self):
        stackCode = "sh.000001"
        isIndex = True
        # isIndex=False
        self.window = 120
        self.totalRmb = 5000
        self.baseRmb = 5000
        self.handTotal = 0
        self.buysell = []
        self.myRmb = []
        # 线性回归横坐标
        self.XI = []
        # 线性回归纵坐标
        self.YI = []
        self.erChengPrice = []
        self.Kflag = []
        self.erjieK = []
        self.KlineBuySellFlag = []
        self.downlimit = -100
        self.date_tickers = []

    def testNewTon(self,NewtonBuySall,indexCloseDict):
        self.startRmb=self.totalRmb
        list=[]
        NewtonBuySall=sorted(NewtonBuySall,key=lambda x: x[0])
        for item in NewtonBuySall:
            if indexCloseDict.get(item[0]+1)!= None:
                price = float(indexCloseDict.get(item[0]+1))
            else:
                if indexCloseDict.get(item[0])!=None:
                    price = float(indexCloseDict.get(item[0]))
                else:
                    price = 10
            # 买入
            if item[1] == 1:
                currentRmb = price * 100 * 1.000
                if self.totalRmb - currentRmb > 0:
                    self.totalRmb = self.totalRmb - currentRmb
                    self.handTotal = self.handTotal + 1
                    self.buysell.append(item[0])
                    self.myRmb.append(self.totalRmb + self.handTotal * 100 * price)
                    #print("buy----总金额：" + str(self.totalRmb) + "   总手数" + str(self.handTotal) + "   账户总金额：" + str(
                        # self.totalRmb + self.handTotal * 100 * price))
                else:
                    self.buysell.append(item[0])
                    self.myRmb.append(self.totalRmb + self.handTotal * 100 * price)
                    #print("buy---资金不足")
            elif item[1] == -1:
                if self.handTotal > 0:
                    currentRmb = self.handTotal * 100 * price * 1
                    self.totalRmb = self.totalRmb + currentRmb
                    self.buysell.append(item[0])
                    self.myRmb.append(self.totalRmb)
                    self.handTotal = 0
                    #print("sell-----总金额：" + str(self.totalRmb) + "   总手数" + str(self.handTotal) + "   账户总金额：" + str(self.totalRmb))
                else:
                    self.buysell.append(item[0])
                    self.myRmb.append(self.totalRmb)
                    #print("sell----不用再往出卖了")
            elif item[1]==0:
                self.buysell.append(item[0])
                self.myRmb.append(self.totalRmb)
            if self.handTotal>0:
                profit=((self.totalRmb+((self.handTotal * 100) * price))-self.startRmb)/self.startRmb*100
                #print("shouyi01:"+str(profit)+"%")
            else:
                profit=(self.totalRmb-self.startRmb)/self.startRmb*100
                #print("shouyi1:" + str(profit) + "%")
            list.append(profit)
        # for item in list:
            #print("收益率："+str(round(item,2))+"%")
        return list[len(list)-1]

    def chipCalculate(self,result,start):
        chipCalculateList=[]
        #传入的数据id,open,high,low,close,volume,typePrice,turn
        #          0,   1,   2,  3,   4,    5,    6,       7
        for index, row in result.iterrows():
            temp=[]
            currentIndex=index-start
            temp.append(currentIndex)
            temp.append(row['open'])
            temp.append(row['high'])
            temp.append(row['low'])
            temp.append(row['close'])
            temp.append(row['volume'])
            temp.append(row['tprice'])
            temp.append(row['turn'])
            chipCalculateList.append(temp)
        calcualate=ChipCalculate()
        resultEnd=calcualate.getDataByShowLine(chipCalculateList)
        return resultEnd

    def getResult(self,code):
        endDate = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        lg = bs.login()
        rs = bs.query_history_k_data_plus(code,
                                          "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                          start_date='2018-11-01', end_date=endDate,
                                          frequency="d", adjustflag="2")

        #### 打印结果集 ####
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        self.result = pd.DataFrame(data_list, columns=rs.fields)
        # print(self.result)
        self.start = len(self.result) - self.window
        # 二维数组
        self.result = self.result.loc[:, ['date', 'open', 'high', 'low', 'close', 'volume', 'turn']]
        # print(self.result)
        if code == 'sh.000001':
            self.result['temp'] = 1000
            self.result['open'] = talib.DIV(self.result['open'], self.result['temp'])
            self.result['high'] = talib.DIV(self.result['high'], self.result['temp'])
            self.result['low'] = talib.DIV(self.result['low'], self.result['temp'])
            self.result['close'] = talib.DIV(self.result['close'], self.result['temp'])

        self.result = self.result[-self.window:]
        # 计算三十日均线
        self.result['M30'] = talib.SMA(self.result['close'], 30)
        self.result['T30'] = talib.T3(self.result['close'], timeperiod=30, vfactor=0)
        self.result['tprice'] = talib.TYPPRICE(self.result['high'], self.result['low'], self.result['close'])
        slowk, slowd = talib.STOCH(self.result['high'], self.result['low'], self.result['close'], fastk_period=9, slowk_period=3,
                                   slowk_matype=0, slowd_period=3, slowd_matype=0)
        slowj = list(map(lambda x, y: 3 * x - 2 * y, slowk, slowd))
        self.result['k'] = slowk
        self.result['d'] = slowd
        self.result['j'] = slowj
        # 主力线，散户线
        zz, ss = self.zsLine(self.result)
        mm = self.convertXQH(self.result)
        self.result['z'] = zz
        self.result['s'] = ss
        self.result['m'] = mm

        self.result['VAR618']=618
        self.result['VAR100']=100
        self.result['VAR10']=10
        self.result['VAR0']=0

        #主力散户吸筹
        # VAR2:=REF(LOW,1);      前一日的最低价
        self.result['VAR2'] = self.result['low']
        self.result['VAR2']=self.result['VAR2'].shift(1)
        self.result=self.result.fillna(0)
        self.result['low']=self.result['low'].astype(float)
        self.result['VAR2']=self.result['VAR2'].astype(float)
        self.result['closeP']=self.result['close']
        self.result['closeP']=self.result['closeP'].astype(float)

        # VAR3 := SMA(ABS(LOW - VAR2), 3, 1) / SMA(MAX(LOW - VAR2, 0), 3, 1) * 100;
        self.result['LOW_VAR2']=self.result['low']-self.result['VAR2']
        self.result['var3Pre']=talib.SMA(self.result['LOW_VAR2'].abs(),3)
        self.result = self.result.assign(var3sub=np.where(self.result.LOW_VAR2 > 0, self.result.LOW_VAR2, 0.00000000000000000001))
        self.result['var3sub']=talib.SMA(self.result['var3sub'],3)

        self.result['VAR3']=talib.MULT(talib.DIV(self.result['var3Pre'],self.result['var3sub']),self.result['VAR100'])
        self.result=self.result.assign(tianjingle=np.where(self.result.closeP*1.3!=0,round(self.result.VAR3*10,2),self.result.VAR3/10))
        self.result['tianjingle']=self.result['tianjingle'].astype(float)
        self.result['tianjingle'].fillna(0)
        self.result['VAR4']=talib.EMA(self.result['tianjingle'],3)
        #print(self.result['VAR4'])
        # VAR5 := LLV(LOW, 30);
        self.result['VAR5']=self.result['low'].rolling(30).min()
        # VAR6 := HHV(VAR4, 30);
        self.result['VAR6']=self.result['VAR4'].rolling(30).max()
        #print(self.result['VAR6'])
        # VAR7 := IF(MA(CLOSE, 58), 1, 0);
        self.result['VAR7temp']=talib.MA(self.result['close'], 58)
        #这里做判断
        self.result=self.result.assign(VAR7=np.where(self.result.VAR7temp!=0,1,0))
        # VAR8 := EMA(IF(LOW <= VAR5, (VAR4 + VAR6 * 2) / 2, 0), 3) / 618 * VAR7;
        self.result=self.result.assign(VAR8TEMP=np.where(self.result.low<=self.result.VAR5,(self.result.VAR4+self.result.VAR6*2)/2,0))
        self.result['VAR8TEMP']=talib.EMA(self.result['VAR8TEMP'],3)
        self.result['VAR8']=talib.MULT(talib.DIV(self.result['VAR8TEMP'],self.result['VAR618']),self.result['VAR7'])
        #print(self.result['VAR8'].max())
        #print(self.result['VAR8'].min())
        self.result['VAR8']=self.result['VAR8']/10000000000000000000
        # VAR9 := IF(VAR8 > 100, 100, VAR8);
        self.result=self.result.assign(VAR9=np.where(self.result.VAR8>100,100,self.result.VAR8))
        #输出吸筹:当满足条件VAR9>-120时,在0和VAR9位置之间画柱状线,宽度为2,5不为0则画空心柱.,画洋红色
        # 输出地量:当满足条件0.9上穿1/成交量(手)*1000>0.01AND"KDJ的J"<0时,在最低价*1位置书写文字,COLOR00FFFF
        # 吸筹: STICKLINE(VAR9 > -120, 0, VAR9, 2, 5), COLORMAGENTA;
        # 地量: DRAWTEXT(CROSS(0.9, 1 / VOL * 1000 > 0.01 AND "KDJ.J" < 0), L * 1, '地量'), COLOR00FFFF;
        self.result=self.result.assign(VARXC=np.where(self.result.VAR9>5,self.result.VAR9,0))
        #print(self.result[['low','VAR4','VAR5','VAR6','VAR7','VAR8','VAR9','VARXC']])
        return self.result,self.start








    def execute(self,code,mywidth,mylength,isTest):
        self.init()
        if self.start==-1:
            #print("result is None...")
            self.result, self.start=self.getResult(code)

        # 计算KDJ值，数据存于DataFrame中
        # date_tickers=result.date.values
        self.result.date = range(0, len(self.result))  # 日期改变成序号
        matix = self.result.values  # 转换成绘制蜡烛图需要的数据格式(date, open, close, high, low, volume)


        self.current=self.result[-1:]
        #逐个计算最近7天的趋势
        self.currentPrice=float(self.current.iloc[0].iat[4])
        myyj=mywidth
        Kflag=self.everyErChengPrice(self.result,mywidth)
        erjieSlow=self.everyErChengPrice(self.result,mylength)
        #将收盘价转化为字典
        testX=[]
        testY=[]
        VARXCX = []
        VARXCHIGH = []
        for index, row in self.result.iterrows():
            currentIndex=index-self.start
            price=row['close']
            XCH=row['VARXC']
            if float(XCH)>0:
                VARXCX.append(currentIndex)
                VARXCHIGH.append(float(XCH))
            testX.append(currentIndex)
            testY.append(price)
        indexCloseDict=dict(zip(testX,testY))


        xdates = matix[:,0] # X轴数据(这里用的天数索引)
        t3Price = talib.T3(self.result['close'], timeperiod=30, vfactor=0)
        # 设置外观效果



        plt.rc('font', family='Microsoft YaHei')  # 用中文字体，防止中文显示不出来
        plt.rc('figure', fc='k')  # 绘图对象背景图
        plt.rc('text', c='#800000')  # 文本颜色
        plt.rc('axes', axisbelow=True, xmargin=0, fc='k', ec='#800000', lw=1.5, labelcolor='#800000',
               unicode_minus=False)  # 坐标轴属性(置底，左边无空隙，背景色，边框色，线宽，文本颜色，中文负号修正)
        plt.rc('xtick', c='#d43221')  # x轴刻度文字颜色
        plt.rc('ytick', c='#d43221')  # y轴刻度文字颜色
        plt.rc('grid', c='#800000', alpha=0.9, ls=':', lw=0.8)  # 网格属性(颜色，透明值，线条样式，线宽)
        plt.rc('lines', lw=0.8)  # 全局线宽
        # 创建绘图对象和4个坐标轴
        fig = plt.figure(figsize=(16, 8))
        left, width = 0.05, 0.9
        ax1 = fig.add_axes([left, 0.5, width, 0.48])  # left, bottom, width, height
        ax2 = fig.add_axes([left, 0.25, width, 0.24], sharex=ax1)  # 共享ax1轴
        ax3 = fig.add_axes([left, 0.15, width, 0.09], sharex=ax1)  # 共享ax1轴
        # ax4 = fig.add_axes([left, 0.15, width, 0.09], sharex=ax1)  # 共享ax1轴
        ax5 = fig.add_axes([left, 0.05, width, 0.09], sharex=ax1)  # 共享ax1轴
        ax6 = fig.add_axes([left, 0.01, width, 0.04], sharex=ax1)  # 共享ax1轴
        plt.setp(ax1.get_xticklabels(), visible=True)  # 使x轴刻度文本不可见，因为共享，不需要显示
        plt.setp(ax2.get_xticklabels(), visible=True)  # 使x轴刻度文本不可见，因为共享，不需要显示
        ax1.xaxis.set_major_formatter(ticker.FuncFormatter(self.format_date))  # 设置自定义x轴格式化日期函数
        ax1.xaxis.set_major_locator(ticker.MultipleLocator(max(int(len(self.result) / 15), 5)))  # 横向最多排15个左右的日期，最少5个，防止日期太拥挤
        # # 下面这一段代码，替换了上面注释的这个函数，因为上面的这个函数达不到同花顺的效果
        opens, closes, highs, lows = matix[:, 1], matix[:, 4], matix[:, 2], matix[:, 3]  # 取出ochl值
        avg_dist_between_points = (xdates[-1] - xdates[0]) / float(len(xdates))  # 计算每个日期之间的距离
        delta = avg_dist_between_points / 4.0  # 用于K线实体(矩形)的偏移坐标计算
        barVerts = [((date - delta, open), (date - delta, close), (date + delta, close), (date + delta, open)) for date, open, close in zip(xdates, opens, closes)]  # 生成K线实体(矩形)的4个顶点坐标
        rangeSegLow = [((date, low), (date, min(open, close))) for date, low, open, close in  zip(xdates, lows, opens, closes)]  # 生成下影线顶点列表
        rangeSegHigh = [((date, high), (date, max(open, close))) for date, high, open, close in zip(xdates, highs, opens, closes)]  # 生成上影线顶点列表
        rangeSegments = rangeSegLow + rangeSegHigh  # 上下影线顶点列表
        cmap = {
                True: mcolors.to_rgba('#000000', 1.0),
                False: mcolors.to_rgba('#54fcfc', 1.0)
           }  # K线实体(矩形)中间的背景色(True是上涨颜色，False是下跌颜色)
        inner_colors = [cmap[opn < cls] for opn, cls in zip(opens, closes)]  # K线实体(矩形)中间的背景色列表
        cmap = {True: mcolors.to_rgba('#ff3232', 1.0),
                False: mcolors.to_rgba('#54fcfc', 1.0)}  # K线实体(矩形)边框线颜色(上下影线和后面的成交量颜色也共用)
        updown_colors = [cmap[opn < cls] for opn, cls in zip(opens, closes)]  # K线实体(矩形)边框线颜色(上下影线和后面的成交量颜色也共用)列表
        ax1.add_collection(LineCollection(rangeSegments, colors=updown_colors, linewidths=0.5,antialiaseds=True))
        # 生成上下影线的顶点数据(颜色，线宽，反锯齿，反锯齿关闭好像没效果)
        ax1.add_collection(PolyCollection(barVerts, facecolors=inner_colors, edgecolors=updown_colors, antialiaseds=True,linewidths=0.5))
        # 生成多边形(矩形)顶点数据(背景填充色，边框色，反锯齿，线宽)
        # 绘制均线
        mav_colors = ['#ffffff', '#d4ff07', '#ff80ff', '#00e600', '#02e2f4', '#ffffb9', '#2a6848']  # 均线循环颜色
        mav_period = [5, 10]  # 定义要绘制的均线周期，可增减
        n = len(self.result)
        for i in range(len(mav_period)):
            if n >= mav_period[i]:
                mav_vals = self.result['close'].rolling(mav_period[i]).mean().values
                if i==0:
                    priceTwo=mav_vals
                ax1.plot(xdates, mav_vals, c=mav_colors[i % len(mav_colors)], label='MA' + str(mav_period[i]))

        ax1.plot(xdates,t3Price,label='t3price')
        ax1.set_title('sz.002918')  # 标题
        ax1.grid(True)  # 画网格
        ax1.legend(loc='upper left')  # 图例放置于右上角
        ax1.xaxis_date()  # 好像要不要效果一样？

        #计算二阶导数
        erjieK=self.doubleErJie(Kflag,3)
        x1=[]
        y1=[]
        currentIndex=0
        for index, row in self.result.iterrows():
            currentIndex=index-self.start
            x1.append(currentIndex)
            y1.append(row['tprice'])
        #筹码计算
        resultEnd=self.chipCalculate(self.result,self.start)

        x=[]
        p=[]
        priceBigvolPriceIndexs=[]
        resultEnd.sort(key=lambda resultEnd: resultEnd[0])
        resultEndLength=len(resultEnd)
        string=""
        mystart=0
        bigVolPrice={}
        for i in range(len(resultEnd)):
            if i==0:
                mystart=resultEnd[i][0]
            x.append(resultEnd[i][0])
            string=string+","+str(resultEnd[i][1])
            p.append(resultEnd[i][1])
            if i==resultEndLength-1:
                self.priceJJJ=resultEnd[i][1]
            if resultEnd[i][4]==1:
                priceBigvolPriceIndexs.append(resultEnd[i][0])
                bigVolPrice[resultEnd[i][0]]=1

        myResult = pd.DataFrame()
        myResult['tprice']=p
        tianjingle=self.everyErChengPriceForArray(np.array(x),np.array(p),myyj)
        x1=[]
        y1=[]
        for item in tianjingle:
            kX = item[0]
            kk = item[1]
            if kk>0 and len(y1)>3 and y1[len(y1)-1]>kk and y1[len(y1)-2]>y1[len(y1)-3]:
                ax3.axvline(kX + mystart, ls='-', c='r', lw=2)
            if kk>0 and len(y1)>2 and y1[len(y1)-1]<0:
                ax1.axvline(kX + mystart, ls='-', c='orange',ymin=0.5,ymax=0.7, lw=2)
            if kk<0 and len(y1)>2 and y1[len(y1)-1]>0:
                ax1.axvline(kX + mystart, ls='-', c='b',ymin=0.4,ymax=0.6, lw=2)

            x1.append(kX+mystart)
            y1.append(kk)
        pingjunchengbendic = dict(zip(x1, y1))
        #一节导数
        ax3.plot(x1, y1, color="orange", linewidth=1, label='一阶导数')

        # choumaerJieTidu=everyErChengPriceForArray(np.array(x1),np.array(y1),myyj)

        # choumaErX=[]
        # choumaErY=[]
        # # old=0
        # for item in choumaerJieTidu:
        #     kX = item[0]
        #     kk = item[1]
        #     if kk<0 and len(choumaErY)>3 and choumaErY[len(choumaErY)-1]<kk and choumaErY[len(choumaErY)-2]<choumaErY[len(choumaErY)-3]:
        #         ax4.axvline(kX+mystart+myyj, ls='-', c='#33FFff', lw=2)
        #     choumaErX.append(kX+mystart+myyj)
        #     choumaErY.append(kk)
        # ax3.plot(choumaErX, choumaErY, color="#33FFff", linewidth=1,label='慢速导数')

        #print("平均成本移动")
        #print(tianjingle)
        ax1.plot(x, p, c='orange',linewidth=2, label='移动成本')

        #线性回归展示
        wangX=[]
        wangY=[]
        for item in Kflag:
            kX=item[0]
            kk=item[1]
            wangX.append(kX)
            wangY.append(kk)
        ax2.plot(wangX, wangY, color="w", linewidth=1,label='一阶导数')
        yijiedict=dict(zip(wangX,wangY))

        wangX=[]
        wangY=[]
        for item in erjieK:
            kX=item[0]+myyj
            kk=item[1]
            wangX.append(kX)
            wangY.append(kk)
        ax2.plot(wangX, wangY, color="y", linewidth=1,label='二阶导数')

        wangXSlow=[]
        wangYSlow=[]
        for item in erjieSlow:
            kX1=item[0]
            kk1=item[1]
            wangXSlow.append(kX1)
            wangYSlow.append(kk1)
        ax3.axhline(0,ls='-', c='g', lw=0.5)


        yijieSlowdict=dict(zip(wangXSlow,wangYSlow))
        NewtonBuySall=[]

        oldTwok=0
        oldOne=0

        downlimitTemp=0
        #找到最小的那一个
        for item in erjieK:
            if item[1]!=None and item[1]<downlimitTemp:
                downlimitTemp=item[1]
        downlimitTemp=abs(downlimitTemp)

        #print("最小值"+str(downlimitTemp))
        for item in erjieK:
            item[2]=item[1]/downlimitTemp*100
            #print("最小值："+str(downlimitTemp)+"  当前二阶："+str(item[1])+"  百分比："+str(item[2]))

        #print(yijieSlowdict)
        #print("---------------")
        #print(pingjunchengbendic)
        for i in range(len(erjieK)):
            item=erjieK[i]
            currentx=item[0]+myyj-1
            twok=item[1]
            downParent=item[2]
            onek=yijiedict.get(currentx)
            onkslow=yijieSlowdict.get(currentx)
            onkchengben=pingjunchengbendic.get(currentx)

            #print(str(onkslow)+"--"+str(onkchengben))
            if onek==None or onkslow ==None or onkchengben==None:
                continue
            if onkslow<0 and onkchengben<0:
                #print("ytes")
                onslowyestaday=yijieSlowdict.get(currentx)
                chengbenyestaday=pingjunchengbendic.get(currentx)
                if onslowyestaday == None or chengbenyestaday == None:
                    continue
                if onslowyestaday<0 and chengbenyestaday<0 and onslowyestaday<onkslow and onkchengben<chengbenyestaday:
                    # ax1.axvline(currentx,ls='-', c='g', lw=0.5)
                    if bigVolPrice.__contains__(currentx):
                        newTonTemp = []
                        newTonTemp.append(currentx)
                        newTonTemp.append(1)
                        # 1表示吸筹买入
                        newTonTemp.append("XC-MR")
                        newTonTemp.append("<b style=\"background-color:rgba(255,255,0);font-size:20px;line-height:20px;margin:0px 0px;\">🌈🌈🌈买入：此处应该吸筹买入，当下筹码集中，获利股东大于50%，此时的股票基本处于底部，未来爆发的潜力很大。<font color='red'>但是也不排除此刻是底部的相对高位，您可以在此刻买入1手，一般情况下，股价会有回调,暴涨之后这里不建议买入。/font></b>")
                        NewtonBuySall.append(newTonTemp)
                        ax1.axvline(currentx, ls='-', c='g', lw=5,ymin=0,ymax=0.02)
                    # ax2.axvline(currentx, ls='-',color="g", lw=2)
            if onkslow<0:
                # newTonTemp = []
                # newTonTemp.append(currentx)
                # newTonTemp.append(-1)
                # NewtonBuySall.append(newTonTemp)
                # ax1.axvline(currentx,ls='-', c='orange', lw=0.5)
                # ax2.scatter(currentx, twok, color="orange", linewidth=0.0004)
                continue
            #一阶导数大于0，二阶导数大于0，一阶导数大于二阶导数，二阶导数递减
            if oldTwok>0 and oldOne>0 and oldTwok>=oldOne and onek>0 and onek<twok:
                #添加历史回测里
                newTonTemp = []
                newTonTemp.append(currentx)
                newTonTemp.append(-1)
                #高位清仓
                newTonTemp.append("DDQC-MC")
                newTonTemp.append("<b style=\"background-color:rgba(255,255,0);font-size:20px;line-height:20px;margin:0px 0px;\">⛈⛈⛈卖出：此处可能是潜在的历史高位，应该卖出，<font color='red'>但股价趋势向上，而且移动平均成本与当前价位差别较小，就应该继续持股等待。</font></b>")
                NewtonBuySall.append(newTonTemp)
                ax1.axvline(currentx,ls='-', c='r',ymin=1, ymax=0.95, lw=2)
                # ax2.axvline(currentx, color="r", ls='-',lw=1)
            if oldOne>0 and onek>0 and oldOne>onek and oldTwok>oldOne and onek>twok:
                #添加历史回测里
                newTonTemp = []
                newTonTemp.append(currentx)
                newTonTemp.append(-1)
                newTonTemp.append("XDDQC-MC")
                newTonTemp.append("<b style=\"background-color:rgba(255,255,0);font-size:20px;line-height:20px;margin:0px 0px;\">⛈⛈⛈卖出：待验证的顶点判断：此处可能是潜在的历史高位<，应该卖出，<font color='red'>但股价趋势向上，而且移动平均成本与当前价位差别较小，就应该继续持股等待。</font></b>")
                NewtonBuySall.append(newTonTemp)
                ax1.axvline(currentx,ls='-', c='r',ymin=1, ymax=0.95, lw=2)
                # ax2.axvline(currentx, color="r", ls='-',lw=1)
            # if  onek>0 and oldOne<0:
            #     #添加历史回测里
            #     newTonTemp = []
            #     newTonTemp.append(currentx)
            #     newTonTemp.append(-1)
            #     NewtonBuySall.append(newTonTemp)
            #     ax1.axvline(currentx,ls='-', c='orange', lw=0.5)
            #     ax2.scatter(currentx, twok, color="orange", linewidth=0.0004)
            #一阶导数小于0，二阶导数小于0,一阶导数小于二阶导数，二阶导数递增,并且在之前的三天都被一阶导数压制
            # if onek<=0 and twok>onek and oldTwok<oldOne and downParent<downlimit and abs(twok-oldTwok)>abs(onek-oldOne):
            # if onek<0 and twok>onek and oldTwok<onek:
                #print(1)
                #添加到历史回测里
                # newTonTemp = []
                # newTonTemp.append(currentx)
                # newTonTemp.append(1)
                # newTonTemp.append("XMR")
                # newTonTemp.append("<b style=\"background-color:rgba(255,255,0);font-size:20px;line-height:20px;margin:0px 0px;\">待验证的买点.....请不要乱操作</b>")
                # NewtonBuySall.append(newTonTemp)
                # ax1.axvline(currentx,ls='-', c='g', lw=2)
            elif onek <= 0 and twok > onek and oldTwok < oldOne and downParent > self.downlimit and twok>0:
                # newTonTemp = []
                # newTonTemp.append(currentx)
                # newTonTemp.append(1)
                # NewtonBuySall.append(newTonTemp)
                ax2.axvline(currentx, color="#5EA26B", ls='-',lw=1)
                ax1.axvline(currentx,ls='-', c='#5EA26B', lw=0.5)
            # elif onek <= 0 and twok > onek and oldTwok < oldOne and downParent > self.downlimit and twok<0:
                # newTonTemp = []
                # newTonTemp.append(currentx)
                # newTonTemp.append(1)
                # NewtonBuySall.append(newTonTemp)
                # ax2.axvline(currentx, color="g", ls='-',lw=1)
                # ax1.axvline(currentx,ls='-', c='orange', lw=1)
                #print(1)
            oldTwok=twok
            oldOne=onek

        ax2.axhline(0, ls='-', c='g', lw=0.5)  # 水平线
        #吸筹界限
        tianLien=abs(downlimitTemp)*(self.downlimit/100)
        tianDownLien=abs(downlimitTemp*0.3)*(self.downlimit/100)


        ax2.axhline(tianLien, ls='-', c='b', lw=0.5)  # 水平线
        ax2.axhline(tianDownLien, ls='-', c='b', lw=0.5)  # 水平线
        ax2.grid(True)  # 画网格
        ax1.axhline(self.priceJJJ,ls='-',c='#c7001b',lw=0.5)
        ax2.axhline(0, ls='-', c='g', lw=0.5)  # 水平线
        oldKK=0
        oldTwokk=0
        old2=0
        #线性回归展示
        newYY=[]
        newXX=[]
        yestodayOneTwoValue=0
        yestodayTwoValue=0
        yestodayOneValue=0

        yesOnlTwoTemp=0
        for item in erjieK:
            kX=item[0]+myyj
            kk=item[1]
            item[2]=0
            #print(old2)
            olddictvalue=yijiedict.get(kX)
            threeOneValue=yijiedict.get(kX-3)
            if olddictvalue==None:
                continue
            newXX.append(kX)
            currentOneTwoValue=float(kk)+float(olddictvalue)
            newYY.append(currentOneTwoValue)


            if len(newYY)>3 and currentOneTwoValue>0 and currentOneTwoValue<newYY[len(newYY)-2] and newYY[len(newYY)-2] >newYY[len(newYY)-3]:
                #添加到历史回测里
                newTonTemp = []
                newTonTemp.append(kX)
                newTonTemp.append(-1)
                newTonTemp.append("GAOWEIDAOSHU")
                newTonTemp.append("<b style=\"background-color:rgba(255,255,0);font-size:20px;line-height:20px;margin:0px 0px;\">卖出，阶段性高位，继续上涨空间较小，可参考导数趋势，建议卖出，否贼会有亏损！</b>")
                NewtonBuySall.append(newTonTemp)

                # ax2.axvline(kX, color="r", ls='-',lw=0.2)
                ax1.axvline(kX,ls='-', c='r',ymin=1,ymax=0.8, lw=2)

            if len(newYY)>3 and currentOneTwoValue<0 and currentOneTwoValue>newYY[len(newYY)-2] and newYY[len(newYY)-2] <newYY[len(newYY)-3] and currentOneTwoValue<kk and kk<olddictvalue:
                #添加到历史回测里
                newTonTemp = []
                newTonTemp.append(kX)
                newTonTemp.append(1)
                newTonTemp.append("DIWEIDAOSHU")
                newTonTemp.append("<b style=\"background-color:rgba(255,255,0);font-size:20px;line-height:20px;margin:0px 0px;\">买入，但是二阶导数的形态和空间要足够，还有高位的要注意，最好不要操作！</b>")
                NewtonBuySall.append(newTonTemp)
                # ax2.axvline(kX, color="g", ls='-',lw=2)
                ax1.axvline(kX,ls='-', c='g',ymax=0.05,ymin=0, lw=2)

            # ax2.scatter(kX, float(kk)+float(olddictvalue), color="r", linewidth=0.0004)
            #总导数小于零，总导数趋势向上，总导数大于界限 and yestodayOneTwoValue<currentOneTwoValue and currentOneTwoValue>tianLien
            if currentOneTwoValue<0 and yestodayOneTwoValue<currentOneTwoValue and yestodayOneValue<0 and olddictvalue<0 and olddictvalue<tianDownLien:
                # 一阶导数趋势向上，二阶导数趋势向上，二阶导数在一阶导数之上，总导数在一阶导数之下 kk>yestodayOneValue and and olddictvalue>kk and kk>currentOneTwoValue
                if kk>yestodayTwoValue and olddictvalue>yestodayOneValue and olddictvalue>currentOneTwoValue and olddictvalue>threeOneValue:
                    newTonTemp = []
                    newTonTemp.append(kX)
                    newTonTemp.append(1)
                    newTonTemp.append("CHAODI-MR")
                    newTonTemp.append("<b style=\"background-color:rgba(255,255,0);font-size:20px;line-height:20px;margin:0px 0px;\">🏍🏍买入：短期内股价处于底部，未来有一定的上涨反弹空间，您可以在此买入，几天之后再卖出，前提明日股价高于今日，但是涨幅不能很大！，前提是今日不能大涨，明日不能大涨。\n<font color='red'>但是：如果当前一阶导数和二阶导数在0轴附近纠缠不清，而且股价趋势向下，那么此刻的反弹很有可能是庄家的欺骗行为！应该当避而远之！！！、如果明日股价低于今日股价，一定不要买入！。如果明日股价张福过大，按照均衡原理，买入很可能回调，请慎重！</font></b>")
                    NewtonBuySall.append(newTonTemp)
                    ax2.axvline(kX, ls='-', c="g",lw=2)
                    ax1.axvline(kX,ls='-', c='g',ymin=0, ymax=0.1, lw=6)
                    # ax2.axvline(kX,ls='-', c='g',ymin=0, ymax=0.7, lw=1)
            #
            #                             *
            #           *                 $
            #------------------------------------------------------------------
            #                   *
            #                   $
            if olddictvalue>0 and olddictvalue>yestodayOneValue and currentOneTwoValue>yestodayOneTwoValue \
                    and yestodayOneValue>yestodayOneTwoValue and olddictvalue>currentOneTwoValue and threeOneValue<olddictvalue and kk>olddictvalue:
                newTonTemp = []
                newTonTemp.append(kX)
                newTonTemp.append(1)
                newTonTemp.append("CHANGNUI-MR")
                newTonTemp.append("<b style=\"background-color:rgba(255,255,0);font-size:20px;line-height:20px;margin:0px 0px;\">🚄买入：股价长期向好，此刻应该买入，未来可能具有快速拉伸的前景，前提是之前没有筹码积压，30天内没有前高。<font color='red'>但是：如果股价处于高位，那么此刻指标失效，您应当避而远之！！！</font></b>")
                NewtonBuySall.append(newTonTemp)
                # ax2.scatter(kX, twok, color="g", linewidth=0.0004)
                ax1.axvline(kX, ls='-', c='g', ymin=0, ymax=0.3, lw=3)
                # ax2.axvline(kX,ls='-', c='g',ymin=0, ymax=0.7, lw=1)

            #二阶上穿
            if kk>=0 and oldKK<0:
                if old2==-1:
                    # ax2.scatter(kX, kk, color="b", linewidth=0.0004)
                    # ax1.axvline(kX, ls='-', c='b', lw=0.5)
                    item[2] = 1
                    # #print("买入"+str(kX))
                    # #买入
                    # newTonTemp = []
                    # newTonTemp.append(kX)
                    # newTonTemp.append(1)
                    # NewtonBuySall.append(newTonTemp)
            #二阶下穿越
            if kk<=0 and oldKK>0:
                #卖出
                newTonTemp = []
                newTonTemp.append(kX)
                newTonTemp.append(-1)
                newTonTemp.append("EJXC-MC")
                newTonTemp.append("<b style=\"background-color:rgba(255,255,0);font-size:20px;line-height:20px;margin:0px 0px;\">⛈⛈⛈卖出：明日应该卖出，股价上行动力不足，今后几天可能会有一定程度的回调！</b>")
                NewtonBuySall.append(newTonTemp)
                ax1.axvline(kX, ls='-', c='y',ymin=1, ymax=0.8, lw=2)
                # ax2.axvline(kX, color="y", ls='-',lw=1)
                item[2] = -1

            old2=item[2]
            oldKK=kk
            #缓存一下前一天的总情况
            yestodayOneTwoValue=currentOneTwoValue
            yestodayTwoValue=kk
            yestodayOneValue=olddictvalue
        ax2.plot(newXX, newYY, color="r", linewidth=1,label='1')


        iList =[]
        zList =[]
        sList =[]
        fList=[]

        zsm={}
        for index, row in self.result.iterrows():
            iList.append(index-self.start)
            z=float(row['z'])
            s=float(float(row['s']))
            zList.append(z)
            sList.append(s)
            convert=int(row['m'])
            if convert==1:
                fList.append(index-self.start)
            if z>s and convert==1:
                zsm[index-self.start]=1

        # ax5.axhline(baseRmb, ls='-', c='w', lw=0.5)  # 水平线
        for c in fList:
            ax5.axvline(c, ls='-', c='#ed1941', lw=1)
            ax1.axvline(c, ls='-', c='#ed1941', ymin=0, ymax=0.04,lw=2)


        for i in priceBigvolPriceIndexs:
            if zsm.__contains__(i):
                newTonTemp = []
                newTonTemp.append(i)
                newTonTemp.append(1)
                newTonTemp.append("GAOWEIFANTAN-MR")
                newTonTemp.append("<b style=\"background-color:rgba(255,255,0);font-size:20px;line-height:20px;margin:0px 0px;\">🚀🚀🚀买入：如果底部筹码没有松动，此刻应该买入，此刻买入，股价可能会快速拉升。<font color='red'>如果底部筹码很少，那么请不要买入！！</font></b>")
                NewtonBuySall.append(newTonTemp)
                ax1.axvline(i, ls='-', c='#ed1941', ymin=0, ymax=0.3, lw=2)
                ax1.axvline(i, ls='-', c='#f47920',ymin=0, ymax=0.02,lw=5)

        ax5.plot(iList, zList, c='#6950a1',lw=2, label='主力')
        ax5.plot(iList, sList, c='#45b97c', lw=2 ,label='散户')
        ax5.legend(loc='upper left')  # 图例放置于右上角
        ax5.grid(True)  # 画网格


        for i in range(len(VARXCX)):
            newTonTemp = []
            newTonTemp.append(VARXCX[i])
            newTonTemp.append(0)
            newTonTemp.append("XC-MR")
            newTonTemp.append("<b style=\"background-color:rgba(255,255,0);font-size:20px;line-height:20px;margin:0px 0px;\">买入，此处为通达信吸筹买入点，但是一般会连续出现，如果没有其他买入点（小绿线，反弹线，粗短绿线）您可以最后出现后买入，或参考导数图！</b>")
            NewtonBuySall.append(newTonTemp)
            ax1.axvline(VARXCX[i], ls='-', c='orange',ymax=0.02,ymin=0, lw=2)

        profit=self.testNewTon(NewtonBuySall,indexCloseDict)
        ax6.plot(self.buysell, self.myRmb, c='orange', label="回测收益率:"+str(round(profit,2))+"%")
        ax6.legend(loc='upper left')  # 图例放置于右上角
        ax6.grid(True)  # 画网格

        # 登出系统
        if isTest==0:
            tempDir = os.getcwd() + "/temp/"
            plt.savefig(tempDir+ code + ".png")
            bs.logout()
        else:
            plt.close(fig)
        # plt.show()
        return NewtonBuySall,profit,currentIndex


    def start(self,codes):
        imgsOKstr=""
        imgsOK=[]
        oldTotal=0
        currentTotal=0
        for items in codes:


            item=items[0]
            self.start = -1
            NewtonBuySall,profit,currentIndex=self.execute(item,int(items[4]),int(items[5]),0)
            if profit<=0:
                historyProfit="<span style=\"background-color:	rgb(216,216,216) ;font-size:20px;line-height:20px\"><font color='#003366'>回测收益率："+str(round(profit,2))+"%</font>  （🤪🤪🤪不建议投资该股票！）</span></br>"
            else:
                historyProfit = "<span style=\"background-color:rgb(255,255,0);font-size:20px;line-height:20px\"><font color='red'>回测收益率：" + str(round(profit, 2)) + "%</font>👍👍👍</span></br>"
            zhidaoToday="<span style=\"background-color:rgb(255,255,0);font-size:20px;line-height:20px\"><font color='red'>❤❤❤当前走势尚不能操盘指令✔✔✔✔~~~~</font></span></br>"
            zhidao=""
            isToday=False
            caozuoHistory=sorted(NewtonBuySall, key=lambda x: x[0], reverse=True)
            for mmzd in caozuoHistory[:3]:
                if mmzd[0]>currentIndex:
                    zhidaoToday=mmzd[3]
                    isToday=True
                if isToday==False and mmzd[0]==currentIndex:
                    zhidaoToday=mmzd[3]
                    isToday=True
                else:
                    temp=mmzd[3]
                    temp=temp.replace("b","span")
                    temp=temp.replace("20","16")
                    zhidao=zhidao+"<font color='orange'>"+temp+"</font></br>"
                    isToday=False
            if isToday:
                zhidaoToday="<p><b><font color='red'>"+zhidaoToday+"</font></b></p>"
            imgsOKstr=imgsOKstr+ historyProfit+zhidaoToday
            color="red"
            shouyi=0
            if items[1]!=0:
                # sh.000001, 3.568, 100, 上证指数, 0, 30
                shouyi=float(self.currentPrice)-float(items[1])
                oldTotal=oldTotal+(float(items[1])*int(items[2]))
                currentTotal=currentTotal+(float(self.currentPrice)*int(items[2]))
            if shouyi>0:
                shouyidisc="<font color='red'>" + str(round(shouyi*int(items[2]),2)) + "</font>"
            else:
                shouyidisc = "<font color='green'>" + str(round(shouyi*int(items[2]),2)) + "</font>"
            if self.currentPrice>float(items[1]):
                color="green"
            imgsOKstr = imgsOKstr+"<span style=\"background-color:rgba(255,255,0,0.75);font-size:20px;line-height:20px\">"+str(items[3])+"<font color='"+color+"'>"+str(self.currentPrice)+"-"+str(items[1])+"="+str(round(self.currentPrice-float(items[1]),2))+"  "+shouyidisc+"</span></br><img src='cid:" + item + "'></front>"+zhidao
            imgsOK.append(item)

            # print("\033[1;33;40m \t"+items[0]+","+items[3]+"\tok         \033[0m")
            print("\t"+items[0]+","+items[3]+"\tok         ")


        endDate=time.strftime('%Y-%m-%d',time.localtime(time.time()))
        conf=Config()
        my_pass = conf.emailPass  # 发件人邮箱密码
        my_user = conf.emaialUser  # 收件人邮箱账号，我这边发送给自己
        sender = conf.emaialUser
        receive=conf.receiver.split(",")
        #print(receive)
        receivers = [receive]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
        msgRoot = MIMEMultipart('related')
        dic=round(currentTotal - oldTotal,2)
        mycolor="red"
        if dic<=0:
            mycolor="green"
        zijingbiandong=str(currentTotal) + "-" + str(oldTotal) + "=" + str(dic)
        msgRoot['From'] = Header(str(endDate)+"  "+str(currentTotal - oldTotal), 'utf-8')
        msgRoot['To'] = Header("sMain操作简报", 'utf-8')
        subject = str(endDate)+' 收益：'+str(dic)
        msgRoot['Subject'] = Header(subject, 'utf-8')

        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)

        mail_msg = "<span style=\"background-color:rgba(255,255,0,0.25);font-size:20px;line-height:20px\">第一次持股收益：<font color='"+mycolor+"'>"+zijingbiandong+"</font></span><p>"+imgsOKstr+"</p>"
        msgAlternative.attach(MIMEText(mail_msg, 'html', 'utf-8'))

        # 指定图片为当前目录
        cur_path = os.getcwd()
        tempDir = cur_path + "/temp/"
        for item in imgsOK:
            fp = open(tempDir+item+".png", 'rb')
            msgImage = MIMEImage(fp.read())
            fp.close()
            temp="<"+item+">"
            # 定义图片 ID，在 HTML 文本中引用
            msgImage.add_header('Content-ID', temp)
            msgRoot.attach(msgImage)
        # print("\033[1;32;40m 3.邮件发送  \033[0m")
        print("3.邮件发送  ")
        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect('smtp.qq.com', 25)    # 25 为 SMTP 端口号
            smtpObj.login(my_user,my_pass)
            smtpObj.sendmail(sender, receivers, msgRoot.as_string())
            print("邮件发送成功")
        except smtplib.SMTPException:
            print("Error: 无法发送邮件")

        # os.system('shutdown -s -f -t 180')

    # 在k线基础上计算KDF，并将结果存储在df上面(k,d,j)
    def zsLine(self,df):
        df = df.astype({'low': 'float', 'close': 'float', 'high': 'float'})
        low_list = df['low'].rolling(34, min_periods=9).min()
        low_list.fillna(value=df['low'].expanding().min(), inplace=True)
        high_list = df['high'].rolling(34, min_periods=9).max()
        high_list.fillna(value=df['high'].expanding().max(), inplace=True)
        rsv = (df['close'] - low_list) / (high_list - low_list) * 100
        df['k'] = pd.DataFrame(rsv).ewm(com=2).mean()
        df['d'] = df['k'].ewm(com=2).mean()
        df['j'] = 3 * df['k'] - 2 * df['d']
        #主力线
        zz = pd.Series.ewm(df['j'], com=2.5).mean()
        # 计算散户线代码：
        low_list1 = df['low'].rolling(55, min_periods=9).min()
        low_list1.fillna(value=df['low'].expanding().min(), inplace=True)
        high_list1 = df['high'].rolling(55, min_periods=9).max()
        high_list1.fillna(value=df['high'].expanding().max(), inplace=True)
        #散户线
        ss = (high_list1 - df['close']) / ((high_list1 - low_list1)) * 100
        return zz,ss

    # 判断反转信号代码：
    def convertXQH(self,df):
        df = df.astype({'low': 'float', 'close': 'float', 'high': 'float'})
        low_list2 = df['low'].rolling(9, min_periods=9).min()
        low_list2.fillna(value=df['low'].expanding().min(), inplace=True)
        high_list2 = df['high'].rolling(9, min_periods=9).max()
        high_list2.fillna(value=df['high'].expanding().max(), inplace=True)
        rsv1 = (df['close'] - low_list2) / (high_list2 - low_list2) * 50
        df['K1'] = pd.Series.ewm(rsv1, com=2).mean()
        df['D1'] = pd.Series.ewm(df['K1'], com=2).mean()
        df['J1'] = 3 * df['K1'] - 2 * df['D1']
        # stock_datas['M'] =(stock_datas['J1']>3)&
        df['J2'] = df['J1'].shift(1)
        #是否反转，1表示反转，0表示没有反转
        mm = (df['J1'] > 3) & (df['J2'] <= 3)
        return mm
