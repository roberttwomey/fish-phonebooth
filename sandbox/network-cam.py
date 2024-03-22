import cv2

# cap = cv2.VideoCapture("tcp://192.168.1.108:37777")
# cap = cv2.VideoCapture("udp://192.168.1.108:37778")
# cap = cv2.VideoCapture("https://192.168.1.108:443")
# cap = cv2.VideoCapture("rtsp://192.168.1.108:554")

cap = cv2.VideoCapture(0)

while(True): 
    ret, frame = cap.read() 
    cv2.imshow('frame', frame) 
      
    # the 'q' button is set as the 
    # quitting button you may use any 
    # desired button of your choice 
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break
cap.release() 
cv2.destroyAllWindows() 