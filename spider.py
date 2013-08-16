# -*- coding: utf8 -*-


import urllib2
from threading import Thread
import Queue 
import re
import time
import sys
import urllib
import os

baseUrl = "http://www.chemicalbook.com/ProductCASList_12_%d00_EN.htm"
viewBaseUrl = "http://www.chemicalbook.com/ProductChemicalPropertiesCB%s_EN.htm"
viewUrlList = Queue.Queue(maxsize = 0)
listUrlList = Queue.Queue(maxsize = 0)

dataList = Queue.Queue(maxsize = 0)

pageDic = {};

idDic = {}

ISOTIMEFORMAT='%Y-%m-%d %X'
total = 0
totalGot = 0


getViewThreads = {}

listThreadNum = 30
viewThreadNum = 30

pIndex = 0
#proxies = ['110.4.12.170:80',]

proxies = [
           #'111.1.55.19:8080',
           '211.142.236.135:80',
           '110.4.24.170:80',
           #'203.86.79.227:80',
           '221.10.40.232:81',
           #'173.213.113.111:8089',
           '219.239.227.81:8121',
           '119.254.90.18:8080',
           '121.26.229.197:8081',
           '60.8.63.52:8081',
           '125.91.4.146:3328',
           '221.10.40.236:83',
           '202.116.160.89:80',
           '110.4.12.170:83',
           '119.167.231.72:8080',
           #'222.180.173.10:8080',
           #'106.3.43.73:80',
           ''
           ] #'110.4.12.170:80','173.213.113.111:8089' 


def logStatus(str):
    fp = open("/spider.log","a")
    fp.write(str+'\n');
    fp.close()

def changeProxy():
    global pIndex
    proxy = proxies[pIndex]
    pIndex += 1
    
    if pIndex == len(proxies):
        pIndex = 0
        
    if proxy:
        proxy_support = urllib2.ProxyHandler({'http':'http://'+proxy})  
        opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
        urllib2.install_opener(opener)
    else:
        opener = urllib2.build_opener(urllib2.BaseHandler, urllib2.HTTPHandler)
        urllib2.install_opener(opener)


def getUrlContent(url):
    req = urllib2.Request(url)
    req.add_header("Referer","http://www.chemicalbook.com/")
    req.add_header("User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36")
    req.add_header("Cookie","ASP.NET_SessionId=j1vaqq55e5y5gu454ic3icrt")
    fp = urllib2.urlopen(req)
    content = fp.read()
    fp.close()
    return {'fp':fp,'content':content}
    
def forSafe():
    global totalGot
    global total
    
    if total%500==0 and total>0:
        logStatus('oh  500 ,change proxy')
        changeProxy()
        
        for k,thread in getViewThreads.items():
            thread.waitLong = 600 #休息10分钟
            try:
                thread.fp.close()
            except:
                pass
        
    
    if total%100==0 and total>0:
        for k,thread in getViewThreads.items():
            if 100>thread.wait:
                thread.wait = 100
            
            try:
                thread.fp.close()
            except:
                pass
        
    


class getUrl(Thread):
    def __init__(self,tid):
        Thread.__init__(self)
        self.tid = tid
        self.wait = 0
        self.waitLong = 0
    def run(self):
        global total
        while True:
            if self.wait>0:
                print 'thread list_',self.tid,' waiting...'
                time.sleep(self.wait)
                self.wait = 0
            if self.waitLong>0:
                print 'thread list_',self.tid,' waitingLong...'
                time.sleep(self.waitLong)
                self.waitLong = 0
            
            id = listUrlList.get()
            url =  baseUrl%(id,)
            #print url
            try:
                content = getUrlContent(url)
                self.fp = content['fp']
                content = content['content']
            except:
                listUrlList.put(id)
                continue
            
            total += 1
            
            #print 'the ',total,'st page'
            
            if 'System busy' in content:
                listUrlList.put(id)
                global pIndex
                logStatus('oh got some shit!'+str(pIndex))
                time.sleep(60*60*2)
                continue
            viewList = re.findall("CB(\d+)\_EN\.htm",content);
            pageList = re.findall("ProductCASList\_12\_(\d+)00\_EN\.htm",content);
            
            for vid in viewList:
                if idDic.has_key(vid):
                    continue
                else:
                    idDic[vid] = 1
                    viewUrlList.put(vid);
            
            for pid in pageList:
                if pageDic.has_key(pid):
                    continue
                else:
                    pageDic[pid] = 1
                    listUrlList.put(int(pid))
            
            forSafe()

