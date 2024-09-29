#!/usr/bin/env python
'''
opencv code to:
- calculate and track movement in foreground
- display fisheye network cam with tracking + booth view IR cam
'''
import numpy as np
import cv2
import os
from dotenv import load_dotenv
import argparse
import sys
from collections import deque
import json

SHOW_TIMER_TEXT = True

# https://github.com/ContinuumIO/anaconda-issues/issues/223
# a better video write (alternative to opencv videowriter)
# https://github.com/scikit-video/scikit-video

def sort_by_area(cnts):
	# adapted from  https://github.com/kraib/open_cv_tuts/blob/master/sorting_contours.py

	# initialize the reverse flag and sort index
	i = 0
	reverse = True

	areas = [cv2.contourArea(c) for c in cnts]
	(cnts, areas) = zip(*sorted(zip(cnts, areas),
		key=lambda b:b[1], reverse=reverse))

	# return the list of sorted contours and areas
	return (cnts, areas)


def resize_to_bounding_box(image, box_width, box_height):
	# Get the original dimensions of the image
	original_height, original_width = image.shape[:2]

	# Calculate aspect ratios
	aspect_ratio_image = original_width / original_height
	aspect_ratio_box = box_width / box_height

	# Determine new dimensions
	if aspect_ratio_image > aspect_ratio_box:
		# Image is wider than the box
		new_width = box_width
		new_height = int(box_width / aspect_ratio_image)
	else:
		# Image is taller than the box
		new_height = box_height
		new_width = int(box_height * aspect_ratio_image)

	# Resize the image
	resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

	return resized_image

def crop_to_center_square(image):
	# Get the original dimensions of the image
	height, width = image.shape[:2]

	# Determine the size of the square (smallest dimension)
	square_size = min(height, width)

	# Calculate the starting coordinates for the crop
	start_x = (width - square_size) // 2
	start_y = (height - square_size) // 2

	# Crop the image to a square
	cropped_image = image[start_y:start_y + square_size, start_x:start_x + square_size]

	return cropped_image

def center_crop(image, target_height, target_width):
	# Get the original dimensions of the image
	height, width = image.shape[:2]

	# Calculate the starting coordinates for the crop
	start_x = (width - target_width) // 2
	start_y = (height - target_height) // 2

	# Ensure the crop dimensions fit within the original image
	start_x = max(0, start_x)
	start_y = max(0, start_y)

	# Crop the image
	cropped_image = image[start_y:start_y + target_height, start_x:start_x + target_width]

	return cropped_image

def translate_image(image, xoffset, yoffset):
		# shift image to the left
		M = np.float32([[1, 0, xoffset], [0, 1, yoffset]])
		
		# Perform the translation
		translated_image = cv2.warpAffine(
			image, 
			M, 
			(image.shape[1], image.shape[0])
		)

		return translated_image

