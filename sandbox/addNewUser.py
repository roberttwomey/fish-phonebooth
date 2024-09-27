import json
import datetime
from os import path

filename = 'numbers.json'
dictObj = []

with open(filename) as fp:
    listObj = json.load(fp)

# print(listObj)
# print(type(listObj))
#numbers = ["phoneNum" for each in ]
    
# Makes uid be the next possible number
uid = len(listObj)

#print("phone number of user 0 is ", listObj[0]['phoneNum'])
inNum = input("Enter Phone Number: \n+1")

# Stores the current time
time = datetime.datetime.now()

#Test if number is valid
if len(inNum) == 10:
    formNum = '+1' + inNum
    add = 0
    
    # Test if number is already stored
    for num in listObj:
        if formNum == num['phoneNum']:
            add = 1
else:
    add = 2

#add if valid and new
if add == 0:
    listObj.append({"uid": uid, 'phoneNum': formNum, 'startTime': time.strftime("%c")})
    print("added ", listObj[uid])
    with open(filename, 'w') as json_file:
        json.dump(listObj, json_file, 
                            indent=4,  
                            separators=(',',': '))
elif add == 1: 
    print("Number already stored")
elif add == 2: 
    print("Invalid Phone Number")

#print("added ", listObj[uid])
 

 
