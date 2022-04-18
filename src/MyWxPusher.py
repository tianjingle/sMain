from wxpusher import WxPusher

#发送wxpusher消息
class MyWxPusher:

    token="AT_Ntno2FyMjDOGaJSBaDnNp6yfBYFmQyd2"
    topicIds=['4839']
    userid="UID_AF9JbC5LTa31Kbyh16cPFRbplwn0"
    uids=[]
    uids.append(userid)

    #发送微信pusher消息
    def sendWxPusher(self,buy,sell):
        buyHtm="<h2>买入</h2>"
        sellHtm="<h2>买出</h2>"
        isBuy=False
        isSell=True
        for item in buy:
            isBuy=True
            buyHtm=buyHtm+"<h3>"+item+"</h3>"
        buyHtm=buyHtm+"<hr>"
        for item in sell:
            isSell=True
            sellHtm=sellHtm+"<h3>"+item+"</h3>"
        sellHtm=sellHtm+"<hr>"
        endHtml=buyHtm+sellHtm
        couldBuySell=isBuy&isSell
        if couldBuySell:
            res=WxPusher.send_message(endHtml,
                                  # uids=uids,
                                topic_ids=self.topicIds,
                                  content_type=2,
                                  token=self.token)
            print(res)