# Frame class
# Contains box Objects.
# Supports the Root Class.
# Requires the Box to be imported. 
import cv2
import numpy as np
from BoxClass import Box
from BlobClass import Blob
from scipy.optimize import linear_sum_assignment


class Frame:

    def __init__(self, number=0, box_list=None, blob_list=None, mask_file=False, rgb_file=False):
        if not box_list:
            self.__box_list = []
        if not blob_list:
            self.__blob_list = []
        self.__number = number
        self.__mask_file = mask_file
        self.__rgb_file = rgb_file
        self.__is_soon_in_occlusion = False
        self.__is_in_occlusion = False
        self.__soon_occluding_blobs = []
        self.__occluding_blobs = []
        self.__occluded_blobs = []

    def set_number(self, number):
        self.__number = number

    def set_is_soon_in_occlusion(self, b):
        self.__is_soon_in_occlusion = b

    def set_is_in_occlusion(self, b):
        self.__is_in_occlusion = b

    def set_soon_occluding_blobs(self, blobs):
        self.__soon_occluding_blobs.append(blobs)

    def add_occluding_blobs(self, blobs):
        self.__occluding_blobs.append(blobs)

    def add_occluded_blobs(self, blobs):
        self.__occluded_blobs.append(blobs)

    def get_is_soon_in_occlusion(self):
        return self.__is_soon_in_occlusion

    def get_is_in_occlusion(self):
        return self.__is_in_occlusion

    def get_soon_occluding_blobs(self):
        return self.__soon_occluding_blobs

    def get_occluding_blobs(self):
        return self.__occluding_blobs

    def get_occluded_blobs(self):
        return self.__occluded_blobs

    def get_all_blob_contours(self):
        contours = []
        blob_list = self.get_all_blobs()
        for blob in blob_list:
            contours.append(blob.get_contour())
        return contours

    def get_number(self):
        return self.__number

    def get_file(self):
        return self.__mask_file

    def get_rgbfile(self):
        return self.__rgb_file

    def add_box(self, box):
        self.__box_list.append(box)

    def add_blob(self, blob):
        self.__blob_list.append(blob)

    def pop(self):
        if self.len() > 0:
            self.__box_list.pop()

    def del_box(self, box_id):
        for i in range(0, self.len()):
            if self.__box_list[i].get_id() == box_id:
                del self.__box_list[i]
                break

    def del_blob(self, blob_id):
        for i in range(0, self.blob_len()):
            if self.__blob_list[i].get_id() == blob_id:
                del self.__blob_list[i]
                break

    def del_all_boxes(self):
        self.__box_list = []

    def del_all_blobs(self):
        self.__blob_list = []

    def get_all_boxes(self):
        return self.__box_list

    def get_all_blobs(self):
        return self.__blob_list

    def get_a_box(self, box_id):
        for i in range (0, self.len()):
            if self.__box_list[i].get_id() == box_id:
                return self.__box_list[i]
        raise ValueError('Requested box_id not in box_list')

    def get_a_blob(self, blob_id):
        for i in range (0, self.blob_len()):
            if self.__blob_list[i].get_id() == blob_id:
                return self.__blob_list[i]
        raise ValueError('Requested blob_id not in blob_list')

    def len(self):
        return len(self.__box_list)

    def blob_len(self):
        return len(self.__blob_list)

    # Sorts the list of boxes based on id number
    def sort_boxes(self):
        self.__box_list.sort(key = lambda x: x.get_id(), reverse = False)

    # Sorts the list of blobs based on id number
    def sort_blobs(self):
        self.__blob_list.sort(key = lambda x: x.get_id(), reverse = False)

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

    def get_blob_id_list(self):
        blob_id_list = []
        for i in range (0, self.blob_len()):
            blob_id_list.append(self.__blob_list[i].get_id())
        return blob_id_list

    def get_unused_id(self):
        id_list = self.get_id_list()
        unused_id = len(id_list)
        for count, id in enumerate(id_list):
            if count not in id_list:
                unused_id = count
        return unused_id

    def set_box_blob_list(self, thresh=0):
        mask = self.__mask_file
        blobs, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for counter, i in enumerate(blobs):
            x, y, w, h = cv2.boundingRect(i)
            if w*h > thresh:
                box = Box(xcenter=x+w/2, ycenter=y+h/2, w=w, h=h, id=counter)  # init id
                self.add_box(box)

                center_pos, blob_indicies = self.set_blob_props(mask, i, x, y, w, h)
                blob = Blob(xcenter=center_pos[0], ycenter=center_pos[1], contour=i, indicies=blob_indicies, id=counter)  # init id
                self.add_blob(blob)

    def set_blob_props(self, mask, c, x, y, w, h):
        M = cv2.moments(c)
        blob_indicies = []
    
        # Get blob indicies for average
        for j in range(y, y + h):
            for k in range(x, x + w):
                if mask[j,k] == 1:
                    blob_indicies.append([j,k]) 
        
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        center_pos = [cX, cY]
        return center_pos, blob_indicies

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

            # For blobs
            curr_blob_list = self.get_all_blobs()
            curr_blob_list[curr_matched_index].set_id(prev_list[prev_matched_index].get_id())

        for i in range(0,len(unmatched_among_curr)): #handle incoming box
            curr_list = self.get_all_boxes()
            new_id = self.get_unused_id()
            curr_list[unmatched_among_curr[i]].set_id(new_id)

            # For blobs
            curr_blob_list = self.get_all_blobs()
            curr_blob_list[unmatched_among_curr[i]].set_id(new_id)

        self.sort_boxes()
        self.sort_blobs()







