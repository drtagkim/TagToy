import socket,sys
import kickstarter
import kickstarter_server_port as KSP
from threading import active_count

if __name__ == "__main__":
    probe = kickstarter.KsProjectProbe()
    probe.start()
    sys.stdout.write("Server Starts\n")
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind(('',KSP.PROJECT_PROBE_PORT))
    server.listen(1) #only one
    while 1:
        try:
            conn, addr = server.accept()
            data = conn.recv(1024*1024) # 1mb data
            probe.add(data)
        except KeyboardInterrupt:
            print "\nServer Stops"
            break
        except socket.error, msg:
            print msg
            print "Socket error"
            break
    probe.stop()
    probe.join()
    print "Active threads: %d" % active_count()
    print "Bye"