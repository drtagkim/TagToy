'''
import imei
a = imei.Imei()
result = a.get("353852051399878")
'''


import web3
import copy
from bs4 import BeautifulSoup as BS

class Imei:
    site_call = "http://www.imei.info"
    param = {'imei':''}
    select_code = 'div#content div.body div#dane'
    def get(self,item_number):
        wr = web3.WebReader2()
        param = copy.deepcopy(Imei.param)
        param['imei'] = str(item_number)
        page = wr.read(url=Imei.site_call,parameters=param)
        soup = BS(page,'html.parser')
        return soup
        s_obj = soup.select(Imei.select_code)
        print s_obj[0].text
        ##
        rv = {}
        if len(s_obj) > 0:
            keys = s_obj[0].select('div.tt')
            values = s_obj[0].select('div.cc')
            assert len(keys) == len(values), "Items are not matched!"
            for i,k in enumerate(keys):
                rv[k] = values[i]
        else:
            print "error"
        return rv
def test(n):
    for i in range(n):
        print i
        a = Imei()
        result = a.get("353852051399878")