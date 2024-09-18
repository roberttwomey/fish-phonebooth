import subprocess
import os
from subprocess import check_call
import serial
import pyautogui
import time
ran= False
oc = ""

arduinoDoor = serial.Serial(port='/dev/cu.usbmodem143301', baudrate=115200, timeout=.1) 
#arduinoScreen = serial.Serial(port='/dev/cu.usbmodem143401', baudrate=9600, timeout=.1) 
def write_read():
    #arduinoDoor.write(bytes(x,   'utf-8'))
    #time.sleep(0.05)
    global oc
    data = arduinoDoor.readline().decode('ascii').strip()
    #print(data)

    if data == "open":
        oc = "open"
    elif data == "closed":
        oc = "closed"
    return oc
	


while True:

	door = write_read()
	
	if ran == False and door == "closed":
		print(door)
		time.sleep(3)
		p = subprocess.Popen(['python', 'phoneBoothMain.py'])
		#os.system("python phoneBoothMain.py")
		#time.sleep(10)
		# pyautogui.press('`')
		ran = True

	elif ran == True and door == "open":
            
		print(door)
		#time.sleep(3)
		pyautogui.press('`')
		ran = False

	#if k == "l":
		# check_call(["pkill", "-f", "phoneBoothMain.py"])
		#pyautogui.press("num1")
		

