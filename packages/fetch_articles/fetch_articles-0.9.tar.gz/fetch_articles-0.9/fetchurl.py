#!/usr/bin/env python
# encoding=utf-8
"""
@summary: 从指定pop服务器上取得有图书馆资源url的邮件。
@author: luoboiqingcai<sf.cumt@163.com>
@version: $Id$
"""

import email
from email.header import decode_header
import re
import codecs
import fetch_articles.config as cfg

ERROR = None

def url_list(mail_str,accepted_addrs=None):
    """
    @brief 从字串格式的email中提取url。 只支持非multipart的纯文本邮件。url放在邮件正文里以空行隔开。
    @param accepted_addrs: 一列表或元组，表示可接收的开信地址
    @return ([url1,url2,...],from_)
    """
    global ERROR
    msg = email.message_from_string(mail_str)
    from_ = msg['from']
    #>>>re.sub(r'.*<(.+@.+)>',r'\1','dfjks <123@163.com>')
    #'123@163.com'
    from_ = re.sub(r'.*<(.+@.+)>',r'\1',from_)
    if accepted_addrs and (not from_ in accepted_addrs):
        return -1
    if not msg.is_multipart():
        decoded_string,charset = decode_header(msg['Subject'])[0]
        dec = codecs.getdecoder(charset)
        #if '施峰' == dec(decoded_string)[0]: 是错误的，准确地说是不可移植的，因为不同的python版本里内部用的是不同的默认编码。在python3x里用的所有的内部字符串自动用unicode表示，但在python2x里内部字符串在不同的系统里用的是不同的编码。因此这是在'施峰'前要加上u前缀
        if u'施峰' == dec(decoded_string)[0]:
            body = msg.get_payload(decode=True)
            urls_list_t_ = re.split(r'(\r?\n)+',body)
            urls_list_ = []
            for i in range(len(urls_list_t_)):
                if re.match(r'http://',urls_list_t_[i]):
                    urls_list_.append(urls_list_t_[i])
            return (urls_list_,from_)
        else:
            cfg.fetchurl_logger.warning("该请求不接收")
            return -1
    elif msg.is_multipart():
        cfg.fetchurl_logger.info("含url邮件不能为mutltipart格式！")
        return -1

def fetch_emails_with_url(pop_server,user_name,password,accept_from_addrs,to_file=None,debug_level=None):
    """
    @brief 从pop服务器上取得带有文章url的邮件,这些邮件的发件人必须在accept_from_addrs列表中
    @param accept_from_addrs 指定可接受发件人地址
    @return mail_pairs 以所有行为成员的列表及所有行连起来组成的字串两者组成的元组为成员的列表。
    """
    server = pop_server # 把pop_server提到外面有利于测试。
    pattern = []
    mail_pairs = []
    for i in accept_from_addrs:
        pattern.append(re.compile(r'From:.*'+i))
    if debug_level:
        server.set_debug_level(debug_level)
    server.user(user_name)
    server.pass_(password)
    numMessages = len(server.list()[1])
    #print '开始过滤发件人'
    for i in range(numMessages):
        lines = server.retr(i+1)[1]
        flag = 0
        for j in lines:
            for k in pattern:
                if re.match(k,j):
                    #print 'accepted from:' + j
                    flag = 1
                    server.dele(i+1)
                    break
            if flag == 1:
                break
        # mail_list为以行为分隔把邮件拆成的列表，
        # mail_str是把这些行组合在一起形成的字串形式的邮件
        if flag == 1:
            #print 'i' + str(i)
            mail_list,mail_str = lines,'\n'.join(lines)
            mail_pairs.append((mail_list,mail_str))
    server.quit()
    return mail_pairs
