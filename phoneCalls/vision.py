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
import time

import norfair
from norfair.tracker import Tracker

def euclidean_distance(detection, tracked_object):
	return np.linalg.norm(detection.points - tracked_object.estimate)


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

VIDEO_FILE = "/Volumes/Work/bigdata/housemachine/data/ceiling/livingroom/livingroom_motion_2017-08-13_20.17.02_27.mp4"
NETWORK_CAMERA = "rtsp://admin:CameraRed@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0"

class VisionSystem:
	def __init__(self, args=None):
		'''
		Creates a CameraDisplay object that will process incoming frames and 
		'''
		
		if args is None:
			# Default values when no args provided
			self.doWrite = False
			self.doHeadless = False
			self.doUndistort = False
			self.minBlobSize = 400.0
			self.maxBlobSize = 50000.0
			self.searchRadius = 50.0
			self.doConvexHull = False
			self.hullDist = 150.0
			self.video_file = VIDEO_FILE
			self.output_video = 'vision_output.mp4'
		else:
			self.doWrite = args.write
			self.doHeadless = args.headless
			self.doUndistort = False

			self.minBlobSize = args.minblob if hasattr(args, 'minblob') else 400.0
			self.maxBlobSize = 50000.0
			self.searchRadius = args.radius if hasattr(args, 'radius') else 50.0
			self.doConvexHull = getattr(args, 'convexhull', False)
			self.hullDist = getattr(args, 'hulldist', 150.0)

			self.maxNumTrails = 50
			self.video_file = getattr(args, 'video', VIDEO_FILE)
			self.output_video = getattr(args, 'output', 'vision_output.mp4')

		self.maxNumTrails = 50
		self.showMask = True
		self.fullResolution = True

		self.outputsize = 600#800 # rescales input video

		self.targetWidth = 1280
		self.targetHeight = 800

		load_dotenv()
		self.CAM1 = os.getenv('CAM1')
		self.CAM2 = os.getenv('CAM2')

		self.showTimerText = os.getenv('SHOW_TIMER_TEXT') == 'True'

		self.frame_count = 0
		self.total_time = 0

	def start(self):
		# set up the various parts of the background and video
		self.setup_video()
		self.setup_recording()
		self.setup_gui()
		self.setup_cv()

	def setup_video(self):
		# set up overhead capture
		# self.cap1 = cv2.VideoCapture(self.video_file)
		self.cap1 = cv2.VideoCapture(self.CAM1)
		# net cam 2880 x 2160 native or 2048 x 1536
		# self.cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 1440)
		# self.cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
		self.cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 2048)
		self.cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 1536)
		self.cap1.set(cv2.CAP_PROP_FPS, 15)

		if self.cap1 is None:
			print("Couldn't open overhead camera")
			exit(0)

		# configure size and buffers
		self.width = self.cap1.get(3)
		self.height = self.cap1.get(4)
		print("camera size: ", self.width, self.height)

		# booth camera
		self.cap2 = cv2.VideoCapture(int(self.CAM2))#self.CAM2) # booth cam is device 0
		if self.cap2 is None:
			print("Couldn't open frontal camera")
			exit(0)
		
		# proportionally scaled to match fit within 
		self.outheight = self.outputsize
		self.scalef = float(self.outputsize)/float(self.height)
		self.outwidth = int(self.scalef*self.width)
		print("resized frame: ", self.outwidth, self.outheight)

		# create mask to mask aroud circular fisheye frame
		self.circlemask = np.zeros((self.outheight, self.outwidth), np.uint8)
		cv2.circle(self.circlemask, (int(self.outwidth/2), int(self.outheight/2)), int(self.outputsize*0.45), (255, 255, 255), -1)

	def setup_recording(self):
		if not self.doWrite:
			return
		fourcc = cv2.VideoWriter_fourcc(*'mp4v')
		# Save video out to the exact final output layout (targetWidth x targetHeight)
		self.out = cv2.VideoWriter(self.output_video, fourcc, 15.0, (self.targetWidth, self.targetHeight))
		print(f"Writing video output to {self.output_video}")

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
		# disabling shadows (False) helps unite a person's upper body with their floor shadow as one unit
		# self.fgbg = cv2.createBackgroundSubtractorKNN(history=500, dist2Threshold=400.0, detectShadows=False)
		self.fgbg = cv2.createBackgroundSubtractorKNN(history=500, dist2Threshold=400.0, detectShadows=True)
		
		# Replace trails with norfair tracker
		self.tracker = Tracker(distance_function=euclidean_distance, distance_threshold=self.searchRadius)
		self.tracked_paths = {}

	def update(self, time_left=-1):
		start_time = time.time()
		ret, frame = self.cap1.read()

		if not ret:
			print('looping at end of video')
			self.cap1.set(cv2.CAP_PROP_POS_FRAMES, 0)
			ret, frame = self.cap1.read()

		if frame is None:
			return

		resize_start = time.time()
		dataframe = cv2.resize(frame, (self.outwidth, self.outheight))
		resize_time = time.time() - resize_start

				# print "mask"
		maskedframe = cv2.bitwise_and(dataframe, dataframe, mask = self.circlemask)

		# frame = cv2.fisheye.undistortImage(frame, K, D=D, Knew=Knew)

		# Pre-process with Gaussian Blur to reduce noise and help blob fusion
		blurred_frame = cv2.GaussianBlur(maskedframe, (3, 3), 0)

		# ADVANCED BGSEGM METHODS
		fgmask = self.fgbg.apply(blurred_frame)

		# print("threshold")
		ret, thresh = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)

		if thresh is None:
			return

		# Enhanced Morphology Pipeline
		# 1. Close holes inside the foreground objects (reconnecting stray legs/arms to the body)
		kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
		thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
		
		# 2. Aggressive Dilation to merge fragmented torso/limb shapes into a single whole-body blob
		thresh = cv2.dilate(thresh, kernel, iterations=3)

		# print "find contours"
		cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

		norfair_detections = []

		if len(cnts) > 0:
			(newcnts, areas) = sort_by_area(cnts)

			valid_cnts = []
			for i in range(len(newcnts)):
				if areas[i] > self.minBlobSize and areas[i] < self.maxBlobSize:
					valid_cnts.append(newcnts[i])

			if self.doConvexHull and len(valid_cnts) > 0:
				grouped_cnts = []
				used = [False] * len(valid_cnts)
				for i in range(len(valid_cnts)):
					if used[i]: continue
					current_group = [valid_cnts[i]]
					used[i] = True
					queue = [valid_cnts[i]]
					
					while queue:
						curr = queue.pop(0)
						# Use bounding box center for proximity measure
						x,y,w,h = cv2.boundingRect(curr)
						cx_c, cy_c = x + w/2.0, y + h/2.0
						
						for j in range(len(valid_cnts)):
							if not used[j]:
								xj,yj,wj,hj = cv2.boundingRect(valid_cnts[j])
								cx_j, cy_j = xj + wj/2.0, yj + hj/2.0
								dist = np.linalg.norm(np.array([cx_c, cy_c]) - np.array([cx_j, cy_j]))
								
								if dist < self.hullDist:
									queue.append(valid_cnts[j])
									current_group.append(valid_cnts[j])
									used[j] = True
					
					merged_cnt = np.vstack(current_group)
					hull = cv2.convexHull(merged_cnt)
					grouped_cnts.append(hull)
				valid_cnts = grouped_cnts

			for cnt in valid_cnts:
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

				M = cv2.moments(cnt.astype(np.float32))

				# Avoid division by zero if moment is very tiny
				if M['m00'] != 0:
					cx = M['m10']/M['m00']
					cy = M['m01']/M['m00']
				else:
					x,y,w,h = cv2.boundingRect(cnt)
					cx, cy = x + w/2.0, y + h/2.0

				norfair_detections.append(norfair.Detection(points=np.array([[cx, cy]]), scores=np.array([1.0])))

		masked = cv2.bitwise_and(dataframe, dataframe, mask=fgmask)

		# Update norfair tracker
		tracked_objects = self.tracker.update(detections=norfair_detections)

		for obj in tracked_objects:
			if obj.id not in self.tracked_paths:
				self.tracked_paths[obj.id] = deque(maxlen=1000)
			
			# Current centroid
			center = tuple(obj.estimate[0].astype(int))
			self.tracked_paths[obj.id].append(center)
			
			pts = self.tracked_paths[obj.id]
			for i in range(1, len(pts)):
				thickness = 3
				if self.fullResolution:
					cv2.line(frame, pts[i-1], pts[i], (0, 0, 255), thickness, cv2.LINE_AA)
				else:
					cv2.line(dataframe, pts[i-1], pts[i], (0, 0, 255), thickness, cv2.LINE_AA)
		
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
		if self.showTimerText:
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

		if not self.doHeadless:
			cv2.imshow('tracking',frame2)

		if self.doWrite:
			self.out.write(frame2)

		# Timing
		self.frame_count += 1
		frame_time = time.time() - start_time
		self.total_time += frame_time

		if self.frame_count % 10 == 0:
			avg_time = self.total_time / self.frame_count
			fps = 1.0 / avg_time
			print(f"Frame {self.frame_count}: Avg FPS: {fps:.2f}, Avg time: {avg_time:.4f}s, Resize time: {resize_time:.4f}s")


	def reset(self):
		self.tracked_paths.clear()
		self.tracker = Tracker(distance_function=euclidean_distance, distance_threshold=self.searchRadius)

	def cleanup(self):
		self.cap1.release()

		if self.doWrite:
			self.out.release()
			paths = []
			for trail in self.tracked_paths.values():			
				thistrail = []
				for i in range(1, len(trail)):
					thistrail.append(trail[i])
				paths.append(thistrail)

			pathfile = os.path.splitext(self.output_video)[0]+".json"
			print(f"Write paths json logic completed: {pathfile}")
			with open(pathfile, 'w') as outf:
				json.dump(paths, outf, indent=2)

		cv2.destroyAllWindows()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Run background foreground segmentation on overhead video', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--video', type=str, default=VIDEO_FILE, help='Path to input video')
	parser.add_argument('--output', type=str, default='vision_output.mp4', help='Path to output .mp4 video if writing')
	parser.add_argument('--write', action='store_true', help='Save tracked image as new .mp4 video')
	parser.add_argument('--headless', action='store_true', help='Do not display video on screen')
	parser.add_argument('--minblob', type=float, default=600.0, help='Minimum blob size to track')
	parser.add_argument('--radius', type=float, default=70.0, help='Maximum search radius for tracking blobs')
	parser.add_argument('--convexhull', action='store_true', help='Enable proximity convex hulls to merge nearby disjoint blobs')
	parser.add_argument('--hulldist', type=float, default=150.0, help='Distance threshold to merge blobs into a single hull')
	args = parser.parse_args()

	vision = VisionSystem(args)

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