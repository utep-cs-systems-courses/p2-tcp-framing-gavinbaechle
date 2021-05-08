import socket, sys, re, os
import framedSocket
sys.path.append("../lib")
import params
import threading
from threading import Thread

threadNum = 0
lock = threading.Lock()

class Worker(Thread):
    def __init__(self,conn=None,addr=None):
        global threadNum
        Thread.__init__(self, name = "Thread-%d" % threadNum)
        threadNum += 1
        self.conn = conn
        self.addr = addr

    def checkTransfer(self, fileName,fileSet):
        global lock
        canUse = True
        lock.acquire()                                         #lock the thread
        if fileName in fileSet:                                #file in use
            canUse = False
        lock.release()                                         #unlock it
        return canUse

    def start(self,fileSet):
        framedSock = framedSocket.Framed_Socket(self.conn)
        fileName = framedSock.rx()
        if fileName == "QUIT":
            self.conn.shutdown(socket.SHUT_WR)
            sys.exit(1)
        filePath = './receivedFiles/' + fileName
        canUse = self.checkTransfer(filePath,fileSet)
        if not canUse:
            framedSock.tx(b'WAIT')
        elif os.path.isfile(filePath):
            framedSock.tx(b'File already in receivedFiles')
        else:
            framedSock.tx(b'OK')
            try:
                fd = open(filePath, "w")
                data = framedSock.rx()
                print('Writting: ',data)
                fd.write(data)
                fd.close()
                print("Complete")
            except:
                print(f"Error writing into file at {filePath}")
                self.conn.shutdown(socket.SHUT_WR)
                return None
        self.conn.shutdown(socket.SHUT_WR)
        return fileName
