'''
** EXAMPLE **


** TODO **

'''





# PROGRAM STARTS
# -- Web --
from web3 import PhantomBrowser as PB
from bs4 import BeautifulSoup as BS
# -- System --
import time,sys,re,math,re,csv,zlib
# -- Multithreading --
from threading import Thread, active_count
import Queue
#
class KICKSTARTER:
    """
|  General string values for the Kickstarter site
    """
    CATEGORY_ART = "https://www.kickstarter.com/discover/advanced?category_id=1&sort=launch_date"
    CATEGORY_COMICS = "https://www.kickstarter.com/discover/advanced?category_id=3&sort=launch_date"
    CATEGORY_DANCE = "https://www.kickstarter.com/discover/advanced?category_id=6&sort=launch_date"
    CATEGORY_DESIGN = "https://www.kickstarter.com/discover/advanced?category_id=7&sort=launch_date"
    CATEGORY_FASHION = "https://www.kickstarter.com/discover/advanced?category_id=9&sort=launch_date"
    CATEGORY_FILM = "https://www.kickstarter.com/discover/advanced?category_id=11&sort=launch_date"
    CATEGORY_FOOD = "https://www.kickstarter.com/discover/advanced?category_id=10&sort=launch_date"
    CATEGORY_GAMES = "https://www.kickstarter.com/discover/advanced?category_id=12&sort=launch_date"
    CATEGORY_MUSIC = "https://www.kickstarter.com/discover/advanced?category_id=14&sort=launch_date"
    CATEGORY_PHOTOGRAPHY = "https://www.kickstarter.com/discover/advanced?category_id=15&sort=launch_date"
    CATEGORY_PUBLISHING = "https://www.kickstarter.com/discover/advanced?category_id=18&sort=launch_date"
    CATEGORY_TECHNOLOGY = "https://www.kickstarter.com/discover/advanced?category_id=16&sort=launch_date"
    CATEGORY_THEATER = "https://www.kickstarter.com/discover/advanced?category_id=17&sort=launch_date"
    XPATH_RELOAD_BUTTON = "id('projects')/div/div/a"
    CSS_COUNTER = "b.count"
    CSS_GET_CARD = "div.project-card"
    CSS_TITLE = "h6.project-title a"
    CSS_AUTHOR = "p.mb1"
    CSS_DESC1 = "p.project-blurb"
    CSS_DESC2 = "p.blurb"
    CSS_LOCATION_NAME = "span.location-name"
    CSS_STAT = "ul.project-stats"
    ATT_DUE_DATE = "data-end_time"

class KickstarterProjectCollector:
    def __init__(self,url):
        self.url = url
    def factory_kickstarter(self,url):
        pb = PB()
        pb.goto(url)
        first_only = True
        try:
            btn_reload = pb.xpath_element(KICKSTARTER.XPATH_RELOAD_BUTTON)
            btn_reload.click()
            first_only = False
        except:
            pass
        return (pb,first_only)
    def target_N(self,phantomB):
        counter_we = phantomB.css_selector_element(KICKSTARTER.CSS_COUNTER)
        counter_str = counter_we.text.strip()
        temp_1 = re.findall(r'[0-9,]+',counter_str)
        if len(temp_1) > 0:
            counter_n = int(temp_1[0].replace(",",""))
        else:
            counter_n = 0
        target_n = int(math.ceil(counter_n / float(20) - 1))
        # COUNTER <= 20 * (N + 1)
        return target_n
    def execute(self,foutput):
        assert len(self.url) > 0, "Error"
        pb, first_only =  self.factory_kickstarter(self.url)
        if not first_only:
            N = self.target_N(pb)
            for i in xrange(N):
                wait_tolerance = 15
                pb.scroll_down()
                sys.stdout.write("page: %03d" % (i,))
                while pb.check_scroll_complete_ajax() and i < N:
                    time.sleep(1)
                    sys.stdout.write(".")
                    wait_tolerance -= 1
                    if wait_tolerance < 0:
                        break
                sys.stdout.write(" OK\n")
        pb.page_source_save(foutput)
        del pb


