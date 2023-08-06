# encoding=utf-8
"""
@summary: 把带有文章的邮件寄到指定邮箱
@version: $Id$
@auther: luoboiqingcai<sf.cumt@163.com>
"""

import email
import email.mime.base
import email.mime.multipart
import email.mime.application
import email.mime.text
import mimetypes
import errno
import smtplib
import fetch_articles.config as cfg
from fetch_articles.get_article import FileWraper

ERROR = None

class Message_with_articles(email.mime.multipart.MIMEMultipart):
    """
    一封装有资料的邮件。
    @warning: 必须要设发件人('From')和收件人('To')
    """
    def __init__(self,*args,**kargs):
        """ """
        email.mime.multipart.MIMEMultipart.__init__(self,*args,**kargs)
        self._from_address= ''
        self._to_address = ''
        self._articles = [] # self._articles为一个成员为文件对象的列表
    def attach_articles(self,articles):
        """
        增加资料
        @param articles: 为一个文件列表，其中的文件都必须是用'rb'模式打开。
        """
        global ERROR
        if  isinstance(articles,list):
            for i in articles:
                if not isinstance(i,FileWraper):
                    ERROR = errno.EACCES
                    return -1
            self._articles.extend(articles)
            return len(articles)
        else:
            cfg.mailit_logger.error('需要一个文件列表。')
            ERROR = errno.EACCES
            return -1
    def detach_articles(self,id_):
        """删去加入的资料"""
        try:
            del self._articles[id_]
            return 0
        except IndexError,e:
            cfg.mailit_logger.error("指定的序号不存在！\n     %s"%e)
            return errno.EACCES
    def list_articles(self,id_ = None):
        """列出已增加进的资料"""
        if not id_:
            t=""
            for i in range(len(self._articles)):
                t += 'no.' + str(i) +'\n' + str(self._articles[i]) + '\n'
            output_str = """

            此刻本实例中共有%s份资料:
                %s
                END.
            """ %(len(self._articles),t)
            print output_str
            return 0
        else:
            try:
                print self._articles[id_]
            except IndexError,e:
                cfg.mailit_logger.error("指定序号(%s)的资料不存在"%id_)
                return errno.EACCES
    def _compose_msg(self):
        """把资料编码以适合邮件传输."""
        for article in self._articles:
            # 处理资料
            ctype,encoding = mimetypes.guess_type(article.real_name)
            if ctype is None:
                # 不能确定文件类型的指定为二进制类型。subtype必须有，因此这里octet-sream一定要。
                ctype = 'applicaiton/octet-stream'
            maintype,subtype = ctype.split('/',1)
            #print "maintype:%s.subtype:%s"%(maintype,subtype)
            if maintype == 'application':
                # Class email.mime.appllication.MIMEApplication(_data,...)
                # _data为二进制串。
                # f = open(f_str,'rb')
                msg = email.mime.application.MIMEApplication(article.file_object.read(),_subtype=subtype)
                article.file_object.close()
            elif maintype == 'text':
                msg = email.mime.text.MIMEText(article.file_object.read(),_subtype=subtype)
                article.file_object.close()
            else:
                msg = email.mime.base.MIMEBase(maintype,subtype)
                msg.set_payload(article.file_object.read())
                article.file_object.close()
                email.encoders.encode_base64(msg)
            msg.add_header('Content-Disposition','attachment',filename=article.real_name)
            self.attach(msg)
        return self
    def output(self):
        """
        用于smtp协议的输出
        @return: [发件人,收件人,带有文章的邮件]
        """
        msg = self._compose_msg()
        global ERROR
        if msg['From'] and msg['To']:
            return [msg['From'],msg['To'],msg]
        else:
            cfg.mailit_logger.error("请补全发件人及收件人")
            ERROR = errno.EACCES
            return -1

def postit(smtp_server,user_name,password,from_addr,to_addr,msg = None,message_with_articles = None,debug=1):
    """
    发送邮件
    @todo: 现只能实现最基本的发邮件功能，以后要实现可选择tls、ssl发送邮件。
    @param message_with_articles: 是Message_with_articles对象。
    @param smtp_server: 指定发件用smtp服务器对象。原来设计给定smtp服务器的地址，但这样做会产生闭包，显然不利于单元测试，所以把smtp服务器对象改放在外面。
    @param from_addr: 指定发件人地址
    @param to_add: 指定 收件人地址
    @param debug: 指定本函数的调试级别
    """
    try:
        smtp_server.login(user_name,password)
    except smtplib.SMTPHeloError, e:
        cfg.mailit_logger.error("网络错误,%s"%str(e))
        return errno.EACCES
    except smtplib.SMTPAuthenticationError, e:
        cfg.mailit_logger.error("SMTP认证错误，请检查用户名及密码,%s"%str(e))
        return errno.EACCES
    except smtplib.SMTPException, e:
        cfg.mailit_logger.error("认证方式有误，%s"%str(e))
        return errno.EPFNOSUPPORT
    except Exception, e:
        cfg.mailit_logger.error("其它异常,%s"%str(e))
        raise e
    smtp_server.set_debuglevel(debug)
    if from_addr and to_addr and msg:
        #smtp_server.sendmail(from_addr,to_addr,msg)
        smtp_server.sendmail(from_addr,to_addr,msg.as_string())
    elif message_with_articles:
        smtp_server.sendmail(*message_with_articles.output())
    else:
        cfg.mailit_logger.warning("请检查函数参数")
        return errno.EPERM
    smtp_server.quit()
    return 0
