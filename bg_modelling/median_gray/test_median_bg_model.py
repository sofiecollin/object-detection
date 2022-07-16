from matplotlib import pyplot as plt
import numpy as np
import PIL.Image
from matplotlib.animation import ArtistAnimation
from median_bg_model import median_bg_model
from scipy.signal import medfilt2d

plt.set_cmap("gray")

first_frame = np.asarray(PIL.Image.open('../../frames/Walk1000.jpg').convert('L'))
median = medfilt2d(first_frame, 9)

frames = []
fig = plt.figure()

for i in range(611):
    file_name = '../../frames/Walk1{:03d}.jpg'.format(i)
    frame = np.asarray(PIL.Image.open(file_name).convert('L'))

    (bg_fg, median) = median_bg_model(frame, 0.5, 40, median)

    if i > 40:
        frames.append([plt.imshow(bg_fg, animated=True)])


ani = ArtistAnimation(fig, frames, interval=50, blit=True,
                                repeat_delay=1000)
plt.show()