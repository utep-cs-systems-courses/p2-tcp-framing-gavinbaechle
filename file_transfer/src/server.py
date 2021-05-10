import socket, sys, re
import workerThread
sys.path.append("../lib")
import params

switchesVarDefaults = (
        (('-l', '--listenPort') ,'listenPort', 50001),
        (('-?', '--usage'), "usage", False), 
        )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

listenPort = paramMap['listenPort']
listenAddr = ''                                        

if paramMap['usage']:
        params.usage()
fileSet = set()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((listenAddr, listenPort))
s.listen(1)

while True:
    print(f"Waiting on client...")
    conn, addr = s.accept()                           # wait for incoming connection request
    print(f"Connected to client: {addr}\n")
    fileSet.add(workerThread.Worker(conn,addr).start(fileSet))
