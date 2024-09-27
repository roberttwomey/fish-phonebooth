#!/opt/homebrew/anaconda3/envs/fishphone/bin/python
import json
import datetime
import subprocess
import os
from time import sleep
import serial
import time
import sys
# camera imports
import numpy as np
import cv2
from collections import deque

from dotenv import load_dotenv
from makeCalls import fishPhoneCall

from vision import VisionSystem

firstCallDelay = 191#181 # call delay in seconds
endCallDelay =  650#401 # call delay in seconds

DEBUG_ARDUINO = True
DEBUG_PHONECALL = True
DEBUG_AUDIO = False
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


if not DEBUG_LIGHTS:
	# reset_blue
	subprocess.Popen(['python', '../bulb/blue.py']) # run once

#write_read('w')

CLOSED = 0
OPEN = 1

class PhoneBooth(): 

	def __init__(self):
		# handle phone stuff
		self.filename = 'numbers.json'
		self.listObj = []
		self.number = ''
		self.value = ''
		self.doorState = OPEN

		self.setup()

		self.audioProcess = None
		self.lightProcess = None

	def setup(self):
		with open(self.filename) as fp:
			self.listObj = json.load(fp)

	def reset(self):
		if self.audioProcess:
			self.audioProcess.terminate()
		if self.lightProcess:
			self.lightProcess.terminate()
		self.write_read('n') # turn off "On Air" light
		self.number = ''
		self.value = ''

	def write_read(self, x):
		data = x
	
		if data == 'n' or data == '~':
			if not DEBUG_ARDUINO: 
				arduinoDoor.write(bytes(x, 'utf-8'))
			print(data+" --> door arduino")

		if not DEBUG_ARDUINO: 
			arduinoScreen.write(bytes(x, 'utf-8'))
		print(data+" --> screen arduino")

		return data
	
	def update_doorstate(self):
		if not DEBUG_ARDUINO:
			data = arduinoDoor.readline().decode('ascii').strip()
			if data == "open":
				self.doorState = OPEN
				print("open")
			elif data == "closed":
				self.doorState = CLOSED
				print("closed")

	def storeNum(self):

		handle = None

		time = datetime.datetime.now()
		firstTime = time + datetime.timedelta(seconds=firstCallDelay)
		endTime = time + datetime.timedelta(seconds=endCallDelay)
		
		# Makes uid be the next possible number
		uid = len(self.listObj)

		#Test if number is valid
		if len(self.number) == 10:
			formNum = '+1' + self.number
			add = 0
			i = 0
			# Test if number is already stored
			for num in self.listObj:
				if formNum == num['phoneNum']:
					uid = i
					add = 1
				i += 1
		else:
			add = 2

		#add if valid and new
		if add == 0:
			self.listObj.append({"uid": uid, 'phoneNum': formNum, 'startTime': time.strftime("%c")})
			
			if not DEBUG_STORAGE:
				with open(filename, 'w') as json_file:
					json.dump(self.listObj, json_file, 
						indent=4,  
						separators=(',',': '))
			
			print("added ", listObj[uid])
			if not DEBUG_AUDIO:
				self.audioProcess = subprocess.Popen(['python', 'play-audio.py'])
				
			if not DEBUG_LIGHTS:
				self.lightProcess = subprocess.Popen(['python', '../bulb/descent_reidVersion.py'])
			
			if not DEBUG_PHONECALL:
				handle = fishPhoneCall(uid, firstTime.hour, firstTime.minute, firstTime.second)
			
			if handle == 'END':
					
				# this cycle of phone call is done
				
				if not DEBUG_AUDIO:
					self.audioProcess.terminate()
				if not DEBUG_LIGHTS:
					self.lightProcess.terminate()
				
				self.write_read('n')
				
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
						self.audioProcess.terminate()
					if not DEBUG_LIGHTS:
						self.lightProcess.terminate()
					
					self.write_read('n')

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
				self.audioProcess = subprocess.Popen(['python', 'play-audio.py'])
			
			# lightProcess = subprocess.Popen(['python', '../../govee-btled-controller/descent_reidVersion.py'])
			
			if not DEBUG_PHONECALL:
				handle = fishPhoneCall(uid, firstTime.hour, firstTime.minute, firstTime.second)
			
			if handle == 'END':
				if not DEBUG_AUDIO:
					self.audioProcess.terminate()

				if not DEBUG_LIGHTS:
					self.lightProcess.terminate()

				self.write_read('n') # signal arduino

				if not DEBUG_LIGHTS:
					# reset_blue
					subprocess.Popen(['python', '../bulb/blue.py']) # run once

			elif handle == 'CALLED':
				if not DEBUG_PHONECALL:
					handle = fishPhoneCall(uid, endTime.hour, endTime.minute, endTime.second)
				
				# subprocess.Popen(['python', 'afterCalls.py'])
				
				if handle == 'END':
					if not DEBUG_AUDIO:
						self.audioProcess.terminate()

					if not DEBUG_LIGHT:
						self.lightProcess.terminate()

					self.write_read('n')

					if not DEBUG_LIGHTS:
						# reset_blue
						subprocess.Popen(['python', '../bulb/blue.py']) # run once

			# lightProcess.terminate()
			return
		
		elif add == 2: 
			print("Invalid Phone Number")
			return

	def takeNum(self, key_char):
		c = key_char
		
		if key_char:
			c_ord = ord(c)
			if len(self.number) < 10:    
				if c == '0':
					self.value = self.write_read('0') 
					self.number = self.number + self.value
				if c == '1':
					self.value = self.write_read('1') 
					self.number = self.number + self.value
				if c == '2':
					self.value = self.write_read('2') 
					self.number = self.number + self.value
				if c == '3':
					self.value = self.write_read('3') 
					self.number = self.number + self.value
				if c == '4':
					self.value = self.write_read('4') 
					self.number = self.number + self.value
				if c == '5':
					self.value = self.write_read('5') 
					self.number = self.number + self.value
				if c == '6':
					self.value = self.write_read('6') 
					self.number = self.number + self.value
				if c == '7':
					self.value = self.write_read('7') 
					self.number = self.number + self.value
				if c == '8':
					self.value = self.write_read('8') 
					self.number = self.number + self.value
				if c == '9':
					self.value = self.write_read('9') 
					self.number = self.number + self.value
				if c_ord == 127:
					# BACKSPACE
					self.value = self.write_read('*') 
					self.number = self.number[:-1]
				if c_ord == 144:
					# num lock keycode https://www.foreui.com/articles/Key_Code_Table.htm
					self.value = self.write_read('n') 
					self.number = 'END'
					return True
				if c == '`':
					self.value = self.write_read('n') 
					self.number = 'END'
					return True
				print(self.number, c_ord)
			
			if len(self.number) == 10:
				print("reached 10")
				if c_ord == 13:
					# ENTER key in OpenCV is 13
					self.write_read('~')
					print("...completed number entry")
					sys.stdout.flush()
					return True
				if c_ord == 127:
					# backspace
					self.value = self.write_read('*') 
					self.number = self.number[:-1]
				print(self.number, c_ord)
			
			return False



