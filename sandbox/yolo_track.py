import argparse
import cv2
import numpy as np
from collections import deque
from ultralytics import YOLO

def main():
    parser = argparse.ArgumentParser(description="Overhead tracking using YOLOv11 and ByteTrack")
    parser.add_argument("--video", type=str, required=True, help="Path to input video")
    parser.add_argument("--output", type=str, default="yolo_tracked.mp4", help="Path to output video")
    parser.add_argument("--model", type=str, default="yolo11n-obb.pt", help="Model size: yolo11n.pt (fastest), yolo11s.pt, yolo11m.pt (accurate)")
    # parser.add_argument("--model", type=str, default="yolo11n.pt", help="Model size: yolo11n.pt (fastest), yolo11s.pt, yolo11m.pt (accurate)")
    parser.add_argument("--conf", type=float, default=0.15, help="Confidence threshold for detection (lower to find obscured people)")
    parser.add_argument("--imgsz", type=int, default=512, help="Resolution for inference (higher retains fisheye details)")
    # parser.add_argument("--imgsz", type=int, default=1024, help="Resolution for inference (higher retains fisheye details)")
    args = parser.parse_args()

    print(f"Loading Ultralytics YOLO model '{args.model}'...")
    # Will automatically download the model on the first run, and offload to 'mps' if on Apple Silicon.
    model = YOLO(args.model)

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

    # Dictionary to maintain historical centroid paths for line drawing
    # track_id -> deque of (x, y) coordinates
    tracked_paths = {}

    window_name = "YOLO Tracking Preview"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    print(f"Starting video processing at imgsz={args.imgsz} and conf={args.conf}... Press 'q' to stop.")
    
    # Process the video directly utilizing the built-in ultralytics tracker
    # Setting classes=[0] filters object detections to ONLY track 'person' class!
    results = model.track(source=args.video, stream=True, classes=[0], tracker="bytetrack.yaml", conf=args.conf, imgsz=args.imgsz, verbose=False)

    for r in results:
        # Get raw current frame
        frame = r.orig_img.copy() 

        if r.boxes is not None and r.boxes.id is not None:
            # zip through the boxes and track IDs
            boxes = r.boxes.xyxy.cpu().numpy()  # Extract boxes in (x1, y1, x2, y2)
            track_ids = r.boxes.id.int().cpu().tolist()

            for box, track_id in zip(boxes, track_ids):
                x1, y1, x2, y2 = box
                # Calculate centroid
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                if track_id not in tracked_paths:
                    tracked_paths[track_id] = deque(maxlen=1000)
                tracked_paths[track_id].append((cx, cy))

                # Draw bounding box on the person
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                
                # Plot the red trailing paths replicating vision.py
                pts = tracked_paths[track_id]
                for i in range(1, len(pts)):
                    cv2.line(frame, pts[i-1], pts[i], (0, 0, 255), 3, cv2.LINE_AA)

        out.write(frame)
        cv2.imshow(window_name, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Stopped by user.")
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Done! Saved perfectly tracked video to: {args.output}")

if __name__ == "__main__":
    main()
