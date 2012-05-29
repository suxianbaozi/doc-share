# -*- coding: utf8 -*-


##################################
#万能抓取工具
#v1.0
##################################

import urllib
import Queue
import time
import re
from threading import Thread

class config:
    mainUrl = "http://www.baidu.com"
    contentThreadNum = 5
    contentQue = Queue.Queue(0)
reList = []
queList = []
spiderList = []
reCell = {}
reCell['list'] = re.compile('''xxx.php''');
reCell['nextList'] = re.compile('''xxx.php''');
reCell['toGet'] = {};
reCell['toGet']['url'] = 0;
reCell['toGet']['other'] = 1;



reList.append(object)

class spiderGo(Thread):
    def __init__(self,queList,reList,index):
        Thread.__init__(self)
        self.queList = queList
        self.reList = reList
        self.reLen = len(self.reList)
        self.index = index
    def packageData(self,cell):
        data = {}
        for k,i in self.reList[self.index]['toGet'].items():
            data[k] = cell[i]
    def getContent(self,url):
        return url
    def run(self):
        if self.index==0:#第一级
            reList = self.reList[self.index].findall(self.getContent(config.mainUrl))
            for k in reList:
                k = self.packageData(k)
                self.queList[self.index].put(k)
        elif self.index>0 and self.index<self.reLen-1:#中间级别
            while True:
                data = self.queList[self.index-1].get()
                if data is not 0:
                    content = self.getContent(data[self.index-1]['url'])
                    reList = self.reList[self.index].findall(content)
                    for k in reList:
                        k= (data,self.packageData(k))
                        self.queList[self.index].put(k)
                else:
                    break
        elif self.index == self.reLen-1:
            while True:
                data = self.queList[self.index-1].get()
                if data is not 0:
                    content = self.getContent(data[self.index-1]['url'])
                    content = (data,content)
                    config.contentQue.put(content)

class contentGet(Thread):
    def __init__(self):
        Thread.__init__()
    def run(self):
        return False


for i in range(len(reList)):
    queList.append(Queue.Queue(0))
    spiderList.append(spiderGo(queList,reList,i))

for i in range(config.contentThreadNum):
    ct = contentGet()
    ct.start()
#最终内容获取正则