#!/usr/bin/env python
# -*- encoding:utf-8 -*-
'''
@author: luoboiqingcai<sf.cumt@163.com>
@summary: 实现发件的队列管理
'''

import time
import StringIO
import sys
import fetch_articles.config as cfg
import anydbm
import re
import tempfile
import os
import os.path
import shutil
import pickle

class Metadata(object):
    """队列中对象的元信息"""
    def __init__(self,pickled_str=''):
        """该对象一般都是直接初始化，其它对象一般不需调用。当从数据库中重建meta信息时才会需要提供参数。
        @param pickled_str: pickle后的字串，用于重建Metadata对象。
        """
        self.to_addr = ''
        if pickled_str:
            self.meta = pickle.loads(pickled_str)
            #print self.meta
            self.ctime = self.meta['ctime']
            self.to_addr = self.meta['to_addr']
        else:
            self.ctime = time.time()
            self.to_addr = ''
            self.meta = {'ctime':self.ctime,'to_addr':self.to_addr}
    def __str__(self):
        """
        返回格式化信息以便于在L{add}方法中进行存入或提取.
        """
        if not self.to_addr:
            raise AttributeError,'self.to_addr has not been set yet!'
        return 'time:%f;to_addr:%s'%(self.ctime,self.to_addr)
    def serialized(self):
        """返回序列后的字串"""
        if not self.to_addr:
            raise AttributeError,'self.to_addr has not been set yet!'
        else:
            self.meta['to_addr'] = self.to_addr
        return pickle.dumps(self.meta)

