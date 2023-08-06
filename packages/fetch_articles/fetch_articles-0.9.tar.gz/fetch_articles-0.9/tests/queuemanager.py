#!/usr/bin/env python
# -*- encoding:utf-8 -*-

'''
对 quequemanager.py进行测试
'''
import unittest
import re
import pickle
import os
import sys
sys.path.append('/home/shifeng/code/my_python_projects/win_sync/calculator/')
from fetch_articles.queuemanager import Queue,Metadata
from fetch_articles import config as cfg

PROJECT_URI = "/home/shifeng/code/my_python_projects/win_sync/calculator/fetch_articles/"

class TestMetadata(unittest.TestCase):
    """测试queuemanger.py中的Metadata"""
    def setUp(self):
        self.metadata = Metadata()
        self.metadata.to_addr = 'sf.cumt@163.com'
    def test_print(self):
        #print self.metadata
        self.assert_(re.match(r'time:.+;to_addr:.*',str(self.metadata)))

class TestQueue(unittest.TestCase):
    """测试queuemanger.py中的Queue"""
    def setUp(self):
        """前期准备"""
        self.m_p = PROJECT_URI + 'tests/meta.db'
        self.u_p = PROJECT_URI + 'tests/users.db'
        self.m_p1 = PROJECT_URI + 'tests/meta1.db'
        self.u_p1 = PROJECT_URI + 'tests/users1.db'
        self.qp = PROJECT_URI + 'tests/queue'
        self.qp1 = PROJECT_URI + 'tests/queue1'
        for i in (self.m_p,self.m_p1,self.u_p,self.u_p1):
            if os.path.exists(i):
                os.remove(i)
        self.queueobj = Queue(meta_path=self.m_p,users=['sf.cumt@163.com','717968750@qq.com'],userdbpath=self.u_p,queue_path=self.qp)
        self.i_file = open(PROJECT_URI+'tests/articles/软件架构设计.pdf','r')
        self.i_item = ('封俯孔技术研究.pdf',self.i_file)
        self.queueobj1 = Queue(meta_path=self.m_p1,users=['sf.cumt@163.com','717968750@qq.com'],userdbpath=self.u_p1,queue_path=self.qp1)
        self.queueobj1.add([self.i_item,],'717968750@qq.com')
    def test_add(self):
        """测试add方法"""
        self.assertTrue(self.queueobj.add([self.i_item,],'717968750@qq.com'))
        self.assertTrue(self.queueobj1.add([self.i_item,],'717968750@qq.com'))
    def test_pop(self):
        """测试pop方法"""
        self.assertRaises(KeyError,self.queueobj.pop,0)
    def test_pick(self):
        """测试pick方法"""
        self.assertRaises(KeyError,self.queueobj.pick,0)
        self.assertRaises(KeyError,self.queueobj.pick,1)
        self.assertEqual(self.queueobj1.pick(1)[0],'封俯孔技术研究.pdf')
    def testcandidate(self):
        """测试candidate方法"""
        self.assertEqual(0,len(self.queueobj.candidate()))
        rt = self.queueobj1.candidate()
        self.assert_(isinstance(rt[0],tuple))
        self.queueobj1.add([self.i_item,],'717968750@qq.com')
        rt = self.queueobj1.candidate(protect=False,strategy=2)
        self.assertEqual(rt[1],'717968750@qq.com')
        self.assertEqual(rt[0][0][0],'封俯孔技术研究.pdf')
        self.assertTrue(self.queueobj1.candidate() in (None, [])) #上一行代码把队列里仅有的一个成员取走了
    def test_show(self):
        """测试show方法"""
        self.assertEqual(self.queueobj.show(),0)
    def tearDown(self):
        """清理测试"""
        self.i_file.close()
        del self.queueobj
        del self.i_file
        del self.i_item
        del self.queueobj1
        os.remove(self.m_p)
        os.remove(self.m_p1)
        os.remove(self.u_p)
        os.remove(self.u_p1)
        #TODO 以下两个语句可注释掉
        for i in os.listdir(self.qp):
            os.remove(self.qp+'/'+i)
        for i in os.listdir(self.qp1):
            os.remove(self.qp1+'/'+i)

