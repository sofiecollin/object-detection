import numpy as np


def median_bg_model(frame, adaption_rate, threshold, median):
    lt = frame > median
    lt = (lt - 0.5) * 2

    median = median + lt * adaption_rate

    bg_fg = np.zeros((frame.shape[0], frame.shape[1]))

    bg_fg = np.abs(frame - median) <= threshold

    return (bg_fg, median)