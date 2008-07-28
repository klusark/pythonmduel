import socket, cPickle
from threading import Thread
try:
    import psyco
    psyco.full()
except ImportError:
    print "Could not import psyco.\nPsyco is not required but it will speed up."
class Main():
    def __init__(self):
        #settings
        self.ip = "127.0.0.1"
        self.port = 63836
        
        self.s = socket.socket()

        self.s.bind((self.ip, self.port))
        self.s.listen(10)
        #self.connections = []
        self.servers = {}
        self.thread1 = Thread(None, self.ConnectThread, self.ConnectThread)
        self.thread1.start()
        print "Master Mduel server running on", self.ip + ":" + str(self.port)

    def ConnectThread(self):
        """Gets all incoming connections"""
        while 1:
            conn, addr = self.s.accept()
            thread = Thread(None, self.SendRecvThread, None, (), {"conn" : conn, "addr" : addr})
            thread.start()
            
    def SendRecvThread(self, conn, addr):
        ip, port = addr
        print "Incoming connection from", ip+":"+str(port)
        reads = conn.recv(512)
        if len(reads):
            info = cPickle.loads(reads)
            if info["type"] is 1:
                if addr[0] in self.servers:
                    print info["name"], "Updated"
                else:
                    print info["name"], "Listed"
                self.servers[addr[0]] = {"name" : info["name"], "port" : info["port"]}

            if info["type"] is 2:
                if info["ip"] in self.servers:
                    packet = self.servers[info["ip"]]
                    packet["type"] = 3
                    
                    dump = cPickle.dumps(packet)
                    conn.send(dump)
                    print "Sent info about", packet["name"], "to", addr[0]
                else:
                    packet = {"type" : 4}
                    
                    conn.send(cPickle.dumps(packet))
            if info["type"] is 5:
                #sends all the servers to the client
                packet = self.servers
                packet["type"] = 8
                self.connections[0][0].send(cPickle.dumps(packet))
        conn.shutdown(2)
        return
        
Main()