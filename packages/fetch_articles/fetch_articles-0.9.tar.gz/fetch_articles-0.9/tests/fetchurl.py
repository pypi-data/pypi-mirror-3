# encoding=utf-8
import unittest
import mock
import re
import sys
sys.path.append('/home/shifeng/code/my_python_projects/win_sync/calculator/')
import fetch_articles.fetchurl

class Test_urls_list(unittest.TestCase):
    """测试fetchurl.py中的urls_list函数"""
    def __init__(self, *args,**kargs):
        super(Test_urls_list, self).__init__(*args,**kargs)
    def setUp(self):
        """fixtures"""
        f = open('/home/shifeng/code/my_python_projects/win_sync/calculator/fetch_articles/tests/t_mails/url_mail1','rb')
        self.msg = f.read()
        self.pattern = re.compile(r'http://')
    def test_with_1line(self):
        """测试当只有一行要下载文章地址时urls_list函数的行为。"""
        self.assertTrue(isinstance(fetch_articles.fetchurl.urls_list(self.msg),list))
    def test_with_1line_url(self):
        """测试当只有一行要下载文章地址时urls_list函数返回的列表中的内容是否正确。"""
        self.assertTrue(re.match(self.pattern,fetch_articles.fetchurl.urls_list(self.msg)[0]))
    def test_with_2line(self):
        """测试当有两行要下载文章地址时urls_list函数的行为。"""
        self.assertTrue(isinstance(fetch_articles.fetchurl.urls_list(self.msg),list))
    def test_with_2line_url(self):
        """测试当只有一行要下载文章地址时urls_list函数返回的列表中的内容是否正确。"""
        flag = 1
        for i in fetch_articles.fetchurl.urls_list(self.msg):
            if not re.match(self.pattern,i):
                flag = 0
        self.assertTrue(flag)

class Test_fetch_emails_with_url(unittest.TestCase):
    """测试fetchurl.py里的fetch_emails_with_url函数"""
    def setUp(self):
        """fixtures"""
        self.pop_str = 'pop3.cqu.edu.cn'
        self.user_name = 'foo'
        self.password = 'password'
        self.accept_from_addr = ['20102002043@cqu.edu.cn',]
        self.mail_str_list = open('/home/shifeng/code/my_python_projects/win_sync/calculator/fetch_articles/tests/t_mails/url_mail1','r').readlines()
    @mock.patch('poplib.POP3')
    def test_return_form(self,Mock_POP3):
        """测试返回值的形式。"""
        from poplib import POP3
        self.pop_server = POP3(self.pop_str)
        self.pop_server.list.return_value = ['response',['n',],'octets']
        self.pop_server.retr.return_value = ['response',self.mail_str_list,'octets']
        self.assertTrue(isinstance(fetch_articles.fetchurl.fetch_emails_with_url(self.pop_server,self.user_name,self.password,self.accept_from_addr),list))

    @mock.patch('poplib.POP3')
    def test_return_len(self,Mock_POP3):
        """测试返回值的形式。"""
        from poplib import POP3
        self.pop_server = POP3(self.pop_str)
        self.pop_server.list.return_value = ['response',['n',],'octets']
        self.pop_server.retr.return_value = ['response',self.mail_str_list,'octets']
        self.assertTrue(len(fetch_articles.fetchurl.fetch_emails_with_url(self.pop_server,self.user_name,self.password,self.accept_from_addr)[0])>0)

if __name__ == '__main__':
    unittest.main()
