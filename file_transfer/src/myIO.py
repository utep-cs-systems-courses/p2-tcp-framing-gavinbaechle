from os import read

limit = 0
index = 0

def myGetChar():                                #reads input char by char
        global limit
        global index
        if index == limit:
            index = 0
            limit = read(0,1000)                # fills array from input
            if limit == 0:                      # nothing to read
                return "EOF"
        if index < len(limit) - 1:              # Avoids out of bounds
            character = chr(limit[index])
            index +=1
            return character
        else:                                   # reached end of input
            return "EOF"
def myReadLine():
    global limit
    global index
    line = ""
    character = myGetChar()                        
    while character!='' and character!= "EOF":
        line += character                          
        character = myGetChar()
    index = 0
    limit = 0
    return line
