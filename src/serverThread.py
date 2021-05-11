#! /usr/bin/env python3

import socket, sys, re, os
sys.path.append("../lib")       # for params
import params
import framedSocket
import _thread
import Worker


lock = _thread.allocate_lock()

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "fileServer"
paramMap = params.parseParams(switchesVarDefaults)

listenPort = paramMap['listenPort']
listenAddr = ''       # Symbolic name meaning all available interfaces

if paramMap['usage']:
    params.usage()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((listenAddr, listenPort))
s.listen(1)              # allow only one outstanding request
# s is a factory for connected sockets

    
while True:
    conn, addr = s.accept() # wait until incoming connection request (and accept it)
    Worker.Worker(conn,addr).start()
