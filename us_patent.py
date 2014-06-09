'''
Taekyung Kim
US Patent Search
'''
from web3 import WebReader2 as WR
from web3 import list_to_queue #helper
from web3 import queue_to_list #helper
from web3 import run_web_reader_pool #web reader pool
import csv, re, sys, copy, cPickle, zlib
from Queue import Queue
from bs4 import BeautifulSoup as BS

class UsPatentLiteral:
    site_home = "http://patft.uspto.gov"
    quick_search_base = "http://patft.uspto.gov/netacgi/nph-Parser"
    quck_search_param = {
        "Sect1":"PTO2",
        "Sect2":"HITOFF",
        "u":"/netahtml/PTO/search-bool.html",
        "r":"0",
        "p":"1", #page
        "f":"S",
        "l":"50", # max 50 (line)
        "FIELD1":"",
        "co1":"AND",
        "TERM1":"", #search term
        "TERM2":"",
        "FIELD2":"",
        "d":"PTXT"
    }
    advanced_search_param = {
        "Sect1":"PTO2",
        "Sect2":"HITOFF",
        "u":"/netahtml/PTO/search-adv.htm",
        "r":"0",
        "p":"1",
        "f":"S",
        "l":"50",
        "Query":"",
        "d":"PTXT"
    }
    advanced_search_term = {
        "company":"AN",
        "issued":"ISD", #ISD/1/1/1995 (for example)
        "issued_link":"->", # ISD/1/1/1995->mon/day/year
        "us_classification":"CCL" #Current US Classification
        # if you want to concatenate queries, use blank (not plus!) and "AND".
    }
# urllib.quote_plus, unquote_plus...

class PatentSearcher:
    def __init__(self):
        self.results = None #main page for collecting links
        self.patent_pages = [] #actual webpage (patent) title and url
    def get_total_patent_number_pagination(self, soup, line_cnt = 50):
        """
|  input = (soup object on patent main page)
|  output = (total patent number, pagination count)
        """
        assert soup != None,"Soup object should not be None"
        assert line_cnt > 0, "Line count should be positive"
        text = soup.text
        tn = re.findall(r": ([0-9,]+) patents",text)
        if len(tn) > 0:
            tnn = int(tn[0].replace(",",""))
            quti = divmod(tnn,line_cnt)
            if quti[1] > 0:
                pagination_cnt = quti[0] + 1
            else:
                pagination_cnt = quti[0]
            return (tnn,pagination_cnt,)
        else:
            return (0,0,)
    def main_page_source(self,keyword,page=1):
        param = copy.deepcopy(UsPatentLiteral.quck_search_param)
        param['p'] = page
        param['TERM1'] = keyword
        wr = WR()
        page = wr.read(url=UsPatentLiteral.quick_search_base,
            parameters = param
        )
        return page
    def read_patent_data(self,keyword,n_pool=4,loud=False):
        main_page_source_in_string = self.main_page_source(keyword = keyword)
        (total_page, pagination) = self.get_total_patent_number_pagination(BS(self.main_page_source(keyword),'html.parser'))
        if loud:
            print "pagination = %d"%pagination
            print "total = %d"%total_page
        params = []
        address_list = [UsPatentLiteral.quick_search_base for _ in range(pagination)]
        for i in range(1,pagination+1):
            param = copy.deepcopy(UsPatentLiteral.quck_search_param)
            param['p'] = i
            param['TERM1'] = keyword
            params.append(param)
        self.results = run_web_reader_pool(address_list=address_list,n_pool=n_pool,loud=loud,params=params)
        if loud:
            print "\n-- Complete --"
    def export_results_pickle(self, fname,explain=False):
        assert self.results != None, "You don't have results."
        if explain:
            print "use cPickle\nThe result is a list object.\nEach item is tuple: (zlib,zlib)."
        f = open(fname,'wb')
        cPickle.dump(self.results,f)
        f.close()
    def import_results_pickle(self, fname):
        f = open(fname)
        results = cPickle.load(f)
        f.close()
        assert type(results) == list,"List!"
        self.results = copy.deepcopy(results)

    def read_items(self,loud = False):
        assert self.results != None,"You should have items!"
        if loud:
            sys.stdout.write("processing...")
        results = self.results
        patent_pages_append = self.patent_pages.append
        for result in results:
            page = zlib.decompress(result[1])
            if loud:
                sys.stdout.write("_")
            soup = BS(page,'html.parser')
            lines = soup('tr')
            for l in lines:
                ele_td = l('td')
                t1 = ele_td[0].text
                if t1.encode('utf-8').strip().isalnum():
                    title = ele_td[3].text.strip()
                    title = re.sub(r"\n"," ",title)
                    title = re.sub(r"\s\s+"," ",title)
                    try:
                        url_item = "%s%s" % (UsPatentLiteral.site_home, ele_td[3]('a')[0]['href'],)
                    except:
                        url_item = "na"
                    patent_pages_append((title,url_item))
        print "OK"
class PatentPageAnalyzer:
    def read_item_page(self,item):
        title = item[0]
        url = item[1]
        wr = WR()
        page = wr.read(url=url)
        return BS(page,'html.parser')
    def find_reference_table(self,soup):
        markup_text = soup(text=re.compile(r"U.S. Patent Documents"))
        result = []
        if len(markup_text) > 0:
            table_ele = markup_text[0].parent.parent.next_sibling.next_sibling
            table_items = table_ele('tr')
            for ti in table_items:
                ti_sub = ti.text.split('\n')
                if len(ti_sub) == 4:
                    result.append(copy.deepcopy(ti_sub[1:]))
        return result
    def find_info_table(self,soup):
        """
|  HOT FIX! 2014/06/09
        """
        tables = soup('table')
        target_table = None
        for table in tables:
            text = table.text
            # there is a unicode error because of some characters...like cp949 (euc-kr)
            # we need to correct this.
            txt1 = re.findall(r'Inventors:',text)
            txt2 = re.findall(r'Assignee:',text)
            #txt3 = re.findall(r'Family ID:',text)
            if len(txt1) > 0 and len(txt2) > 0: #and len(txt3) > 0:
                target_table = table
        assert target_table != None, "Error in data"
        result = {}
        trs = target_table('tr')
        for tr in trs:
            th = tr('th')
            td = tr('td')
            if len(th) > 0:
                key = th[0].text.strip()
                key = re.findall(r'.+:',key)
                if len(key) > 0:
                    key = key[0].replace(":","").strip()
                if len(key) > 0 and len(td) > 0:
                    try:
                        content = re.sub(r"\n"," ",td[0].text.strip())
                        content = re.sub(r"\s\s+"," ",content)
                    except:
                        content = ""
                    result[key] = content
                else:
                    result[key] = ""
        return result #TODO - test
