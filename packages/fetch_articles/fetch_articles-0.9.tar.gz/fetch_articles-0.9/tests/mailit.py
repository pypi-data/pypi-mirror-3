#!/usr/bin/env python
# encoding=utf-8

import unittest
import mock
import sys
import errno
sys.path.append('/home/shifeng/code/my_python_projects/win_sync/calculator')
import email
import email.mime.nonmultipart
import fetch_articles.mailit

#class Testmain(unittest.TestCase):
#    """test main function"""
#    def test_return(self):
#        """test the return value"""
#        self.assertEqual(0,m())

class Test_Message_with_articles(unittest.TestCase):
    """@brief 测试 Message_with_articles 类"""
    def setUp(self):
        """"""
        # 这样是不行的，当离开该上下文file自动关闭.如果上下文里有return，return出的file才有可能是打开状态,原因是python的闭包机制。
        #with open('/home/shifeng/code/my_python_projects/win_sync/calculator/fetch_articles/tests/articles/Python Programming on Win32.pdf') as f:
        #    self.articles = [f,]
        #    self.message_with_articles = fetch_articles.mailit.Message_with_articles()
        f = open('/home/shifeng/code/my_python_projects/win_sync/calculator/fetch_articles/tests/articles/Python Programming on Win32.pdf','rb')
        self.articles = [f,]
        self.from_addr = '20102002043@cqu.edu.cn'
        self.to_addr = 'sf_cumt@yeah.net'
        self.message_with_articles = fetch_articles.mailit.Message_with_articles()
    def test_messge_with_articles(self):
        """测message_with_articles这个实例"""
        self.failIf(not isinstance(self.message_with_articles,fetch_articles.mailit.Message_with_articles))
    def test_attach_articles(self):
        """测试Message_with_articles的attach_articles方法"""
        n = self.message_with_articles.attach_articles(self.articles)
        self.assertEqual(len(self.articles),n)
    def test_attach_articles_with_emptylist(self):
        """测试当给一个空列表时的情况"""
        self.assertEqual(self.message_with_articles.attach_articles([]),0)
    def test_attach_articles_with_str(self):
        """测试当给一空字符串时的反应"""
        self.assertEqual(self.message_with_articles.attach_articles(''),errno.EACCES)
    def test_detach_articles(self):
        """测试Message_with_articles的detach_articles方法"""
        flag = 0
        for i in range(len(self.articles)):
            if self.message_with_articles.detach_articles(i) == errno.EACCES:
                flag = 1
                break
        self.assertTrue(flag)
    def test_list_empty_articles(self):
        """测试Message_with_articles的list_articles方法"""
        self.assertEqual(self.message_with_articles.list_articles(),0)
    def test_list_articles(self):
        self.message_with_articles.attach_articles(self.articles)
        self.message_with_articles.list_articles()
    def test_output_without_fromto(self):
        """测试Message_with_articles的output方法"""
        #self.assertRaises(AttributeError,self.message_with_articles.output)
        self.assertEqual(self.message_with_articles.output(),errno.EACCES)
    def test_output_with_fromto(self):
        """测试当给定了From和To时的行为"""
        self.message_with_articles['From'] = self.from_addr
        self.message_with_articles['To'] = self.to_addr
        self.assertEqual(self.message_with_articles.output(),[self.from_addr,self.to_addr,self.message_with_articles])
class Test_Message_with_articles1(unittest.TestCase):
    """测试带有文章时的行为,暂时只测试pdf文章附件的邮件"""
    def __init__(self, *args,**kargs):
        super(Test_Message_with_articles1, self).__init__(*args,**kargs)
    def setUp(self):
        """fixs"""
        # 这个样子是不得行的。
        #with open('/home/shifeng/code/my_python_projects/win_sync/calculator/fetch_articles/tests/articles/Python Programming on Win32.pdf') as f:
        f = open('/home/shifeng/code/my_python_projects/win_sync/calculator/fetch_articles/tests/articles/Python Programming on Win32.pdf','rb')
        self.articles = [f,]
        self.message_with_articles = fetch_articles.mailit.Message_with_articles()
        self.from_addr = '20102002043@cqu.edu.cn'
        self.to_addr = 'sf_cumt@yeah.net'
        self.message_with_articles['From'] = self.from_addr
        self.message_with_articles['To'] = self.to_addr
        self.message_with_articles.attach_articles(self.articles)
        f_t = open('/home/shifeng/code/my_python_projects/win_sync/calculator/fetch_articles/tests/temps/output.pdf','wb')
        self.f_output = [f_t,]
    def test_articles_output(self):
        """输出文章附件"""
        from_,to_,msg = self.message_with_articles.output()
        self.f_output[0].write(msg.get_payload()[0].get_payload(decode=True))
    def test_len_email(self):
        self.assertEqual(len(self.message_with_articles.output()[2].get_payload()),1)
    def test_output_with_articles1(self):
        """测试当带有文章时邮件的行为"""
        self.message_with_articles.list_articles()
        from_,to_,msg = self.message_with_articles.output()
        self.assertTrue(isinstance(msg.get_payload(),list),"附件不应有更深层次结构")
        def test_output_with_articles2(self):
            """测试当带有文章时邮件的行为"""
            self.assertTrue(issubclass(type(msg.get_payload()[0],email.message.Message),'是一个Message实例'))

if __name__ == "__main__":
    unittest.main()
