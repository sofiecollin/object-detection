from matplotlib import pyplot as plt
import numpy as np
import PIL.Image
from matplotlib.animation import ArtistAnimation
from median_bg_model import median_bg_model
from init_median import init_median

plt.set_cmap("gray")

first_frame = np.asarray(PIL.Image.open('../../frames/Walk1000.jpg')) # Should always be first frame of sequence
median = init_median(first_frame) # Estimate starting median with median filter

frames = []
fig = plt.figure()

for i in range(611):
    file_name = '../../frames/Walk1{:03d}.jpg'.format(i)
    frame = np.asarray(PIL.Image.open(file_name))

    (bg_fg, median) = median_bg_model(frame, 0.5, 40, median)

    if i > 40:
        frames.append([plt.imshow(bg_fg, animated=True)])

# Only used for visualization
ani = ArtistAnimation(fig, frames, interval=50, blit=True,
                                repeat_delay=1000)
plt.show()