# The root class
# TODO. Read from xml. Compare two frame, find common box id n stuff

from FrameClass import Frame
from BoxClass import Box
import xml.etree.ElementTree as ET

class Root:
    def __init__(self):
        self.frame_list = []

    def add_frame(self, frame):
        self.frame_list.append(frame)

    def len(self):
        return len(self.frame_list)

    def print_all_numbers(self):
        for i in range (0, self.len()):
            print(self.frame_list[i].get_number())

    def pop(self):
        if (self.len() > 0):
            self.frame_list.pop()

    def del_frame(self, frame_number):
        for i in range(0, self.len()):
            if self.frame_list[i].get_number() == frame_number:
                del self.frame_list[i]
                break

    def get_all_frames(self):
        return self.frame_list

    def get_a_frame_index(self,i):
        return self.frame_list[i]


    def get_a_frame(self, frame_number):
        for i in range (0, self.len()):
            if self.frame_list[i].get_number() == frame_number:
                return self.frame_list[i]
                break
        raise ValueError('Requested frame_number not in frame_list')

    # Sorts the list of frames based on number
    def sort_frames(self):
        self.frame_list.sort(key = lambda x: x.get_number(), reverse = False)


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
        frame = Frame([], number = number)
        return frame

    def add_frame_boxes(self,objFrame, xmlFrame):
        for xmlBox in xmlFrame.iter('object'):
            objFrame.add_box(self.create_xml_box(xmlBox))

    def add_xml_root_frames_n_boxes(self,root):
        for xmlFrame in root.iter('frame'):
            tempFrame = self.create_xml_frame(xmlFrame)
            self.add_frame(tempFrame)
            self.add_frame_boxes(tempFrame,xmlFrame)


myRoot = Root()
myBox = Box(15, 20, 4, 3, 0, 1)
myBox2 = Box(id = 2)
myBox14 = Box(id = 14)
myBox12 = Box(id = 12)

myBox20 = Box(id = 20)
myBox99 = Box(id = 99)
myBox7 = Box(id = 7)
myBox0 = Box(id = 0)

myFrame = Frame([],number = 1)
myFrame.add_box(myBox)
myFrame.add_box(myBox2)
myFrame.add_box(myBox14)
myFrame.add_box(myBox12)

myFrame3 = Frame([],number = 3)

myFrame3.add_box(myBox20)
myFrame3.add_box(myBox99)
myFrame3.add_box(myBox7)
myFrame3.add_box(myBox0)

myRoot.add_frame(myFrame3)
myRoot.add_frame(myFrame)
# myRoot.print_all_numbers()


tree = ET.parse('wk1gt.xml')
root = tree.getroot()

for frame in root.iter('frame'):
    if int(frame.get('number')) == 240:
        f240 = frame

boxObj = f240.find('objectlist').find('object')


myLittleBox = myRoot.create_xml_box(boxObj)

myLittleFrame = myRoot.create_xml_frame(f240)
myRoot.add_frame(myLittleFrame)
myRoot.get_a_frame(240).print_all_id()


myRoot.add_frame_boxes(myRoot.get_a_frame(240),f240)

myRoot2 = Root()
myRoot2.print_all_numbers()
myRoot2.add_xml_root_frames_n_boxes(root)
myRoot2.print_all_numbers()
for i in range(0, myRoot2.len()):
    myRoot2.get_a_frame_index(i).print_all_id()


#Hejsan Hoppsan
