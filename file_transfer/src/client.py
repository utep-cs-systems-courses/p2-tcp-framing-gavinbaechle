import socket, sys, re, time, os
import framedSocket
import workerThread
from myIO import myReadLine
sys.path.append("../lib")
import params

switchesVarDefaults = (
        (('-s', '--server'), 'server', "127.0.0.1:50001"),
        (('-d', '--delay'), 'delay', "0"),
        (('-?', '--usage'), "usage", False), # boolean (set if present)
        )

progname = "echoclient"
paramMap = params.parseParams(switchesVarDefaults)
server, usage  = paramMap["server"], paramMap["usage"]

if usage:
    params.usage()
    
try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)
    
s = None
for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        print(" error: %s" % msg)
        s = None
        continue
    try:
        print(" attempting to connect to %s" % repr(sa))
        s.connect(sa)
    except socket.error as msg:
        print(" error: %s" % msg)
        s.close()
        s = None
        continue
    break
                                                                                    
if s is None:
    print('could not open socket')
    sys.exit(1)

delay = float(paramMap['delay'])
if delay:
    print(f'sleeping for {delay}s')
    time.sleep(delay)
    print('done sleeping')
    
framedSock = framedSocket.Framed_Socket(s)

fileName = os.read(0,1024).decode().strip()
print(f'Sending {fileName}...')
framedSock.tx(fileName.encode())
if fileName == 'QUIT':
    print("Quitting...")
    sys.exit(1)
serverReply = framedSock.rx()

print(f"Server response:{serverReply}\n ")


if serverReply == "OK":
    fd = open(('./files/'+fileName),'r')       #open file to be sent
    content = fd.read()
    fd.close()
    framedSock.tx(content.encode())
else:
    os.write(2,("Error").encode())           #if the file already exists then print error
    sys.exit(1)
