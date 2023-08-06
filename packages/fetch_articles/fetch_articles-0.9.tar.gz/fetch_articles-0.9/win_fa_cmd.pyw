# encoding=utf-8
'''
@author: luoboiqingcai<sf.cumt@163.com>
@brief: 这个是用来做后台运行的。后来想了想还是用py2exe把fa_cmd.py变成exe文件，再让任务说计划每隔一段时间运行一次比较好。但运行会出现黑框就不爽了。
'''
import os
import sys
import time
import os.path
#import atexit
#sys.path.insert(0,'C:/cygwin/home/Administrator/code')
#sys.path.insert(0,'/home/shifeng/code/my_python_projects/win_sync/calculator/')
import fetch_articles
import fetch_articles.config as cfg
import fetch_articles.fa_cmd as fa_cmd

delay = 10*60
pid = os.getpid()
pid_f = 'pid.lock'

#@atexit.register
def cleanup():
    """cleanup"""
    try:
        os.remove(pid_f)
    except:
        sys.stderr.write('cleanup goes wrong')

if __name__ == '__main__':
    try:
        with open(pid_f,'w') as f:
            f.write(str(pid))
        while True:
            # 不能连接太频繁，小心被ISP拉进黑名单里！
            #win32api.ShellExecute(0,'open','fa.py','','',0)
            fa_cmd.main(cfg.from_addr,smtp_server_str=cfg.smtp_server_str,smtp_user_name=cfg.smtp_user_name,smtp_password=cfg.smtp_password,pop_server_str=cfg.pop_server_str,pop_user_name=cfg.pop_user_name,pop_password=cfg.pop_password,from_local=cfg.from_local)
            time.sleep(delay)
        os.remove(pid_f)
        sys.exit(0)
    except KeyboardInterrupt:
        cleanup()
        sys.exit(1)
