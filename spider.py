# -*- coding: utf8 -*-


import urllib2
from threading import Thread
import Queue 
import re
import time
import sys

baseUrl = "http://www.chemicalbook.com/ProductCASList_13_%d00_EN.htm"
viewBaseUrl = "http://www.chemicalbook.com/ProductChemicalPropertiesCB%s_EN.htm"
viewUrlList = Queue.Queue(maxsize = 0)
listUrlList = Queue.Queue(maxsize = 0)

ISOTIMEFORMAT='%Y-%m-%d %X'
total = 0
totalGot = 0


getViewThreads = {}

listThreadNum = 50
viewThreadNum = 50

pIndex = 0
#proxies = ['110.4.12.170:80',]
proxies = [
           '221.10.40.232:81',
           '121.26.229.197:8081',
           '60.8.63.52:8081',
           '125.91.4.146:3328',
           '221.10.40.236:83',
           '202.116.160.89:80',
           '222.180.173.10:8080',
           '203.86.79.227:80',
           '173.213.113.111:8089',
           ''
           ] #'110.4.12.170:80','173.213.113.111:8089'


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
        print 'oh  500 ,change proxy'
        changeProxy()
        
        
        for k,thread in getViewThreads.items():
            thread.waitLong = 60*10*0.5 #休息十分钟
            try:
                thread.fp.close()
            except:
                pass
        #try:
        #    getUrlContent('http://www.chemicalbook.com/')
        #    time.sleep(1)
        #    getUrlContent('http://www.chemicalbook.com/ProductCASList_13_0_EN.htm');
        #    time.sleep(1)
        #    getUrlContent('http://www.chemicalbook.com/BuyingLeadList_EN.aspx');
        #    time.sleep(1)
#        except:
#            try:
#                getUrlContent('http://www.chemicalbook.com/')
#                time.sleep(1)
#                getUrlContent('http://www.chemicalbook.com/ProductCASList_13_0_EN.htm');
#                time.sleep(1)
#                getUrlContent('http://www.chemicalbook.com/BuyingLeadList_EN.aspx');
#                time.sleep(1)
#            except:
#                pass
#            return
#        return
    
    if total%100==0 and total>0:
        for k,thread in getViewThreads.items():
            if 100>thread.wait:
                thread.wait = 100
            
            try:
                thread.fp.close()
            except:
                pass
        try:
            getUrlContent('http://www.chemicalbook.com/')
            time.sleep(1)
            getUrlContent('http://www.chemicalbook.com/ProductCASList_13_0_EN.htm');
            time.sleep(1)
            getUrlContent('http://www.chemicalbook.com/BuyingLeadList_EN.aspx');
            time.sleep(1)
        except:
            try:
                getUrlContent('http://www.chemicalbook.com/')
                time.sleep(1)
                getUrlContent('http://www.chemicalbook.com/ProductCASList_13_0_EN.htm');
                time.sleep(1)
                getUrlContent('http://www.chemicalbook.com/BuyingLeadList_EN.aspx');
                time.sleep(1)
            except:
                pass
            return;
    


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
            if listUrlList.qsize()==0:
                break
            id = listUrlList.get()
            url =  baseUrl%(id,)
            #print url
            try:
                content = getUrlContent(url)
                self.fp = content['fp']
                content = content['content']
            except:
                listUrlList.put(id)
                return
            
            total += 1
            
            #print 'the ',total,'st page'
            
            if 'System busy' in content:
                listUrlList.put(id)
                print 'oh got some shit!'
                time.sleep(60*60*2)
                continue
            
            viewList = re.findall("CB(\d+)\_EN\.htm",content);
            
            for vid in viewList:
                viewUrlList.put(vid);
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
                print 'get view, oh got some shit!'
                viewUrlList.put(id)
                time.sleep(60*60*2)
                continue
            #get img
            try:
                img = re.findall("CAS\\\GIF\\\(.+)\.gif",content)
                #print img
            except:
                viewUrlList.put(id)
                
            #print "Geted:",id,time.strftime( ISOTIMEFORMAT, time.localtime() )
            totalGot += 1
            forSafe()
            



class Timer(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        t = 0
        while True:
            t+=1
            sys.stdout.write('time has passed:'+str(t)+'S===total got:'+str(totalGot)+'===total page:'+str(total))
            sys.stdout.write('===viewQueue length:'+str(viewUrlList.qsize()))
            sys.stdout.write('\r')
            sys.stdout.flush()
            time.sleep(1)
                  
print time.strftime( ISOTIMEFORMAT, time.localtime() )

#检查代理可用

for i in range(0,range(len(proxies))):
    
    changeProxy()
    
    cp = pIndex-1;
    
    print 'check ',proxies[cp],'...'
    
    try:
        c  = getUrlContent('http://www.baidu.com');
        if 'baidu' not in c:
            print proxies[cp],' seemed not available remove it';
            proxies.remove(proxies[cp])
        else:
            print proxies[cp],' available'
    except:
        cp = pIndex-1;
        print proxies[cp],' seemed not available remove it';
        proxies.remove(proxies[cp])
    


pIndex = 0
changeProxy()

for i in range(0,101):
    listUrlList.put(i)

for i in range(0,listThreadNum):
    getViewThreads['list_'+str(i)] = getUrl(i)
    getViewThreads['list_'+str(i)].start()

#get view start...
for i in range(0,viewThreadNum):
    getViewThreads['view_'+str(i)] = getView(i)
    getViewThreads['view_'+str(i)].start()

print "Let's go timer:"
Timer().start()
