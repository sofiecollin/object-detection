# Class for box
# Contains data for a labeling box.
# Supports the Frame and, through it, also the Root class.
import cv2
import numpy as np
from PIL import Image
from scipy.spatial.distance import cdist

class Blob:
    def __init__(self, xcenter=0, ycenter=0, contour=None, indicies=None, direction_vector=None, color_hist=None, id=np.nan):
        self.__xcenter = xcenter
        self.__ycenter = ycenter
        self.__contour = contour
        self.__indicies = indicies
        self.__direction_vector = direction_vector
        self.__color_hist = color_hist
        self.__min_distances = np.full((40), np.inf)
        self.__is_soon_in_occlusion = False
        self.__is_in_occlusion = False
        self.__id = id

    # Get functions
    def get_xcenter(self):
        return self.__xcenter

    def get_ycenter(self):
        return self.__ycenter

    def get_contour(self):
        return self.__contour

    def get_indicies(self):
        return self.__indicies

    def get_direction_vector(self):
        return self.__direction_vector

    def get_color_hist(self):
        return self.__color_hist

    def get_id(self):
        return self.__id

    def get_contour_distance(self, other_blob):
        cnts1 = np.vstack(self.get_contour()).squeeze()
        cnts2 = np.vstack(other_blob.get_contour()).squeeze()

        return np.amin(cdist(cnts1, cnts2))

    def get_min_distances_to_blobs(self):
        return self.__min_distances

    # Set functions
    def set_xcenter(self, x):
        self.__xcenter = x

    def set_ycenter(self, y):
        self.__ycenter = y

    def set_contour(self, contour):
        self.__contour = contour

    def set_indicies(self, indicies):
        self.__indicies = indicies

    def set_direction_vector(self, direction_vector):
        self.__direction_vector = direction_vector
        
    def set_color_hist(self, color_hist):
        self.__color_hist = color_hist

    def set_id(self, id):
        self.__id = id

    def get_area(self):
        area = cv2.contourArea(self.__contour)
        return area

    def set_min_distance_to_blob(self, distance, other_blob_id):
        self.__min_distances[other_blob_id] = distance
