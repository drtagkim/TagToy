'''
KICKSTARTER SCHEDULER
AUTHOR: DRTAGKIM
2014
'''
from apscheduler.scheduler import Scheduler
# sudo pip install apscheduler
from datetime import datetime
import sys,socket,sqlite3, logging

import server_setting as SS

logging.basicConfig()

def call_log():
    host = socket.gethostname() # local computer
    sys.stdout.write(host+"\n")
    sys.stdout.write("KICKSTARTER PROJECT LOG =======\n")
    sys.stdout.write("[%s]\n"%datetime.now().__str__())
    sys.stdout.flush()
    for category_id in SS.CATEGORIES:
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.connect((host,SS.PROJECT_LOG_PORT))
        client.send(category_id)
        client.shutdown(socket.SHUT_RDWR) #disconnet
        client.close() #stream socket out
    sys.stdout.write("PROJECT LOG SERVER CALL COMPLETE\n\n")
    sys.stdout.flush()
def call_page():
    host = socket.gethostname()
    sys.stdout.write(host+"\n")
    sys.stdout.write("KICKSTARTER PAGE LOG =======\n")
    sys.stdout.write("[%s]\n"%datetime.now().__str__())
    sys.stdout.flush()    
    #
    con = sqlite3.connect(SS.DATABASE_NAME)
    sql_read_project_search = """
        SELECT ts_id,project_id,project_url FROM project_serach_temp;
    """
    cur = con.cursor()
    cur.execute(sql_read_project_search)
    rows = cur.fetchall()
    for row in rows:
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.connect((host,SS.PROJECT_PAGE_PORT))
        client.send(repr(row))
        client.shutdown(socket.SHUT_RDWR) #disconnet
        client.close() #stream socket out
    sql_clear_search = """
        DELETE FROM project_search_temp;
    """
    cur.execute(sql_clear_search)
    con.commit()
    cur.close()
    con.close()
    sys.stdout.write("PAGE LOG SERVER CALL COMPLETE\n\n")
    sys.stdout.flush()
def vacuum_database():
    con = sqlite3.connect(SS.DATABASE_NAME)
    cur = con.cursor()
    cur.execute("VACUUM")
    con.commit()
    cur.close()
    con.close()
    
if __name__ == "__main__":
    sched = Scheduler()
    sched.start()
    # project_log
    sched.add_cron_job(call_log,
                       month = '1-12',
                       day = '1-31',
                       hour = SS.PROJECT_LOG_START_HOUR,
                       minute = SS.PROJECT_LOG_START_MIN,
                       second = SS.PROJECT_LOG_START_SEC)
    sched.add_cron_job(call_page,
                       month = '1-12',
                       day = '1-31',
                       hour = SS.PROJECT_PAGE_START_HOUR,
                       minute = SS.PROJECT_PAGE_START_MIN,
                       second = SS.PROJECT_PAGE_START_SEC)
    sched.add_cron_job(vacuum_database,
                       month = '1-12',
                       day = '1-31',
                       hour = SS.VACUUM_DATABASE_HOUR,
                       minute = SS.VACUUM_DATABASE_MIN,
                       second = SS.VACUUM_DATABASE_SEC)
    while 1:
        try:
            pass
        except KeyboardInterrupt:
            sched.shutdown()
            break
# END OF PROGRAM ==================