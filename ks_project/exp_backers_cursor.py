import requests
from bs4 import BeautifulSoup as BS
def retrieve_backers(url):
    assert url.endswith("backers"),""
    param = {}
    all_data = []
    #first page
    c = requests.get(url)
    cursors = get_cursors(c.text)
    c.close()
    all_data.extend(cursors)
    print len(all_data)
    while len(cursors) > 0:
        param['cursor'] = cursors[-1]
        print cursors[-1]
        c = requests.get(url,params=param)
        cursors = get_cursors(c.text)
        c.close()
        all_data.extend(cursors)
        print len(all_data)
    return all_data
def get_cursors(text):
    soup = BS(text,'html.parser')
    eles = soup.select("div.NS_backers__backing_row")
    data = [ele['data-cursor'] for ele in eles]
    return data

if __name__ == "__main__":
    test_url = "https://www.kickstarter.com/projects/1935800597/wheely-a-wheelchair-accessible-guide/backers"
    print "start"
    data = retrieve_backers(test_url)
    print "end"
    print len(data)