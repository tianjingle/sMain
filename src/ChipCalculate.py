from src.Chip import Chip

#筹码量的计算


class ChipCalculate:

    shuanJian=1

    #1.价格和筹码量的分布
    price_vol={}

    #2.每个交易日的筹码量
    DayChouMaList=[]


    # def getChouMa(self,data):
        #print("---基于行为金融学的筹码分布--")


    #倒叙计算每日的筹码量
    #传入的数据id,open,high,low,close,volume,typePrice,trun
    #          0,   1,   2,  3,   4,    5,    6,       7
    def getDataByShowLine(self,data):
        # result = result.loc[:, ['date', 'open', 'high', 'low', 'close', 'volume']]
        result=[]
        dataLength=len(data)
        csdnAvcPrice=[]
        TtodayChouma=[]
        TTprice=0
        TTmax=0
        shuanjian=0
        #保障显示120天的筹码线
        # if dataLength>=239:
        #倒叙计算每日的筹码量,当日的筹码分布和最近的120天有关系
        for k in range(len(data)-80):
            self.DayChouMaList.clear()
            #倒数第k日的基本数据
            Baseline = data[dataLength -1- k]
            #拿到id
            baseIndex=int(Baseline[0])
            currentPrice=float(Baseline[4])
            for i in range(80):
                if i<1:
                    continue
                line=data[dataLength-k-i]
                if line[0]=='':
                    index=0
                else:
                    index=int(line[0])
                open=float(line[1])
                close=float(line[4])
                max=float(line[2])
                min=float(line[3])
                vol=float(line[5])
                avc_price=float(line[6])
                if line[7]=='':
                    line[7]=0
                if i==1:
                    currentChouMa=vol
                    chip=Chip(index,open,close,max,min,avc_price,currentChouMa)
                    shuanjian=(1-float(data[dataLength-i][7])/100)
                    self.DayChouMaList.append(chip)
                else:
                    chouma=shuanjian*float(data[dataLength-i][5])
                    shuanjian=shuanjian*(1-float(data[dataLength-i][7])/100)
                    chip=Chip(index,open,close,max,min,avc_price,chouma)
                    self.DayChouMaList.append(chip)
            #倒序计算完每日的筹码量，然后将筹码平均分布到当日的价格上
            todayChouma,tmax,csdn,maxVolprice=self.adviseChouMa2Price()
            if k==0:
                TtodayChouma=todayChouma
                TTmax=tmax
            csdnTemp=[]
            csdnTemp.append(baseIndex)
            csdnTemp.append(csdn)
            # csdnTemp.append(TtodayChouma)
            csdnTemp.append("")
            csdnTemp.append(TTmax)
            if currentPrice*100>maxVolprice:
                #当前的价格大于筹码的平均价格
                csdnTemp.append(1)
            else:
                csdnTemp.append(0)
            result.append(csdnTemp)
        return result




        #将每日的筹码分布到价格上
    def adviseChouMa2Price(self):
        length=len(self.DayChouMaList)
        self.price_vol.clear()
        for i in range(length):
            # #print("下表："+str(i))
            #当日的筹码
            chouma=self.DayChouMaList[i].getChouMa()
            index=self.DayChouMaList[i].getIndex()
            open=self.DayChouMaList[i].getOpen()
            close=self.DayChouMaList[i].getClose()
            max=self.DayChouMaList[i].getMax()
            min=self.DayChouMaList[i].getMin()
            avcPrice=self.DayChouMaList[i].getAvcPrice()
            #移入地时候，矩形和三角形的面积比为3比7，其中矩形的筹码分布占0.3，三角形占0.7
            #1.先算矩形部分的筹码迁移，将每股价格精确到分。
            maoshu=round((max-min),2)*100
            if maoshu<=0:
                continue
            #得到矩形部分筹码量
            everyMao=chouma*0.3/maoshu
            for j in range(int(maoshu)):
                #从最小价格向最大价格进行逐个筹码分布
                key=j+round(min*100)
                #如果已经包含了当前价格，那么就进行累加
                if self.price_vol.__contains__(key):
                    volTemp=self.price_vol.get(key)
                    volTemp=volTemp+everyMao
                    self.price_vol[key]=volTemp
                else:
                    #当前价格上的筹码量
                    self.price_vol[key]=everyMao

            # 三角形一半的筹码量
            totalChouma=chouma*0.35
            #将三角形的筹码分布到价格上
            for j in range(int(maoshu/2)):
                #从下往上
                if min*100+j<avcPrice*100:
                   key=int(j+min*100)
                   # --   max
                   # -----
                   # -----------  avrageprice
                   # -------
                   # ------   min
                   #看是递增还是递减的，k大于零表示递增，k小于零表示递减
                   k=(avcPrice-min)/((max-min)/2)
                   #当前价格上应该分配的筹码在三角形半上所占据的比列多少
                   ditVol=(j*k)/(((avcPrice-min)*(max-min)/2)/2)
                   ditChouma=totalChouma*ditVol
                   #下三角筹码分配
                   if self.price_vol.__contains__(key):
                       volTemp=self.price_vol[key]
                       volTemp=volTemp+ditChouma
                       self.price_vol[key] = volTemp
                   else:
                       self.price_vol[key]=ditChouma
                   #上三角筹码分布
                   if self.price_vol.__contains__(int(max*100-j)):
                       volTemp = self.price_vol[int(max*100-j)]
                       volTemp = volTemp + ditChouma
                       self.price_vol[int(max*100-j)]=volTemp
                   else:
                       self.price_vol[int(max*100-j)]=ditChouma
        choumaList=[]
        isFirst=1
        totalVol=0
        totalPrice=0
        tmax=0
        maxVolprice=0
        for i in sorted(self.price_vol):
            #这里的i就表示价格
            if isFirst==1:
                isFirst=0
            cm=[]
            #寻找最大的筹码量
            if self.price_vol[i]>tmax:
                tmax=self.price_vol[i]
                #缓存一下最大筹码位置的价格
                maxVolprice=i
            #计算当日的各个价格上的筹码量之和
            totalVol=totalVol+self.price_vol[i]
            #计算当前价格上筹码的累计大小
            totalPrice=totalPrice+i*self.price_vol[i]
            #封装当前价格和价格上的筹码量
            cm.append(i)
            cm.append(self.price_vol[i])
            choumaList.append(cm)

        dP = 0
        for item in choumaList:
            dP = dP + item[0] * item[1] / totalVol

        if totalVol==0:
            csdn=0
            return choumaList, 0, tmax, csdn,0
        else:
            csdn=round((totalPrice / totalVol) / 100, 2)
            return choumaList, tmax, csdn, maxVolprice