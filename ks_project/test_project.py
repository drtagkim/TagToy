import sys,socket,sqlite3,time
from datetime import datetime
import server_setting as SS
import mysql.connector
def call_page():
    host = socket.gethostname()
    sys.stdout.write("KICKSTARTER PAGE LOG =======\n")
    sys.stdout.write("[%s]\n"%datetime.now().__str__())
    sys.stdout.flush()    
    #
    sql_read_project_search = """
        SELECT ts_id,project_id,project_url FROM project_search_temp
    """
    if SS.SQLITE_MYSQL == 'sqlite':
        con = sqlite3.connect(SS.DATABASE_NAME, timeout=10)
        cur = con.cursor()
        cur.execute(sql_read_project_search)
        rows = cur.fetchall()
        for k,row in enumerate(rows):
            client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            client.connect((host,SS.PROJECT_PAGE_PORT))
            client.send(repr(row))
            client.shutdown(socket.SHUT_RDWR) #disconnet
            client.close() #stream socket out
            print k
            time.sleep(0.1)
    else:
        con = mysql.connector.connect(user=SS.USER,
                                      password=SS.PASSWORD,
                                      host=SS.HOST,
                                      database=SS.DATABASE,
                                      connection_timeout=SS.LOCK_TIMEOUT)
        cur = con.cursor()
        cur.execute(sql_read_project_search)
        rows = cur.fetchall()
        for k,row in enumerate(rows):
            client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            client.connect((host,SS.PROJECT_PAGE_PORT))
            client.send(repr(row))
            client.shutdown(socket.SHUT_RDWR) #disconnet
            client.close() #stream socket out
            print k
            time.sleep(0.1)        
def call_log():
    host = socket.gethostname() # local computer
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
    
if __name__ == "__main__":
    call_log()
    #call_page()
