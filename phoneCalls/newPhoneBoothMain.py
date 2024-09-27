#!/opt/homebrew/anaconda3/envs/fishphone/bin/python
import json
import datetime
import subprocess
import os
from time import sleep
import serial
import time
import sys

from dotenv import load_dotenv
from makeCalls import fishPhoneCall
from kbhit import KBHit

inNum = '0'
firstCallDelay = 191#181 # call delay in seconds
endCallDelay =  650#401 # call delay in seconds

DEBUG_ARDUINO = True
DEBUG_PHONECALL = True
DEBUG_AUDIO = True
DEBUG_LIGHTS = True
DEBUG_STORAGE = True

# load variables from .env file: 
load_dotenv()

THIS_PYTHON = '/opt/homebrew/anaconda3/envs/fishphone/bin/python'

if not DEBUG_ARDUINO:
    USB_ONAIR = os.getenv('USB_ONAIR')
    USB_KEYPAD = os.getenv('USB_KEYPAD')
    arduinoScreen = serial.Serial(port=USB_KEYPAD, baudrate=9600, timeout=.1) 
    arduinoDoor = serial.Serial(port=USB_ONAIR, baudrate=115200, timeout=.1) 

# pygame.init()
kb = KBHit()

# creating display
# display = pygame.display.set_mode((300, 300))

def write_read(x):
    data = x
    if not DEBUG_ARDUINO: 
        arduinoScreen.write(bytes(x, 'utf-8'))
        if data == 'n':
            arduinoDoor.write(bytes(x, 'utf-8'))
        elif data == '~':
            arduinoDoor.write(bytes(x, 'utf-8'))
    print(data+" --> arduino")
    return data
	
if not DEBUG_LIGHTS:
    # reset_blue
    subprocess.Popen(['python', '../bulb/blue.py']) # run once

#write_read('w')

def takeNum():
    number = ''
    value = ''
    try:
        while True:
            if kb.kbhit():                            
                # checking if key was pressed
                c = kb.getch()
                c_ord = ord(c)

                if len(number) < 10:    
                    if c == '0':
                        value = write_read('0') 
                        number = number + value
                    if c == '1':
                        value = write_read('1') 
                        number = number + value
                    if c == '2':
                        value = write_read('2') 
                        number = number + value
                    if c == '3':
                        value = write_read('3') 
                        number = number + value
                    if c == '4':
                        value = write_read('4') 
                        number = number + value
                    if c == '5':
                        value = write_read('5') 
                        number = number + value
                    if c == '6':
                        value = write_read('6') 
                        number = number + value
                    if c == '7':
                        value = write_read('7') 
                        number = number + value
                    if c == '8':
                        value = write_read('8') 
                        number = number + value
                    if c == '9':
                        value = write_read('9') 
                        number = number + value
                    if c_ord == 127:
                        # BACKSPACE
                        value = write_read('*') 
                        number = number[:-1]
                    if c_ord == 144:
                        # num lock keycode https://www.foreui.com/articles/Key_Code_Table.htm
                        value = write_read('n') 
                        number = 'END'
                        return number
                    if c == '`':
                        value = write_read('n') 
                        number = 'END'
                        return number
                    print(number, c_ord)
                if len(number) == 10:
                    print("reached 10")
                    if c_ord == 10:
                        # ENTER / CR
                        write_read('~')
                        print("...completed number entry")
                        sys.stdout.flush()
                        return number
                    if c_ord == 127:
                        value = write_read('*') 
                        number = number[:-1]
                    print(number, c_ord)

    except KeyboardInterrupt:
        pass

