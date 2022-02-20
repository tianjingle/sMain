import time

import baostock as bs
import pandas as pd
import talib
from matplotlib import pyplot as plt


class BuySell:


    result=None
    start=0
    window=200

    # VAR2 := LLV(LOW, 10);
    # VAR3 := HHV(HIGH, 25);
    # 阶段卖出: 3.2, COLORCYAN;
    # 3.5, COLOR0088FF;
    # 清仓卖出: 3.5;
    # 动力线 := EMA((CLOSE - VAR2) / (VAR3 - VAR2) * 4, 4);
    # STICKLINE(动力线 > REF(动力线, 1), 动力线, REF(动力线, 1), 8, 1), COLORRED;
    # STICKLINE(动力线 <= REF(动力线, 1), 动力线, REF(动力线, 1), 8, 1), COLORGREEN;
    # 底部: 0.2, COLORGREEN;
    # 关注: 0.5, COLORYELLOW;
    # DRAWICON(FILTER(CROSS(动力线, 关注), 20), 动力线 + 0.02, 1);
    # DRAWICON(FILTER(CROSS(清仓卖出, 动力线), 20), 动力线 + 0.02, 2);
    # DRAWICON(FILTER(CROSS(动力线, 底部), 20), 动力线 + 0.02, 1);
    # DRAWICON(FILTER(CROSS(阶段卖出, 动力线), 20), 动力线 + 0.02, 4);
    # 强弱分界线: 1.75, POINTDOT, LINETHICK2, COLOR70DB93;
    # 数值: 动力线, COLORFFFFFF;

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
        self.start = len(self.result) - self.window
        # 二维数组
        self.result = self.result.loc[:, ['date', 'open', 'high', 'low', 'close', 'volume', 'turn']]
        if code == 'sh.000001':
            self.result['temp'] = 1000
            self.result['open'] = talib.DIV(self.result['open'], self.result['temp'])
            self.result['high'] = talib.DIV(self.result['high'], self.result['temp'])
            self.result['low'] = talib.DIV(self.result['low'], self.result['temp'])
            self.result['close'] = talib.DIV(self.result['close'], self.result['temp'])

        self.result = self.result[-self.window:]
        self.result['VAR_4']=4
        # VAR2 := LLV(LOW, 10);
        self.result['VAR2']=self.result['low'].rolling(10).min().astype(float)
        # VAR3 := HHV(HIGH, 25);
        self.result['VAR3']=self.result['high'].rolling(25).max().astype(float)
        # 动力线 := EMA((CLOSE - VAR2) / (VAR3 - VAR2) * 4, 4);
        self.result['CLOSE_VAR2']=self.result['close'].astype(float)-self.result['VAR2'].astype(float)
        self.result['VAR3_VAR2']=self.result['VAR3'].astype(float)-self.result['VAR2'].astype(float)
        self.result['VAR3_VAR2_4_AFTER']=talib.MULT(self.result['VAR3_VAR2'], self.result['VAR_4'])
        self.result['CLOSE_VAR2_VAR3_VAR2X4']=talib.DIV(self.result['CLOSE_VAR2'], self.result['VAR3_VAR2_4_AFTER'])
        self.result['DONGLILINE'] = talib.EMA(self.result['CLOSE_VAR2_VAR3_VAR2X4'], 4)

        x=[]
        y=[]
        for index, row in self.result.iterrows():
            currentIndex=index-self.start
            x.append(currentIndex)
            a = round(row['DONGLILINE'], 2)
            y.append(float(a))
        return x,y
by=BuySell()
x,y=by.getResult("sz.000009")
plt.plot(x, y, marker="o", mec="r", mfc="w",label=u"y=x2曲线图")


plt.title("一个简单的折线图") #标题

plt.show()