class Queue(object):
    """
    队列类
    @todo: 原子操作

    """
    def __init__(self,meta_path,users,userdbpath,queue_path,candidate_num=10,warn_limit=2,reset_limit=4):
        '''
        @param meta_path: 元数据库文件的位置
        @param users: [user1,user2,user3,...]被允许的用户的邮箱列表
        @param userdbpath: 许可用户数据库位置
        @param queue_path: 队列目录的位置
        @param warn_limit: 当队列中的成员个数超过warn_limit后就会发出警示信息
        @param reset_limit: 当_unique(self)生成的唯一标识超过reset_limit后会调用reset(self)对队列进行重置,为了不至于死锁，连续add的次数不能超过reset_limit!
        '''
        self._warn_limit = warn_limit
        self._meta_path = meta_path
        self._users = users
        self._userdb_path = userdbpath
        self._reset_limit = reset_limit
        self._cad_num = candidate_num
        self._LOCK = False #sel._LOCK 用于标识队列管理器正在进行重置，不要打扰它。
        self._last_cand_time = 0
        if re.match(r'.+/$',queue_path):
            self._queue_path = queue_path[:-1]
        else:
            self._queue_path = queue_path
        try:
            # self.db:
            #
            # {
            #  '1':pickle.dumps({'title':'xxx.pdf','metadata':pickle.dumps(Metadata())}),
            #  '2':pickle.dumps({'title':'xxx.pdf','metadata':pickle.dumps(Metadata())})
            # }
            self.db = anydbm.open(meta_path,'c')
        except Exception,e:
            cfg.queuemanager_logger.error('meta_path:%s.打开元数据库出错！'%self._meta_path)
            raise e
        try:
            # self.userdb:
            #
            # {
            #   'xx@163.com':pickle.dumps([1,2]),
            #  'yy@126.com':pickle.dumps([4,]),
            #  'zz@gmail.com':pickle.dumps([5,])
            # }
            self.userdb = anydbm.open(userdbpath,'c')
        except Exception, e:
            cfg.queuemanager_logger.error('meta_path:%s.打开用户数据库出错！'%self._userdb_path)
            raise e
        for user in users:
            if user not in self.userdb:
                self.userdb[user] = pickle.dumps(set())
        for i in self.userdb:
            if i not in users:
                cfg.queuemanager_logger.warn('%s has been excluded.'%i)
        if 'top' in self.db:
            self._K = int(self.db['top']) # self.db['top']是目录最大的标识号
        else:
            self._K = 0
            self.db['top'] = '0'
    def _unique(self):
        """产生在相当长的时间内不重复的对象标识"""
        self._K += 1
        return self._K
    def reset(self):
        """当长时间运行后，_unique(self)产生的唯一标识会越界。因此要进行清理。还有一种情况是进程被信号中断或意外关机导致数据不一致。"""
        if self._LOCK == True:
            self.queuemanager_logger.warn("正在重置队列，请勿打扰。")
            return
        self._LOCK = True
        self.db.close()
        tempdir_path = tempfile.mkdtemp()
        tempdir1_path = tempfile.mkdtemp()
        tempf_fd,tempf_path = tempfile.mkstemp(text=False)
        tempf = os.fdopen(tempf_fd,'wb')
        for i in os.listdir(self._queue_path):
            if re.match(r'[0-9]+',i):
                shutil.copy(self._queue_path+'/'+i,tempdir_path)
            else:
                shutil.copy(self._queue_path+'/'+i,tempdir1_path)
        with open(self._meta_path,'rb') as f:
            tempf.write(f.read())
            tempf.close()
        os.remove(self._meta_path)#以前少了这行,找了半天才找到这个bug
        db_ = anydbm.open(tempf_path)
        self.db = anydbm.open(self._meta_path,'c')
        i = 0
        for k,v in db_.iteritems():
            if re.match(r'[0-9]+',k):
                i += 1
                self.db[str(i)] = v
                if os.path.isfile(tempdir_path + '/' + k):
                    shutil.copy(tempdir_path + '/' + k, self._queue_path + '/' + str(i))
                self.db['top'] = str(i)
                self._K = i
        shutil.rmtree(tempdir_path)
        #TODO 将莫名文件打包返回
        shutil.rmtree(tempdir1_path)
        os.remove(tempf_path)
        to_s = self.userdb.keys()
        for to_ in to_s:
            del self.userdb[to_]
        for i in self.db:
            #print pickle.loads(pickle.loads(self.db[i])['metadata'])
            #print pickle.loads(self.db[i])['metadata']
            if i == 'top':
                continue
            pickled_meta = pickle.loads(self.db[i])['metadata']
            to_addr = Metadata(pickled_meta).to_addr
            #print 'to_addr' + to_addr
            if to_addr in self.userdb:
                    #self.userdb[to_addr] = pickle.dumps(pickle.loads(self.userdb[to_addr]).add(int(i)))
                temp = pickle.loads(self.userdb[to_addr])
                temp.add(int(i))
                self.userdb[to_addr] = pickle.dumps(temp) #set()的add方法不返回对象！
            else:
                self.userdb[to_addr] = pickle.dumps(set([int(i),]))
        self._LOCK = False
    def add(self,file_pairs,to_addr):
        """
        加入一组对象
        @param file_pairs: 某个对象
              file_pairs[(文件对象中文章标题,文件对象),...]
        @param to_addr 新加入的成员列表要发到的邮箱
        @return: 返回加入的成员个数
        """
        if self._LOCK == True:
            self.queuemanager_logger.warn("正在重置队列，请勿打扰。")
            return
        count = 0
        #cfg.queuemanager_logger.debug('file_pairs passed to add method: %s'%file_pairs)
        for i in file_pairs:
            if not isinstance(i,tuple):
                raise TypeError, 'file_pairs must be list type'
        if to_addr in self._users:
            for file_pair in file_pairs:
                id_ = self._unique()
                with open(self._queue_path+'/'+str(id_),'wb') as f:
                    file_pair[1].seek(0)
                    #TODO 这里read用来一次读取整个文件，如果文件对象太大效率可能就会有问题
                    #print 'len of file_pair[1]:' + len(file_pair[1])
                    f.write(file_pair[1].read())
                    meta = Metadata()
                    meta.to_addr = to_addr
                self.db[str(id_)] = pickle.dumps({'title':file_pair[0],'metadata':meta.serialized()}) #self.db的键都是字串型的
                self.db['top'] = str(id_)
                if to_addr in self.userdb:
                    #print 'userdb:'
                    #print self.userdb
                    #print 'to_addr:%s'%to_addr
                    #print 'to_addr in self.userdb'
                    tem = pickle.loads(self.userdb[to_addr])
                    tem.add(id_)
                    self.userdb[to_addr] = pickle.dumps(tem)
                else:
                    self.userdb[to_addr] = pickle.dumps(set([id_,]))
                if len(self.db) >= self._warn_limit:
                    #print '达到或超过warn_limit'
                    cfg.queuemanager_logger.warning('当前队列中对象数为%d'%(len(self.db)-1))
                if len(self.db)>self._reset_limit or len(self.db)>self._reset_limit:
                    #print len(self.db)
                    raise cfg.QueueOverflow, "self._reset_limit:%s,len(self.db):%s"%(self._reset_limit,len(self.db))
                if id_ >= self._reset_limit:
                    cfg.queuemanager_logger.info('进行重置...')
                    self.reset()
                    cfg.queuemanager_logger.info('重置完成')
                count += 1
            return count
        elif to_addr in self.userdb:
            cfg.queuemanager_logger.info('%s已被排除在许可列表之外'%to_addr)
            return 0
        else:
            cfg.queuemanager_logger.error('%s不在self.userdb中。'%to_addr)
            return 0
    def pop(self,id_):
        """
        给定对象在队列中的编号，将之删除
        @return: (对象标题,已读入内存的内容)
        """
        if self._LOCK == True:
            self.queuemanager_logger.warn("正在重置队列，请勿打扰。")
            return
        if not isinstance(id_,int):
            raise TypeError, "in pop: the type of id_ provided here is %s. But id_ must be a integar!"%type(id_)
        pair = self.pick(id_)
        try:
            to_addr = Metadata(pickle.loads(self.db[str(id_)])['metadata']).to_addr #太复杂了，还是用关系数据库吧
            id_s = pickle.loads(self.userdb[to_addr])
            #print to_addr
            #print id_s
            cfg.queuemanager_logger.debug("in pop,id_s before remove:%s"%id_s)
            id_s.remove(id_) #id_s为一set()对象
            cfg.queuemanager_logger.debug("in pop,id_s after remove:%s"%id_s)
            self.userdb[to_addr] = pickle.dumps(id_s) #id_s 为一空set()也不要删,
            del self.db[str(id_)]
            os.remove(self._queue_path+'/'+str(id_))
        except:
            cfg.queuemanager_logger.error("Queue的pop方法发生严重错误！")
            raise
        return pair
    def pick(self,id_):
        """
        给定对象的标识，返回对象
        @param id_: 对象在队列中的标识
        @return: (对象标题,已读入内存的内容)
        """
        if self._LOCK == True:
            self.queuemanager_logger.warn("正在重置队列，请勿打扰。")
            return
        try:
            self.db[str(id_)]
        except KeyError, e:
            cfg.queuemanager_logger.error('pick 方法中id_越界！')
            raise e
        f_in_mem = StringIO.StringIO()
        with open(self._queue_path+'/'+str(id_),'rb') as f:
            f_in_mem.write(f.read())
        f_in_mem.seek(0)
        return pickle.loads(self.db[str(id_)])['title'],f_in_mem
    def candidate(self,protect=True,strategy=1):
        """
        返回当前最需要发送的对象,正常情况下只有candidate被调用。
        @param strategy: 返回策略
         
         - B{1} 默认策略，排序后抽成员
         - B{2} 按收件人进行成员的选择
        @param protect: 是否防止被服务器发现。一般取默认值即可,当调度时才可能需要设成False
        @todo: 要选择最合适的算法来选择候选对象。最好是每次加入对象时都建个索引。不用像以下这样遍历所有对象。
        @return:
            - strategy == 2 返回([("对象标题",文件对象),....],to_addr)
            - strategy == 1 [(("对象标题",文件对象),to_addr),....]
        """
        if self._LOCK == True:
            self.queuemanager_logger.warn("正在重置队列，请勿打扰。")
            return
        if protect:
            if time.time() - self._last_cand_time < 60*3: #小于3分钟
                return
            self._last_cand_time = time.time()
        rt = []
        if strategy == 1:
            db_len = len(self.db)
            tem = self.db.keys()
            keys = [int(i) for i in tem if i != 'top']
            if db_len < self._cad_num:
                for k in keys:
                    to_ = Metadata(pickle.loads(self.db[str(k)])['metadata']).to_addr
                    rt.append((self.pop(k), to_))
            else:
                keys.sort()
                for k in keys[:self._cad_num]:
                    to_ = Metadata(pickle.loads(self.db[str(k)])['metadata']).to_addr
                    rt.append((self.pop(k),to_))
            return rt
        elif strategy == 2:
            for to_ in self.userdb:
                keys = pickle.loads(self.userdb[to_])
                if keys:
                    if len(keys) < self._cad_num:
                        for k in keys:
                            try:
                                rt.append(self.pop(k))
                            except TypeError:
                                print 'to_:%s;keys:%s'%(to_,keys)
                                raise
                    else:
                        key_list = list(keys)
                        key_list.sort()
                        for k in key_list[:self._cad_num]:
                            rt.append(self.pop(k))
                    return (rt,to_)
        else:
            cfg.queuemanager_logger.error("该功能正等你来实现")
    def show(self, id_=None, output_obj=None, verbose=False):
        """
        显示目前队列的情况
        @param output_obj: 已打开的输出流对象
        @return: 返回队列中信件的个数
        """
        if self._LOCK == True:
            self.queuemanager_logger.warn("正在重置队列，请勿打扰。")
            return
        if not id_:
            if not verbose:
                if not output_obj or output_obj.closed():# 能这么写是因为or是可以短路的
                    for k in self.db:
                        print self.db[k]
                elif output_obj and not output_obj.closed():
                    for k,i in self.db:
                        output_obj.write(k)
                return len(self.db) - 1 # self.db 里有个'top'
            else:
                if not output_obj or output_obj.closed():
                    for k,i in self.db:
                        print '%s,%s'%(k,i)
                elif output_obj and not output_obj.closed():
                    for k,i in self.db:
                        output_obj.write('%s,%s'%(k,i))
        else:
            if not verbose:
                if not output_obj or output_obj.closed():
                    print self.db[str(id_)]
                elif output_obj and not output_obj.closed():
                    output_obj.write('%s'%self.db[str(id_)])
            else:
                #TODO 应该打印更详细的内容，但现在没空实现
                if not output_obj or output_obj.closed():
                    print self.db[str(id_)]
                elif output_obj and not output_obj.closed():
                    output_obj.write('%s'%self.db[str(id_)])
