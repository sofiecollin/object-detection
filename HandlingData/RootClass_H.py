# The Root class' purpose is to create a data structure that can easily be accept
# labeling boxes from several data structures.
# Currently supported datasets: CAVIAR - xml
# The Root class contains a list which can be filled with Frame objects and
# requires the Frame and Box classes.
# There are also functions that manipulates the list
# The main function is add_xml_root_frames_n_boxes, which takes an xml root
# and adds all its frames and their boxes to itself as objects.
# More data structures will be supported in the future.

from FrameClass import Frame
from BoxClass import Box
import xml.etree.ElementTree as ET
import math
import settings
import copy

class Root:
    def __init__(self, gt_list = None, det_list = None):
        if not gt_list:
            self.gt_list = []
        if not det_list:
            self.det_list = []

    def get_gt(self):
        return self.gt_list

    def get_det(self):
        return self.det_list

    def add_frame(self, frame, type):
        if type == 'gt':
            self.gt_list.append(frame)
        if type == 'det':
            self.det_list.append(frame)

    def len(self, type):
        if type == 'gt':
            return len(self.gt_list)
        if type == 'det':
            return len(self.det_list)

    def print_all_numbers(self, type):
        if type == 'gt':
            for i in range (0, self.len(type)):
                print(self.gt_list[i].get_number())
        if type == 'det':
            for i in range (0, self.len(type)):
                print(self.det_list[i].get_number())

    def pop(self, type):
        if type == 'gt':
            if (self.len(type) > 0):
                self.gt_list.pop()
        if type == 'det':
            if (self.len(type) > 0):
                self.det_list.pop()

    def del_frame(self, frame_number, type):
        if type == 'gt':
            for i in range(0, self.len(type)):
                if self.gt_list[i].get_number() == frame_number:
                    del self.gt_list[i]
                    break
        if type == 'det':
            for i in range(0, self.len(type)):
                if self.det_list[i].get_number() == frame_number:
                    del self.det_list[i]
                    break

    def get_a_frame(self, frame_number, type):
        if type == 'gt':
            for i in range (0, self.len(type)):
                if self.gt_list[i].get_number() == frame_number:
                    return self.gt_list[i]
            raise ValueError('Requested frame_number not in frame_list')
        if type == 'det':
            for i in range (0, self.len(type)):
                if self.det_list[i].get_number() == frame_number:
                    return self.det_list[i]
            raise ValueError('Requested frame_number not in frame_list')

    # Sorts the list of frames based on number
    def sort_frames(self,type):
        if type == 'gt':
            self.gt_list.sort(key = lambda x: x.get_number(), reverse = False)
        if type == 'det':
            self.det_list.sort(key = lambda x: x.get_number(), reverse = False)

    # Takes an xmlBox and returns an objBox.
    def create_xml_box(self,xmlBox):
        id = int(xmlBox.attrib['id'])
        orientation = int(xmlBox.find('orientation').text)
        boxObject = xmlBox.find('box')

        h = int(boxObject.attrib['h'])
        w = int(boxObject.attrib['w'])
        xc = int(boxObject.attrib['xc'])
        yc = int(boxObject.attrib['yc'])

        box = Box(id = id, orientation = orientation, h = h, w = w,xcenter = xc, ycenter = yc)
        return box

    # Takes an xmlFrame and returns an objFrame
    def create_xml_frame(self,xmlFrame):
        number = int(xmlFrame.attrib['number'])
        frame = Frame(number = number)
        return frame

    #Adds all boxes from an xml frame to an objFrame. Should perhaps be included in create_xml_frame
    def add_frame_boxes(self,objFrame, xmlFrame):
        for xmlBox in xmlFrame.iter('object'):
            objFrame.add_box(self.create_xml_box(xmlBox))

    # Adds all frames and their boxes. Takes a xml root
    def add_xml_root_frames_n_boxes(self,root, type):
        for xmlFrame in root.iter('frame'):
            tempFrame = self.create_xml_frame(xmlFrame)
            self.add_frame(tempFrame, type)
            self.add_frame_boxes(tempFrame,xmlFrame)

    def create_MOT_box(self,line_arr):
        id = int(line_arr[1])
        w = int(line_arr[4])
        h = int(line_arr[5])
        xc = int(line_arr[2])+int(math.floor(w/2))
        yc = int(line_arr[3]) +int(math.floor(h/2))

        box = Box(id = id, orientation = 0, h = h, w = w,xcenter = xc, ycenter = yc)
        return box

    def add_MOT_root_frames_n_boxes(self, path, type):
        data = open(path)
        line = data.readline()
        curr_frame = 0
        # While not EOF
        while len(line) > 0:
            line_arr = line.split(',')
            frame_nr = int(line_arr[0])
            # Test if we've reached a new frame, if so add it
            if curr_frame != frame_nr:
                frame = Frame(number = frame_nr)
                self.add_frame(frame, type)
                curr_frame = frame_nr

            box = self.create_MOT_box(line_arr)
            if type == 'gt':
                self.gt_list[-1].add_box(box)
            if type == 'det':
                self.det_list[-1].add_box(box)
            line = data.readline()
        data.close()

    def get_Frame_Scores(self,number):
        TP = 0
        FP = 0
        box_match = False
        det_boxes = copy.deepcopy(self.get_a_frame(number,'det').get_all_boxes())
        gt_boxes = copy.deepcopy(self.get_a_frame(number,'gt').get_all_boxes())
        #Loop over all boxes in det
        for i in range(0, len(det_boxes)):
            curr_box = det_boxes[i]

            #Loop over all boxes in gt
            for j in range(0, len(gt_boxes)):
                # If id match, test if true or neg pos, add corresponding
                # remove gt_box and set box_match to true
                if curr_box.get_id() == gt_boxes[j].get_id():
                    if (curr_box.get_overlapping_score(gt_boxes[j]) >= 0.2):
                        TP += 1
                    else:
                        FP += 1
                    del gt_boxes[j]
                    box_match = True
                    break
            #If we haven't found a box match for the det box, cout up FP
            if not box_match:
                FP = FP + FP
            box_match = False

        # Since gt_boxes are deleted whenever they're matched, the rest of them
        # will match upp to the number of False negatives
        FN = len(gt_boxes)
        return TP, FP, FN, TP_score

    def get_Frame_Scores_real(self,number):
        det_frame = self.get_a_frame(number,'det')
        gt_frame = self.get_a_frame(number,'gt')
        TP = 0
        FP = 0
        FN = 0
        TP_overlay = 0
        score_matrix = det_frame.get_score_matrix(gt_frame)
        matched, gt_unmatched, det_unmatched = det_frame.search_for_matches(gt_frame)
        gt_matched = matched[0]
        det_matched = matched[1]
        for i in range (0, len(matched[0])):
            if score_matrix[gt_matched[i],det_matched[i]] >= 0.2:
                TP += 1
                TP_overlay += score_matrix[gt_matched[i],det_matched[i]]
                #Calculate id switches and then add to avg tp-overlay
            elif score_matrix[gt_matched[i],det_matched[i]] < 0.0000001:
                gt_unmatched.append(gt_matched[i])
                det_unmatched.append(det_matched[i])
            else:
                FP += 1
        FP += len(det_unmatched)
        FN += len(gt_unmatched)
        return TP, FP, FN, TP_overlay

    def get_summed_Scores(self):
        TP_sum = 0
        FP_sum = 0
        FN_sum = 0
        TP_overlay_sum = 0
        for i in range(settings.FRAMES_START, settings.FRAMES_END):
            TP, FP, FN, TP_overlay= self.get_Frame_Scores_real(i)
            TP_sum += TP
            FP_sum += FP
            FN_sum += FN
            TP_overlay_sum += TP_overlay
            if TP != 0:
                avg_TP = TP_overlay_sum/TP_sum
        return TP_sum, FP_sum, FN_sum, avg_TP

    def get_results(self):
        TP, FP, FN, avg_TP = self.get_summed_Scores()
        Precision = TP/(TP+FP)
        Recall = TP/(TP+FN)
        return Precision, Recall, avg_TP

