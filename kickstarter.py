'''
Author: Taekyung Kim 2014
Contact: masan.korea@gmail.com
'''
# -- Web --
from web3 import PhantomBrowser as PB
from web3 import WebReader2 as WR
from bs4 import BeautifulSoup as BS
# -- System --
import time,sys,re,math,re,csv,zlib
from datetime import datetime
# -- Multithreading --
from threading import Thread, active_count
import Queue,re
# -- Web, Imaging --
from PIL import Image
from StringIO import StringIO
import requests #Apache requests
import os, glob, shutil
# PROGRAM STARTS ===========

# global functions
def time_stamp():
    now = time.localtime()
    return "%04d_%02d_%02d_%02d_%02d" % (now.tm_year,now.tm_mon,now.tm_mday,now.tm_hour,now.tm_min)
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

# classes
class KICKSTARTER:
    """
|  General string values for the Kickstarter site
    """
    MAIN = "https://www.kickstarter.com"
    CATEGORY_ART = "https://www.kickstarter.com/discover/advanced?category_id=1&sort=end_date"
    CATEGORY_COMICS = "https://www.kickstarter.com/discover/advanced?category_id=3&sort=end_date"
    CATEGORY_DANCE = "https://www.kickstarter.com/discover/advanced?category_id=6&sort=end_date"
    CATEGORY_DESIGN = "https://www.kickstarter.com/discover/advanced?category_id=7&sort=end_date"
    CATEGORY_FASHION = "https://www.kickstarter.com/discover/advanced?category_id=9&sort=end_date"
    CATEGORY_FILM = "https://www.kickstarter.com/discover/advanced?category_id=11&sort=end_date"
    CATEGORY_FOOD = "https://www.kickstarter.com/discover/advanced?category_id=10&sort=end_date"
    CATEGORY_GAMES = "https://www.kickstarter.com/discover/advanced?category_id=12&sort=end_date"
    CATEGORY_MUSIC = "https://www.kickstarter.com/discover/advanced?category_id=14&sort=end_date"
    CATEGORY_PHOTOGRAPHY = "https://www.kickstarter.com/discover/advanced?category_id=15&sort=end_date"
    CATEGORY_PUBLISHING = "https://www.kickstarter.com/discover/advanced?category_id=18&sort=end_date"
    CATEGORY_TECHNOLOGY = "https://www.kickstarter.com/discover/advanced?category_id=16&sort=end_date"
    CATEGORY_THEATER = "https://www.kickstarter.com/discover/advanced?category_id=17&sort=end_date"
    XPATH_RELOAD_BUTTON = "id('projects')/div/div/a"
    CSS_COUNTER = "b.count"
    CSS_GET_CARD = "div.project-card"
    CSS_TITLE = "h6.project-title a"
    CSS_AUTHOR = "p.mb1"
    CSS_DESC1 = "p.project-blurb"
    CSS_DESC2 = "p.blurb"
    CSS_LOCATION_NAME = "span.location-name"
    CSS_STAT = "ul.project-stats"
    CSS_BOTTOM = "div.absolute-bottom"
    ATT_DUE_DATE = "data-end_time"

class KickstarterProjectCollector:
    def __init__(self,url):
        self.url = url
    def factory_kickstarter(self,url):
        pb = PB(noimage = True)
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
            i = 0
            terminate = False
            while 1:
                politeness = 0
                if pb.scroll_down():
                    sys.stdout.write("\r%s"%(" "*40,))
                    sys.stdout.flush()
                    sys.stdout.write("\rpage: %03d" % (i+1,))
                    sys.stdout.flush()
                    while 1:
                        politeness += 1
                        if pb.check_scroll_complete_ajax():
                            if i < N:
                                time.sleep(politeness)
                                sys.stdout.write(".")
                                sys.stdout.flush()
                            else:
                                terminate = True
                                break
                        else:
                            break
                if terminate:
                    break
                i += 1
            #for i in xrange(N):
                #wait_tolerance = 15
                #politeness = 1
                #pb.scroll_down()
                #sys.stdout.write("page: %03d" % (i,))
                #sys.stdout.flush()
                #if pb.check_scroll_complete_ajax() and i >= N:
                    #break
                ##while not pb.check_scroll_complete_ajax() and i < N:
                    ##time.sleep(politeness)
                    ##politeness +=1 
                    ##sys.stdout.write(".")
                    ##sys.stdout.flush()
                    ##wait_tolerance -= 1
                    ##if wait_tolerance < 0:
                        ##break
                #sys.stdout.write(" OK\n")
                #sys.stdout.flush()
            sys.stdout.write("\nOK\n")
            sys.stdout.flush()
        pb.page_source_save(foutput,remove_js=True)
        del pb


