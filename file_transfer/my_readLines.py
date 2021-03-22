import os,sys
from os import read,write

next = 0
limit = 0

def my_getChar():
    global next
    global limit
    if next == limit:
        next = 0
        limit = os.read(0,100)

        if limit == 0: 
            return 'EOF'
    if next < len(limit) -1:
        char = chr(limit[next])
        next += 1
        return char
    else:
        return 'EOF'

def my_readLine():
    global next
    global limit
    string = ''
    char = my_getChar
    while(char != '' and char != 'EOF'): 
        string += char
        char = my_getChar
    next = 0
    limit = 0
    return string
