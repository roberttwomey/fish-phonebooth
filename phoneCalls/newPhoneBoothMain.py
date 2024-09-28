#!/opt/homebrew/anaconda3/envs/fishphone/bin/python
import json
import datetime
import subprocess
import os
from time import sleep
import serial
import time
import sys

import numpy as np
import cv2

from makeCalls import updateFishPhoneCall
from vision import VisionSystem
from dotenv import load_dotenv

# load variables from .env file: 
load_dotenv()

# FIRST_CALL_DELAY = 191#181 # call delay in seconds
# END_CALL_DELAY =  650#401 # call delay in seconds

FIRST_CALL_DELAY = int(os.getenv('FIRST_CALL_DELAY'))
END_CALL_DELAY =  int(os.getenv('END_CALL_DELAY'))

DEBUG_ARDUINO = os.getenv('DEBUG_ARDUINO') == 'True'
DEBUG_PHONECALL = os.getenv('DEBUG_PHONECALL') == 'True'
DEBUG_AUDIO = os.getenv('DEBUG_AUDIO') == 'True'
DEBUG_LIGHTS = os.getenv('DEBUG_LIGHTS') == 'True'
DEBUG_STORAGE = os.getenv('DEBUG_STORAGE') == 'True'

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

# door state
CLOSED = 0
OPEN = 1

# phone number
NEW = 0
EXISTS = 1
INVALID = 3

# program state
WAITING_TO_START = 0
KEYBOARD_ENTRY = 1
RUNNING_PROGRAM = 2
DONE = 3