class TestAdd(unittest.TestCase):
    """测试Queue的add方法"""
    def setUp(self):
        self.m_p = PROJECT_URI + 'tests/meta.db'
        self.u_p = PROJECT_URI + 'tests/users.db'
        self.qp = PROJECT_URI + 'tests/queue'
        for i in (self.m_p,self.u_p):
            if os.path.exists(i):
                os.remove(i)
        self.i_file = open(PROJECT_URI+'tests/articles/软件架构设计.pdf','r')
        self.i_item = ('封俯孔技术研究.pdf',self.i_file)
        self.queueobj = Queue(meta_path=self.m_p,users=['717968750@qq.com','sf.cumt@163.com'],userdbpath=self.u_p,queue_path=self.qp,candidate_num=5,warn_limit=1,reset_limit=4)
    def test_add0(self):
        '''
        file_pairs
        '''
        self.assertRaises(TypeError,self.queueobj.add,self.i_item,'717968750@qq.com')
        self.assertRaises(TypeError,self.queueobj.add,self.i_item,'sf.cumt@qq.com')
    def test_add(self):
        for i in range(3):
            self.queueobj.add([self.i_item,],'717968750@qq.com')
        #self.queueobj.show()
        self.assertRaises(cfg.QueueOverflow,self.queueobj.add,[self.i_item,],'717968750@qq.com') #由于reset_limit为4
        self.assertEqual(4,len(self.queueobj.candidate()))
        #print self.queueobj.db
    def tearDown(self):
        del self.queueobj
        os.remove(self.m_p)
        os.remove(self.u_p)
        self.i_file.close()
        del self.i_file
        del self.i_item
        for i in os.listdir(self.qp):
            os.remove(self.qp+'/'+i)
class TestCandidate(unittest.TestCase):
    """测试Queue的candidate方法"""
    def setUp(self):
        self.m_p = PROJECT_URI + 'tests/meta.db'
        self.u_p = PROJECT_URI + 'tests/users.db'
        self.qp = PROJECT_URI + 'tests/queue'
        for i in (self.m_p,self.u_p):
            if os.path.exists(i):
                os.remove(i)
        self.i_file = open(PROJECT_URI+'tests/articles/软件架构设计.pdf','r')
        self.i_item = ('封俯孔技术研究.pdf',self.i_file)
        self.queueobj = Queue(meta_path=self.m_p,users=['717968750@qq.com','sf.cumt@163.com'],userdbpath=self.u_p,queue_path=self.qp,candidate_num=5,warn_limit=1,reset_limit=10)
        for i in range(7):
            self.queueobj.add([self.i_item,],'717968750@qq.com')
        del self.queueobj
    def test_candidate(self):
        """测试Queue的candidate方法在重启时的行为"""
        q = Queue(meta_path=self.m_p,users=['717968750@qq.com','sf.cumt@163.com'],userdbpath=self.u_p,queue_path=self.qp,candidate_num=5,warn_limit=1,reset_limit=10)
        self.assertEqual(5,len(q.candidate(False)))
        self.assertEqual(2,len(q.candidate(False)))
        self.assertEqual(0,len(q.candidate(False)))
    def test_candidate1(self):
        """测试strategy 2时的行为"""
        q = Queue(meta_path=self.m_p,users=['717968750@qq.com','sf.cumt@163.com'],userdbpath=self.u_p,queue_path=self.qp,candidate_num=6,warn_limit=1,reset_limit=10)
        rt = q.candidate(protect=False,strategy=2)
        self.assertEqual(6,len(rt[0]))
        self.assertEqual('717968750@qq.com',rt[1])
        for i in range(4):
            q.add([self.i_item,],'sf.cumt@163.com')
        #print pickle.loads(q.userdb['sf.cumt@163.com'])
        #print pickle.loads(q.userdb['717968750@qq.com'])
        rt = q.candidate(protect=False,strategy=2)
        self.assertTrue(len(rt[0]) in (1,4))
        rt = q.candidate(protect=False,strategy=2)
        self.assertTrue(len(rt[0]) in (1,4))
    def test_addcandidate(self):
        """测试重启后一边增加成员一边candidate时的行为"""
        q = Queue(meta_path=self.m_p,users=['717968750@qq.com','sf.cumt@163.com'],userdbpath=self.u_p,queue_path=self.qp,candidate_num=6,warn_limit=1,reset_limit=10)
        self.assertEqual(6,len(q.candidate(False)))
        q.candidate(False)
        q.add([self.i_item,],'717968750@qq.com')
        self.assertEqual(1,len(q.candidate(False)))
    def tearDown(self):
        os.remove(self.m_p)
        os.remove(self.u_p)
        for i in os.listdir(self.qp):
            os.remove(self.qp+'/'+i)
        self.i_file.close()
        del self.i_file
        del self.i_item
