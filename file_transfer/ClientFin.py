''''''
import socket, sys, re, os
sys.path.append("../lib")       # for params
import params
from framedThreads import framedSocket

switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-d', '--debug'), 'debug', False),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "client"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]

if usage:
    params.usage()

try:
    serverHost, serverPort = re.split(":", server) 
    serverPort = int(serverPort) 
except:
    print("Can't Parse Server:Port From '%s'" % server)
    sys.exit(1)

port = (serverHost, serverPort)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Establishing connection with the socket
s.connect(port) # Connecting to socket

if s is None:
    print('Could Not Open Socket!')
    sys.exit(1)
    
FILE_PATH = "clientFiles/" # To get access of our client files
fSock = framedSocket(s) # Establish framed socket

while True:
    print("Enter File That You Wanna Send: ") 
    fileName = os.read(0, 1024).decode()
    filePath = (FILE_PATH + fileName).strip()
    if fileName != "exit":
        if os.path.isfile(filePath): # Checks the whole path if the file is a actually a file
            print("File Contents Are Sending") 
            file = open(filePath, "rb") # This is reading in binary mode
            fileData = file.read()
            if len(fileData) < 1: # This can't handle empty files
                print("Empty File")
                continue
            fSock.frameSend(fileName, fileData) # This will send the file and file contents
        else:
            print("File Does Not Exist, Please Try Again!")
            sys.exit(1)
        status = int(fSock.getStatus())  # This is if the file successfully transfered (the status of the server)
        if status == 1:
            print("Server Received File!")
            fSock.closeSock() # This will close connection in order to open it up 
            sys.exit(0)
        else:
            print("Recieving the File Failed by the Server!")
            fSock.closeSock()  
            sys.exit(1)
    else:
        print("Now Exiting!")
        fSock.closeSock()
        sys.exit(0)
