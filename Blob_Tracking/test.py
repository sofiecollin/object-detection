import sys
sys.path.append("/Users/Sofie/Desktop/TSBB15Tracking/tsbb15-project-1/HandlingData")
from FrameClass import Frame
from BoxClass import Box
from RootClass import Root
import cv2
import scipy
from scipy import optimize
import PIL.Image
import numpy as np
from scipy.optimize import linear_sum_assignment

first_im = cv2.imread('blobs.png')
binfirst_im = cv2.cvtColor(first_im, cv2.COLOR_BGR2GRAY)
im_arr = [cv2.imread('blobs_moved.png'),
          cv2.imread('blobs_moved3.png'),
          cv2.imread('blobs_moved.png'),
          cv2.imread('blobs.png')]

im_arr2 = [np.asarray(PIL.Image.open('blobs_moved.png')),
          np.asarray(PIL.Image.open('blobs_moved3.png')),
          np.asarray(PIL.Image.open('blobs_moved.png')),
          np.asarray(PIL.Image.open('blobs.png'))]

## convert PIL to opencv
#pil_image = PIL.Image.open('blobs.png')
#opencvImage = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
frame_prev = Frame(im_file=binfirst_im.astype('float64'), rgb_file=first_im)
frame_prev.set_box_list(first_frame=True)
im = frame_prev.draw_boxes(first_im)


for i in range(0, len(im_arr2)):
    #imfile = opencvImage = cv2.cvtColor(np.array(im_arr2[i]), cv2.COLOR_RGB2BGR)
    imfile = cv2.cvtColor(im_arr2[i], cv2.COLOR_BGR2GRAY)
    imfile = imfile.astype('float64')

    #print(imfile.dtype)
    frame_curr = Frame(im_file=imfile,rgb_file=im_arr2[i])
    frame_curr.set_box_list()
    frame_curr.update_id(frame_prev)
    print(frame_curr.get_id_list())
    print(frame_curr.get_unused_id())
    im = frame_curr.draw_boxes(im_arr2[i])
    frame_prev = frame_curr

    cv2.destroyAllWindows()
    cv2.imshow('bounding boxes', im)
    cv2.waitKey(0)













