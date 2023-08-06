#!/usr/bin/env python
# encoding=utf-8
"""
@summary: 本包的可执行文件。
@author: luoboiqingcai<sf.cumt@163.com>
@version: $Id$
"""

import smtplib
import poplib
import getopt
import errno
import os
import os.path
import sys
#sys.path.insert(0,'/home/shifeng/code/my_python_projects/win_sync/calculator')
#sys.path.append('C:/cygwin/home/Administrator/code/')
# optparse:
# Deprecated since version 2.7: The optparse module is deprecated and will not be developed further; development will continue with argparse module.
#import argparse
import fetch_articles.mailit
import fetch_articles.fetchurl
import fetch_articles.get_article
from fetch_articles.queuemanager import Queue
from fetch_articles.get_article import FileWraper
import fetch_articles.config as cfg

ERROR = None

def main(from_addr,to_addr='',articles='',smtp_server_str='',smtp_user_name='',smtp_password='',pop_server_str='',pop_user_name='',pop_password='',from_local=False):
    """
    有pop_server则从pop服务器上取得要传输的文章url并在图书馆中下载这些文章。article为本地文件名,如果没有提供pop_server才用article来传输本地文章。
    @param articles: 是一个所有资料文件名组成的列表,当from_local为False时articles可不管。
    @param to_addr: 收件人地址，对于from_local为False时to_addr可不管。
    """
    #article,article_name = fetch_articles.get_article()
    articles_file = []
    global ERROR
    try:
        smtp_server = smtplib.SMTP(smtp_server_str)
    except Exception, e:
        cfg.fetch_articles_logger.error("不能与smtp服务器建立连接!smtp_server_str: %s"%smtp_server_str)# 提前进行smtp连接测试，免得之后从队列里取出信件smtp又连不上时发生信件丢失。
        ERROR = errno.EREMOTE
        return
    try:
        pop_server = poplib.POP3(pop_server_str)
    except Exception, e:
        cfg.fetch_articles_logger.error("不能与pop服务器建立连接！pop_server_str: %s"%pop_server_str)
        ERROR = errno.EREMOTE
        return
    if not os.path.isdir(cfg.queue_path):
        cfg.fetch_articles_logger.error("队列目录还未建立!")
        os.mkdir(cfg.queue_path)
        cfg.fetch_articles_logger.info("创建队列目录成功")
    queue = Queue(meta_path=cfg.meta_path, users=cfg.accept_from_addrs, userdbpath=cfg.user_path, queue_path=cfg.queue_path, candidate_num=cfg.candidate_num, reset_limit=cfg.reset_limit)
    if not from_local: #从队列中发件
        m_with_articles = fetch_articles.mailit.Message_with_articles()
        m_with_articles['From'] = from_addr
        mail_pairs = fetch_articles.fetchurl.fetch_emails_with_url(pop_server,user_name=pop_user_name,password=pop_password,accept_from_addrs=cfg.accept_from_addrs)
        for i,j in mail_pairs:
            url_set = set()
            rt = fetch_articles.fetchurl.url_list(j,cfg.accept_from_addrs)
            if  rt == -1:
                continue
            else:
                [url_set.add(i) for i in rt[0]]
            if url_set:
                for url in url_set:
                    article_wraper = fetch_articles.get_article.get_article(url)
                    if article_wraper.file_object and article_wraper.real_name:
                        try:
                            queue.add([(article_wraper.real_name,article_wraper.file_object),],rt[1])
                        except cfg.QueueOverflow, e:
                            cfg.fetch_articles_logger.error('队列将要溢出！剩下的资料将丢弃')
                            break
            else:
                cfg.fetch_articles_logger.warning("未从pop服务器处取得%s的url_set为空。"%rt[1])
        tem = queue.candidate(strategy=2)
        if tem:
            cads_list,to_addr = tem[0], tem[1]
        else:
            cfg.fetch_articles_logger.info("队列中没有候选成员以供发出")
            return 0
        cfg.fetch_articles_logger.debug('cads_list:%s'%cads_list)
        if cads_list:
            #articles_file = [FileWraper(f_obj=obj,f_name=name) for name,obj,to_addr in cads_list]
            articles_file = [FileWraper(f_obj=obj,f_name=name) for name,obj in cads_list]
            m_with_articles['To'] = to_addr
            m_with_articles.attach_articles(articles_file)
            fetch_articles.mailit.postit(smtp_server,smtp_user_name,smtp_password,*m_with_articles.output(),debug=cfg.smtp_debug)
            cfg.fetch_articles_logger.info("共%d份资料发送到%s!"%(len(articles_file),to_addr))
        else:
            cfg.fetch_articles_logger.info("队列中没有候选成员以供发出")
            return 0
    else:
        if isinstance(articles,list):
            m_with_articles = fetch_articles.mailit.Message_with_articles()
            m_with_articles['From'],m_with_articles['To'] = from_addr,to_addr
            for i in range(len(articles)):
                try:
                    f = open(articles[i],'rb')
                    articles_file[i] = FileWraper(f,f.name),
                except IOError, e:
                    cfg.fetch_articles_logger.warning("打开文件%s时出错"%articles[i])
                    raise e
            m_with_articles.attach_articles(articles_file)
            fetch_articles.mailit.postit(smtp_server,smtp_user_name,smtp_password,*m_with_articles.output(),debug=cfg.smtp_debug)
        else:
            cfg.fetch_articles_logger.warning("给的参数应是一个文件名列表，而现在给的是%s"%articles)

