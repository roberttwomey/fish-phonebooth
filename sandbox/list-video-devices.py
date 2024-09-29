import cv2

def list_video_devices(max_devices=10):
    available_devices = []
    
    for device_index in range(max_devices):
        cap = cv2.VideoCapture(device_index)
        
        if cap.isOpened():
            available_devices.append(device_index)
            cap.release()  # Release the device if opened
    
    return available_devices

if __name__ == "__main__":
    devices = list_video_devices()
    if devices:
        print("Available video devices:")
        for device in devices:
            print(f"Device index: {device}")
    else:
        print("No video devices found.")
