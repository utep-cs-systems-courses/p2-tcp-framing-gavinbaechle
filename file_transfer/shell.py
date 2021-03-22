#r/bin/env python3

import os, sys, re

                                      
def inputHandler(args):
    wait_child = True
    if len(args) == 0: #checks if there is an arguement
        return

    if "exit" in args:
        sys.exit(0)

    # Here we are changing the directory
    elif "cd" == args[0]:
        try:
            if len(args)==1: # This is here if cd is specified then reprompt the user
                return

            else:
                os.chdir(args[1])

        except: # It does not exist
            os.write(1, ("cd %s: No such file or directory\n" % args[1]).encode())

    elif '<' in args or '>' in args:
        reDir(args)

    elif '|' in args:
        pipe(args)

    elif '&' in args:
        wait_child = False 

    else:
        rc = os.fork()
        if rc < 0:
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)

        elif rc == 0:
            executeCommand(args)
            sys.exit(0)
        else:
            if wait_child: #we wait for the child
                child_wait = os.wait()


def executeCommand(args): # Executes command
    if '/' in args[0]: #for python commands
            prog = args[0]
            try:
                os.execve(prog, args, os.environ)
            except FileNotFoundError:
                pass #fail smoothly
            os.write(2, ("Could not exec. File not Found: %s\n" % args[0]).encode())
            sys.exit(1) 

    for dir in re.split(":", os.environ['PATH']):
        program = "%s/%s" % (dir, args[0])

        try:
            os.execve(program, args, os.environ) #see if program can be executed

        except FileNotFoundError:
            pass

    # error message
    os.write(2, ("%s: command not found\n" % args[0]).encode())
    sys.exit(0)


def reDir(args):
    if '<' in args: #check input
        leftProg = args[:args.index('<')]
        rightProg = args[args.index('<')+1:]
        os.close(0)
        os.open(rightProg[0], os.O_RDONLY) 
        os.set_inheritable(0, True) 
        args.remove('<')

    else: 
        leftProg = args[:args.index('>')]
        rightProg = args[args.index('>')+1:]
        os.close(1) #close input fd
        os.open(rightProg[0], os.O_CREAT | os.O_WRONLY) 
        os.set_inheritable(1, True) 
        args.remove('>')

    if '<' in rightProg or '>' in rightProg: 
        reDir(rightProg)
    executeCommand(args)

def pipe(args):
    #piping: 2 programs sharing info
    leftProg = args[:args.index('|')]
    rightProg = args[args.index('|')+1:]

    pread, pwrite = os.pipe() #parent write and read
    rc = os.fork() #child process

    if rc < 0:
        os.write(2, ('fork failed, returning %d\n'%rc).encode())
        sys.exit(1)

    elif rc == 0:
        os.close(1) 
        os.dup(pwrite) #use parent write
        os.set_inheritable(1, True) 
        for fd in (pread, pwrite): 
            os.close(fd)
        executeCommand(leftProg) #left pipe
        os.write(2, ('Execution Failed: %s\n' %leftProg[0]).encode())
        sys.exit(1)

    else:
        os.close(0) 
        os.dup(pread) 
        os.set_inheritable(0, True) 
        for fd in (pread, pwrite): 
            os.close(fd)
        if '|' in rightProg: 
            pipe(rightProg) 
        executeCommand(rightProg) #left pipe
        #incase of error
        os.write(2, ('Execution Failed: %s\n' %rightProg[0]).encode())
        sys.exit(1)



while True: #this allows shell to always be ready for input
    if 'PS1' in os.environ: #if there is custom prompt 1 then it re prints it out
        os.write(1, os.environ['PS1'].encode())
    else: # we set our own prompt
        os.write(1, ('$ ').encode())

    try: #error handling with os.read
        inpt = os.read(0,1024) #acts like myreadline and passes entirity of what is read
        if (len(inpt)>1):#input
          inpt = inpt.decode().split('\n') 
          for i in inpt:
            inputHandler(i.split()) #tokenize input
        

    except EOFError:
      os.write(1, ('There has been an error').encode())