class KickstarterCard:
    def __init__(self,collection_id):
        self.collection_id = collection_id
        self.title_text = ""
        self.title_url = ""
        self.author_text= ""
        self.desc_text = ""
        self.location_text = ""
        self.funded_text = ""
        self.pledged_text = ""
        self.days_to_go_text = ""
        self.due_day_date = ""
        self.funded_end = ""
    def __str__(self):
        rv = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
            self.collection_id,
            self.title_text.encode('utf-8'),
            self.title_url.encode('utf-8'),
            self.author_text.encode('utf-8'),
            self.desc_text.encode('utf-8'),
            self.location_text.encode('utf-8'),
            self.funded_text.encode('utf-8'),
            self.pledged_text.encode('utf-8'),
            self.days_to_go_text.encode('utf-8'),
            self.due_day_date.encode('utf-8'),
            self.funded_end.encode('utf-8'))
        return rv
    def line(self):
        return [self.collection_id,
            self.title_text.encode('utf-8'),
            self.title_url.encode('utf-8'),
            self.author_text.encode('utf-8'),
            self.desc_text.encode('utf-8'),
            self.location_text.encode('utf-8'),
            self.funded_text.encode('utf-8'),
            self.pledged_text.encode('utf-8'),
            self.days_to_go_text.encode('utf-8'),
            self.due_day_date.encode('utf-8'),
            self.funded_end.encode('utf-8')]

class KickstarterProjectAnalyzer:
    def __init__(self,file_name):
        self.cards = []
        self.results = []
        self.get_soup(file_name)
        self.get_cards()
    def get_soup(self,file_name):
        f = open(file_name)
        self.soup = BS(f,'html.parser')
        f.close()
    def assert_card(self):
        if len(self.cards) <= 0:
            return False
        return True
    def get_cards(self):
        self.cards = self.soup.select(KICKSTARTER.CSS_GET_CARD)
    def execute(self,collection_id):
        assert self.assert_card, "No data!"
        append_result = self.results.append
        for card in self.cards:
            kickstarter_card = KickstarterCard(collection_id)
            kickstarter_card.title_text,kickstarter_card.title_url = self.get_title(card)
            kickstarter_card.author_text = self.get_author(card)
            kickstarter_card.desc_text = self.get_desc(card)
            kickstarter_card.location_text = self.get_location_name(card)
            kickstarter_card.funded_text,kickstarter_card.pledged_text,kickstarter_card.days_to_go_text,kickstarter_card.due_day_date,kickstarter_card.funded_end = self.get_stat(card)
            append_result(kickstarter_card)
    def export_result_tsv(self,file_name):
        f = open(file_name,'wb')
        w = csv.writer(f,lineterminator='\n',delimiter='\t')
        for result in self.results:
            w.writerow(result.line())
        f.close()
    def get_title(self,card):
        title = card.select(KICKSTARTER.CSS_TITLE)
        title_text = "no title"
        title_url = "no url"
        if len(title) > 0:
            title_text = title[0].text.strip().replace("\n","").replace("\t","")
            title_url = title[0]['href'].strip()
            if not title_url.startswith("http"):
                title_url = "https://www.kickstarter.com%s"%(title_url)
        return title_text,title_url
    def get_author(self,card):
        author = card.select(KICKSTARTER.CSS_AUTHOR)
        author_text = "anonimous"
        if len(author) > 0:
            author_text = author[0].text.replace("by\n","").strip().replace("\n","").replace("\t","")
        return author_text
    def get_desc(self,card):
        desc1 = card.select(KICKSTARTER.CSS_DESC1)
        desc2 = card.select(KICKSTARTER.CSS_DESC2)
        desc_text = ""
        if len(desc1) > 0:
            desc_text = desc1[0].text.strip().replace("\n","")
        if len(desc2) > 0:
            desc_text = desc2[0].text.strip().replace("\n","")
        return desc_text
    def get_location_name(self,card):
        location_name = card.select(KICKSTARTER.CSS_LOCATION_NAME)
        location_text = ""
        if len(location_name) > 0:
            location_text = location_name[0].text.strip().replace("\n","").replace("\t","")
        return location_text
    def get_stat(self,card):
        stat = card.select(KICKSTARTER.CSS_STAT)
        funded_text = "0"
        pledged_text = "0"
        days_to_go_text = "0"
        due_day_date = "0000-00-00"
        funded_end = ""
        if len(stat) > 0:
            stat_data = stat[0]('li')
            if len(stat_data) > 0:
                if len(stat_data) > 3:
                    stat1_bin = stat_data[0]('strong')
                    stat2_bin = stat_data[1]('strong')
                    stat3_bin = stat_data[3]('strong')
                    if len(stat1_bin) > 0:
                        funded = stat1_bin[0].text.strip()
                        a = re.findall(r"[0-9\.]+",funded)
                        if len(a) > 0:
                            funded_text = a[0]
                    if len(stat2_bin) > 0:
                        pledged = stat2_bin[0].text.strip()
                        a = re.findall(r"[0-9\.]+",pledged)
                        if len(a) > 0:
                            pledged_text = a[0]
                    if len(stat3_bin) > 0:
                        days_to_go = stat3_bin[0].text.strip()
                        a = re.findall(r"[0-9]+",days_to_go)
                        if len(a) > 0:
                            days_to_go_text = a[0]
                        due_day = stat_data[3][KICKSTARTER.ATT_DUE_DATE].strip()
                        b = re.findall(r"[0-9]{4}-[0-9]{2}-[0-9]{2}",due_day)
                        if len(b) > 0:
                            due_day_date = b[0]
                else:
                    stat1_bin = stat_data[0]('strong')
                    stat2_bin = stat_data[1]('strong')
                    stat3_bin = stat_data[2]('div')
                    if len(stat1_bin) > 0:
                        funded = stat1_bin[0].text.strip()
                        a = re.findall(r"[0-9\.]+",funded)
                        if len(a) > 0:
                            funded_text = a[0]
                    if len(stat2_bin) > 0:
                        pledged = stat2_bin[0].text.strip()
                        a = re.findall(r"[0-9\.]+",pledged)
                        if len(a) > 0:
                            pledged_text = a[0]
                    if len(stat3_bin) > 0:
                        funded_end = stat3_bin[0].text.strip().replace("\t","").replace("\n","")
        return (funded_text,pledged_text,days_to_go_text,due_day_date,funded_end)
