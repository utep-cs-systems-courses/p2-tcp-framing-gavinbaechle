'''This is where the magic happens, framing the message to be able to send and recieve the message!'''
import socket

class framedSocket:
    def __init__(self, socket):
        self.sock = socket
        self.rbuff = b"" # Making rbuff an attribute to prevent multiple threads from writing to one global buff

    def closeSock(self): # Socket closes
        self.sock.close() 

    def sendStatus(self, status): # Sending the status of the server
        self.sock.send(str(status).encode()) 

    def getStatus(self): # Getting the status
        status = self.sock.recv(100)
        return status.decode()
            
    def frameSend(self, fileName, fileData): # Sending the file and data
        msg = str(len(fileData)).encode() + b':' + fileName.encode() + b':' + fileData
        while len(msg):
            sentMsg = self.sock.send(msg)
            msg = msg[sentMsg:] 

    def frameRecv(self): # Recieving the file name and message from the file itself
        recvMessage = self.sock.recv(100) 
        framedMessage = recvMessage.split(b':') # Spliting it!
        msgLength = int(framedMessage[0])
        fileName = framedMessage[1].decode() # Decoding the message
        self.rbuff += framedMessage[2]
        while True:
            if len(self.rbuff) >= msgLength:
                fileData = self.rbuff[0:msgLength] # Using our buffer to get the data of the file 
                self.rbuff = self.rbuff[msgLength:] 
                return fileName, fileData
            recvMessage = self.sock.recv(100)
            self.rbuff+=recvMessage
