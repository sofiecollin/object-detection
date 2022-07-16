import cv2
import numpy as np
import imutils
import matplotlib.pyplot as plt
from PIL import Image
import settings
from utils.image_loader import load_image

# Should maybe be named set optic flow
def get_optic_flow(prev_frame, curr_frame, seperated_blobs=None):
    # Convert to grayscale
    prev_frame_img = cv2.cvtColor(np.float32(prev_frame.get_rgbfile()), cv2.COLOR_RGB2GRAY)
    curr_frame_img = cv2.cvtColor(np.float32(curr_frame.get_rgbfile()), cv2.COLOR_RGB2GRAY)
    next_img = cv2.cvtColor(np.float32(load_image(curr_frame.get_number()+1)), cv2.COLOR_RGB2GRAY)

    # Claculate flow
    flow = cv2.calcOpticalFlowFarneback(curr_frame_img, next_img, None, 0.5, 3, 15, 3, 5, 3, 0)
    
    if seperated_blobs:
        blob_list = seperated_blobs
    else:
        blob_list = curr_frame.get_all_blobs()

    # Make average flow
    for blob in blob_list:
        blob_indicies = blob.get_indicies()
        direction_vector = np.zeros((2,1))
        for i in blob_indicies:
            direction_vector[0] += flow[i[0], i[1]][0]
            direction_vector[1] += flow[i[0], i[1]][1]

        for i in blob_indicies:
            flow[i[0], i[1]][0] = direction_vector[0]
            flow[i[0], i[1]][1] = direction_vector[1]

        blob.set_direction_vector(direction_vector)
    return flow
 
def draw_optic_flow(curr_frame, flow):
    first_img = load_image(1)
    mask = np.uint8(curr_frame.get_file())
    img = curr_frame.get_rgbfile()
    img = cv2.cvtColor(img.astype('float32'), cv2.COLOR_RGB2BGR)

    blob_list = curr_frame.get_all_blobs()

    # Draw direction line on each blob
    for blob in blob_list:
        if any(i < 15 for i in blob.get_min_distances_to_blobs()): # Only visulize occluding blobs vectors

            cX = blob.get_xcenter()
            cY = blob.get_ycenter() 
            
            directionVector = blob.get_direction_vector()
            if directionVector[0]:   
                #epsilon = 0.00001 # To check if object is standing still
                #if np.linalg.norm(directionVector) < epsilon:
                #    continue
                directionVector = directionVector/np.linalg.norm(directionVector)*40
                
                directionVectorX = cX+directionVector[0]
                directionVectorY = cY+directionVector[1]
                cv2.circle(img, (cX, cY), 2, (255, 255, 255), -1)
                cv2.line(img, (cX, cY), (directionVectorX,directionVectorY), (0, 0, 255), 2)
    img = cv2.cvtColor(img.astype('float32'), cv2.COLOR_BGR2RGB)
    return img