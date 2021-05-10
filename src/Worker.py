#! /usr/bin/env python3

import sys, os
import framedSocket
import socket
from time import time
from threading import Thread, enumerate
import threading

threadNum = 0
inTransfer = set()
transferLock = threading.Lock()

class Worker(Thread):                       # for my threaded file transfer
    def __init__(self, conn, addr):
        global threadNum
        Thread.__init__(self, name="Thread-%d" % threadNum);
        threadNum += 1
        self.conn = conn                   
        self.addr = addr

    def checkTransfer(self, fileName):      # checks if a file is already in transfer
        global inTransfer
        global transferLock
        transferLock.acquire()              # acquires a lock on checking if a file is in use
        if fileName in inTransfer:
            canTransfer = False
        else:
            canTransfer = True
            inTransfer.add(fileName)
        transferLock.release()
        return canTransfer

    def endTransfer(self, fileName):        # removes the file from the files currently in transfer
        global inTransfer
        inTransfer.remove(fileName)

    def run(self):
        print("Connected by: %s %d\n"%self.addr)  # prints where the connection comes from
        framedSocket.receiveMessage(self.conn)    # recieves "Send"
        filename = framedSocket.receiveMessage(self.conn)  # recieves the name of the file to save
        canTransfer = self.checkTransfer(filename)
        if(canTransfer == False): # cannot transfer yet and await message is sent
            framedSocket.sendMessage(self.conn,b"AW")
        elif os.path.isfile("./server/"+filename): # checks if file already exists
            framedSocket.sendMessage(self.conn,b"NO")
        else:
            framedSocket.sendMessage(self.conn,b"OK")
            try:                                    # tries to write to the file
                fd = os.open("./server/"+filename, os.O_CREAT | os.O_WRONLY)
                os.write(fd, framedSocket.receiveMessage(self.conn).encode())
                os.close(fd)
                framedSocket.sendMessage(self.conn, b"SUCCESS")   # success
            except:
                framedSocket.sendMessage(self.conn,b"FAILURE WRITING FILE")
            self.endTransfer(filename)
        self.conn.shutdown(socket.SHUT_WR)
