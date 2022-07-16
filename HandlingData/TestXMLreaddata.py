import xml.etree.ElementTree as ET
import numpy as np

# Idea:
# Write a program that reads an xml file and prepares it in order to
# be used in evaluation
# Flow: Read a file.
# Store the data in an array matching frames
# Make it an object so that we can get the data we need
# OBS, define this in parallell with the evaluation part


# TODO
# write get_a_box, takes what? A frame, an id?
# write compare_boxes
# write all calculations needed to get a box

def read_xml(path):
    return ET.parse(path)

path = 'wk1gt.xml'
tree = read_xml(path)

root = tree.getroot()

#Gets a specific frame from root
def get_a_frame(root, frameId):
    if (ET.iselement(root)):
        for frame in root.iter('frame'):
            if int(frame.get('number')) == frameId:
                return frame

#Get a list of all frames from root
def get_frame_list(root):
    if (ET.iselement(root)):
        frame_list = []
        for frame in root.iter('frame'):
            frame_list.append(frame)
        return frame_list

def print_some_objects(root):
    i = 0
    for box in root.iter('box'):
        if i < 30:
            print(box.attrib)
            i += 1
        else:
            break

# Takes a box, returns stats
# What is orientation for the boxes?
def get_box_data(box):
    height = box.get('h')
    width = box.get('w')
    xcenter = box.get('xc')
    ycenter = box.get('yc')
    return height, width, xcenter, ycenter

list = get_frame_list(root)
frame = get_a_frame(root, 240)
print_some_objects(root)
