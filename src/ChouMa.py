from src.MyChouMa import MyChouMa


class ChouMa:

    shuanJian=1

    #1.价格和筹码量的分布
    price_vol={}

    #2.每个交易日的筹码量
    DayChouMaList=[]


    # def getChouMa(self,data):
        #print("---基于行为金融学的筹码分布--")



    #倒叙计算每日的筹码量
    def getDataByShowLine(self,data):
        dataLength=len(data)
        csdnAvcPrice=[]
        TtodayChouma=[]
        TTprice=0
        TTmax=0
        shuanjian=0
        if dataLength>=239:
            #倒叙计算每日的筹码量
            for k in range(120):
                self.DayChouMaList.clear()
                Baseline = data[dataLength -1- k]
                baseIndex=int(Baseline[0])
                # #print(Baseline)
                for i in range(120):
                    if i<1:
                        continue
                    line=data[dataLength-k-i]
                    if line[0]=='':
                        index=0
                    else:
                        index=int(line[0])
                    # #print(line)
                    open=float(line[3])
                    close=float(line[6])
                    max=float(line[4])
                    min=float(line[5])
                    vol=float(line[8])
                    avc_price=float(line[19])
                    if line[11]=='':
                        line[11]=0
                    if i==1:
                        currentChouMa=vol
                        mychouMa=MyChouMa(index,open,close,max,min,avc_price,currentChouMa)
                        shuanjian=(1-float(data[dataLength-i][11])/100)
                        self.DayChouMaList.append(mychouMa)
                    else:
                        chouma=shuanjian*float(data[dataLength-i][8])
                        shuanjian=shuanjian*(1-float(data[dataLength-i][11])/100)
                        mychouMa=MyChouMa(index,open,close,max,min,avc_price,chouma)
                        self.DayChouMaList.append(mychouMa)

                todayChouma,avc_price,tmax,csdn=self.adviseChouMa2Price()
                if k==0:
                    TtodayChouma=todayChouma
                    TTprice=avc_price
                    TTmax=tmax
                data[dataLength - 1 - k][31]=csdn
                csdnTemp=[]
                csdnTemp.append(baseIndex)
                csdnTemp.append(csdn)
                csdnAvcPrice.append(csdnTemp)
        return data,TtodayChouma, TTprice, TTmax, csdnAvcPrice




        #将每日的筹码分布到价格上
    def adviseChouMa2Price(self):
        length=len(self.DayChouMaList)
        self.price_vol.clear()
        for i in range(length):
            chouma=self.DayChouMaList[i].getChouMa()
            max=self.DayChouMaList[i].getMax()
            min=self.DayChouMaList[i].getMin()
            avcPrice=self.DayChouMaList[i].getAvcPrice()
            #移入地时候，矩形和三角形的面积比为3比7，其中矩形的筹码分布占0.3，三角形占0.7
            #1.先算矩形部分的筹码迁移
            maoshu=round((max-min),2)*100
            if maoshu<=0:
                continue
            everyMao=chouma*0.3/maoshu
            for j in range(int(maoshu)):
                key=j+round(min*100)
                if self.price_vol.__contains__(key):
                    volTemp=self.price_vol.get(key)
                    volTemp=volTemp+everyMao
                    self.price_vol[key]=volTemp
                else:
                    self.price_vol[key]=everyMao
            totalChouma=chouma*0.35
            #计算三角形部分
            for j in range(int(maoshu/2)):
                if min*100+j<avcPrice*100:
                   key=int(j+min*100)
                   k=(avcPrice-min)/((max-min)/2)
                   ditVol=(j*k)/(((avcPrice-min)*(max-min)/2)/2)
                   ditChouma=totalChouma*ditVol
                   if self.price_vol.__contains__(key):
                       volTemp=self.price_vol[key]
                       volTemp=volTemp+ditChouma
                       self.price_vol[key] = volTemp
                   else:
                       self.price_vol[key]=ditChouma

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
        # #print(self.price_vol)
        for i in sorted(self.price_vol):
            if isFirst==1:
                isFirst=0
            cm=[]
            if self.price_vol[i]>tmax:
                tmax=self.price_vol[i]
            totalVol=totalVol+self.price_vol[i]
            totalPrice=totalPrice+i*self.price_vol[i]
            cm.append(i)
            cm.append(self.price_vol[i])
            choumaList.append(cm)
        if totalVol==0:
            csdn=0
            return choumaList, 0, tmax, csdn
        else:
            csdn=round((totalPrice / totalVol) / 100, 2)
            return choumaList, totalPrice / totalVol, tmax, csdn








