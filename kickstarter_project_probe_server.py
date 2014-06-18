import socket,sys,os
import kickstarter
import kickstarter_server_port as KSP
import Queue
from threading import active_count

REPOSITORY_NAME = 'repo_project'
CONTINUE_ = True # if True, only collect in-progress projects
def create_repository():
    if not os.path.exists(REPOSITORY_NAME):
        os.mkdir(REPOSITORY_NAME)
if __name__ == "__main__":
    create_repository()
    probes = []
    inque = Queue.Queue()
    # make four...
    for _ in range(4):
        probe = kickstarter.KsProjectProbe(inque,continue_=CONTINUE_)
        probe.repository = "%s/"%(REPOSITORY_NAME,)
        probe.setDaemon(True)
        probes.append(probe)
        probe.start()
    sys.stdout.write("Server Starts\n")
    print "Active threads: %d" % active_count()
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind(('',KSP.PROJECT_PROBE_PORT))
    server.listen(1) #only one
    while 1:
        try:
            conn, addr = server.accept()
            data = conn.recv(1024*1024) # 1mb data
            #probe.add(data)
            data = eval(data)
            inque.put(data)
        except KeyboardInterrupt:
            print "\nServer Stops"
            break
        except socket.error, msg:
            print msg
            print "Socket error"
            break
    inque.join() #no more data
    for probe in probes: #terminate threads
        probe.stop()
        probe.join()
    print "Active threads: %d" % active_count()
    print "Bye"