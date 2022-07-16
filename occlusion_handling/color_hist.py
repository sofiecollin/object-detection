import numpy as np
import cv2
import matplotlib.pyplot as plt

# Calculates Hue color values for each blob
def get_color_vectors(frame, splitted_blobs=None):
    rgb_frame = np.float32(frame.get_rgbfile())*255
    hsv_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_BGR2HSV)
    histograms = []

    # TODO: 
    '''
    # Make cleaner
    # DO as in optic flow?
    '''
    # If the splitted blobs are sent in, do only color hist for them
    if splitted_blobs:
        splitted_contours = []
        for sb in splitted_blobs:
            splitted_contours.append(sb.get_contour())

        for i, c in enumerate(splitted_contours):
            black = np.zeros((frame.get_file().shape[0], frame.get_file().shape[1]), np.uint8)
            #points_to_fill = splitted_contours[:i]+splitted_contours[i+1:]
            cv2.fillPoly(black, [c],(255,255,255, -1))
            hist = cv2.calcHist([hsv_frame],[0],black,[179],[1,180])
            histograms.append(hist)
    else:
        blobs_list = frame.get_all_blobs()
        
        for i, blob in enumerate(blobs_list):
            cnts = frame.get_all_blob_contours()
            tempMask = np.uint8(frame.get_file()).copy()
            if len(blobs_list) > 1: 
                blobs_to_fill = cnts[:i]+cnts[i+1:]
                blobs_to_fill = np.vstack(blobs_to_fill).squeeze()
                cv2.fillPoly(tempMask, pts = [blobs_to_fill], color=(0,0,0))
            
            hist = cv2.calcHist([hsv_frame],[0],tempMask,[179],[1,180]) # Remove completely black to get more fair hist
            blob.set_color_hist(hist)
            histograms.append(hist)  
    
    return histograms

# Calculates color histograms for previous and current blobs and compares
def compare_hist(prev_frame, current_frame):
    print("comparing..")
    hists = get_color_vectors(current_frame)
    prev_hists = get_color_vectors(prev_frame) # Change to remember last frame

    for curr_blob in current_frame.get_all_blobs():
        for prev_blob in prev_frame.get_all_blobs():
            histDiff = cv2.compareHist(prev_blob.get_color_hist(), curr_blob.get_color_hist(), cv2.HISTCMP_CORREL)
            print("blob " + str(prev_blob.get_id()) + " in prev and blob " + str(curr_blob.get_id()) + " in current is this similar: " + str(histDiff))
    
