import cv2
import numpy as np
from ultralytics import YOLO

from ultralytics.utils.checks import check_imshow
from ultralytics.utils.plotting import Annotator, colors

from collections import defaultdict

track_history = defaultdict(lambda: [])
# model = YOLO("YOLOv8n-obb.pt")
model = YOLO("yolov8n.pt")
names = model.model.names

# video_path = "livingroom_motion_2017-08-13_10.59.15_1.mp4"
# video_path = "Screen Recording 2022-12-03 at 12.50.13 PM.mov"

# cap = cv2.VideoCapture(video_path)

# define a video capture object 

# VIDEO_FILE = "/Volumes/Work/Projects/housemachine/data/ceiling/livingroom/livingroom_motion_2017-08-13_20.17.02_27.mp4"
VIDEO_FILE = "/Volumes/Work/Projects/housemachine/data/ceiling/livingroom/livingroom_motion_2017-08-16_18.07.52_8.mp4"
SAVE_OUTPUT = True

cap = cv2.VideoCapture(VIDEO_FILE)
# cap = cv2.VideoCapture("rtsp://192.168.1.108:554")
# cap = cv2.VideoCapture("tcp://192.168.1.108:37777")

assert cap.isOpened(), "Error reading video file"

w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

if SAVE_OUTPUT:
    result = cv2.VideoWriter("object_tracking2.avi",
        cv2.VideoWriter_fourcc(*'mp4v'),
        fps,
        (w, h))

destframe = np.zeros((h, w, 3))

# yolo base        
while cap.isOpened():
    success, frame = cap.read()

    if success:
        results = model.track(frame, persist=True, verbose=False)

        boxes = results[0].boxes.xyxy.cpu()

        if results[0].boxes.id is not None:

            # Extract prediction results
            clss = results[0].boxes.cls.cpu().tolist()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            confs = results[0].boxes.conf.float().cpu().tolist()

            # Annotator Init
            annotator = Annotator(frame, line_width=2)

            for box, cls, track_id in zip(boxes, clss, track_ids):
                annotator.box_label(box, color=colors(int(cls), True), label=names[int(cls)])

                # Store tracking history
                track = track_history[track_id]
                track.append((int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2)))
                # if len(track) > 30:
                    # track.pop(0)

                # Plot tracks
                points = np.array(track, dtype=np.int32).reshape((-1, 1, 2))
                cv2.circle(frame, (track[-1]), 7, colors(int(cls), True), -1)
                cv2.polylines(frame, [points], isClosed=False, color=colors(int(cls), True), thickness=2)
                cv2.polylines(destframe, [points], isClosed=False, color=colors(int(cls), True), thickness=2)

        cv2.imshow("video", frame)
        cv2.imshow("trails", destframe)

        if SAVE_OUTPUT:
            result.write(frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break


# YOLO oriented bounding box - obb
# while cap.isOpened():
#     success, frame = cap.read()

#     if success:
#         # results = model.track(frame, persist=True, verbose=False)
#         results = model(frame, show=True)
#         if cv2.waitKey(1) & 0xFF == ord("q"):
#             break
#     else:
#         break  

if SAVE_OUTPUT:
    result.release()
cap.release()
cv2.destroyAllWindows()