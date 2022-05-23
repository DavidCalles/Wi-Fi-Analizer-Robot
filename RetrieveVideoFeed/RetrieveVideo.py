# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import cv2 as cv

cap = cv.VideoCapture(0) #Choosing the caemra ID
fourcc = cv.VideoWriter_fourcc(*'MJPG')
out = cv.VideoWriter('output.avi', fourcc, 20.0, (640,  480))

# Check if openned succesfully
if not cap.isOpened():
    print("Cannot open camera")
    exit()

# Show frames    
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    # Our operations on the frame come here
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # Save gray frame
    out.write(frame)
    hsvFrame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    # Show resulting frames
    cv.imshow('frameBGR', gray)
    cv.imshow('frameHSV', hsvFrame)
    cv.imshow('frameColor', frame)
    if cv.waitKey(1) == ord('q'):
        break
# When everything done, release the capture
cap.release()
out.release()
cv.destroyAllWindows()