class KickstarterCard:
    def __init__(self,collection_id):
        self.collection_id = collection_id
        self.title_text = " "
        self.title_url = " "
        self.author_text= " "
        self.desc_text = " "
        self.location_text = " "
        self.funded_text = " "
        self.pledged_text = " "
        self.days_to_go_text = " "
        self.on_going = "0"
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
            self.days_to_go_text.encode('utf-8'))
        return rv
    def line(self):
        return [self.collection_id,
            self.on_going,
            self.title_text.encode('utf-8'),
            self.title_url.encode('utf-8'),
            self.author_text.encode('utf-8'),
            self.desc_text.encode('utf-8'),
            self.location_text.encode('utf-8'),
            self.funded_text.encode('utf-8'),
            self.pledged_text.encode('utf-8'),
            self.days_to_go_text.encode('utf-8')]

class KickstarterProjectFilter:
    def analyze(self,page_source):
        soup = BS(page_source,'html.parser')
        cards = soup.select(KICKSTARTER.CSS_GET_CARD)
        found_completed = False
        if len(cards) > 0:
            for card in cards:
                stat = card.select(KICKSTARTER.CSS_BOTTOM)
                if len(stat) > 0:
                    text_in = stat[0].text.lower()
                    compiled_re = re.findall(r'(\w{3}\s[0-9]{1,2},\s[0-9]{4})',text_in)
                    if len(compiled_re) > 0:
                        # today?
                        current_time_stamp = datetime.strptime(compiled_re[0],'%b %d, %Y')
                        today_time_stamp = datetime.today()
                        tdff = today_time_stamp - current_time_stamp
                        if tdff.days > 0: # containing past data
                            found_completed = True
                            break
        return found_completed
    def only_on_going(self,card):
        rv = "1" # means, yes on going
        stat = card.select(KICKSTARTER.CSS_BOTTOM)
        if len(stat) > 0:
            text_in = stat[0].text.lower()
            compiled_re = re.findall(r'successful',text_in)
            if len(compiled_re) > 0:
                rv = "0"
        return rv
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
        kpf = KickstarterProjectFilter()
        for card in self.cards:
            kickstarter_card = KickstarterCard(collection_id)
            kickstarter_card.title_text,kickstarter_card.title_url = self.get_title(card)
            kickstarter_card.author_text = self.get_author(card)
            kickstarter_card.desc_text = self.get_desc(card)
            kickstarter_card.location_text = self.get_location_name(card)
            kickstarter_card.funded_text,kickstarter_card.pledged_text,kickstarter_card.days_to_go_text = self.get_stat(card)
            kickstarter_card.on_going = kpf.only_on_going(card)
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
        funded_text = " "
        pledged_text = " "
        days_to_go_text = "funding unsuccessful"
        if len(stat) > 0:
            funded_text_ele = stat[0].select('li.first strong')
            if len(funded_text_ele) > 0:
                funded_text = funded_text_ele[0].text.strip()
            pledged_text_ele = stat[0].select('li.pledged strong')
            if len(pledged_text_ele) > 0:
                pledged_text = pledged_text_ele[0].text.strip()
            days_to_go_text_ele = stat[0].select('li.last strong div.num')
            if len(days_to_go_text_ele) > 0:
                days_to_go_text = days_to_go_text_ele[0].text.strip()
            else:
                days_to_go_text = "funded"
        return (funded_text,pledged_text,days_to_go_text)
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
        self.title = " "
        self.founder = " "
        self.url = " "
        self.stat_result = ()
        self.projects_reward_result = []
        self.images = []
        self.condition_desc = " "
        self.full_description = " "
        self.risks = " "
        self.backers = []
    def terminate(self):
        self.pb.close()
        del self.pb
    def read(self,url):
        if not self.quietly:
            sys.stdout.write("Get set...")
            sys.stdout.flush()
        if self.pb == None:
            self.pb = PB(noimage=True)
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
            p = pb.get_page_source()
            s = BS(p,'html.parser')
            current_rows = s.select("div.NS_backers__backing_row")
            if len(current_rows) != 0:
                no_backers = False
            breaker = False
            while 1:
                safety = 1
                if pb.scroll_down():
                    if not self.quietly:
                        sys.stdout.write("^")
                        sys.stdout.flush()
                    #checking...
                    while 1:
                        if pb.check_scroll_complete_ajax():
                            if safety < 0:
                                breaker = True
                                break
                            else:
                                if not self.quietly:
                                    sys.stdout.write(".")
                                    sys.stdout.flush()
                                time.sleep(1)
                                safety -= 1
                        else:
                            break
                if breaker:
                    break
            if not self.quietly:
                sys.stdout.write("$")
                sys.stdout.flush()
            #while 1:
                #p = pb.get_page_source()
                #s = BS(p,'html.parser')
                #current_rows = s.select("div.NS_backers__backing_row")
                #if len(current_rows) == 0:
                    #break
                #else:
                    #no_backers = False
                ## AJAX
                
                #last_backer_cursor_now = current_rows[-1]['data-cursor']
                #if last_backer_cursor != last_backer_cursor_now:
                    #last_backer_cursor = last_backer_cursor_now
                    #if pb.scroll_down():
                        #if not self.quietly:
                            #sys.stdout.write("^")
                            #sys.stdout.flush()
                        #wait_tolerance = 2
                        #politeness = 0.5
                        #if pb.check_scroll_complete_ajax():
                            #break
                        #while pb.check_scroll_complete_ajax():
                            #time.sleep(1)
                            #if not self.quietly:
                                #sys.stdout.write("*")
                                #sys.stdout.flush()
                            #if wait_tolerance < 0:
                                #break
                        #if not self.quietly:
                            #sys.stdout.write("$")
                            #sys.stdout.flush()
                    #else:
                        #break
                #else:
                    #if not self.quietly:
                        #sys.stdout.write("\n")
                        #sys.stdout.flush()
                    #break
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
        #title
        title_ele = soup.select('div.title')
        if len(title_ele) > 0:
            self.title = title_ele[0].text.strip()
        #founder
        founder_ele = re.findall(r"/projects/(.+)/",self.url)
        if len(founder_ele) > 0:
            self.founder = "https://www.kickstarter.com/profile/%s"%(founder_ele[0],)
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
            waiting = 1
            while 1:
                try:
                    facebook_count = int(frame[0].text) #error prone
                    break
                except:
                    time.sleep(1)
                    if not self.quietly:
                        sys.stdout.write("\r[facebook waiting...%d]\n"%waiting)
                        sys.stdout.flush()
                        waiting += 1
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
            

