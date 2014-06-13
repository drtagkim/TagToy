'''
** EXAMPLE **


** TODO **

'''





# PROGRAM STARTS
# -- Web --
from web3 import PhantomBrowser as PB
from web3 import WebReader2 as WR
from bs4 import BeautifulSoup as BS
# -- System --
import time,sys,re,math,re,csv,zlib
# -- Multithreading --
from threading import Thread, active_count
import Queue,re
# -- Web, Imaging --
from PIL import Image
from StringIO import StringIO
import requests #Apache requests
#
class KICKSTARTER:
    """
|  General string values for the Kickstarter site
    """
    MAIN = "https://www.kickstarter.com"
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
                politeness = 1
                pb.scroll_down()
                sys.stdout.write("page: %03d" % (i,))
                sys.stdout.flush()
                while pb.check_scroll_complete_ajax() and i < N:
                    time.sleep(politeness)
                    politeness +=1 
                    sys.stdout.write(".")
                    sys.stdout.flush()
                    wait_tolerance -= 1
                    if wait_tolerance < 0:
                        break
                sys.stdout.write(" OK\n")
                sys.stdout.flush()
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
class KickstarterPageAnalyzer:
    """
|  Page analyzer
|  For example, https://www.kickstarter.com/projects/1311317428/a-limited-edition-cleverly-designed-leather-collec
|  >>> kpa = KickstarterPageAnalyzer()
|  >>> kpa.read(url)
|  >>> kpa.analyze()

    """
    def __init__(self,quietly=True):
        self.pb = None #phantom browser
        self.quietly = quietly
        #data clear
        self.clear()
    def clear(self):
        self.url = ""
        self.stat_result = ()
        self.projects_reward_result = []
        self.images = []
        self.condition_desc = ""
        self.full_description = ""
        self.risks = ""
        self.backers = []
    def terminate(self):
        self.pb.close()
        del self.pb
    def read(self,url):
        if not self.quietly:
            sys.stdout.write("Get set...")
            sys.stdout.flush()
        if self.pb == None:
            self.pb = PB()
        self.url = url
        self.pb.goto(url)
        if not self.quietly:
            sys.stdout.write("OK\n")
            sys.stdout.flush()
    def analyze(self):
        pb = self.pb
        page = pb.get_page_source()
        self.page_compressed = zlib.compress(page.encode('utf-8'))
        if not self.quietly:
            sys.stdout.write("Page data compressed: self.page_compressed..\n")
            sys.stdout.flush()
        soup = BS(page,'html.parser')
        assert soup != None, "No Page!"
        #main page
        if not self.quietly:
            sys.stdout.write("..Main..")
            sys.stdout.flush()
        self.analyze_main(soup)
        if not self.quietly:
            sys.stdout.write("OK\n")
            sys.stdout.flush()
        #backers
        btn = pb.css_selector_element("#backers_nav")
        soup = None
        if not self.quietly:
            sys.stdout.write("..Visiting backers data..")
            sys.stdout.flush()
        try:
            btn.click()
            no_backers = True #which means, no update yet (still there may be backers)
            last_backer_cursor = "-1"
            #scroll down until we reach bottom
            while 1:
                p = pb.get_page_source()
                s = BS(p,'html.parser')
                current_rows = s.select("div.NS_backers__backing_row")
                if len(current_rows) == 0:
                    break
                else:
                    no_backers = False
                # AJAX
                last_backer_cursor_now = current_rows[-1]['data-cursor']
                if last_backer_cursor != last_backer_cursor_now:
                    last_backer_cursor = last_backer_cursor_now
                    if pb.scroll_down():
                        if not self.quietly:
                            sys.stdout.write("^")
                            sys.stdout.flush()
                        wait_tolerance = 15
                        politeness = 1
                        while pb.check_scroll_complete_ajax():
                            if not self.quietly:
                                sys.stdout.write("*")
                                sys.stdout.flush()
                            time.sleep(politeness)
                            politeness += 1
                            wait_tolerance -= 1
                            if wait_tolerance < 0:
                                break
                        if not self.quietly:
                            sys.stdout.write("$")
                            sys.stdout.flush()
                    else:
                        break
                else:
                    if not self.quietly:
                        sys.stdout.write("\n")
                        sys.stdout.flush()
                    break
            if not no_backers:
                p = pb.get_page_source()
                soup = BS(p,'html.parser')
        except:
            pass
        if not self.quietly:
            sys.stdout.write("OK\n")
            sys.stdout.flush()
        if soup != None:
            if not self.quietly:
                sys.stdout.write("..Backers..")
                sys.stdout.flush()
            self.analyze_backers(soup)
            if not self.quietly:
                sys.stdout.write("OK\n")
                sys.stdout.flush()
    def analyze_backers(self,soup):
        # get backers data
        frame = soup.select("div.NS_backers__backing_row .meta a")
        backers = []
        if len(frame) > 0:
            for backer in frame:
                profile_url = "%s%s"%(KICKSTARTER.MAIN,backer['href'])
                backer_name = backer.text
                backers.append((profile_url,backer_name,))
        self.backers = backers
    def analyze_main(self,soup):
        
        # statistics
        self.stat_result = self.analyze_stat(soup)
        # projects reward
        frame = soup.select(".NS-projects-reward")
        self.projects_reward_result = self.analyze_project_reward(frame)
        # collect images
        frame = soup.select("img.fit")
        self.images = self.analyze_images(frame)
        # collect add_data
        frame = soup.select(".tiny_type")
        self.condition_desc = self.analyze_condition(frame)
        # collect full description
        frame = soup.select(".full-description")
        self.full_description = self.analyze_full_description(frame)
        # collect risk
        frame = soup.select("#risks")
        self.risks = self.analyze_full_description(frame)
    def analyze_full_description(self,frame):
        rv = ""
        if len(frame) > 0:
            desc = frame[0].text
            rv = re.sub(r"\n\n\n+","\n",desc)
            try:
                rv = rv.strip()
            except:
                pass
        return rv
    def analyze_condition(self,frame):
        rv = ""
        if len(frame) > 0:
            rv = frame[0].text
        return rv
    def analyze_images(self,frame):
        rv = []
        if len(frame) > 0:
            for imgf in frame:
                src = imgf['src']
                src = re.sub(r"\?.*$","",src)
                r = requests.get(src)
                if r.status_code == 200:
                    rv.append(r.content)
                del r
        return rv
    def analyze_stat(self,soup):
        frame = soup.select("div#stats") #move
        if len(frame) > 0:
            frame1 = frame[0].select("div#backers_count")
            if len(frame1) > 0:
                number_of_backers = int(frame1[0]['data-backers-count'])
            else:
                number_of_backers = 0
            frame2 = frame[0].select("div#pledged")
            if len(frame2) > 0:
                try:
                    goal = float(frame2[0]['data-goal'])
                except:
                    goal = 0.0
                try:
                    percent_raised = float(frame2[0]['data-percent-raised'])
                except:
                    percent_raised = 0.0
                try:
                    amount_pledged = float(frame2[0]['data-pledged'])
                except:
                    amount_pledged = 0.0
                frame21 = frame2[0]('data')
                if len(frame21) > 0:
                    try:
                        currency = frame21[0]['data-currency']
                    except:
                        currency = ""
                else:
                    currency = ""
            else:
                goal = 0.0
                percent_raised = 0.0
                amount_pledged = 0.0
                currency = ""
            frame3 = frame[0].select("#project_duration_data")
            if len(frame3) > 0:
                try:
                    duration = float(frame3[0]['data-duration'])
                except:
                    duration = 0.0
                try:
                    end_time = frame3[0]['data-end_time']
                except:
                    end_time = "na"
                try:
                    hours_remaining = float(frame3[0]['data-hours-remaining'])
                except:
                    hours_remaining = 0.0
            else:
                duration = 0.0
                end_time =""
                hours_remaining = 0.0
        else:
            number_of_backers = 0
            goal = 0.0
            percent_raised = 0.0
            amount_pledged = 0.0
            currency = ""
            duration = 0.0
            end_time = ""
            hours_remaining = 0.0
        #Facebook count
        frame = soup.select("li.facebook.mr2 .count")
        if len(frame) > 0:
            facebook_count = int(frame[0].text) #error prone
        else:
            facebook_count = 0
        #minimum pledge
        frame = soup.select("#button-back-this-proj .money")
        if len(frame) > 0:
            minimum_pledge = frame[0].text
        else:
            minimum_pledge = ""
        #update
        return (number_of_backers,goal,percent_raised,
                amount_pledged,currency,duration,end_time,
                hours_remaining,facebook_count,minimum_pledge)
    def analyze_project_reward(self,frame):
        #projects reward
        projects_reward_rv = []
        if len(frame) > 0:
            #
            for card in frame:
                #money
                money_f = card.select(".money")
                if len(money_f) > 0:
                    money = money_f[0].text.strip()
                else:
                    money = ""
                #backers
                backers_f = card.select(".num-backers")
                if len(backers_f) > 0:
                    num_backers = backers_f[0].text.strip()
                else:
                    num_backers = ""
                #description
                desc_f = card.select(".desc")
                if len(desc_f) > 0:
                    description = desc_f[0].text.strip()
                else:
                    description = ""
                #delivery
                delivery_f = card.select("time")
                if len(delivery_f) > 0:
                    delivery_estimated = delivery_f[0]['datetime']
                else:
                    delivery_estimated = ""
                #limited
                limited_f = card.select(".limited-number")
                if len(limited_f) > 0:
                    limited_num = int(re.findall(r"of ([0-9]+)",limited_f[0].text)[0])
                else:
                    limited_num = 0
                projects_reward_rv.append([
                    money,
                    num_backers,
                    description,
                    delivery_estimated,
                    limited_num,
                ])
            #for
        #
        return projects_reward_rv
            

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
                sys.stdout.write("At %s\n" % time.asctime(time.localtime()))
                sys.stdout.flush()
                assert len(url) > 0, "Error"
                pb, first_only =  self.factory_kickstarter(url)
                if not first_only:
                    N = self.target_N(pb)
                    for i in xrange(N):
                        # evaluate, compare data with the benchmark -> if nothing new? stop! if new? add!
                        wait_cue = 1
                        wait_tolerance = 15
                        pb.scroll_down()
                        sys.stdout.write("^")
                        sys.stdout.flush()
                        while pb.check_scroll_complete_ajax() and i < N:
                            time.sleep(wait_cue)
                            wait_cue += 1
                            sys.stdout.write("*")
                            sys.stdout.flush()
                            wait_tolerance -= 1
                            if wait_tolerance < 0:
                                break
                        sys.stdout.write("$")
                        sys.stdout.flush()
                #TODO -> pb.get_page_source()
                del pb # terminate the session
                sys.stdout.write("\nWork complete\n")
                sys.stdout.write("At %s\n\n"%time.asctime(time.localtime()))
                sys.stdout.flush()
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
def save_image_to_file(image_data,fname):
    """
>>> for i,k in enumerate(kpa.images):
    fname = "d:/%d.jpg"%i
    KS.save_image_to_file(k,fname)
    
    """
    if fname.endswith('.jpg'):
        fname = "%s.jpg"%fname
    i = Image.open(StringIO(image_data))
    i.save(fname)
# PROGRAM END