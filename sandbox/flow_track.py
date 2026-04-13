import cv2
import numpy as np
import argparse
import norfair
from norfair.tracker import Tracker
from collections import deque

def euclidean_distance(detection, tracked_object):
    return np.linalg.norm(detection.points - tracked_object.estimate)

def main():
    parser = argparse.ArgumentParser(description="Dense Optical Flow Tracking Example")
    parser.add_argument("--video", type=str, required=True, help="Path to input video")
    parser.add_argument("--output", type=str, default="flow_tracked.mp4", help="Path to output video")
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        print(f"Error: Could not open {args.video}")
        return

    # Info for video writer
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(args.output, fourcc, int(fps), (width, height))

    window_name = "Optical Flow Tracking Preview"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # 1. Read the very first frame to initialize the background baseline
    ret, frame1 = cap.read()
    if not ret:
        print("Error reading first frame.")
        return

    # Optical flow requires grayscale images
    prvs = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    
    # Create an empty HSV canvas equal in size to the video to draw our colored heatmap onto
    hsv = np.zeros_like(frame1)
    hsv[..., 1] = 255 # Force maximum saturation dynamically

    # Initialize Norfair tracker and paths dictionary
    tracker = Tracker(distance_function=euclidean_distance, distance_threshold=100.0)
    tracked_paths = {}

    print("Starting Dense Optical Flow processing... Press 'q' to stop early.")

    while cap.isOpened():
        ret, frame2 = cap.read()
        if not ret:
            break

        next_gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        # 2. Calculate Dense Optical Flow (Farneback algorithm)
        # Analyzes the physical pixel variance between `prvs` (last frame) and `next_gray` (current frame)
        flow = cv2.calcOpticalFlowFarneback(prvs, next_gray, None,
                                            pyr_scale=0.5, levels=3, winsize=15,
                                            iterations=3, poly_n=5, poly_sigma=1.2, flags=0)

        # 3. Translate Cartesian movement vectors (dx, dy) into Polar vectors (magnitude/speed, and angle/direction)
        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])

        # Multiply raw pixel movement speed into a visible 0-255 spectrum, safely capping it at 255
        # Instead of cv2.normalize which mathematically forces background noise to max brightness!
        mag_8u = np.clip(mag * 20, 0, 255).astype(np.uint8)
        
        # 4. Filter pixel motion mathematically extracting only substantial moving physical blobs
        _, motion_mask = cv2.threshold(mag_8u, 20, 255, cv2.THRESH_BINARY)
        
        # Merge disjoint moving shadows (like swirling hands isolated from torso) with geometry expansion kernel
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        motion_mask = cv2.dilate(motion_mask, kernel, iterations=2)
        
        # 5. Extract active motion bounding limits
        cnts, _ = cv2.findContours(motion_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        norfair_detections = []
        for cnt in cnts:
            if cv2.contourArea(cnt) > 800: # Drop small static flutter
                x,y,w,h = cv2.boundingRect(cnt)
                cx, cy = x + w/2.0, y + h/2.0
                norfair_detections.append(norfair.Detection(points=np.array([[cx, cy]]), scores=np.array([1.0])))

        # 6. Apply logic vectors to Norfair Tracking physics
        tracked_objects = tracker.update(detections=norfair_detections)

        # 7. Paint neon visual heatmap representation layers
        hsv[..., 0] = ang * 180 / np.pi / 2
        hsv[..., 2] = mag_8u
        rgb_flow = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        result_frame = cv2.addWeighted(frame2, 0.7, rgb_flow, 0.8, 0)

        # 8. Render Tracker History Path Overlays
        for obj in tracked_objects:
            if obj.id not in tracked_paths:
                tracked_paths[obj.id] = deque(maxlen=1000)
            
            tracked_paths[obj.id].append(tuple(obj.estimate[0].astype(int)))
            
            pts = tracked_paths[obj.id]
            for i in range(1, len(pts)):
                cv2.line(result_frame, pts[i-1], pts[i], (0, 0, 255), 3, cv2.LINE_AA)

        # Draw Norfair dynamic centroid dots tracking over optical elements
        norfair.draw_tracked_objects(result_frame, tracked_objects, draw_labels=True, id_size=2, id_thickness=2)

        out.write(result_frame)

        cv2.imshow(window_name, result_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Stopped early by user.")
            break

        # Move to next frame natively
        prvs = next_gray

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Tracking complete. Output saved to: {args.output}")

if __name__ == "__main__":
    main()
