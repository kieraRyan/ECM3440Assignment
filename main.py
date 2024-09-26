
import cv2 as cv
import sys
import numpy as np
from PIL import Image, ImageTk


print('Creating Video Capture .. Please wait')
cam = cv.VideoCapture(0)
while True:
    ret, im =cam.read()
    ## here we can adjust the image


	## here we can adjust the image	
    cv.imshow('Original',im)
    #cv.imshow('Adjusted',drawonme)

    ##PRESS q keyboard key to quit

    if cv.waitKey(10) & 0xFF==ord('q'):
        break ## break the while TRUE
cam.release()
cv.destroyAllWindows()