# encoding=utf-8

"""
@summary: 从给的网址下载文章，并放到指定目录下。
@version: $Id$
@author: luoboiqingcai<sf.cumt@163.com>
"""
import urllib2
import re
import os
import tempfile
import fetch_articles.config as cfg

class FileWraper(object):
    """给内置文件对象增加功能"""
    def __init__(self, f_obj=None,f_name=''):
        self.file_object = f_obj
        self.real_name = f_name

def get_article(url,to_dir=None):
    """
    根据url取得文章
    @param url: 图书馆里某篇文章的地址。
    @return: 返回[文件对象,文章题目]
    """
    pattern1 = re.compile(r'^.*=(.*\.pdf|.*\.kdh)\r\n')
    try:
        article = urllib2.urlopen(url)
    except:
        cfg.get_article_logger.error("打开链接地址时出错！")
        return FileWraper()
    article_name = re.sub(pattern1,r'\1',article.info().headers[4])
    if to_dir and os.path.isdir(to_dir):
        try:
            f = open(os.path.join(to_dir,article_name),'w+b')
            f.write(article.read())
            os.fsync(f.fileno())
            f.flush()
        except:
            cfg.get_article_logger.error('打开临时文件%s出错!'%article_name)
            raise
    else:
        try:
            f = tempfile.SpooledTemporaryFile()
            f.write(article.read())
            os.fsync(f.fileno())
            f.flush()
        except:
            cfg.get_article_logger.error('默认位置临时文件写入出错！')
    f.seek(0,os.SEEK_SET)
    f_wraper = FileWraper(f,article_name)
    return f_wraper
