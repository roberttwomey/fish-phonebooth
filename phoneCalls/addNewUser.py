import json
import datetime
from os import path
from time import sleep

import serial

from makeCalls import fishPhoneCall

inNum = '0'
firstCallDelay = 181
endCallDelay = 401

def readserial(comport, baudrate):

    ser = serial.Serial(comport, baudrate, timeout=0.1)         # 1/timeout is the frequency at which the port is read

    while True:
        data = ser.readline().decode().strip()
        if data:
            inNum = data
            print(inNum)
            # time.sleep(500)
            return inNum

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
        fishPhoneCall(uid, firstTime.hour, firstTime.minute, firstTime.second)
        fishPhoneCall(uid, endTime.hour, endTime.minute, endTime.second)

        return
    
    elif add == 1: 
        print("Number already stored at uid: ", uid)
        fishPhoneCall(uid, firstTime.hour, firstTime.minute, firstTime.second)
        fishPhoneCall(uid, endTime.hour, endTime.minute, endTime.second)

        return
    
    elif add == 2: 
        print("Invalid Phone Number")
        return



filename = 'numbers.json'
dictObj = []

with open(filename) as fp:
    listObj = json.load(fp)

# print(listObj)
# print(type(listObj))
#numbers = ["phoneNum" for each in ]
    


#print("phone number of user 0 is ", listObj[0]['phoneNum'])
# inNum = input("Enter Phone Number: \n+1")

if __name__ == '__main__':

    while True:
        print("Enter Phone # \n")
        inNum = readserial('/dev/cu.usbmodem142301', 9600)
        addNum(inNum)
 

 
