class Framed_Socket:
    def __init__(self, socket):
        self.connected = socket
        self.data = ''

    def tx(self,message):
        length = str(len(message))+":"
        byteLength = bytearray(length,'utf-8')
        message = byteLength + message
        self.connected.send(message)
        
    def rx(self):
        message = ''
        if not self.data:
            self.data += self.connected.recv(100).decode()    #get 100 bytes of data
            start, end = splitter(self.data)                  #find first and last data index
            message += self.data[start:end]                   #append first packet of data
            self.data = self.data[end:]                       #start from end of first packet


        while self.data:
            start, end = splitter(self.data)
            if len(self.data) < end:                            #more data to be received
                self.data += self.connected.recv(1024).decode() 
            else:
                message += self.data[start:end]
                self.data = self.data[end:]

        return message

def splitter(data):
    num = ''
    while data[0].isdigit():
        num += data[0]
        data = data[1:]

    if num.isnumeric():
        first = len(num) + 1                                  #skips the seperator
        last  = int(num) + first
        return first, last
    return None                                               #error in framing or empty
