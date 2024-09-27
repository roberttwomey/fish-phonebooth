import cv2
import numpy as np
import time

# Create a black image
img = np.zeros((300, 600, 3), dtype=np.uint8)

# Display the image in a window
cv2.imshow("Key Press Tracker", img)

lastKey = None
lastKeyTime = None
while True:
    key = cv2.pollKey()  # Wait for 1 millisecond for a key event

    if key != -1:  # If a key is pressed
        # print("*")
        if key != lastKey:
            lastKey = key
            print(f"Key pressed: {key}")
            # lastKeyTime = time.time()
            # You can add a small delay to simulate the key release
    else:
        # print(".")
        lastKey = None

        # if time.time()-lastKey > 0.03:

    if key == 27:  # Escape key to exit
        break

# Clean up
cv2.destroyAllWindows()