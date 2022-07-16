from HandlingData.dataHandling import import_image_sequence
from bg_modelling.gaussian_mix.gaussian_mix_vectorized import GMM
from occlusion_handling.handle_occlusion import occlusion_handling, distance_check, prepare_occlusion, occlusion_check
from utils.clean_mask import clean_mask
import numpy as np
import PIL.Image
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import settings
from utils.image_loader import load_image
import sys
import xml.etree.ElementTree as ET
sys.path.append("HandlingData")
#from FrameClass import Frame
from FrameClass_P import Frame
from RootClass import Root
from BoxClass import Box
import cv2

if __name__ == "__main__":
    # Configure GMM with first frame
    first_frame = load_image(1)

    gmm = GMM(first_frame)
    prev_frame = Frame()

    # Settings for plot
    plt.set_cmap("gray")
    ax1 = plt.subplot(111)
    im1 = ax1.imshow(first_frame)

    # Configure Root with ground truth data
    root = Root()
    if settings.IS_GROUND_TRUTH:
        if settings.GROUND_TRUTH_TYPE == 'xml':
            # Illustration: configure with .xml file
            root.add_xml_root_frames_n_boxes(ET.parse(settings.GROUDN_TRUTH_PATH).getroot(), 'gt')
        if settings.GROUND_TRUTH_TYPE == 'txt':
            # Illustration: configure with .txt file, switch test.txt for another .txt file
            root.add_MOT_root_frames_n_boxes(settings.GROUDN_TRUTH_PATH, 'gt')


    def update(i):
        global prev_frame
        print(i)
        
        # Read frame
        frame = load_image(i)

        # Gaussian mixture model
        B_hat = gmm.next(frame)

        # Shadow segmentation
        Sp = gmm.shadow(B_hat, frame)

        B_hat = Sp
            
        # Morphological operations
        curr_mask = 1-(B_hat)
        curr_mask = clean_mask(curr_mask, thresh_to_draw = 80)

        current_frame = Frame(number = i, mask_file=curr_mask,rgb_file=frame)
        root.add_frame(current_frame, 'det')
        
        current_frame.set_box_blob_list(thresh = 10)

        if i==settings.FRAMES_START:
            prev_frame=current_frame

        #current_frame.update_id(prev_frame)
        if i != settings.FRAMES_START:
            current_frame.update_id(root.get_a_frame(i-1, 'det'))

        #print("Currently used ids': {ids} ".format(ids=current_frame.get_id_list()))
        #print("First unused id: {id} ".format(id=current_frame.get_unused_id()))
        occlusion_check(prev_frame, current_frame)
        if current_frame.get_is_in_occlusion():
            print("DO OCCLUSION HANDLING")
            occlusion_handling(prev_frame, current_frame)

        distance_check(current_frame)
        if current_frame.get_is_soon_in_occlusion(): # and ~current_frame.get_is_in_occlusion(): needed?
            print("PREPARE FOR OCCLUSION")
            frame = prepare_occlusion(prev_frame, current_frame)

        im = current_frame.draw_boxes(frame)
        prev_frame = current_frame

        im1.set_data(im)
        # Write resulting images to a folder
        #cv2.imwrite('/Users/pontusarnesson/Desktop/cv_video/intro-gif/fake_blobs' + '{:03d}.jpg'.format(i),im*255)

    ani = FuncAnimation(plt.gcf(), update, frames=range(settings.FRAMES_START, settings.FRAMES_END), interval=1, repeat=False)
    plt.show()

    #print("Precision, recall: ", root.get_results())
    print("TP, FP, FN: ", root.get_summed_Scores())

    if settings.IS_WRITE_TO_CSV:
        root.write_data(settings.CSV_FILE_NAME)

    # root.get_a_frame(103,'gt').print_all_id()
    # root.get_a_frame(103,'det').print_all_id()

    #print(root.get_a_frame(103, 'gt').get_a_box(0).get_xcenter())
    #print(root.get_a_frame(103, 'det').get_a_box(2).get_xcenter())
    #print(root.get_a_frame(103, 'gt').get_a_box(0).get_ycenter())
    #print(root.get_a_frame(103, 'det').get_a_box(2).get_ycenter())

    #print(root.get_Frame_Scores(103))
    