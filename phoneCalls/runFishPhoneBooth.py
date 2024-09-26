#!/opt/homebrew/anaconda3/envs/fishphone/bin/python
import subprocess
import os
from subprocess import check_call
import serial
import pyautogui
import time
import os
from os import path
from dotenv import load_dotenv

ran= False
oc = ""

# load variables from .env file: 
load_dotenv()

USB_ONAIR = os.getenv('USB_ONAIR')
USB_KEYPAD = os.getenv('USB_KEYPAD')

arduinoDoor = serial.Serial(port=USB_ONAIR, baudrate=115200, timeout=.1) 
arduino = serial.Serial(port=USB_KEYPAD, baudrate=9600, timeout=.1) 

THIS_PYTHON = '/opt/homebrew/anaconda3/envs/fishphone/bin/python'

#arduinoScreen = serial.Serial(port='/dev/cu.usbmodem143401', baudrate=9600, timeout=.1) 
def write_read():
    #arduinoDoor.write(bytes(x,   'utf-8'))
    #time.sleep(0.05)
    global oc
	
    while True:

        data = arduinoDoor.readline().decode('ascii').strip()
		#print(data)

        if data == "open":
            oc = "open"
            return oc
        elif data == "closed":
            oc = "closed"
            return oc
	

camera = subprocess.Popen([THIS_PYTHON, 'camera-views.py'])
                     

while True:

	door = write_read()
	
	if ran == False and door == "closed":
		print(door)
		time.sleep(3)
		print("waited 3 seconds")
		door = write_read()
		print(door)

		if door == "closed":
			# p = subprocess.Popen(['python', 'phoneBoothMain.py'])
			p = subprocess.Popen([THIS_PYTHON, 'phoneBoothMain.py'])
			# p = subprocess.Popen(['phoneBoothMain.py'])
            
			#os.system("python phoneBoothMain.py")
			#time.sleep(10)
			# pyautogui.press('`')
			ran = True

	elif ran == True and door == "open":
            
		print(door)
		time.sleep(5)
            
		door = write_read()
		if door == "open":
			pyautogui.press('`')
			ran = False

	#if k == "l":
		# check_call(["pkill", "-f", "phoneBoothMain.py"])
		#pyautogui.press("num1")
		

