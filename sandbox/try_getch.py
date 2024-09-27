import time
import sys
import fcntl
import os

def getch():
    # from https://stackoverflow.com/a/75438160
    fd = sys.stdin.fileno()
    # fetch stdin's old flags
    old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    # set the none-blocking flag 
    fcntl.fcntl(fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)
    try:
        ch = sys.stdin.read(1)
    except:
        ch = None
    finally:
        # resetting stdin to default falgs
        fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)
    return ch 


while 1: 
    thischar = getch()
    if len(thischar)>0:
        print(thischar, ord(thischar))
        if ord(thischar) == 27:
            break
    time.sleep(0.1)
    print('.')
    sys.stdout.flush()