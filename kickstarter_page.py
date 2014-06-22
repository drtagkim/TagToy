'''
KICKSTARTER PAGE DATA COLLECTION
AUTHOR: DRTAGKIM
2014
'''

from web3 import PhantomBrowser as PB
from bs4 import BeautifulSoup as BS
from hsaudiotag import mp4 # $ pip install hsaudiotag
from StringIO import StringIO
from threading import Thread
import zlib,re,time,sys,Queue
import requests # $ pip install requests
import sqlite3 # database
'''
HELPER FUNCTIONS
CONVERSION BETWEEN LIST AND QUEUE
'''

def list_to_queue(list_data):
    queue = Queue.Queue()
    map(lambda x : queue.put(x), list_data)
    return queue

def queue_to_list(queue_data):
    list_data = []
    list_data_append = list_data.append
    while True:
        try:
            list_data_append(queue_data.get_nowait())
        except:
            break
    return list_data


class ImageDownloader(Thread):
    '''
|  IMAGE DOWNLOADER
|  GET IMAGES FROM WEBSITES AND MAKE THEM BINARY FILES
    '''
    def __init__(self,inque,outque,quietly = True,has_image = True):
        Thread.__init__(self)
        self.inque = inque
        self.outque = outque
        self.running = True
        self.quietly = quietly
        self.has_image = has_image

    def stop(self):
        self.running = False

    def run(self):
        inque = self.inque
        outque = self.outque
        while self.running:
            try:
                src = inque.get(block=True,timeout=1)
                if self.has_image:
                    r = requests.get(src)
                    if r.status_code == 200:
                        c = r.content
                        outque.put([c,src])
                    if not self.quietly:
                        sys.stdout.write("i")
                        sys.stdout.flush()
                else:
                    if not self.quietly:
                        sys.stdout.write("o")
                        sys.stdout.flush()
                    outque.put(['',src])
                inque.task_done()
            except Queue.Empty:
                pass