class KsProjectProbe(Thread):
    def __init__(self,url_queue,screen,loc_id,continue_=False):
        Thread.__init__(self)
        #self.url = url
        self.url_queue = url_queue
        self.running = True
        self.repository = "" # file repository
        self.continue_ = continue_
        self.screen = screen
        self.loc_id = loc_id
        
        #self.bench_mark = bench_mark #bench mark card (to decide a stopping point)
    #def add(self,url):
        #self.url_queue.put(url)
    def stop(self):
        self.running = False
    def run(self):
        filter = KickstarterProjectFilter()
        screen = self.screen
        while self.running:
            try:
                url,identifier = self.url_queue.get(block=True,timeout=10) #wait for 10 second
                screen.gotoXY(7,self.loc_id)
                screen.cprint(15,0,"ACTIVE  ")
                sys.stdout.flush()
                #sys.stdout.flush()
                start_tstamp = time_stamp()
                assert len(url) > 0, "Error"
                screen.gotoXY(25,self.loc_id)
                screen.cprint(13,0,"Processing at %s%s"%(time.asctime(time.localtime())," "*20))
                sys.stdout.flush()
                pb, first_only =  self.factory_kickstarter(url)
                if self.continue_:
                    if filter.analyze(pb.get_page_source()):
                        first_only = True # cancel the rest
                if not first_only:
                    scroll_line = 0
                    N = self.target_N(pb)
                    i = 0
                    terminate = False
                    while 1:
                        politeness = 0
                        if pb.scroll_down():
                            scroll_line += 1
                            screen.gotoXY(0,self.loc_id)
                            screen.cprint(10,0,"%04d"%scroll_line)
                            sys.stdout.flush()
                            while 1:
                                politeness += 1
                                if pb.check_scroll_complete_ajax():
                                    if i < N:
                                        time.sleep(politeness)
                                    else:
                                        terminate = True
                                        break
                                else:
                                    break
                            screen.gotoXY(5,self.loc_id)
                            screen.cprint(9,0," ")
                            sys.stdout.flush()
                            #check (whether or not continuing...)
                            if self.continue_:
                                if filter.analyze(pb.get_page_source()):
                                    terminate = True
                                    break
                        if terminate:
                            break
                        i += 1
                    screen.gotoXY(0,self.loc_id)
                    screen.cprint(12,0,"OK   ")
                    sys.stdout.flush()
                
                fname = "%s%s_%s_page_source.html" % (self.repository,
                                                      start_tstamp,
                                                      identifier)
                pb.page_source_save(fname,remove_js=True) #for testing...
                del pb # terminate the session
                screen.gotoXY(25,self.loc_id)
                screen.cprint(13,0,"Complete at %s%s"%(time.asctime(time.localtime())," "*30))
                sys.stdout.flush()
            except Queue.Empty:
                self.screen.gotoXY(0,self.loc_id)
                self.screen.cprint(12,0," "*12)
                screen.gotoXY(7,self.loc_id)
                screen.cprint(15,0,"INACTIVE")
                sys.stdout.flush()                
                sys.stdout.flush()
    def factory_kickstarter(self,url):
        pb = PB(noimage = True)
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

