#! /usr/bin/env python3

# Echo client program
import socket, sys, re, time
sys.path.append("../lib")       # for params
import params

switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-d', '--delay'), 'delay', "0"),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage  = paramMap["server"], paramMap["usage"]

if usage:
    params.usage()

try:
    serverHost, serverPort = re.split(":", server)
    print(serverHost)
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

delay = float(paramMap['delay']) # delay before reading (default = 0s)
if delay != 0:
    print(f"sleeping for {delay}s")
    time.sleep(delay)
    print("done sleeping")

while 1:
    data = s.recv(1024).decode()
    full_msg = ""
    msg_length = 0
    msg = ""
    fragmented = False
    while data:
        if not fragmented:
            delim = data.index(":")
            msg_length = int(data[:delim])
            
            if msg_length <= (len(data) + 1 - len(str(msg_length))):
                msg = data[delim + 1: delim + msg_length + 1]
                data = data[delim + 1 + msg_length:]
                full_msg = msg
                msg_length = 0
            else:
                msg = data[delim + 1:]
                full_msg += msg
                msg_length -= len(msg)
                fragmented = True
                data = s.recv(1024).decode()
        
        elif ":" in data:
            msg = data[:msg_length]
            data = data[msglength:]
            full_msg += msg
            msg_length = 0
            fragmented = False
        
        else:
            full_msg += data
            msg_length -= len(data)
            data = s.recv(1024).decode()
        
        if msg_length <= 0:
            print(full_msg)
            full_msg = ""
            

print(full_msg)
print("Zero length read.  Closing")
s.close()
