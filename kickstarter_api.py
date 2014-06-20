'''
Kickstarter 
Crawling API New
Author: DrTagKim
'''

import web3,sys,time, requests
from bs4 import BeautifulSoup as BS

class ProjectBacker:
    def __init__(self,url,quietly=False):
        self.url = url
        self.quietly = quietly
    def find_target(self):
        headers = { 'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11',
                 'connection' : 'close',
                 'charset' : 'utf-8'}
        params = {'format':'json'}
        con = requests.get(self.url,headers=headers,params=params)
        j = con.json()
        board = j['running_board']
        s = BS(board,'html.parser')
        eles = s.select('a#backers_nav data')
        if len(eles) > 0:
            t = eles[0].text.replace(",","")
            n = int(t)
            pn = n/40 + 2
        else:
            n = 0
            pn = 0
        print n
        self.pagination = pn
        return pn
    def measure(self,pb):
        p = pb.get_page_source()
        s = BS(p,'html.parser')
        frame = s.select("div.NS_backers__backing_row .meta a")
        return len(frame)
    def explore(self):
        """
|  main function
        """
        self.find_target()
        pb = web3.PhantomBrowser(noimage=True)
        url = self.url+"/backers"
        pb.goto(url) #TODO
        page = 1
        prevc = self.measure(pb)
        nowc = 0
        while 1:
            pb.scroll_down()
            nowc = self.measure(pb)
            sys.stdout.write(".")
            sys.stdout.write("%d"%nowc)
            sys.stdout.flush()
            if nowc > prevc:
                prevc = nowc
            else:
                break
        self.get_backer(pb)
        del pb
    def get_backer(self,pb):
        p = pb.get_page_source()
        s = BS(p,'html.parser')
        frame = s.select("div.NS_backers__backing_row .meta a")
        backers = []
        if len(frame) > 0:
            for backer in frame:
                profile_url = "%s"%(backer['href'])
                backer_name = backer.text
                backers.append((profile_url,backer_name,))
        self.backers = backers        