class getView(Thread):
    def __init__(self,tid):
        Thread.__init__(self)
        self.tid = tid
        self.wait = 0
        self.waitLong = 0
    def run(self):
        global total
        global totalGot
        while True:
            if self.wait>0:
                print 'thread view_',self.tid,' waiting...'
                time.sleep(self.wait)
                self.wait = 0
                
            if self.waitLong>0:
                print 'thread view_',self.tid,' waitingLong...'
                time.sleep(self.waitLong)
                self.waitLong = 0
                
            id = viewUrlList.get()
            viewUrl = viewBaseUrl%(id,)
            #print url
            try:
                content = getUrlContent(viewUrl)
                self.fp = content['fp']
                content = content['content']
            except:
                viewUrlList.put(id)
                continue
            
            total += 1
            #print 'the ',total,'st page'
            
            if 'System busy' in content:
                global pIndex
                logStatus('get view, oh got some shit!'+str(pIndex))
                viewUrlList.put(id)
                time.sleep(60*60*2)
                continue
            
            data = {'cas_index':1,'content':content,'id':id}
            dataList.put(data)
            
            totalGot += 1
            #print "Geted:",id,time.strftime( ISOTIMEFORMAT, time.localtime() )
            forSafe()

class SendData(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.hasSend = 0
        print 'sendData'
    def run(self):
        while True:
            data = dataList.get()
            dataStr = urllib.urlencode(data)
            
            try :
                api = urllib.urlopen('http://www.mq35.com/gather_en/gather.php',dataStr)
                insertId =  api.read()
                api.close()
                self.hasSend += 1
            except Exception,e:
                print e
                dataList.put(data)
            time.sleep(2);
            
                
                
class Timer(Thread):
    def __init__(self):
        Thread.__init__(self)
        
    def run(self):
        t = 0
        while True:
            t+=1
            
            ar = (t,totalGot,total,viewUrlList.qsize(),listUrlList.qsize(),ST.hasSend,dataList.qsize())
            status = 'passed:%d,got:%d,page:%d,viewq:%d,pageq:%d,sended:%d,remain:%d'%ar;
#            sys.stdout.write(status);
#            sys.stdout.write('\r')
#            sys.stdout.flush()
            
            logFp = open('/spider.log',"a")
            logFp.write(status+"\n")
            logFp.close()
            time.sleep(1)

def demaeon():
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        sys.exit(4)

    os.chdir('/')
    os.umask(0)
    os.setsid()

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        sys.exit(4)


    for f in sys.stdout, sys.stderr: f.flush()


    si = file('/spider.log', 'r')
    so = file('/spider.log', 'a+')
    se = file('/spider.log', 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

demaeon()
                  
print time.strftime( ISOTIMEFORMAT, time.localtime() )

#检查代理可用

for i in range(0,len(proxies)):
    
    changeProxy()
    
    cp = pIndex-1;
    
    logStatus('check '+proxies[cp]+'...')
    
    try:
        c  = getUrlContent('http://www.baidu.com');
        
        if 'baidu' not in c['content']:
            print proxies[cp],' seemed not available remove it';
            proxies.remove(proxies[cp])
        else:
            logStatus( proxies[cp]+' available')
    except Exception,e:
        print e
        cp = pIndex-1;
        print proxies[cp],' seemed not available remove it';
        proxies.remove(proxies[cp])
    





pIndex = 0
changeProxy()

for i in range(0,1):
    listUrlList.put(i)

for i in range(0,listThreadNum):
    getViewThreads['list_'+str(i)] = getUrl(i)
    getViewThreads['list_'+str(i)].start()

#get view start...
for i in range(0,viewThreadNum):
    getViewThreads['view_'+str(i)] = getView(i)
    getViewThreads['view_'+str(i)].start()

print "Let's go timer:"

ST = SendData()
ST.start()

Timer().start()
