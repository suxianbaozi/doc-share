import urllib2
from threading import Thread
import Queue 
import re
import time

baseUrl = "http://www.chemicalbook.com/ProductCASList_13_%d00_EN.htm"
viewBaseUrl = "http://www.chemicalbook.com/ProductChemicalPropertiesCB%s_EN.htm"
viewUrlList = Queue.Queue(maxsize = 0)
ISOTIMEFORMAT='%Y-%m-%d %X'
total = 0
wait = False

class getUrl(Thread):
    def __init__(self,id):
        Thread.__init__(self)
        self.id = id
    def run(self):
        url =  baseUrl%(self.id,)
        #print url
        req = urllib2.Request(url)
        req.add_header("Referer","http://www.chemicalbook.com/")
        req.add_header("User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36")
        req.add_header("Cookie","ASP.NET_SessionId=j1vaqq55e5y5gu454ic3icrt")    
        fp = urllib2.urlopen(req)
        content = fp.read()
        fp.close()
        if 'System busy' in content:
            print 'shit shit'
            return
        viewList = re.findall("CB(\d+)\_EN\.htm",content);
        for id in viewList:
            viewUrlList.put(id);



class getView(Thread):
    def __init__(self,tid):
        Thread.__init__(self)
        self.tid = tid
        
    def run(self):
        global total
        global wait
        while True:
            if wait:
                print 'thread',self.tid,' waiting...'
                time.sleep(20)
                wait = False
            
            id = viewUrlList.get()
            viewUrl = viewBaseUrl%(id,)
            #print url
            req = urllib2.Request(viewUrl)
            req.add_header("Referer","http://www.chemicalbook.com/")
            req.add_header("User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36")
            req.add_header("Cookie","ASP.NET_SessionId=j1vaqq55e5y5gu454ic3icrt")    
            fp = urllib2.urlopen(req)
            content = fp.read()
            fp.close()
            total += 1
            print total

            if 'System busy' in content:
                print 'get view shit shit'
                break
            #get img
            img = re.findall("CAS\\\GIF\\\(.+)\.gif",content)
            print img
            print "Geted:",id,time.strftime( ISOTIMEFORMAT, time.localtime() )
            
            if total%100==0:
                wait = True
        
print time.strftime( ISOTIMEFORMAT, time.localtime() )

for i in range(0,101):
    getUrl(i).start()

for i in range(0,20):
    getView(i).start()
