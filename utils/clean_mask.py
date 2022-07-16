import cv2
import imutils
import numpy as np

def clean_mask(mask, thresh_to_draw = 50):
    mask = morph_operations(mask)
    mask = draw_over_blobs(mask, thresh_to_draw)

    return mask

# Do morph operations
def morph_operations(mask):
    kernel = np.ones((4,4),np.uint8) # Structure element 1
    kernel2 = np.ones((6,6),np.uint8) # Structure element 2
    kernel3 = np.ones((10,10),np.uint8) # Structure element 3

    # Closing
    mask = cv2.morphologyEx(np.float32(mask), cv2.MORPH_CLOSE, kernel)

    # Dilate
    #mask = cv2.dilate(mask,kernel,iterations = 3) # Temporary for fake blobs

    # Erode
    #mask = cv2.erode(mask,kernel2,iterations = 1) # Temporary for fake blobs

    return mask

# Fill small blobs with black
def draw_over_blobs(mask, thresh):
    mask = np.uint8(mask)
    cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    for counter, c in enumerate(cnts):
        if cv2.contourArea(c) < thresh:
            cv2.fillPoly(mask, pts = [c], color=(0,0,0))
    return mask