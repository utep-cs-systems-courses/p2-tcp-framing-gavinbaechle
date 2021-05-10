import socket, sys, re, os
from framedSocket import FramedSocket
sys.path.append("../lib")       # for params
import params

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


progname = "server"
paramMap = params.parseParams(switchesVarDefaults)

listenPort = paramMap['listenPort']
listenAddr = ''       # Symbolic name meaning all available interfaces

if paramMap['usage']:
    params.usage()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((listenAddr, listenPort))
s.listen(1)              # allow only one outstanding request

while True:
    conn, addr = s.accept() # wait until incoming connection request (and accept it)
    if os.fork() == 0:      # child becomes server
        print('Connected by', addr)
        fs = FramedSocket(conn)

        fs.sendMsg("OK")
        msg = fs.recvMsg()

        try:
            fd = os.open(msg, os.O_CREAT | os.O_WRONLY)
            while True:
                msg = fs.recvMsg()
                if len(msg) == 0:
                    break
                os.write(fd, msg)
            os.close(fd)
        except:
            print("heres")
            fs.sendMsg("BAD")

        print("Done with", addr)
        conn.close()