def addNum(inNum):
    # Stores the current time
    
    time = datetime.datetime.now()
    firstTime = time + datetime.timedelta(seconds=firstCallDelay)
    endTime = time + datetime.timedelta(seconds=endCallDelay)
    
    # Makes uid be the next possible number
    uid = len(listObj)

    #Test if number is valid
    if len(inNum) == 10:
        formNum = '+1' + inNum
        add = 0
        i = 0
        # Test if number is already stored
        for num in listObj:
            if formNum == num['phoneNum']:
                uid = i
                add = 1
            i += 1
    else:
        add = 2

    #add if valid and new
    if add == 0:
        listObj.append({"uid": uid, 'phoneNum': formNum, 'startTime': time.strftime("%c")})
        
        with open(filename, 'w') as json_file:
            json.dump(listObj, json_file, 
                                indent=4,  
                                separators=(',',': '))
        
        print("added ", listObj[uid])
        if not DEBUG_AUDIO:
            audioProcess = subprocess.Popen(['python', 'play-audio.py'])
        if not DEBUG_LIGHTS:
            lightProcess = subprocess.Popen(['python', '../bulb/descent_reidVersion.py'])
        
        if not DEBUG_PHONECALL:
            handle = fishPhoneCall(uid, firstTime.hour, firstTime.minute, firstTime.second)
        
        if handle == 'END':
                
            # this cycle of phone call is done
            
            if not DEBUG_AUDIO:
                audioProcess.terminate()
            if not DEBUG_LIGHTS:
                lightProcess.terminate()
            
            write_read('n')
            
            if not DEBUG_LIGHTS:
                # reset_blue
                subprocess.Popen(['python', '../bulb/blue.py']) # run once
            
            time.sleep(5)
            return

        elif handle == 'CALLED':
            if not DEBUG_PHONECALL:
                handle = fishPhoneCall(uid, endTime.hour, endTime.minute, endTime.second)
            
            # subprocess.Popen(['python', 'afterCalls.py'])
            
            if handle == 'END':
                if not DEBUG_AUDIO:
                    audioProcess.terminate()
                if not DEBUG_LIGHTS:
                    lightProcess.terminate()
                
                write_read('n')

                if not DEBUG_LIGHTS:
                    # reset_blue
                    subprocess.Popen(['python', '../bulb/blue.py']) # run once
                
                time.sleep(5)
                return
                            
        # lightProcess.terminate()
        return
    
    elif add == 1: 
        print("Number already stored at uid: ", uid)
        if not DEBUG_AUDIO:
            audioProcess = subprocess.Popen(['python', 'play-audio.py'])
        
        # lightProcess = subprocess.Popen(['python', '../../govee-btled-controller/descent_reidVersion.py'])
        
        if not DEBUG_PHONECALL:
            handle = fishPhoneCall(uid, firstTime.hour, firstTime.minute, firstTime.second)
        
        if handle == 'END':
            if not DEBUG_AUDIO:
                audioProcess.terminate()

            if not DEBUG_LIGHTS:
                lightProcess.terminate()

            write_read('n') # signal arduino

            if not DEBUG_LIGHTS:
                # reset_blue
                subprocess.Popen(['python', '../bulb/blue.py']) # run once

        elif handle == 'CALLED':
            if not DEBUG_PHONECALL:
                handle = fishPhoneCall(uid, endTime.hour, endTime.minute, endTime.second)
            
            # subprocess.Popen(['python', 'afterCalls.py'])
            
            if handle == 'END':
                if not DEBUG_AUDIO:
                    audioProcess.terminate()

                if not DEBUG_LIGHT:
                    lightProcess.terminate()

                write_read('n')

                if not DEBUG_LIGHTS:
                    # reset_blue
                    subprocess.Popen(['python', '../bulb/blue.py']) # run once

        # lightProcess.terminate()
        return
    
    elif add == 2: 
        print("Invalid Phone Number")
        return


filename = 'numbers.json'
dictObj = []

with open(filename) as fp:
    listObj = json.load(fp)

# camera = subprocess.Popen(['python', 'camera-views.py'], start_new_session=True)

print("Enter Phone # \n")
write_read('w')
inNum = takeNum()

if not DEBUG_STORAGE:
    addNum(inNum)
    
write_read('n')
print("Fish Phone Booth Completed")