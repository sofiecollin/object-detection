import settings
import numpy as np
import PIL.Image
import cv2

def load_image(i):
    file_name = settings.FOLDER_NAME + '/' + settings.DATASET_NAME + '{:06d}.jpg'.format(i) # Change to '{:03d}.jpg'.format(i) for main file
    frame = np.asarray(PIL.Image.open(file_name))
    frame = frame / 255.0

    if settings.DOWNSAMPLE:
        frame = cv2.pyrDown(frame)
        frame = cv2.pyrDown(frame)
        frame = cv2.pyrDown(frame)

    return frame