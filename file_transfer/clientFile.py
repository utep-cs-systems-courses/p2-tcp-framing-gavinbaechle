#! /usr/bin/env python3

# Echo client program
import socket, sys, re, time, os
sys.path.append("../lib")       # for params
import params


def create_socket(host):
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
        _, serverPort = re.split(":", server)
        serverPort = int(serverPort)
    except:
        print("Can't parse server:port from '%s'" % server)
        sys.exit(1)

    s = None
    for res in socket.getaddrinfo(host, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
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
    
    delay = float(paramMap['delay']) # delay before sending (default = 0s)
    if delay != 0:
        print(f"sleeping for {delay}s")
        time.sleep(delay)
        print("done sleeping")

    return s


def send_file(local_file, remote_file, host):
    s = create_socket(host)
    file_descriptor = os.open(local_file, os.O_RDONLY)
    file_size = os.path.getsize(local_file)
    chunk = os.read(file_descriptor, 1024)
    s.send("{0}:s{1}".format(len(remote_file) + 1, remote_file).encode())
    s.send("{0}:{1}".format(file_size, chunk.decode()).encode())
    
    while True:
        chunk = os.read(file_descriptor, 1024)
        if not chunk:
            break
        else:
            s.send(chunk)
    
    s.close()


def recieve_file(local_file, remote_file, host):
    s = create_socket(host)
    s.send("{0}:r{1}".format(len(remote_file) + 1, remote_file).encode())
    data = s.recv(1024).decode()
    delim = data.index(":")
    msg_length = int(data[:delim])
    data = data[delim + 1:]
    file_descriptor = os.open(local_file, os.O_CREAT | os.O_WRONLY)
    
    full_msg = ""
    while data:
        full_msg += data
        msg_length -= len(data)
        data = s.recv(1024).decode()
            
        if msg_length == 0:
            os.write(file_descriptor, full_msg.encode())
            break
    
    s.close()
