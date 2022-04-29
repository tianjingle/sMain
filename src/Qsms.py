from qcloudsms_py import SmsSingleSender
from qcloudsms_py.httpclient import HTTPError
import ssl


# 发送短信
class Qsms:
    # 短信应用SDK AppID
    appid = 1400218666  # SDK AppID是1400开头
    # 短信应用SDK AppKey
    appkey = "414c40f8dcd85a9806db3be68ecde570"
    # 需要发送短信的手机号码
    default_phone = ["15652466911"]
    # 短信模板ID，需要在短信应用中申请
    template_id = 1285045
    # 签名
    sms_sign = "程序科学"

    # 发送短信
    def sendSms(self, phones, code, price, operation):
        ssl._create_default_https_context = ssl._create_unverified_context
        ssender = SmsSingleSender(self.appid, self.appkey)
        # 当模板没有参数时，`params = []`
        params = []
        if len(code)>4:
            code=code[:4]
        params.append(code)
        params.append(operation)
        print(params)
        if phones == None or phones == "":
            phonesTemp = self.default_phone
        else:
            phonesTemp = phones.split(",")
        for item in phonesTemp:
            try:
                # 签名参数不允许为空串
                ssender.send_with_param(86, item, self.template_id, params, sign=self.sms_sign, extend="", ext="")
                print("send to:" + item)
            except HTTPError as e:
                print(e)
            except Exception as e:
                print(e)