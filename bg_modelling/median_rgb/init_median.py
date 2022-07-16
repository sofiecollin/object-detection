from scipy.signal import medfilt2d
import numpy as np

def init_median(frame):
    median = np.zeros(frame.shape)
    median[:, :, 0] = medfilt2d(frame[:, :, 0], 9)
    median[:, :, 1] = medfilt2d(frame[:, :, 1], 9)
    median[:, :, 2] = medfilt2d(frame[:, :, 2], 9)

    return median