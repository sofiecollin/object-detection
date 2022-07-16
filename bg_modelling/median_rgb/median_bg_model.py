import numpy as np

def median_bg_model(frame, adaption_rate, threshold, median):
    lt = frame > median
    lt = (lt - 0.5) * 2 # Scale [0, 1] to [-1, 1]

    median = median + lt * adaption_rate

    bg_fg_r = np.abs(frame[:, :, 0] - median[:, :, 0]) <= threshold
    bg_fg_g = np.abs(frame[:, :, 1] - median[:, :, 1]) <= threshold
    bg_fg_b = np.abs(frame[:, :, 2] - median[:, :, 2]) <= threshold

    bg_fg = bg_fg_r * bg_fg_g * bg_fg_b # Should check if this is the optimal way of handling RGB

    return (bg_fg, median)