# Imports
import glob
from PIL import Image


def import_image_sequence(path, format):
    #Init list for images and their names
    path_n_format = path + '*' + format
    image_sequence = []
    string_sequence = []
    #Read all names in directory and sort then.
    for im_name in glob.glob(path_n_format):
        string_sequence.append(im_name)
    string_sequence.sort()
    #Import images in order
    for i in range (0, len(string_sequence)):
        image_sequence.append(Image.open(string_sequence[i]))
    return image_sequence, string_sequence

#Example
# Imgs, names = import_image_sequence('JPEGS/','.jpg')