def usage():
    """
    输出帮助文字
    """
    print """
            /\_/\\
       ____/ o o \\
     /~____  =ø= /
    (______)__m_m)

    命令行接口帮助：
    -h,--help 显示本帮助
    -d,--deamon 以守护进程的方式运行本程序
    --smtp_server_str 设置发资料用的smtp服务器地址
    --smtpusername 设置smtp认证的用户名
    --smtppassword 设置smtp认证的密码
    --from_addr 设置寄信人地址
    --to_addr 设置收件人地址
    ---article_file 文章，如pdf文件或kdh文件的全路径
    """
if __name__ == '__main__':
    smtp_sever_str = ''
    smtpusername = ''
    smtppassword = ''
    from_addr = ''
    to_addr = ''
    article_file_str = ''
    article_file = None
    deamon_mode = False

    #parser = argparse.ArgumentParser(description="交互式执行文件传输，本程序一般作为服务执行，交互式执行常用于程序排错。")
    try:
        opts,args = getopt.getopt(sys.argv[1:],'dh',['deamon','help','smtp_server_str=','smtpusername=','smtppassword=','from_addr=','to_addr=','article_file='])
    except getopt.GetoptError,err:
        print str(err)
        sys.exit(2)
    if opts:
        for o,a in opts:
            if o == '--smtp_server_str':
                smtp_server_str = a
            elif o == '--smtpusername':
                smtpusername = a
            elif o == '--smtppassword':
                smtppassword = a
            elif o == '--from_addr':
                from_addr = a
            elif o == '--to_addr':
                to_addr = a
            elif o == '--article_file':
                article_file_str = a
            elif o in ('-h','--help'):
                usage()
            elif o in ('-d','--deamon'):
                deamon_mode = True
            else:
                usage()
                assert False,"unhandled optioin"
    else:
        usage()
        sys.exit(2)
    if deamon_mode:
        main(cfg.from_addr,smtp_server_str=cfg.smtp_server_str,smtp_user_name=cfg.smtp_user_name,smtp_password=cfg.smtp_password,pop_server_str=cfg.pop_server_str,pop_user_name=cfg.pop_user_name,pop_password=cfg.pop_password,from_local=cfg.from_local)
    else:
        main(from_addr,to_addr,articles=[article_file_str,],smtp_server_str=smtp_server_str,smtp_user_name=smtpusername,smtp_password=smtppassword,from_local=True)
