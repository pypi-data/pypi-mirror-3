#encoding:utf-8
"""
@summary: 整个项目的配置在这里。
@author: luoboiqingcai<sf.cumt@163.com>
"""
import logging
import logging.handlers
import sys
import ConfigParser
import os.path
import errno

ERROR = None

class QueueOverflow(Exception):
    """当Queue中add成员的个数超过reset_limit时会发生死锁"""
    def __init__(self, arg):
        Exception.__init__(self, arg)

#logfile = '/home/shifeng/code/my_python_projects/win_sync/calculator/fetch_articles/logfile.log'
logfile = 'logfile.log'
maxByte = 100000
backupCount = 10
debug_level = logging.DEBUG
#cfg_path = '/home/shifeng/code/my_python_projects/win_sync/calculator/fetch_articles/main.cfg'
cfg_path = 'main.cfg'
fetch_articles_logger = logging.getLogger('fetch_articles')
fetch_articles_logger.setLevel(debug_level)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler = logging.handlers.RotatingFileHandler(logfile,'a',maxByte,backupCount)
file_handler.setFormatter(formatter)
fetch_articles_logger.addHandler(file_handler)
fetchurl_logger = logging.getLogger('fetch_articles.fetchurl')
fetchurl_logger.setLevel(debug_level)
get_article_logger = logging.getLogger('fetch_articles.get_article')
get_article_logger.setLevel(debug_level)
config_logger = logging.getLogger('fetch_articles.config')
config_logger.setLevel(debug_level)
queuemanager_logger = logging.getLogger('fetch_articles.queuemanager')
queuemanager_logger.setLevel(debug_level)

if os.path.exists(cfg_path):
    if os.path.isfile(cfg_path):
        try:
            configfile = open(cfg_path,'rb')
        except Exception, e:
            config_logger.error('打开配置文件出错！%s'%str(e))
            raise e
        else:
            config = ConfigParser.SafeConfigParser()
            try:
                config.readfp(open(cfg_path))
            except ConfigParser.ParsingError, e:
                config_logger.error('解析配置文件时出错。')
                raise e
            try:
                from_addr = config.get('Main','from_addr')
                smtp_server_str = config.get('Main','smtp_server_str')
                smtp_user_name = config.get('Main','smtp_user_name')
                smtp_password = config.get('Main','smtp_password')
                pop_server_str = config.get('Main','pop_server_str')
                pop_user_name = config.get('Main','pop_user_name')
                pop_password = config.get('Main','pop_password')
                from_local = config.getboolean('Main','from_local')
                smtp_debug = config.getint('Main','smtp_debug')
                accept_from_addrs = [i for i in config.get('Main','accept_from_addrs').split(',') if '@' in i]
                meta_path = config.get('Main','meta_path')
                user_path = config.get('Main','user_path')
                queue_path = config.get('Main','queue_path')
                candidate_num = config.getint('Main','candidate_num')
                reset_limit = config.getint('Main','reset_limit')
            except ConfigParser.Error, e:
                config_logger.error('配置文件内容有问题。')
                raise e
    else:
        config_logger.error('给出的路径为目录。')
        ERROR = errno.EACCES
        sys.exit(2)
else:
    config = ConfigParser.SafeConfigParser()
    config.add_section('Main')
    from_addr ='xx@163.com'
    config.set('Main','from_addr',from_addr)
    smtp_server_str = 'smtp.163.com'
    config.set('Main','smtp_server_str',smtp_server_str)
    smtp_user_name = 'xx@163.com'
    config.set('Main','smtp_user_name',smtp_user_name)
    smtp_password = 'password'
    config.set('Main','smtp_password',smtp_password)
    pop_server_str = 'pop3.163.com'
    config.set('Main','pop_server_str',pop_server_str)
    pop_user_name = 'xx@163.com'
    config.set('Main','pop_user_name',pop_user_name)
    pop_password = 'password'
    config.set('Main','pop_password',pop_password)
    from_local = 'False'
    config.set('Main','from_local',from_local)
    smtp_debug = '1'
    config.set('Main','smtp_debug',smtp_debug)
    accept_from_addrs = ['xx@163.com',]
    config.set('Main','accept_from_addrs',accept_from_addrs[0])
    meta_path = 'meta.db'
    config.set('Main','meta_path',meta_path)
    user_path = 'user.db'
    config.set('Main','user_path',user_path)
    queue_path = 'queue'
    config.set('Main','queue_path',queue_path)
    candidate_num = '5'
    config.set('Main','candidate_num',candidate_num)
    reset_limit = '4'
    config.set('Main','reset_limit',reset_limit)
    with open(cfg_path,'wb') as configfile:
        config.write(configfile)
