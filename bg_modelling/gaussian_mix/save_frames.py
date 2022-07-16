from PIL import Image
from matplotlib import pyplot as plt
import numpy as np
import os


# sparar en frame med frame nr "f" i directory
# OBS kom ihåg att normalisera bilden mellan [0,1] när ni hämtar sparade bilder.
def save_frames(frame, f, directory):

  if not os.path.exists(directory):
    os.makedirs(directory)
    
  fileName = directory + 'frame{:03d}.jpg'.format(f)
  frame = Image.fromarray((frame * 255).astype(np.uint8)).convert('L')
  frame.save(fileName)