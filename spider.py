# # -*- coding: utf-8 -*-

import urllib;
from threading import Thread
import Queue
import time
import re

from urlparse import urlparse
class Config:
    seed = "http://www.aifang.com"
    domain = 'aifang.com'
    threadNum = 20
    reg = re.compile(r'href="([^"]+)"')
class parsePage(Thread):
    '''解析页面'''
    def __init__(self,queue,urlHistory,spider):
        self.queue = queue
        self.urlHistory = urlHistory
        self.isWait = False
        self.spider = spider
        Thread.__init__(self)

    def run(self):
        while True:
            self.isWait = True
            if self.queue.empty():
                if self.checkOver():
                    print '检测到，已经搜完，开始发送结束命令'
                    self.queue.put(False)
                    break

            myUrl = self.queue.get()
            if not myUrl:
                print '结束线程'
                self.queue.put(False)
            self.isWait = False

            if myUrl==0:
                break

            parentUrl = myUrl.url
            try:
                content = urllib.urlopen(parentUrl).read()
            except Exception:
                print parentUrl
            urlList = self.getUrlList(content)
            for url in urlList:

                self.urlHistory.addUrl(url,parentUrl)
                print self.urlHistory.urlNum
                #print self.urlHistory.dataBase.data
                #time.sleep(1)

    def getUrlList(self,content):
        '''get'''
        urlList = Config.reg.findall(content)
        if urlList is not None:
            return urlList
        else:
            return []
    def checkOver(self):
        over = True
        for k in self.spider.threads:
            if not self.spider.threads[k].wait:
                over = False
        return over
class urlDetail:
    '''链接信息'''
    def __init__(self,url):
        self.url = url
        detail = urlparse(url)
        self.domain = detail.netloc
        self.path = detail.path
        self.query = detail.query
    def isInDomain(self):
        return True
    def getPathList(self):
        pathList = [self.domain,]
        paths = self.path.strip('/').split('/')
        for p in paths:
            pathList.append(p)
        if self.query!='':
            pathList.append(self.query)
        return pathList
    def getBaseUrl(self):
        return 'http://%s'%(self.domain,)
    def getCurrentUrl(self):
        return 'http://%s%s'%(self.domain,self.path)

class myUrl:
    '''一个url单元'''
    def __init__(self,url):
        self.url = url
        detail = urlDetail(url)
        self.path = detail.getPathList()
        self.query = detail.query

class urlHistory:
    '''url的历史记录'''
    def __init__(self,queue):
        self.rootDomainList = [] #把一些根域名 分块。



        self.dataBase = dataBase()
        self.list = []
        self.urlNum = 0
        self.queue = queue
        self.addUrl(Config.seed,'')

    def addUrl(self,url,parentUrl):

        url = self.checkUrl(url,parentUrl)

        if url:
            #self.list.append(url)
            self.urlNum  = self.urlNum + 1
            self.queue.put(myUrl(url))
            self.dataBase.addData(myUrl(url))


    def checkUrl(self,url,parentUrl):

        parentDetail = urlDetail(parentUrl)


        if 'http://' in url:
            if Config.domain not in url:
                print '外链',url
                return False
        else:
            if ':' in url: #针对mailto: ,javascript:等协议式链接
                print '协议',url
                return False
            if url[0:1]=='/':
                url = parentDetail.getBaseUrl()+url
            else:
                url = parentDetail.getCurrentUrl()+'/'+url
        #判断已经存在，这个算法需要改进
        start = time.time()
        myurl = myUrl(url)
        if self.dataBase.findData(myurl):
            print '存在',url
            return False
        end = time.time()
        print end-start

        return url

class Spider:
    '''mainclass'''
    def __init__(self):
        self.urlQueue = Queue.Queue(maxsize = 0)
        self.urlHistory = urlHistory(self.urlQueue)
    def start(self):
        self.threads = {}
        for i in range(0,Config.threadNum):
            self.threads[i] = parsePage(self.urlQueue,self.urlHistory,self)
            self.threads[i].start()

class dataBase:
    '''一棵简单的树,采用字典的key作为指针,
    因为一个url是以/分割的系列数据，
    所以这样存储查询起来要块的多'''
    def __init__(self):
        self.data = {}

    def addNode(self,data):
        ''''''
    def addData(self,myUrl):
        ''''''
        node = self.data
        k = len(myUrl.path)
        for p in myUrl.path:
            if node.has_key(p):
                node = node[p]
            else:
                node[p] = {}
                node = node[p]
            k = k-1
            if k==0:
                node['hit'] = ''
    def findData(self,myUrl):
        '''查找树'''
        node = self.data
        k = len(myUrl.path)
        for p in myUrl.path:
            if node.has_key(p):
                node = node[p]
                k = k-1
                if k==0:
                    if node.has_key('hit'):
                        return True
                    else:
                        return False
            else:
                return False
        return True
    def delData(self,data):
        ''''''
    def delNode(self,nodeName):
        ''''''


def main():
    spider = Spider();
    spider.start()


if __name__ == '__main__':
    main()