class TestReset(unittest.TestCase):
    """测试Queue的reset方法"""
    def setUp(self):
        class MyQueue(Queue):
            """为方法测试,继承并修改原来的Queue"""
            def top(self):
                """@return: top属性"""
                return self._K
        self.m_p = PROJECT_URI + 'tests/meta.db'
        self.u_p = PROJECT_URI + 'tests/users.db'
        for i in (self.m_p,self.u_p):
            if os.path.exists(i):
                os.remove(i)
        self.qp = PROJECT_URI + 'tests/queue'
        self.i_file = open(PROJECT_URI+'tests/articles/软件架构设计.pdf','r')
        self.i_item = ('封俯孔技术研究.pdf',self.i_file)
        self.queueobj = MyQueue(meta_path=self.m_p,users=['717968750@qq.com','sf.cumt@163.com'],userdbpath=self.u_p,queue_path=self.qp,candidate_num=5,warn_limit=1,reset_limit=10)
    def test_reset(self):
        """测试reset方法"""
        self.queueobj.add([self.i_item for i in range(5)],'717968750@qq.com')
        self.queueobj.add([self.i_item for i in range(3)],'sf.cumt@163.com')
        self.assertEqual(8,self.queueobj.top())
        self.queueobj.reset()
        self.assertEqual(8,self.queueobj.top())
    def test_candidatereset(self):
        """测试candidate与reset结合时的行为"""
        for i in range(6):
            self.queueobj.add([self.i_item,],'717968750@qq.com')
        self.queueobj.candidate()
        self.assertEqual(2,len(self.queueobj.db))
        self.assertEqual(6,self.queueobj.top())

        self.queueobj.add([self.i_item,],'sf.cumt@163.com')
        self.queueobj.add([self.i_item,],'sf.cumt@163.com')
        self.assertEqual(4,len(self.queueobj.db))
        self.assertEqual(8,self.queueobj.top())

        #print self.queueobj.db
        self.queueobj.reset()
        #print self.queueobj.db
        self.assertEqual(3,self.queueobj.top())
        self.assertEqual(4,len(self.queueobj.db))
    def test_candidatereset1(self):
        for i in range(6):
            self.queueobj.add([self.i_item,],'717968750@qq.com')
        self.queueobj.candidate(protect=False,strategy=2)
        for i in range(6):
            self.queueobj.add([self.i_item,],'sf.cumt@163.com')
        self.queueobj.candidate(protect=False,strategy=2)
        self.queueobj.reset()
        m_lt = self.queueobj.candidate()
        self.assertTrue(len(m_lt) in (5,1))
    def tearDown(self):
        del self.queueobj
        os.remove(self.m_p)
        os.remove(self.u_p)
        self.i_file.close()
        del self.i_file
        del self.i_item
        for i in os.listdir(self.qp):
            os.remove(self.qp+'/'+i)
if __name__ == '__main__':
    unittest.main()
