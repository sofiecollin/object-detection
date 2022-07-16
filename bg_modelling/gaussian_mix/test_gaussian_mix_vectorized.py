import sys

sys.path.insert(1, "../../")
from gaussian_mix_vectorized import GMM
import numpy as np
import PIL.Image
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import settings

sys.path.insert(1, "../../utils/")

from image_loader import load_image

first_frame = load_image(1)

gmm = GMM(first_frame)

plt.set_cmap("gray")

ax1 = plt.subplot(111)

im1 = ax1.imshow(first_frame)

def update(i):
    frame = load_image(i)

    B_hat = gmm.next(frame)

    Sp = gmm.shadow(B_hat, frame)

    print(i)

    im1.set_data(Sp)

ani = FuncAnimation(plt.gcf(), update, frames=range(2, 400), interval=1)
plt.show()