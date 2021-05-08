''''''
import socket, sys, os, time, threading
sys.path.append("../lib") # For params
import params
from framedThreads import framedSocket
from threading import Thread

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-?', '--usage'), "usage", False),
    (('-d', '--debug'), "debug", False),
    )

progname = "server"
paramMap = params.parseParams(switchesVarDefaults)

listenPort = paramMap['listenPort']
listenAddr = '' # Symbolic name meaning all available interfaces

debug = paramMap['debug']

if paramMap['usage']:
    params.usage()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Establishing the socket which we indicated as "s"
bindAddress = ("127.0.0.1", listenPort)
s.bind(bindAddress) # This is is where we bind the ip and the port
s.listen(10) # This will allow only one outstanding request and s is a factory for connected sockets

lock = threading.Lock()
os.chdir("./serverFiles") # This is where our transferred files will be located

class Server(Thread): # Created class that would handle what it should do when handling a new thread
    def __init__(self, connection, address):
        Thread.__init__(self) # Prevents breaking instances
        self.conn = connection
        self.addr = address

    def run(self):
        global lock
        fSock = framedSocket(self.conn) # Establishing the framed socket (framedThreads)
        print("Connection Made By ", self.addr)
        while True:
            try:
                print("Waiting on Client Request...")
                fileName, byteData = fSock.frameRecv() 
                print("Recieved File Successfully!")
            except:
                print("Transfer Failed!")
                fSock.sendStatus(0) # Failed to receive
                sys.exit(1)
            lock.acquire() # Placed aquire here so threads wont write to same file at the same time
            
            try:
                fileData = byteData.decode()
                transferFile = open(fileName, "w")
                transferFile.write(fileData)
                transferFile.close()
            except:
                print("Failed to Write to File!")
                fSock.sendStatus(0) # Indication that it failed to write (using the number "0")
            lock.release() # Once one thread is finished the other thread can write to file
            fSock.sendStatus(1) # Successfully transfered file
            sys.exit(0)
    
if __name__ == "__main__":
    print("Waiting On Connection...")
    while True:
        conn, addr = s.accept() # Accepting the socket
        server = Server(conn, addr) # Calling the server class
        server.start() 
