# Frame class
# Contains box Objects.
# Supports the Root Class.
# Requires the Box to be imported. 
import cv2
import numpy as np
from BoxClass import Box
from scipy.optimize import linear_sum_assignment


class Frame:

    def __init__(self, number=0, box_list=None, im_file=False):
        if not box_list:
            self.__box_list = []
        self.__number = number
        self.__file = im_file

    def set_number(self, number):
        self.__number = number

    def get_number(self):
        return self.__number

    def get_file(self):
        return self.__file

    def add_box(self, box):
        self.__box_list.append(box)

    def pop(self):
        if self.len() > 0:
            self.__box_list.pop()

    def del_box(self, box_id):
        for i in range(0, self.len()):
            if self.__box_list[i].get_id() == box_id:
                del self.__box_list[i]
                break

    def get_all_boxes(self):
        return self.__box_list

    def get_a_box(self, box_id):
        for i in range (0, self.len()):
            if self.__box_list[i].get_id() == box_id:
                return self.__box_list[i]
        raise ValueError('Requested box_id not in box_list')

    def len(self):
        return len(self.__box_list)

    # Sorts the list of boxes based on id number
    def sort_boxes(self):
        self.__box_list.sort(key = lambda x: x.get_id(), reverse = False)

    def print_all_xcenter(self):
        for i in range (0, self.len()):
            print(self.__box_list[i].get_xcenter())

    def print_all_id(self):
        for i in range (0, self.len()):
            print(self.__box_list[i].get_id())

    def set_box_list(self, first_frame=False):
        #im = cv2.cvtColor(np.array(self.__file), cv2.COLOR_RGB2BGR)
        im = cv2.cvtColor(self.__file, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(im, 127, 255, 0)
        blobs, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for counter, i in enumerate(blobs):
            x, y, w, h = cv2.boundingRect(i)
            if first_frame:
                box = Box(xcenter=x+w/2, ycenter=y+h/2, w=w, h=h, id=counter) # init id
                self.add_box(box)
            else:
                box = Box(xcenter=x+w/2, ycenter=y+h/2, w=w, h=h)  # add id later
                self.add_box(box)

    def draw_boxes(self, image):
        new_image = image.copy()
        for i in range(0, self.len()):
            self.__box_list[i].draw_self(new_image)
        return new_image

    def get_score_matrix(self, previous_frame):
        curr_box_list = self.__box_list
        prev_box_list = previous_frame.get_all_boxes()
        curr_num_of_boxes = self.len()
        prev_num_of_boxes = previous_frame.len()
        score_matrix = np.zeros((prev_num_of_boxes, curr_num_of_boxes))
        for r in range(0, prev_num_of_boxes):  # rows - old tracking boxes
            for c in range(0, curr_num_of_boxes):  # columns - new detected boxes
                score_matrix[r, c] = prev_box_list[r].get_overlapping_score(curr_box_list[c])

        return score_matrix

    def update_id(self, previous_frame):
        score_matrix = self.get_score_matrix(previous_frame)
        row, col = linear_sum_assignment(-score_matrix)
        for i in range(0, len(row)):
            new_ind = col[i]
            old_ind = row[i]
            curr_list = self.get_all_boxes()
            prev_list = previous_frame.get_all_boxes()
            curr_list[new_ind].set_id(prev_list[old_ind].get_id())







