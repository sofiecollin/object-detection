from gaussian_mix_vectorized import GMM
import numpy as np
import PIL.Image
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from save_frames import save_frames
import settings
from utils.image_loader import load_image

first_frame = load_image(1)

gmm = GMM(first_frame)

for f in range(2, 300):
        print(f)
        frame = load_image(f)

        B_hat = gmm.next(frame)
        #save_frames(B_hat, f, '../../generated_modelling_frames/' + 'bb' + '/')
