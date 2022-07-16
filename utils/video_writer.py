import cv2
import glob
import numpy as np

def write_to_video(video_name, video_size, folder_path, image_format):
    out = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*"mp4v"), 25, video_size)
    path_n_format = folder_path + '*' + image_format

    string_sequence = []

    #Read all names in directory and sort then.
    for im_name in glob.glob(path_n_format):
        string_sequence.append(im_name)
    string_sequence.sort()

    #Import images and write to video
    for i in range (0, len(string_sequence)):
        im = cv2.imread(string_sequence[i])
        out.write(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))

# for example:
#write_to_video(video_name='video_fake.mp4', video_size=(384,288), folder_path='/Users/pontusarnesson/Desktop/cv_video/fake_blobs/', image_format='.jpg')