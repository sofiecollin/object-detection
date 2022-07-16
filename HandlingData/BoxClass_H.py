# Class for box
# Contains data for a labeling box.
# Supports the Frame and, through it, also the Root class.
import cv2

class Box:
    color_label_list = [(255, 0, 0),
                        (0, 255, 0),
                        (0, 0, 255),
                        (255, 255, 0),
                        (0, 255, 255),
                        (255, 0, 255),
                        (128, 0, 0),
                        (0, 128, 0),
                        (0, 0, 128),
                        (128, 128, 0),
                        (0, 128, 128),
                        (128, 0, 128)]

    def __init__(self, xcenter=0, ycenter=0, w=0, h=0, orientation=0, id=10):
        self.__xcenter = xcenter
        self.__ycenter = ycenter
        self.__xstart = xcenter - w/2
        self.__ystart = ycenter - h/2
        self.__w = w
        self.__h = h
        self.__orientation = orientation
        self.__id = id

    # Get functions
    def get_xcenter(self):
        return self.__xcenter

    def get_ycenter(self):
        return self.__ycenter

    def get_width(self):
        return self.__w

    def get_height(self):
        return self.__h

    def get_xstart(self):
        return self.__xstart

    def get_ystart(self):
        return self.__ystart

    def get_orientation(self):
        return self.__orientation

    def get_id(self):
        return self.__id


    # Set functions
    def set_xcenter(self, x):
        self.__xcenter = x

    def set_ycenter(self, y):
        self.__ycenter = y

    def set_width(self, w):
        self.__w = w

    def set_height(self, h):
        self.__h = h

    def set_orientation(self, orientation):
        self.__orientation = orientation

    def set_id(self, id):
        self.__id = id

    def draw_self(self, image):
        cv2.rectangle(image, (int(self.__xstart), int(self.__ystart)),
                      ((int(self.__xstart) + int(self.__w)), (int(self.__ystart) + int(self.__h))),
                      self.color_label_list[self.__id], 2)

    def get_area(self):
        dx = abs((self.__xstart+self.__w) - self.__xstart)
        dy = abs((self.__ystart+self.__h) - self.__ystart)
        area = dx*dy

        return area

    def get_union(self, box):
        area1 = self.get_area()
        area2 = box.get_area()
        intersection = self.get_intersection(box)
        union = float(area1 + area2 - intersection)

        return union


    def get_intersection(self, box):
        xmin1 = self.__xstart
        ymin1 = self.__ystart
        xmax1 = xmin1 + self.__w
        ymax1 = ymin1 + self.__h

        xmin2 = box.get_xstart()
        ymin2 = box.get_ystart()
        xmax2 = xmin2 + box.get_width()
        ymax2 = ymin2 + box.get_height()

        dx = min(xmax1, xmax2) - max(xmin1, xmin2)
        dy = min(ymax1, ymax2) - max(ymin1, ymin2)

        if dx < 0 or dy < 0:  # no intersection
            intersection = 0.0
        else:
            intersection = float(dx * dy)

        return intersection

    def get_overlapping_score(self, box):
        intersection = self.get_intersection(box)
        union = self.get_union(box)
        score = intersection/union

        return score



    #Other stuff
    def print_all(self):
        print(self.__xcenter)
        print(self.__ycenter)
        print(self.__w)
        print(self.__h)
        print(self.__orientation)
        print(self.__id)