class KickstarterPageAnalyzer:
    """
|  Page analyzer
|  For example, https://www.kickstarter.com/projects/1311317428/a-limited-edition-cleverly-designed-leather-collec
|  >>> kpa = KickstarterPageAnalyzer()
|  >>> kpa.analyze()
|  >>> kpa.read(url)
|  # OPTIONS
|  >>> kap = KickstarterPageAnalyzer(quietly = False, has_image = True)

|  Backers
|  Condition
|  Full description
|    Images
|    Video
|  Facebook

    """

    def __init__(self,quietly=True,has_image=False):
        self.pb = None #phantom browser
        self.quietly = quietly
        self.has_image = has_image
        #data clear
        self.clear()

    def clear(self):
        self.url = " "
        self.projects_reward_result = []
        self.images = []
        self.full_description = ""
        self.risks = ""
        self.backers = []
        self.image_fnames = []
        self.video_fname = ""
        self.video_length = 0
        self.video_has = False
        self.page_compressed = None
        self.facebook_like = 0

    def terminate(self):
        self.pb.close()
        self.pb == None

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
        #
        assert soup != None, "No Page!"
        #main page
        if not self.quietly:
            sys.stdout.write("..Main..")
            sys.stdout.flush()
        #analyze main page ===========
        # reward
        frame = soup.select(".NS-projects-reward")
        proj_reward_append = self.projects_reward_result.append
        if len(frame) > 0:
            #
            for card in frame:
                #money
                money_f = card.select(".money")
                if len(money_f) > 0:
                    money = filter_number(money_f[0].text.strip())
                else:
                    money = 0.0
                #backers
                backers_f = card.select(".num-backers")
                if len(backers_f) > 0:
                    num_backers = filter_number(backers_f[0].text.strip())
                else:
                    num_backers = 0.0
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
                proj_reward_append([
                    money,
                    num_backers,
                    description,
                    delivery_estimated,
                    limited_num,
                ])
            #for
        # collect images
        frame = soup.select("img.fit")
        image_fnames_append = self.image_fnames.append
        images_append = self.images.append
        if len(frame) > 0:
            for imgf in frame:
                src = imgf['src']
                src = re.sub(r"\?.*$","",src)
                image_fnames_append(src)
                images_append("") #basically nothing is apppended
            if self.has_image:
                inque = list_to_queue(self.image_fnames)
                outque = Queue.Queue()
                tasks = []
                # parallel processing
                for i in range(inque.qsize()):
                    imageD = ImageDownloader(inque,outque,self.quietly,True)
                    imageD.setDaemon(True)
                    tasks.append(imageD)
                    imageD.start()
                inque.join() #wait till being finished
                for task in tasks:
                    task.stop()
                outlist = queue_to_list(outque)
                self.images = copy.deepcopy(outlist)
                
        # video (source file name, length)s
        frame = soup.select("video.has_webm")
        self.video_fname = "no_video"
        v_url = ""
        if len(frame) > 0:
            sources = frame[0].select("source")
            if len(sources) > 0:
                self.video_has = True
                for source in sources:
                    v_url = source['src']
                    if v_url.endswith(".mp4"):
                        self.video_fname = v_url
                        break
                if len(v_url) > 0:
                    # video duration
                    r = requests.get(url,stream = True)
                    a = r.raw.read(2000) #2kb buffer
                    b = StringIO()
                    b.write(a)
                    c = mp4.File(b)
                    self.video_length = c.duration
                    b.close()
                    r.close()
        # collect full description
        frame = soup.select(".full-description")        
        rv = ""
        if len(frame) > 0:
            desc = frame[0].text
            rv = re.sub(r"\n\n\n+","\n",desc)
            try:
                rv = rv.strip()
            except:
                pass
        self.full_description = rv        
        # collect risk
        frame = soup.select("#risks")
        rv = ""
        if len(frame) > 0:
            desc = frame[0].text
            rv = re.sub(r"\n\n\n+","\n",desc)
            try:
                rv = rv.strip()
            except:
                pass
        self.risks = rv        
        # Facebook
        frame = soup.select("li.facebook.mr2 .count")
        waiting = 1
        while 1:
            if len(frame) > 0:
                try:
                    facebook_count = int(frame[0].text) #error prone
                    break
                except:
                    if not self.quietly:
                        sys.stdout.write("[facebook waiting...%d]\n"%waiting)
                        sys.stdout.flush()
                    time.sleep(waiting)
                    waiting += 1
                    temp_soup_facebook = BS(self.pb.get_page_source(),'html.parser')
                    frame = temp_soup_facebook.select("li.facebook.mr2 .count")
            else:
                self.facebook_like = 0
                break
            if waiting >= 10:
                if not self.quietly:
                    sys.stdout.write(" [facebook error] ")
                    sys.stdout.flush()
                self.facebook_like = -1 #means, error
                break
        
        # ============================
        if not self.quietly:
            sys.stdout.write("OK\n")
            sys.stdout.flush()
        #backers =====================
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
    def prep_database(self, dbname):
        sql_create_table1 = """
            CREATE TABLE IF NOT EXISTS project_benchmark_sub (
                ts_id NUMBER,
                project_id NUMBER,
                project_reward_number NUMBER,
                project_reward_mim_money_list TEXT,
                project_reward_description_total_length NUMBER,
                project_reward_description_str TEXT,
                image_count NUMBER,
                image_fnames_list TEXT,
                description_length NUMBER,
                description_str TEXT,
                risks_length NUMBER,
                risks_str TEXT,
                video_has NUMBER,
                video_length NUMBER,
                video_fname TEXT,
                facebook_like NUMBER,
                html_compressed BLOB,
                CONSTRAINT update_rule UNIQUE (ts_id, project_id) ON CONFLICT REPLACE);
            )
        """
        sql_create_table2 = """
            CREATE TABLE IF NOT EXISTS int_project_backer (
                ts_id NUMBER,
                project_id NUMBER,
                backer_slug TEXT,
                CONSTRAINT update_rule UNIQUE (ts_id, project_id, backer_slug) ON CONFLICT REPLACE);
        """
        sql_insert1 = """
            INSERT INTO project_benchmark_sub (
                ts_id, project_id, project_reward_number,
                project_reward_mim_money_list, project_reward_description_total_length,
                project_reward_description_str, image_count, image_fnames_list, description_length, description_str, risks_length, risks_str, video_has, 
                video_length, video_fname, facebook_like,
                html_compressed) VALUES (
                ?,?,?,?,?,?,?,?,?,??,?,?,?,?,?,?
            );
        """
        sql_insert2 = """
            INSERT INTO int_project_backer (
                ts_id, project_id, backer_slug)
                VALUES (?,?,?);
        """
        con = sqlite3.connect(dbname)
        cur = con.cursor()
        cur.execute(sql_create_table1)
        con.commit()
        cur.execute(sql_create_table2)
        con.commit()
    def write_database(self):
        project_reward_number = len(self.projects_reward_result)
        project_reward_mim_money_list = repr([item[0] for item in self.projects_reward_result])
        project_reward_description_total_length = 0
        for item in self.projects_reward_result:
            project_reward_description_total_length += len(item[2])
        image_count = len(self.image_fnames)
        image_fnames_list = repr(self.image_fnames)
        description_length = len(self.full_description)
        risks_length = len(self.risks)
        

# END OF PROGRAM ====================
