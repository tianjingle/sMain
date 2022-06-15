import easyquotation



class Tencent:

    quotation = easyquotation.use('tencent') # 新浪 ['sina'] 腾讯 ['tencent', 'qq']

    def getCurrentStockInfo(self,code):
        #单只股票
        if code.__contains__("."):
            code=code[3:]
        if len(code)==8:
            code=code[2:]
        b=self.quotation.real(code) # 支持直接指定前缀，如 'sh000001'
        return b[code]


    def getCurrentIndex(self):
        b= self.quotation.stocks(['sh000001'], prefix=True)
        print(b['sh000001'])
        return b['sh000001']
# quotation = easyquotation.use('tencent')
# b=quotation.real("000001")
# print(b)
# t=quotation.stocks(['sh000001'], prefix=True)
# # t=Tencent().getCurrentStockInfo('sh000001')
# print(t)