if __name__ == '__main__':

	booth = PhoneBooth()

	vision = VisionSystem()
	vision.start()

	last_key = None
	new_key = None
	timeLastKey = 0

	isRunning = False
	lastDoorState = OPEN
	timeLastChanged = 0

	while(1):
		vision.update()
		booth.update_doorstate()

		k = cv2.pollKey()
		if k == 27:
		   break
		elif k == ord('r'):
			vision.reset()
		elif k == ord('o'):
			if DEBUG_ARDUINO:
				booth.doorState = OPEN
				print("open")
		elif k == ord('c'):
			if DEBUG_ARDUINO:
				booth.doorState = CLOSED
				print("closed")
		else:
			if k != -1:  
				# If a key is pressed
				# Convert the ASCII value to a character
				if k != lastKey:
					lastKey = k
					print(f"Key pressed: {k}")
					lastKeyTime = time.time()
					new_key = chr(k)
			else:
				# print(".")
				lastKey = None	
				new_key = None

		if not isRunning:
			if booth.doorState == CLOSED:
				if lastDoorState == OPEN: 
					timeLastChanged = time.time()
					lastDoorState = CLOSED
				else:
					if time.time() - timeLastChanged > 3:
						# it's been closed for more than three seconds
						print("has been closed for more than three seconds")
						isRunning = True
						print("Enter Phone # \n")
						booth.write_read('w')
		else:
			if booth.doorState == OPEN:
				if lastDoorState == CLOSED:
					timeLastChanged = time.time()
					lastDoorState == OPEN
				else:
					if time.time() - timeLastChanged > 5:
						# it was running but door has been open for more than five seconds
						isRunning = False
						print("... resetting ...")
						booth.reset()

		if isRunning and new_key:
			if booth.takeNum(new_key):
				booth.storeNum()
				
				booth.write_read('n')
				print("Fish Phone Booth Completed")
				
				print("... resetting ...")
				booth.reset()

				print("Enter Phone # \n")
				booth.write_read('w')

			keyIsNew = False

	print("vision is done. ")
	# print "freeing resources"
	
	booth.reset()
	vision.cleanup()