class ksProjectPageAnalyzer(Thread):
    """
|  listen
    """
    def __init__(self,ongoing_dir,listener_dir,speaker_dir,reserver_dir,listen_duration=60):
        Thread.__init__(self)
        self.running = True
        self.ongoing_dir = ongoing_dir #ongoing_data_now
        self.listener_dir = listener_dir #input
        self.speaker_dir = speaker_dir #analysis result
        self.reserver_dir = reserver_dir #move completed ones
        self.listen_duration = listen_duration
        if not os.path.exists(speaker_dir):
            os.mkdir(speaker_dir)
        if not os.path.exists(reserver_dir):
            os.mkdir(reserver_dir)
        if not os.path.exists(self.ongoing_dir):
            os.mkdir(self.ongoing_dir)        
        sys.stdout.write("PROJECT PAGE ANALYZER STARTS...\n")
        sys.stdout.write("\r...WAITING...")
        sys.stdout.flush()
    def stop(self):
        self.running = False
    def run(self):
        while self.running:
            try:
                #collection id
                collection_id = time_stamp()[:10] #year_month_day
                #read file list
                data_files = glob.glob("%s/*.*"%self.listener_dir)
                #current_project_inventory = glob.glob("%s/*.inv"%self.ongoing_dir)
                #for cpi in current_project_inventory:
                    #os.remove(cpi)
                out_dir = "%s/%s"%(self.speaker_dir,collection_id)
                if not os.path.exists(out_dir):
                    os.mkdir(out_dir)
                res_dir = "%s/%s"%(self.reserver_dir,collection_id)
                if not os.path.exists(res_dir):
                    os.mkdir(res_dir)
                current_proj_inv_dir = "%s/%s"%(self.ongoing_dir,collection_id)
                if not os.path.exists(current_proj_inv_dir):
                    os.mkdir(current_proj_inv_dir)
                #working...
                for data_file in data_files:
                    base_file_name = os.path.basename(data_file)
                    remove_int = len("...PROCESSING: %s"%(base_file_name,))
                    sys.stdout.write("\r...PROCESSING: %s"%(base_file_name,))
                    sys.stdout.flush()
                    kpa = KickstarterProjectAnalyzer(data_file)
                    kpa.execute(collection_id)
                    out_fname = "%s/%s.txt" % (out_dir,base_file_name)
                    kpa.export_result_tsv(out_fname)
                    res_fname = "%s/%s"%(res_dir,base_file_name)
                    shutil.move(data_file,res_fname)
                    sys.stdout.write("\r%s"%(" "*remove_int,))
                    sys.stdout.flush()
                    #list up
                    f_inv = open("%s/%s.inv"%(self.ongoing_dir,base_file_name),'wb')
                    f_inv_writer = csv.writer(f_inv,delimiter="\t",lineterminator="\n")
                    for kickstarter_card in kpa.results:
                        if kickstarter_card.on_going == "1":
                            f_inv_writer.writerow([kickstarter_card.title_url])
                    f_inv.close()
                    #list up
                    shutil.copyfile("%s/%s.inv"%(self.ongoing_dir,base_file_name),"%s/%s.inv"%(current_proj_inv_dir,base_file_name))
                    #make backup
                
                sys.stdout.write("\r...WAITING...")
                sys.stdout.flush()
                time.sleep(self.listen_duration)
            except KeyboardInterrupt:
                break
        sys.stdout.write("\nTHANK YOU.\n")
        sys.stdout.flush()
    
class KsPageAnalyzerWrapper(Thread):
    def __init__(self,inque):
        Thread.__init__(self)
        self.inque = inque
        self.running = True
    def stop(itself):
        self.running = False
    def run(self):
        pass ##TODO
# PROGRAM END ===========