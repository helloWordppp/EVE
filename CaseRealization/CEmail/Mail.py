# !/usr/bin/env
# -*- coding=utf-8 -*-

'''
Created on 2014年10月28日
@author: Xuantianbing
@How to use:
    mycls = ClsReport()
    mycls.version = version
    mycls.begin_time =  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(begin_time))
    mycls.end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))
    mycls.easrst_time = GetHMS(end_time - begin_time)
    mycls.product = "TB"
    mymail = MyMail(xlsname, mycls)
    mymail.ExecuteMails()
'''
from __future__ import unicode_literals
import email.encoders as Encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email.header import Header
import os
import smtplib, mimetypes
from CaseRealization.CEmail.OpXlsCls import OpXls
import traceback

class MyMail:
    '''发送邮件'''
    # _sender_name = '625046831@QQ.com'
    # _sender_password = '`111111q'
    # _smtp_address = '192.168.10.141'
    # _smtp_address = 'smtp.qq.com'
    #192.168.10.140   smtp.qq.com
    
    def __init__(self, xlsname, clsreport, comp, receiver_list, sender, password, smtp_address, product="Easeus"):
        '''
                     初始化Mail类
        @xlsname:发送的xls文件名
        @comp:附件列表
        @log:日志
        @db:db路径
        @receiver:接收者，list
        @sender:发送者邮箱名
        @password:发送者密码
        '''
        self.sender_name = sender
        self.sender_password = password
        self.receiver = receiver_list
        self.context = "python test!"
        self.status = False
        self.msg = None
        self.accessory = []
        self.mycls = clsreport
        self._smtp_address = smtp_address
        self.product = product

        #需要添加的附件
        self.xlsname = xlsname
        self.comppath = comp
        self.clsxls = OpXls()
    
    def ExecuteMails(self):
        # 登录smtp
        self.SmtpLogin()
        # 创建邮件
        self.CreateMessage()

        # 添加附件-自动化执行结果
        self.AddAccessory(self.comppath)
        # 发送内容
        self.SmtpSend()
        # 退出登录 smtp
        self.SmtpStop()  
        
    def SmtpLogin(self):
        '''登录smtp'''
        try:
            self.smtp = smtplib.SMTP(host=self._smtp_address)
            self.smtp.connect(self._smtp_address)
            if self.status is False:
                if self._smtp_address == "smtp.qq.com":
                    self.smtp.ehlo()

                    self.smtp.starttls()
                self.sender_name = self.sender_name if isinstance(self.sender_name, str) \
                    else self.sender_name.encode("utf8")
                self.sender_password = self.sender_password if isinstance(self.sender_password, str) \
                    else self.sender_password.encode("utf8")
                self.smtp.login(self.sender_name, self.sender_password)
                self.status = True
        except :
            print(traceback.format_exc())
        
    def CreateMessage(self):
        '''创建邮件体'''
        # 创建MIME，并添加信息头
        self.msg = MIMEMultipart()
        # 邮件发送者
        self.msg['From'] = self.sender_name
        # 邮件标题
        self.msg['Subject'] = self.product
        # 收件人list
        self.msg['To'] = COMMASPACE.join(self.receiver)
        # 发送邮件日期
        self.msg['Date'] = formatdate(localtime=True)
        #统计用例执行情况
        try:
            self.clsxls.Readxls(self.xlsname)
        except:
            print("read excel failed!!")
        try:
            self.AddTotal()
        except:
            # print(traceback.format_exc())
            print("Count fail!")
            Context = self.context.encode("gbk", 'ignore')  # 过滤无效字符
            Context = MIMEText(Context, _subtype='html', _charset='gbk')
            self.msg.attach(Context)
        
    def AddTotal(self):
        '''
                    计算用例执行情况
        '''       
        #统计用例执行情况
        content = "产品:{0}自动化执行结果<br>版本:{1}<br>执行时间:{2}&nbsp&nbsp开始时间:{3}&nbsp&nbsp结束时间:{4}&nbsp&nbsp使用时间:{5}<br>"
        content += "{6}<br>用例级别:{7}<br>"

        content += self.context + "<br>"
        if os.path.exists(self.xlsname):
            func_type = "{0}功能测试: &nbsp&nbsp总执行用例数:{1}&nbsp&nbsp 失败用例数:{2}&nbsp&nbsp成功率:{3}%<br>"

            content_table = '<TABLE style="BORDER-RIGHT: 1px solid; BORDER-TOP: 1px solid; BORDER-LEFT: 1px solid; BORDER-BOTTOM: 1px solid" cellSpacing=1 cellPadding=1 width="100%" border=1>'
            td_style = "<td>{0}</td>"
            td_fail_style = "<td color='red'>{0}</td>"
            td_image_style = '<td><img src="{0}"  type="image"></td>'
            Context = self.mycls.CreateReport(content_table, self.mycls, content, func_type, td_style, td_image_style, td_fail_style, self.clsxls)
        else:
            Context = content.format(self.mycls.product, self.mycls.version,
                                     self.mycls.run_time,
                                     str(self.mycls.begin_time)[0:19],
                                     str(self.mycls.end_time)[0:19],
                                     self.mycls.easrst_time,
                                     self.mycls.auto_Machine,
                                     self.mycls.protity)

        Context = Context.encode("gbk", 'ignore')  # 过滤无效字符
        Context = MIMEText(Context, _subtype='html', _charset='gbk')
        self.msg.attach(Context)
        
    def AddAccessory(self, path_list=[]):
        '''添加附件'''
        #添加附件
        if type(path_list) is list and path_list:
            for path in path_list:
                try:
                    if os.path.exists(path) and os.path.isfile(path):
                        self.msg.attach(self.Attachment(path))
                except:
                    # print(traceback.format_exc())
                    continue
        else:
            print("No accessory add!")

    def SmtpSend(self):     
        '''发送邮件'''   
        # if self.status is True:
        #     # 发送邮件
        #     try:
        #         self.smtp.sendmail(self.sender_name, self.receiver, self.msg.as_string())
        #     except:
        #         print(traceback.format_exc())
        #         print("Send mail fail!")
        # else:
        #     return False
        self.smtp.sendmail(self.sender_name, self.receiver, self.msg.as_string())


    
    def SmtpStop(self):
        '''停止smtp邮件'''
        if self.status is True:
            self.smtp.close()
            self.status = False
            
    def Attachment(self, file_name):
        # 增加附件
        fileobject = open(file_name, "rb")
        mimetype, mimeencoding = mimetypes.guess_type(file_name)
        if mimeencoding or (mimetype is None):
            mimetype = "application/octet-stream"
        maintype, subtype = mimetype.split('/')
        if maintype == "text":
            retval = MIMEText(fileobject.read(), _subtype=subtype, _charset='gb2312')
        else:
            retval = MIMEBase(maintype, subtype, _charset='gb2312')
            retval.set_payload(fileobject.read())
            Encoders.encode_base64(retval)
            # Encoders.encode_quopri(retval)
        filenames = file_name.split("\\")[-1]
        retval.add_header("Content-Disposition", "attachment", filename="%s"%Header(filenames,'gb2312'))
        fileobject.close()
        return retval
