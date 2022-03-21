import configparser
class Config:

    emailPass=''
    emaialUser=''
    receiver=''

    myStock=[]

    def __init__(self):
        self.myStock=[]
        cf = configparser.ConfigParser()
        cf.read("C:\\Users\\tianjingle\\PycharmProjects\\sMain\\src\\config.ini",encoding="utf-8-sig")  # 读取配置文件，如果写文件的绝对路径，就可以不用os模块
        self.emailPass = cf.get("Email","pass")  # 发件人邮箱密码
        self.emaialUser = cf.get("Email","user")  # 收件人邮箱账号，我这边发送给自己
        self.receiver = cf.get("Email","receiver")# 接收邮件，可设置为你的QQ邮箱或者其他邮箱
        file = cf.get("stocks", "file")  # 获取[Mysql-Database]中host对应的值
        fo = open(file, "r", encoding='gbk')
        for line in fo.readlines():
            line = line.replace("]", "").strip()
            line = line.replace("[", "").strip()
            if line =='':
                continue
            abc = line.split(",")
            temp = []
            temp.append(abc[0])
            temp.append(abc[1])
            temp.append(abc[2])
            temp.append(abc[3])
            temp.append(abc[4])
            temp.append(abc[5])
            self.myStock.append(temp)
        fo.close()



    def newTrainValue(self):
        cf = configparser.ConfigParser()
        cf.read("C:\\Users\\tianjingle\\PycharmProjects\\sMain\\src\\config.ini", encoding="utf-8-sig")  # 读取配置文件，如果写文件的绝对路径，就可以不用os模块
        strTemp=''
        file = cf.get("stocks", "file")  # 获取[Mysql-Database]中host对应的值
        f = open(file, "w", encoding='gbk')
        list=[]
        for item in self.myStock:
            temp=item[0]+","+str(item[1])+","+str(item[2])+","+item[3]+","+str(item[4])+","+str(item[5])+"\n"
            list.append(temp)
        f.writelines(list)
        f.close()
