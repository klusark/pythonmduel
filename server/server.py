import socket, threading, time, cPickle, select
from pygame.time import Clock
try:
    import psyco
    psyco.full()
except ImportError:
    print "Could not import psyco.\nPsyco is not required but it will speed up."
class Server():
    def __init__(self):
        #settings
        self.ip = "127.0.0.1"
        self.port = 63835
        self.name = "Joel's Server"
        self.maxPlayers = 2
        self.masterServerIP = "127.0.0.1"
        self.masterServerPort = 63836
        self.public = False #determines if it should update to the master server
        
        self.currentPlayers = 0
        self.players = {}
        self.clock = Clock()
        self.s = socket.socket()
        self.id = 0
        self.s.bind((self.ip, self.port))
        self.s.listen(10)
        #self.connections = []
        #self.players = []
        self.thread1 = threading.Thread(None, self.ConnectThread, self.ConnectThread)
        self.thread1.start()
        #self.thread2 = threading.Thread(None, self.SendRecvThread, self.SendRecvThread)
        #self.thread2.start()
        if self.public:
            self.thread3 = threading.Thread(None, self.MasterUpdateThread, self.MasterUpdateThread)
            self.thread3.start()
        print "Dedicated mduel server running on", self.ip + ":" + str(self.port)
        
    def ConnectThread(self):
        """Gets all incoming connections"""
        while 1:
            conn, addr = self.s.accept()
            thread = threading.Thread(None, self.SendRecvThread, None, (), {"conn" : conn, "addr" : addr})
            thread.start()
            
    def SendRecvThread(self, conn, addr):
        ip, port = addr
        print "Incoming connection from", ip+":"+str(port)
        msg = conn.recv(512)
        if len(msg):
            msg = cPickle.loads(msg)
            if msg["type"] == 6:
                self.currentPlayers += 1
                self.id += 1
                id = self.id
                self.players[id] = {"name":msg["name"]}
                packet = self.players
                packet["type"] = 10
                packet["id"] = id
                conn.send(cPickle.dumps(packet))
                thread = threading.Thread(None, self.PlayerThread, None, (), {"conn" : conn, "addr" : addr, "id":id})
                thread.start()

    def PlayerThread(self, conn, addr, id):
        print "Player", self.players[id]["name"], "has has connected"
        while 1:
            self.clock.tick(60)
            read, write, err = select.select([conn], [conn], [])
            if len(read):
                msg = conn.recv(512)
                #print msg
                msg = cPickle.loads(msg)
                if msg["type"] == 7:
                    self.currentPlayers -= 1
                    print "Player", self.players[id]["name"], "has has disconnected"
                    self.players.pop(id)
                    return
                if msg["type"] == 9:
                    self.players[id]["playerVars"] = msg
            if len(write):
                pass
            #else:
            #    return
                        
    
    def MasterUpdateThread(self):
        while 1:
            try:
                self.s2 = socket.socket()
                self.s2.connect((self.masterServerIP, self.masterServerPort))
                packet = {"type" : 1, "name" : self.name, "port" : self.port, "maxPlayers" : self.maxPlayers}
                self.s2.send(cPickle.dumps(packet))
                self.s2.shutdown(2)
                print "Updated master server"
                time.sleep(60)
            except socket.error, msg:
                if msg[0] == 10061:
                    print "The master server refused the connection. It could be down or busy. Retrying in 100 seconds."
                    time.sleep(100)
                else:
                    print msg
                    #print ""
                    time.sleep(120)
        
Server()