# Clone of KickstarterProjectCollector
class KsProjectProbe(Thread):
    def __init__(self):
        Thread.__init__(self)
        #self.url = url
        self.url_queue = Queue.Queue()
        self.running = True
        #self.bench_mark = bench_mark #bench mark card (to decide a stopping point)
    def add(self,url):
        self.url_queue.put(url)
    def stop(self):
        self.running = False
    def run(self):
        while self.running:
            try:
                url = self.url_queue.get(block=True,timeout=10) #wait for 10 second
                sys.stdout.write("\nData received: %s\n" % url)
                sys.stdout.flush()
                assert len(url) > 0, "Error"
                pb, first_only =  self.factory_kickstarter(url)
                if not first_only:
                    N = self.target_N(pb)
                    for i in xrange(N):
                        # evaluate, compare data with the benchmark -> if nothing new? stop! if new? add!
                        wait_tolerance = 15
                        pb.scroll_down()
                        sys.stdout.write("^")
                        sys.stdout.flush()
                        while pb.check_scroll_complete_ajax() and i < N:
                            time.sleep(1)
                            sys.stdout.write(".")
                            sys.stdout.flush()
                            wait_tolerance -= 1
                            if wait_tolerance < 0:
                                break
                        sys.stdout.write("$")
                        sys.stdout.flush()
                #TODO -> pb.get_page_source()
                del pb # terminate the session
            except Queue.Empty:
                sys.stdout.write(".")
                sys.stdout.flush()
    def factory_kickstarter(self,url):
        pb = PB()
        pb.goto(url)
        first_only = True
        try:
            btn_reload = pb.xpath_element(KICKSTARTER.XPATH_RELOAD_BUTTON)
            btn_reload.click()
            first_only = False
        except:
            pass
        return (pb,first_only)
    def target_N(self,phantomB):
        counter_we = phantomB.css_selector_element(KICKSTARTER.CSS_COUNTER)
        counter_str = counter_we.text.strip()
        temp_1 = re.findall(r'[0-9,]+',counter_str)
        if len(temp_1) > 0:
            counter_n = int(temp_1[0].replace(",",""))
        else:
            counter_n = 0
        target_n = int(math.ceil(counter_n / float(20) - 1))
        # COUNTER <= 20 * (N + 1)
        return target_n
    def execute(self,foutput):
        assert len(self.url) > 0, "Error"
        pb, first_only =  self.factory_kickstarter(self.url)
        if not first_only:
            N = self.target_N(pb)
            for i in xrange(N):
                wait_tolerance = 15
                pb.scroll_down()
                sys.stdout.write("page: %03d" % (i,))
                while pb.check_scroll_complete_ajax() and i < N:
                    time.sleep(1)
                    sys.stdout.write(".")
                    wait_tolerance -= 1
                    if wait_tolerance < 0:
                        break
                sys.stdout.write(" OK\n")
        pb.page_source_save(foutput)
        del pb

# PROGRAM END