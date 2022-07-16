import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import sys
sys.path.append("bg_modelling/gaussian_mix")
sys.path.append("HandlingData")
sys.path.append("utils")
from gaussian_mix_vectorized import GMM
from morph_operations import get_mask
import numpy as np
import PIL.Image
from FrameClass import Frame
from BoxClass import Box
from RootClass import Root
from matplotlib.animation import FuncAnimation
import cv2

dataset_name = 'Walk1'
file_name1 = 'frames2/' + dataset_name + '{:03d}.jpg'.format(1)
first_frame = np.asarray(PIL.Image.open(file_name1))
first_frame = first_frame / 255.0
first_frame = first_frame.astype('float64')
gmm = GMM(first_frame)
B_hat = 1 -(gmm.next(first_frame))
binframe_prev = Frame()
start=30
stop=400

plt.set_cmap("gray")
ax1 = plt.subplot(111)
im1 = ax1.imshow(first_frame)

for i in range(start,stop):
    file_name = 'frames2/' + dataset_name + '{:03d}.jpg'.format(i)
    frame = np.asarray(PIL.Image.open(file_name))
    frame = frame / 255.0
    frame = frame.astype('float64')

    curr_bin_im = 1-(gmm.next(frame))
    curr_bin_im = get_mask(curr_bin_im)

    curr_bin_im = curr_bin_im.astype('float64')
    binframe_curr = Frame(mask_file=curr_bin_im,rgb_file=frame)

    if i==start:
        binframe_curr.set_box_list(thresh = 10)
        binframe_prev=binframe_curr
    else:
        binframe_curr.set_box_list(thresh = 10)

    binframe_curr.update_id(binframe_prev)

    print("Currently used ids': {ids} ".format(ids=binframe_curr.get_id_list()))
    print("First unused id: {id} ".format(id=binframe_curr.get_unused_id()))

    im = binframe_curr.draw_boxes(frame)
    binframe_prev = binframe_curr

    cv2.imshow('bounding boxes', im)
    cv2.waitKey(0)
