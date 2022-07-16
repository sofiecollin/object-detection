# Frame class
# Contains box Objects.
# Supports the Root Class.
# Requires the Box to be imported. 
import cv2
import numpy as np
from BoxClass import Box
from scipy.optimize import linear_sum_assignment


class Frame:

    def __init__(self, number=0, box_list=None, mask_file=False, rgb_file=False):
        if not box_list:
            self.__box_list = []
        self.__number = number
        self.__mask_file = mask_file
        self.__rgb_file = rgb_file

    def set_number(self, number):
        self.__number = number

    def get_number(self):
        return self.__number

    def get_file(self):
        return self.__mask_file

    def get_rgbfile(self):
        return self.__rgb_file

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

    def get_id_list(self):
        id_list= []
        for i in range (0, self.len()):
            id_list.append(self.__box_list[i].get_id())
        return id_list

    def get_unused_id(self):
        id_list = self.get_id_list()
        unused_id = len(id_list)
        for count, id in enumerate(id_list):
            if count not in id_list:
                unused_id = count
        return unused_id

    def set_box_list(self, thresh=0):
        mask = self.__mask_file
        blobs, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for counter, i in enumerate(blobs):
            x, y, w, h = cv2.boundingRect(i)
            if w*h > thresh:
                box = Box(xcenter=x+w/2, ycenter=y+h/2, w=w, h=h, id=counter)  # init id
                self.add_box(box)

    def draw_boxes(self, image):
        for i in range(0, self.len()):
            self.__box_list[i].draw_self(image)
        return image

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

    def search_for_matches(self, previous_frame):
        unmatched_among_prev = []
        unmatched_among_curr = []

        score_matrix = self.get_score_matrix(previous_frame)
        prev_matched_indices, curr_matched_indices = linear_sum_assignment(-score_matrix)

        matched = [prev_matched_indices,curr_matched_indices]

        for row in range(0, score_matrix.shape[0]):
            if row not in prev_matched_indices:
                unmatched_among_prev.append(row)

        for col in range(0, score_matrix.shape[1]):
            if col not in curr_matched_indices:
                unmatched_among_curr.append(col)

        return matched, unmatched_among_prev, unmatched_among_curr


    def update_id(self, previous_frame):
        matched, unmatched_among_prev, unmatched_among_curr = self.search_for_matches(previous_frame)

        curr_matched_indices = matched[1]
        prev_matched_indices = matched[0]

        for i in range(0, len(matched[0])): #handle matched boxes
            curr_matched_index = curr_matched_indices[i]
            prev_matched_index = prev_matched_indices[i]
            curr_list = self.get_all_boxes()
            prev_list = previous_frame.get_all_boxes()
            curr_list[curr_matched_index].set_id(prev_list[prev_matched_index].get_id())

        temp_frame = previous_frame
        for i in range(0,len(unmatched_among_curr)): #handle incoming box
            curr_list = self.get_all_boxes()
            curr_list[unmatched_among_curr[i]].set_id(temp_frame.get_unused_id())
            temp_box = Box(id=temp_frame.get_unused_id())
            temp_frame.add_box(temp_box)

        self.sort_boxes()







