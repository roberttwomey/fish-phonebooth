import json
import datetime
import subprocess
from os import path
from time import sleep

# from numInput import takeNum

import pygame
# import keyboard  # using module keyboard
import serial
import time
# importing sys module
import sys
# import serial

from makeCalls import fishPhoneCall

inNum = '0'
firstCallDelay = 191#181 # call delay in seconds
endCallDelay =  650#401 # call delay in seconds


arduino = serial.Serial(port='/dev/cu.usbmodem143401', baudrate=9600, timeout=.1) 
airduino = serial.Serial(port='/dev/cu.usbmodem143301', baudrate=115200, timeout=.1) 

pygame.init()

    # creating display
display = pygame.display.set_mode((300, 300))

def write_read(x): 
    arduino.write(bytes(x, 'utf-8'))
    data = x
    if data == 'n':
        airduino.write(bytes(x, 'utf-8'))
    elif data == '~':
        airduino.write(bytes(x, 'utf-8'))
    print(data)
    return data
	
subprocess.Popen(['python', '../../govee-btled-controller/blue.py'])
#write_read('w')

def takeNum():
    
    number = ''
    value = ''

    while True:
        
        # creating a loop to check events that 
        # are occurring
        for event in pygame.event.get():
            
                # checking if keydown event happened or not
            if event.type == pygame.KEYDOWN:
                if len(number) < 10:    
                    # checking if key was pressed
                    if event.key == pygame.K_KP0:
                        value = write_read('0') 
                        number = number + value
                    if event.key == pygame.K_KP1:
                        value = write_read('1') 
                        number = number + value
                    if event.key == pygame.K_KP2:
                        value = write_read('2') 
                        number = number + value
                    if event.key == pygame.K_KP3:
                        value = write_read('3') 
                        number = number + value
                    if event.key == pygame.K_KP4:
                        value = write_read('4') 
                        number = number + value
                    if event.key == pygame.K_KP5:
                        value = write_read('5') 
                        number = number + value
                    if event.key == pygame.K_KP6:
                        value = write_read('6') 
                        number = number + value
                    if event.key == pygame.K_KP7:
                        value = write_read('7') 
                        number = number + value
                    if event.key == pygame.K_KP8:
                        value = write_read('8') 
                        number = number + value
                    if event.key == pygame.K_KP9:
                        value = write_read('9') 
                        number = number + value
                    if event.key == pygame.K_BACKSPACE:
                        value = write_read('*') 
                        number = number[:-1]
                    if event.key == pygame.K_NUMLOCK:
                        value = write_read('n') 
                        number = 'END'
                        return number
                    if event.key == pygame.K_BACKQUOTE:
                        value = write_read('n') 
                        number = 'END'
                        return number
                if len(number) == 10:
                    if event.key == pygame.K_KP_ENTER:
                        write_read('~')
                        return number
                    if event.key == pygame.K_BACKSPACE:
                        value = write_read('*') 
                        number = number[:-1]
# def readserial(comport, baudrate):

#     ser = serial.Serial(comport, baudrate, timeout=0.1)         # 1/timeout is the frequency at which the port is read

#     while True:
#         data = ser.readline().decode().strip()
#         if data:
#             inNum = data
#             print(inNum)
#             # time.sleep(500)
#             return inNum--


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
        audioProcess = subprocess.Popen(['python', 'play-audio.py'])
        
        lightProcess = subprocess.Popen(['python', '../../govee-btled-controller/descent_reidVersion.py'])
        handle = fishPhoneCall(uid, firstTime.hour, firstTime.minute, firstTime.second)
        
        if handle == 'END':
            audioProcess.terminate()
            lightProcess.terminate()
            write_read('n')
            subprocess.Popen(['python', '../../govee-btled-controller/blue.py'])
            time.sleep(5)
            #sys.exit()

            return

        elif handle == 'CALLED':
            handle = fishPhoneCall(uid, endTime.hour, endTime.minute, endTime.second)
            # subprocess.Popen(['python', 'afterCalls.py'])
            if handle == 'END':
                audioProcess.terminate()
                lightProcess.terminate()
                write_read('n')
                subprocess.Popen(['python', '../../govee-btled-controller/blue.py'])
                time.sleep(5)
                return
                #sys.exit()
        # lightProcess.terminate()
        return
    
    elif add == 1: 
        print("Number already stored at uid: ", uid)
        audioProcess = subprocess.Popen(['python', 'play-audio.py'])
        lightProcess = subprocess.Popen(['python', '../../govee-btled-controller/descent_reidVersion.py'])
        handle = fishPhoneCall(uid, firstTime.hour, firstTime.minute, firstTime.second)
        
        if handle == 'END':
            audioProcess.terminate()
            lightProcess.terminate()
            write_read('n')
            subprocess.Popen(['python', '../../govee-btled-controller/blue.py'])
        elif handle == 'CALLED':
            handle = fishPhoneCall(uid, endTime.hour, endTime.minute, endTime.second)
            # subprocess.Popen(['python', 'afterCalls.py'])
            if handle == 'END':
                audioProcess.terminate()
                lightProcess.terminate()
                write_read('n')
                subprocess.Popen(['python', '../../govee-btled-controller/blue.py'])
        # lightProcess.terminate()ß
        return
    
    elif add == 2: 
        print("Invalid Phone Number")
        return



filename = 'numbers.json'
dictObj = []

with open(filename) as fp:
    listObj = json.load(fp)


print("Enter Phone # \n")
write_read('w')
# inNum = readserial('/dev/cu.usbmodem142301', 9600)
inNum = takeNum()
addNum(inNum)
write_read('n')
print("Fish Phone Booth Completed")
# write_read('n')

# print(listObj)
# print(type(listObj))
#numbers = ["phoneNum" for each in ]
    


#print("phone number of user 0 is ", listObj[0]['phoneNum'])
# inNum = input("Enter Phone Number: \n+1")

# if __name__ == '__main__':

#     while True:
        
#         subprocess.Popen(['python', '../../govee-btled-controller/blue.py'])
#         print("Enter Phone # \n")
#         # inNum = readserial('/dev/cu.usbmodem142301', 9600)
#         inNum = takeNum()
#         addNum(inNum)
#         #write_read('n')
        
 

 
