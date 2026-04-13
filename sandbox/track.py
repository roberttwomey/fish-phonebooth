import sys
import argparse
import warnings

import cv2
import numpy as np

# Suppress warnings
warnings.filterwarnings("ignore")

import norfair
from norfair.tracker import Tracker

# Add RAPiD to path so we can import it
sys.path.append('RAPiD')
try:
    from RAPiD.api import Detector
except Exception as e:
    from api import Detector

def euclidean_distance(detection, tracked_object):
    return np.linalg.norm(detection.points - tracked_object.estimate)

def main():
    parser = argparse.ArgumentParser(description="Overhead tracking using RAPiD and Norfair")
    parser.add_argument("--video", type=str, required=True, help="Path to input video")
    parser.add_argument("--output", type=str, default="output_tracked.mp4", help="Path to output video")
    parser.add_argument("--model_weights", type=str, default="RAPiD/weights/pL1_MWHB1024_Mar11_4000.ckpt", help="Path to RAPiD weights")
    parser.add_argument("--conf_thres", type=float, default=0.3, help="Confidence threshold")
    parser.add_argument("--input_size", type=int, default=608, help="Input size for RAPiD (lower = faster, e.g. 608 or 416)")
    args = parser.parse_args()

    print("Initializing RAPiD detector...")
    # Initialize RAPiD Detector (Load initially to CPU)
    detector = Detector(model_name='rapid', weights_path=args.model_weights, use_cuda=False)
    
    # Check for Mac GPU (MPS) support and move the model if available
    import torch
    if torch.backends.mps.is_available():
        print("Metal Performance Shaders (MPS) found! Moving model to Mac GPU for acceleration...")
        detector.model = detector.model.to('mps')
    else:
        print("MPS not available. Falling back to CPU...")
    
    print("Initializing Norfair tracker...")
    # Initialize norfair Tracker
    tracker = Tracker(distance_function=euclidean_distance, distance_threshold=75)
    
    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        print(f"Error: Could not open video {args.video}")
        return

    # Video writer setup
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or np.isnan(fps):
        fps = 30.0
        
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(args.output, fourcc, int(fps), (width, height))

    print("Starting tracking... Press 'q' in the preview window to stop early.")
    from PIL import Image

    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Name the preview window and allow resizing
    window_name = "Tracking Preview"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        if frame_count % 10 == 0:
            print(f"Processing frame {frame_count} / {total_frames}")

        # OpenCV uses BGR, PIL uses RGB
        pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        # detect_one returns a list of [x, y, w, h, a, conf] arrays
        dts = detector.detect_one(pil_img=pil_frame, input_size=args.input_size, conf_thres=args.conf_thres)
        
        norfair_detections = []
        for dt in dts:
            if len(dt) >= 6:
                x, y, w, h, a, conf = [float(v) for v in dt[:6]]
                centroid = np.array([[x, y]])
                norfair_detections.append(norfair.Detection(points=centroid, scores=np.array([conf]), data=[x, y, w, h, a, conf]))
            
        # Update tracker
        tracked_objects = tracker.update(detections=norfair_detections)
        
        # Draw on frame
        # Draw RAPiD bounding boxes (Angled)
        for dt in norfair_detections:
            x, y, w, h, a, conf = dt.data
            box = cv2.boxPoints(((float(x), float(y)), (float(w), float(h)), float(a)))
            box = np.int32(box) # changed from np.int0 for numpy 2.x compat
            cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)
            
        # Draw norfair tracked objects (Centroids and IDs)
        norfair.draw_tracked_objects(frame, tracked_objects, draw_labels=True, id_size=2, id_thickness=2)
        
        # Write to file
        out.write(frame)

        # Show real-time preview
        cv2.imshow(window_name, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Tracking stopped early by user.")
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Tracking complete. Output saved to {args.output}")

if __name__ == '__main__':
    main()