def format_time_hundredths(seconds):
    # Calculate minutes, whole seconds, and hundredths of a second
    minutes = int(seconds // 60)
    seconds_whole = int(seconds % 60)
    hundredths = int((seconds - int(seconds)) * 100)

    # Format as "minutes seconds hundredths"
    formatted_time = f"{int(minutes):02}:{int(seconds_whole):02}.{hundredths:02}"
    return formatted_time

def format_time_seconds(seconds):
    # Calculate minutes, whole seconds, and hundredths of a second
    minutes = int(seconds // 60)
    seconds_whole = int(seconds % 60)

    # Format as "minutes seconds hundredths"
    formatted_time = f"{int(minutes):02}:{int(seconds_whole):02}"
    return formatted_time

VIDEO_FILE = "/Volumes/Work/Projects/housemachine/data/ceiling/livingroom/livingroom_motion_2017-08-13_20.17.02_27.mp4"
NETWORK_CAMERA = "rtsp://admin:CameraRed@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0"

class VisionSystem:
	def __init__(self):
		'''
		Creates a CameraDisplay object that will process incoming frames and 
		'''
		
		self.doWrite = False
		self.doHeadless = False
		self.doUndistort = False

		self.minBlobSize = 600.0
		self.maxBlobSize = 50000.0
		self.searchRadius = 70.0

		self.maxNumTrails = 50

		self.showMask = False
		self.fullResolution = True

		self.outputsize = 800

		self.targetWidth = 1280
		self.targetHeight = 800

		load_dotenv()
		self.CAM1 = os.getenv('CAM1')
		self.CAM2 = os.getenv('CAM2')

	def start(self):
		# set up the various parts of the background and video
		self.setup_video()
		self.setup_gui()
		self.setup_cv()

	def setup_video(self):
		# set up overhead capture
		# self.cap1 = cv2.VideoCapture(VIDEO_FILE)
		self.cap1 = cv2.VideoCapture(self.CAM1)
		self.cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 1440)
		self.cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
		self.cap1.set(cv2.CAP_PROP_FPS, 15)

		if self.cap1 is None:
			print("Couldn't open overhead camera")
			exit(0)

		# configure size and buffers
		self.width = self.cap1.get(3)
		self.height = self.cap1.get(4)

		# booth camera
		self.cap2 = cv2.VideoCapture(int(self.CAM2))#self.CAM2) # booth cam is device 0
		if self.cap2 is None:
			print("Couldn't open frontal camera")
			exit(0)
		
		# proportionally scaled to match fit within 
		self.outheight = self.outputsize
		self.scalef = float(self.outputsize)/float(self.height)
		self.outwidth = int(self.scalef*self.width)
	
		# create mask to mask aroud circular fisheye frame
		self.circlemask = np.zeros((self.outheight, self.outwidth), np.uint8)
		cv2.circle(self.circlemask, (int(self.outwidth/2), int(self.outheight/2)), int(self.outputsize*0.45), (255, 255, 255), -1)

	def setup_recording(self):
		print("recording / file output not yet implemented")
		# don't need video output for now
		return

	def setup_gui(self):
		# Create a named window
		cv2.namedWindow('tracking', cv2.WND_PROP_FULLSCREEN)

		# Set the window to fullscreen
		cv2.setWindowProperty('tracking', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
		# cv2.namedWindow('fgmask', cv2.WINDOW_NORMAL)
		# cv2.namedWindow('fgbg', cv2.WINDOW_NORMAL)

	def setup_cv(self):
		# setup background detector
		# http://docs.opencv.org/3.2.0/d2/d55/group__bgsegm.html

		# fgbg = cv2.bgsegm.createBackgroundSubtractorMOG(backgroundRatio=0.7)
		# fgbg = cv2.bgsegm.createBackgroundSubtractorMOG(backgroundRatio=0.3)
		# fgbg = cv2.bgsegm.createBackgroundSubtractorGMG(initializationFrames = 50)#30)
		# fgbg = cv2.bgsegm.createBackgroundSubtractorGMG()

		# history = 50
		# fgbg = cv2.createBackgroundSubtractorMOG2(history = history, detectShadows=True)
		self.fgbg = cv2.createBackgroundSubtractorKNN(detectShadows = True) # default history 500 frames
		
		# stores motion trails
		self.trails = []

	def update(self, time_left=-1):
		ret, frame = self.cap1.read()

		if not ret:
			print('looping at end of video')
			self.cap1.set(cv2.CAP_PROP_POS_FRAMES, 0)
			ret, frame = self.cap1.read()

		if frame is None:
			return

		dataframe = cv2.resize(frame, (self.outwidth, self.outheight))

				# print "mask"
		maskedframe = cv2.bitwise_and(dataframe, dataframe, mask = self.circlemask)

		# frame = cv2.fisheye.undistortImage(frame, K, D=D, Knew=Knew)

		# ADVANCED BGSEGM METHODS
		fgmask = self.fgbg.apply(maskedframe)

		# print "threshold"
		ret, thresh = cv2.threshold(fgmask, 244, 255, cv2.THRESH_BINARY)

		if thresh is None:
			return

		# print "dilate"
		thresh = cv2.dilate(thresh, None, iterations=3)

		# print "find contours"
		cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

		if len(cnts) > 0:
			(newcnts, areas) = sort_by_area(cnts)

			for i in range(len(newcnts)):
				cnt = newcnts[i]
				area = areas[i]

				if area > self.minBlobSize and area < self.maxBlobSize:
					if self.fullResolution:
						largecnt = []
						for point in cnt:
							largepoint = point / self.scalef
							largecnt.append(largepoint)
						largecnt = np.array(largecnt)
						cnt = np.array(largecnt).reshape((-1,1,2)).astype(np.int32)
						cv2.drawContours(frame, [cnt], 0, (0, 255, 0), int(self.width/213))
						
					else:
						cv2.drawContours(frame, [cnt], 0, (0, 255, 0), 3)

					# perimeter = cv2.arcLength(cnt,True)

					M = cv2.moments(cnt.astype(np.float32))

					# center of mass
					cx = M['m10']/M['m00']
					cy = M['m01']/M['m00']

					center = (cx, cy)
					foundTrail = False

					for trail in self.trails:
						if len(trail) == 0:
							trail.appendleft(center)
							break

						dist = np.linalg.norm(np.array(trail[0])-np.array(center))

						if dist < self.searchRadius:
							trail.appendleft(center)
							foundTrail = True

					if not foundTrail:
						self.trails.append(deque(maxlen=10000))
						self.trails[-1].appendleft(center)
		
		masked = cv2.bitwise_and(dataframe, dataframe, mask=fgmask)

		while len(self.trails) > self.maxNumTrails:
			self.trails.pop(0)

		for pts in self.trails:
			for i in range(1, len(pts)-1):
				# if either of the tracked points are None, ignore them
				if pts[i - 1] is None or pts[i] is None:
					continue

				# otherwise, compute the thickness of the line and draw the connecting lines
				thickness = 3
				
				if self.fullResolution:
					# full size
					cv2.line(frame, (int(pts[i-1][0]), int(pts[i-1][1])), (int(pts[i][0]), int(pts[i][1])), (0, 0, 255), thickness, cv2.LINE_AA)
				else:
					# reduced size
					cv2.line(dataframe, (int(pts[i-1][0]), int(pts[i-1][1])), (int(pts[i][0]), int(pts[i][1])), (0, 0, 255), thickness, cv2.LINE_AA)
		
		# # make colored overlay
		# colthresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
		# cv2.addWeighted(colthresh, 0.5, frame, 0.5, 0.0, frame)

		# # make colored overlay
		if self.showMask:
			colthresh = cv2.cvtColor(self.circlemask, cv2.COLOR_GRAY2BGR)
			cv2.addWeighted(colthresh, 0.5, frame, 0.5, 0.0, frame)

		masked = cv2.resize(masked, (self.outwidth, self.outheight))
		thresh = cv2.resize(thresh, (self.outwidth, self.outheight))
		fgmask = cv2.resize(fgmask, (self.outwidth, self.outheight))
		
		if not self.fullResolution:
			frame = cv2.resize(frame, (self.outwidth, self.outheight))
			# Define the translation matrix

		frame2 = resize_to_bounding_box(frame, self.targetWidth, self.targetHeight)
		
		frame2 = crop_to_center_square(frame2)
		
		xoffset = self.targetWidth - frame2.shape[0]

		# pad the right side of the image to make it the right size
		frame2 = cv2.copyMakeBorder(
			frame2,
			0,
			0,
			0,
			xoffset,
			cv2.BORDER_CONSTANT,
			value=[0, 0, 0]  # Black color in BGR
		)
		
		# print(frame2.shape)
		ret, ir_frame =self.cap2.read()

		if ir_frame is not None:
			ir_frame = cv2.rotate(ir_frame, cv2.ROTATE_90_CLOCKWISE)
			ir_frame2 = resize_to_bounding_box(ir_frame, self.targetWidth, self.targetHeight)
			ir_frame2 = center_crop(ir_frame2, self.targetHeight, xoffset)

			# copy cam2 into right hand side of main feed
			frame2[:, -1*ir_frame2.shape[1]:] = ir_frame2[:,:]

		# show time left text
		if SHOW_TIMER_TEXT:
			if time_left < 0:
				# timer_text = format_time_hundredths(time_left)
				timer_text = "READY"
			else:
				timer_text = format_time_seconds(time_left)

			# Define text parameters
			font = cv2.FONT_HERSHEY_SIMPLEX
			font_scale = 2
			font_color = (0, 0, 255)  # White color
			thickness = 10
			# text_size = cv2.getTextSize(timer_text, font, font_scale, thickness)[0]
			text_size = cv2.getTextSize("READY", font, font_scale, thickness)[0]

			# Position the text at the bottom-right corner
			text_x = self.targetWidth - int(text_size[0]*0.5) - int(0.5*ir_frame2.shape[1]) #- 10
			text_y = self.targetHeight - text_size[1] - 20

			# Draw a black rectangle behind the text
			cv2.rectangle(frame2, 
						(text_x - 10, text_y - text_size[1] - 10),  # Top-left corner
						(text_x + text_size[0] + 5, text_y + 15),  # Bottom-right corner
						(0, 0, 0),  # Black color
						thickness=cv2.FILLED)  # Fill the rectangle
		
			# Add text to the image
			cv2.putText(frame2, timer_text, (text_x, text_y), font, font_scale, font_color, thickness)

		cv2.imshow('tracking',frame2)

		if self.doWrite:
			paths = []
			for trail in self.trails:			
				thistrail = []
				for i in xrange(1, len(trail)):
					# if either of the tracked points are None, ignore them
					thistrail.append((trail[i]))
				paths.append(thistrail)

			pathfile = os.path.splitext(outfile)[0]+".json"
			print("write trails",pathfile)
			with open(pathfile, 'w') as outfile:
				json.dump(paths, outfile, indent=2)


	def reset(self):
		self.trails.clear()

	def cleanup(self):
		self.cap1.release()

		if self.doWrite:
			self.out.release()

		cv2.destroyAllWindows()

if __name__ == '__main__':
	vision = VisionSystem()

	vision.start()

	while(1):
		vision.update()

		k = cv2.waitKey(1)
		if k == 27:
			break
		elif k == ord('r'):
			vision.reset()
			# fgbg.clear()
		else:
			if k != -1:  # If a key is pressed
				# Convert the ASCII value to a character
				char = chr(k)
				print(f'Pressed key: {char}')

	print("done. ")
	# print "freeing resources"

	vision.cleanup()



# if __name__ == '__main__':
# 	# global doWrite, infile, outpath
# 	# doWrite = False


# 	# parser = argparse.ArgumentParser(description='run background forground segmentation on input video',
# 	# 	formatter_class=argparse.ArgumentDefaultsHelpFormatter)

# 	# parser.add_argument('--write', default=False, dest='dowrite', action='store_true', help='save tracked image as new video')
# 	# parser.add_argument('--headless', default=False, dest='doheadless', action='store_true', help='do not display video on screen')
# 	# parser.add_argument('--undistort', default=False, dest='doundistort', action='store_true', help='undistort circular fisheye')
# 	# parser.add_argument('--minblob', default=600.0, type=float, help='minimum blob size to track')
# 	# parser.add_argument('--maxblob', default=12000.0, type=float, help='maximum blob size to track')
# 	# parser.add_argument('--radius', default=30.0, type=float, help='maximum radius from frame to frame blob track')
	
# 	# args = parser.parse_args()

# 	# runtime options
# 	doWrite = False #args.dowrite
# 	doHeadless = False #args.doheadless
# 	doUndistort = False #args.doundistort
# 	# minBlobSize = args.minblob
# 	# maxBlobSize = args.maxblob
# 	# searchRadius = args.radius
# 	minBlobSize = 600.0
# 	maxBlobSize = 50000.0
# 	searchRadius = 70.0
	
# 	MAX_LENGTH = 50#20

# 	showMask = False
# 	fullResolution = True
# 	# fullResolution = False
	
# 	# network fisheye camera
# 	# cap = cv2.VideoCapture("rtsp://admin:CameraRed@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0")
# 	cap = cv2.VideoCapture(VIDEO_FILE) # for testing

# 	# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2880)
# 	# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
# 	cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1440)
# 	cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
# 	cap.set(cv2.CAP_PROP_FPS, 15)
# 	# outputsize = 2160
# 	# outputsize = 1440
	
# 	outputsize = 800

# 	targetWidth = 1280
# 	targetHeight = 960

# 	# booth camera
# 	cap2 = cv2.VideoCapture(0) # booth cam is device 0

# 	if cap is None:
# 		print("didn't work")
# 		exit(0)

# 	width = cap.get(3)
# 	height = cap.get(4)

# 	# proportianlly scaled to match fit within 
# 	outheight = outputsize
# 	scalef = float(outputsize)/float(height)
# 	outwidth = int(scalef*width)
	
# 	# create mask to mask aroud circular fisheye frame
# 	circlemask = np.zeros((outheight, outwidth), np.uint8)
# 	cv2.circle(circlemask, (int(outwidth/2), int(outheight/2)), int(outputsize*0.45), (255, 255, 255), -1)

# 	# Define the codec and create VideoWriter object
# 	if doWrite:
# 		exists = True
# 		count = 0

# 		# outfilename = "{0}_cv{1:03d}.mov".format(os.path.splitext(os.path.basename(infile))[0], count)
# 		# outfilename = "{0}_cv{1:03d}.mjpg".format(os.path.splitext(os.path.basename(infile))[0], count)
# 		# outfilename = "{0}.mov".format(os.path.splitext(os.path.basename(infile))[0], count)
# 		# outfilename = "{0}.mjpg".format(os.path.splitext(os.path.basename(infile))[0], count)
		
# 		# outfilename = "{0}.avi".format(os.path.splitext(os.path.basename(infile))[0], count)
# 		# outfile = os.path.join(outpath, outfilename)

# 		# while exists:
# 		# 	outfilename = "{0}_cv{1:03d}.avi".format(os.path.splitext(os.path.basename(infile))[0], count)
# 		# 	outfile = os.path.join(outpath, outfilename)
# 		# 	exists = os.path.exists(outfile)
# 		# 	count = count + 1

# 		fourcc = 0
# 		if fullResolution:
# 			out = cv2.VideoWriter(outfile,fourcc, 15.0, (int(width), int(height)))
# 		else:
# 			out = cv2.VideoWriter(outfile,fourcc, 15.0, (outwidth, outheight))

# 		print("Writing output to", outfile)

# 	if not doHeadless:
# 		# cv2.namedWindow('tracking', cv2.WINDOW_NORMAL)

# 		# Create a named window
# 		cv2.namedWindow('tracking', cv2.WND_PROP_FULLSCREEN)

# 		# Set the window to fullscreen
# 		cv2.setWindowProperty('tracking', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
		
# 		# cv2.namedWindow('fgmask', cv2.WINDOW_NORMAL)
# 		# cv2.namedWindow('fgbg', cv2.WINDOW_NORMAL)

# 	# setup background detector
# 	# http://docs.opencv.org/3.2.0/d2/d55/group__bgsegm.html

# 	# fgbg = cv2.bgsegm.createBackgroundSubtractorMOG(backgroundRatio=0.7)
# 	# fgbg = cv2.bgsegm.createBackgroundSubtractorMOG(backgroundRatio=0.3)
# 	# fgbg = cv2.bgsegm.createBackgroundSubtractorGMG(initializationFrames = 50)#30)
# 	# fgbg = cv2.bgsegm.createBackgroundSubtractorGMG()

# 	# history = 50
# 	# fgbg = cv2.createBackgroundSubtractorMOG2(history = history, detectShadows=True)
# 	fgbg = cv2.createBackgroundSubtractorKNN(detectShadows = True) # default history 500 frames

# 	trails = []

# 	while(1):

# 		ret, frame = cap.read()

# 		if frame is None:
# 			break

# 		dataframe = cv2.resize(frame, (outwidth,outheight))

# 		# print "mask"
# 		maskedframe = cv2.bitwise_and(dataframe, dataframe, mask = circlemask)

# 		# frame = cv2.fisheye.undistortImage(frame, K, D=D, Knew=Knew)

# 		# ADVANCED BGSEGM METHODS
# 		fgmask = fgbg.apply(maskedframe)

# 		# print "threshold"
# 		ret, thresh = cv2.threshold(fgmask, 244, 255, cv2.THRESH_BINARY)

# 		if thresh is None:
# 			break

# 		# print "dilate"
# 		thresh = cv2.dilate(thresh, None, iterations=3)

# 		# print "find contours"
# 		cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

# 		if len(cnts) > 0:
# 			(newcnts, areas) = sort_by_area(cnts)

# 			for i in range(len(newcnts)):
# 				cnt = newcnts[i]
# 				area = areas[i]

# 				if area > minBlobSize and area < maxBlobSize:
# 					if fullResolution:
# 						largecnt = []
# 						for point in cnt:
# 							largepoint = point / scalef
# 							largecnt.append(largepoint)
# 						largecnt = np.array(largecnt)
# 						cnt = np.array(largecnt).reshape((-1,1,2)).astype(np.int32)
# 						cv2.drawContours(frame, [cnt], 0, (0, 255, 0), int(width/213))
						
# 					else:
# 						cv2.drawContours(frame, [cnt], 0, (0, 255, 0), 3)

# 					# perimeter = cv2.arcLength(cnt,True)

# 					M = cv2.moments(cnt.astype(np.float32))

# 					# center of mass
# 					cx = M['m10']/M['m00']
# 					cy = M['m01']/M['m00']

# 					center = (cx, cy)
# 					foundTrail = False

# 					for trail in trails:
# 						if len(trail) == 0:
# 							trail.appendleft(center)
# 							break

# 						dist = np.linalg.norm(np.array(trail[0])-np.array(center))

# 						if dist < searchRadius:
# 							trail.appendleft(center)
# 							foundTrail = True

# 					if not foundTrail:
# 						trails.append(deque(maxlen=10000))
# 						trails[-1].appendleft(center)

# 		masked = cv2.bitwise_and(dataframe, dataframe, mask=fgmask)

# 		while len(trails) > MAX_LENGTH:
# 			trails.pop(0)

# 		for pts in trails:
# 			for i in range(1, len(pts)-1):
# 				# if either of the tracked points are None, ignore them
# 				if pts[i - 1] is None or pts[i] is None:
# 					continue

# 				# otherwise, compute the thickness of the line and draw the connecting lines
# 				thickness = 3
				
# 				if fullResolution:
# 					# full size
# 					cv2.line(frame, (int(pts[i-1][0]), int(pts[i-1][1])), (int(pts[i][0]), int(pts[i][1])), (0, 0, 255), thickness, cv2.LINE_AA)
# 				else:
# 					# reduced size
# 					cv2.line(dataframe, (int(pts[i-1][0]), int(pts[i-1][1])), (int(pts[i][0]), int(pts[i][1])), (0, 0, 255), thickness, cv2.LINE_AA)


# 		# # make colored overlay
# 		# colthresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
# 		# cv2.addWeighted(colthresh, 0.5, frame, 0.5, 0.0, frame)

# 		# # make colored overlay
# 		if showMask:
# 			colthresh = cv2.cvtColor(circlemask, cv2.COLOR_GRAY2BGR)
# 			cv2.addWeighted(colthresh, 0.5, frame, 0.5, 0.0, frame)

# 		masked = cv2.resize(masked, (outwidth,outheight))
# 		thresh = cv2.resize(thresh, (outwidth,outheight))
# 		fgmask = cv2.resize(fgmask, (outwidth,outheight))
		
# 		if not fullResolution:
# 			frame = cv2.resize(frame, (outwidth,outheight))
# 			# Define the translation matrix

# 		frame2 = resize_to_bounding_box(frame, targetWidth, targetHeight)
		
# 		frame2 = crop_to_center_square(frame2)
		
# 		xoffset = targetWidth - frame2.shape[0]

# 		# pad the right side of the image to make it the right size
# 		frame2 = cv2.copyMakeBorder(
# 			frame2,
# 			0,
# 			0,
# 			0,
# 			xoffset,
# 			cv2.BORDER_CONSTANT,
# 			value=[0, 0, 0]  # Black color in BGR
# 		)
		
# 		# print(frame2.shape)
# 		ret, ir_frame = cap2.read()

# 		if ir_frame is not None:
# 			ir_frame = cv2.rotate(ir_frame, cv2.ROTATE_90_CLOCKWISE)
# 			ir_frame2 = resize_to_bounding_box(ir_frame, targetWidth, targetHeight)
# 			ir_frame2 = center_crop(ir_frame2, targetHeight, xoffset)

# 			# copy cam2 into right hand side of main feed
# 			frame2[:, -1*ir_frame2.shape[1]:] = ir_frame2[:,:]

# 		if not doHeadless:
# 			cv2.imshow('tracking',frame2)
# 			# cv2.imshow('fgbg',fgmask)
# 			# cv2.imshow('mask',thresh)

# 		if doWrite:
# 			try:
# 				out.write(frame)
# 			except:
# 				print("Error: video frame did not write")
# 			# out.write(frame)

# 		k = cv2.waitKey(1)
# 		if k == 27:
# 		   break
# 		elif k == ord('r'):
# 			trails.clear()
# 			# fgbg.clear()
# 		else:
# 			if k != -1:  # If a key is pressed
# 				# Convert the ASCII value to a character
# 				char = chr(k)
# 				print(f'Pressed key: {char}')

# 	print("done. ")
# 	# print "freeing resources"

# 	if doWrite:
# 		paths = []
# 		for trail in trails:
# 			thistrail = []
# 			for i in xrange(1, len(trail)):
# 				# if either of the tracked points are None, ignore them
# 				thistrail.append((trail[i]))
# 			paths.append(thistrail)

# 		pathfile = os.path.splitext(outfile)[0]+".json"
# 		print("write trails",pathfile)
# 		with open(pathfile, 'w') as outfile:
# 			json.dump(paths, outfile, indent=2)

# 	cap.release()

# 	if doWrite:
# 		out.release()

# 	cv2.destroyAllWindows()