class PhoneBooth(): 

	def __init__(self):
		# handle phone stuff
		self.filename = 'numbers.json'
		self.listObj = []
		self.number = ''
		self.value = ''
		self.doorState = CLOSED #OPEN

		self.setup()

		self.audioProcess = None
		self.lightProcess = None

		self.runKeyboardInput = False
		self.runProgram = False
		self.isDone = False

		# phone number
		self.numberState = None
		self.uid = None
		
		# phone calls
		self.firstTime = None
		self.endTime = None
		self.firstCalled = False
		self.endCalled = False
		self.waitingToCall = False


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

		self.uid = None
		self.numberState = None
		self.handle = None
		self.firstTime = None
		self.endTime = None

		self.called = False
		self.waiting = False

		self.boothState = WAITING_TO_START
		self.runProgram = False
		self.runKeyboardInput = False
		self.isDone = False


	def write_read(self, x):
		data = x
	
		if data == 'n' or data == '~':
			if not DEBUG_ARDUINO: 
				arduinoDoor.write(bytes(x, 'utf-8'))
			else:
				print(data+" --> door arduino")

		if not DEBUG_ARDUINO: 
			arduinoScreen.write(bytes(x, 'utf-8'))
		else:
			print(data+" --> screen arduino")

		return data
	
	def update_doorstate(self):
		if not DEBUG_ARDUINO:
			arduinoDoor.write(bytes('?', 'utf-8'))
			data = arduinoDoor.readline().decode('ascii').strip()
			if data == "o":
				self.doorState = OPEN
				# print("open")
			elif data == "c":
				self.doorState = CLOSED
				# print("closed")

	def storeNum(self):
		self.handle = None

		time = datetime.datetime.now()
		self.firstTime = time + datetime.timedelta(seconds=FIRST_CALL_DELAY) # first phone call, mid-experience
		self.endTime = time + datetime.timedelta(seconds=END_CALL_DELAY) # second phone call, end of experience
		
		# Makes uid be the next possible number
		self.uid = len(self.listObj)

		#Test if number is valid
		if len(self.number) == 10:
			formNum = '+1' + self.number
			self.numberState = NEW
			i = 0
			# Test if number is already stored
			for num in self.listObj:
				if formNum == num['phoneNum']:
					self.uid = i
					self.numberState = EXISTS
				i += 1
		else:
			self.numberState = INVALID

		#add if valid and new
		if self.numberState == NEW:
			self.listObj.append({"uid": self.uid, 'phoneNum': formNum, 'startTime': time.strftime("%c")})
			
			if not DEBUG_STORAGE:
				with open(filename, 'w') as json_file:
					json.dump(self.listObj, json_file, 
						indent=4,  
						separators=(',',': '))
			
			print("added new number", self.listObj[uid])

			if not DEBUG_AUDIO:
				self.audioProcess = subprocess.Popen(['python', 'play-audio.py'])
				
			if not DEBUG_LIGHTS:
				self.lightProcess = subprocess.Popen(['python', '../bulb/descent_reidVersion.py'])
			
			# if not DEBUG_PHONECALL:
			# 	handle = fishPhoneCall(self.uid, self.firstTime.hour, self.firstTime.minute, self.firstTime.second)
			
			# if handle == 'END':
					
			# 	# this cycle of phone call is done
				
			# 	if not DEBUG_AUDIO:
			# 		self.audioProcess.terminate()
			# 	if not DEBUG_LIGHTS:
			# 		self.lightProcess.terminate()
				
			# 	self.write_read('n')
				
			# 	if not DEBUG_LIGHTS:
			# 		# reset_blue
			# 		subprocess.Popen(['python', '../bulb/blue.py']) # run once
				
			# 	time.sleep(5)
			# 	return

			# elif handle == 'CALLED':
			# 	if not DEBUG_PHONECALL:
			# 		handle = fishPhoneCall(uid, endTime.hour, endTime.minute, endTime.second)
				
				# subprocess.Popen(['python', 'afterCalls.py'])
				
				# if handle == 'END':
				# 	if not DEBUG_AUDIO:
				# 		self.audioProcess.terminate()
				# 	if not DEBUG_LIGHTS:
				# 		self.lightProcess.terminate()
					
				# 	self.write_read('n')

				# 	if not DEBUG_LIGHTS:
				# 		# reset_blue
				# 		subprocess.Popen(['python', '../bulb/blue.py']) # run once
					
				# 	time.sleep(5)
				# 	return
								
			# lightProcess.terminate()
			return
		
		elif self.numberState == EXISTS: 
			print("Number already stored at uid: ", self.uid)
			if not DEBUG_AUDIO:
				self.audioProcess = subprocess.Popen(['python', 'play-audio.py'])
			
			# lightProcess = subprocess.Popen(['python', '../../govee-btled-controller/descent_reidVersion.py'])
			
			# if not DEBUG_PHONECALL:
			# 	handle = fishPhoneCall(uid, firstTime.hour, firstTime.minute, firstTime.second)
			
			# if handle == 'END':
			# 	if not DEBUG_AUDIO:
			# 		self.audioProcess.terminate()

			# 	if not DEBUG_LIGHTS:
			# 		self.lightProcess.terminate()

			# 	self.write_read('n') # signal arduino

			# 	if not DEBUG_LIGHTS:
			# 		# reset_blue
			# 		subprocess.Popen(['python', '../bulb/blue.py']) # run once

			# elif handle == 'CALLED':
			# 	if not DEBUG_PHONECALL:
			# 		handle = fishPhoneCall(uid, endTime.hour, endTime.minute, endTime.second)
				
			# 	# subprocess.Popen(['python', 'afterCalls.py'])
				
			# 	if handle == 'END':
			# 		if not DEBUG_AUDIO:
			# 			self.audioProcess.terminate()

			# 		if not DEBUG_LIGHT:
			# 			self.lightProcess.terminate()

			# 		self.write_read('n')

			# 		if not DEBUG_LIGHTS:
			# 			# reset_blue
			# 			subprocess.Popen(['python', '../bulb/blue.py']) # run once

			# # lightProcess.terminate()
			# return
		
		elif self.numberState == INVALID: 
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
				if c_ord == 13 or c_ord == 3:
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

	lastDoorState = OPEN
	timeDoorLastChanged = 0
	booth.reset()

	try:
		while(1):
			# Update Cameras
			vision.update()

			# Poll keboard inputs
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

			# Poll door sensor
			booth.update_doorstate()

			# Handle main functionality
			if booth.boothState == WAITING_TO_START:
				if booth.doorState == CLOSED:
					# door is now closed
					if lastDoorState == OPEN: 
						# just closed
						timeDoorLastChanged = time.time()
						lastDoorState = CLOSED
					else:
						if time.time() - timeDoorLastChanged > 3:
							# it's been closed for more than three seconds
							print("Door has been closed for more than three seconds... starting.")
							booth.boothState = KEYBOARD_ENTRY
							print("Enter Phone # \n")
							booth.write_read('w')
			
			if booth.boothState == KEYBOARD_ENTRY and new_key:
				if booth.takeNum(new_key):
					booth.storeNum()
					booth.boothState = RUNNING_PROGRAM
				keyIsNew = False

			# check for door open during program execution
			if booth.boothState == RUNNING_PROGRAM:
				# door is now open
				if booth.doorState == OPEN:
					if lastDoorState == CLOSED:
						timeDoorLastChanged = time.time()
						lastDoorState = OPEN
					else:
						if time.time() - timeDoorLastChanged > 5:
							# it was running but door has been open for more than five seconds
							# reset
							booth.boothState = WAITING_TO_START
							print("... was running but door has been open for 5 secs... resetting.")
							booth.reset()

			if booth.boothState == RUNNING_PROGRAM:
				if not booth.firstCalled:
					# continue audio
					# continue lights
					result = updateFishPhoneCall(booth.uid, booth.firstTime.hour, booth.firstTime.minute, booth.firstTime.second)
					if result == 'WAITING' and not booth.waitingToCall:
						booth.waitingToCall = True
						print("waiting until", booth.firstTime.hour, ":", booth.firstTime.minute, ":", booth.firstTime.second, "to call\n")
					if result == 'CALLED':
						booth.firstCalled = True
						booth.waitingToCall = True
						print("finished first call")
				else: 
					result = updateFishPhoneCall(booth.uid, booth.endTime.hour, booth.endTime.minute, booth.endTime.second)
					if result == 'WAITING' and not booth.waitingToCall:
						booth.waitingToCall = True
						print("waiting until", booth.endTime.hour, ":", booth.endTime.minute, ":", booth.endTime.second, "to call\n")
					if result == 'CALLED':
						booth.endCalled = True
						booth.waitingToCall = False
						print("finished end call. Cycle is done.")
						booth.boothState = DONE

			if booth.boothState == DONE: 
				booth.write_read('n')
				print("Fish Phone Booth Completed")
				
				print("... resetting ...")
				booth.reset()

				booth.boothState = WAITING_TO_START

	except KeyboardInterrupt:
		print('Interrupted... quitting')

	print("Booth cleanup")
	booth.reset()
	print("Vision Cleanup")
	vision.cleanup()