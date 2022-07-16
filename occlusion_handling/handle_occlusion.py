import numpy as np
import cv2
from occlusion_handling.optic_flow import get_optic_flow, draw_optic_flow
from occlusion_handling.color_hist import get_color_vectors, compare_hist
import imutils
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
from HandlingData.BlobClass import Blob
from HandlingData.BoxClass import Box

# When blobs are in occlusion
def occlusion_handling(prev_frame, current_frame):
    rgb_image = current_frame.get_rgbfile()

    # Split the blobs assign id to blobs in occlusion
    all_splitted_blobs = blob_seperation(prev_frame, current_frame)

    for i, splitted_blobs in enumerate(all_splitted_blobs):

        occluded_blobs = current_frame.get_occluded_blobs()[i]
        occluding_blobs = current_frame.get_occluding_blobs()[i]

        all_occ_blobs = np.concatenate([occluding_blobs,occluded_blobs]) 

        # Calc new id based on optic flow
        new_ids = new_id_by_flow(prev_frame, current_frame, all_occ_blobs, splitted_blobs)
        
        # Do color hist if ids are occuring more than once
        if len(set(new_ids)) != len(new_ids): # Check if any id occurs more than once
            print("Multiple of same id!")
            new_ids = new_id_by_color(prev_frame, current_frame, all_occ_blobs, splitted_blobs)

        # TODO: Store to later if multiple of same id with both methods
        if len(set(new_ids)) != len(new_ids):
            print("All the same - should store for later")
            return

        if -1 in new_ids:
            return

        # Assign ids to the new blobs and boxes
        assign_id(prev_frame, current_frame, all_occ_blobs, splitted_blobs, new_ids)
        
    return rgb_image

def prepare_occlusion(prev_frame, current_frame):
    print("preparing for occlusion")
    hists = get_color_vectors(current_frame)

    #compare_hist(prev_frame, current_frame)

    flow = get_optic_flow(prev_frame, current_frame)
    
    rgb_image = current_frame.get_rgbfile()
    
    rgb_image = draw_optic_flow(current_frame, flow)
    return rgb_image

# Checks distance to other blobs and sets the frame to is_soon_in_occlusion
def distance_check(frame):
    distance_thresh = 10

    blobs_list = frame.get_all_blobs()
    if len(blobs_list) < 2:
        return

    id_list = frame.get_id_list()
    score_matrix = np.ones((len(blobs_list),len(blobs_list)))*np.inf

    # Loop through and set min distance to every other blob in each blob
    for i, blob in enumerate(blobs_list):
        for j, other_blob in enumerate(blobs_list):
            if i == j:
                continue
            distance = blob.get_contour_distance(other_blob)

            # Set distance to the slot of the id
            blob.set_min_distance_to_blob(distance, other_blob.get_id()) # Not needed?
            other_blob.set_min_distance_to_blob(distance, blob.get_id())
            score_matrix[i,j] = distance

    all_near_occlusions = []
    checked = [] # Use to keep track of already visited blobs

    # Check the matrix for distances that are smaller than the threshold
    # Then serach that blobs samllest distances reccursively
    for col in range(score_matrix.shape[0]):
        if col not in checked:
            checked.append(col)
            blob_group = []
            blob_group = check_matrix(frame, col, checked, score_matrix, blob_group, distance_thresh)
            if blob_group:
                blob_group.append(col)
                corr_ids = []
                for b in blob_group:
                    corr_ids.append(id_list[b])
                all_near_occlusions.append(corr_ids)

    if all_near_occlusions:
        frame.set_is_soon_in_occlusion(True)
        frame.set_soon_occluding_blobs(all_near_occlusions)

# Reccursive matrix checker to find all inbound occusions in the image
def check_matrix(frame, col, checked, score_matrix, blob_group, distance_thresh):
    for row in range(score_matrix.shape[0]):
        if row == col or row in checked:
            continue
        if score_matrix[col,row] < distance_thresh:
            checked.append(row)
            blob_group.append(row)
            # Set row a column
            check_matrix(frame, row, checked, score_matrix, blob_group, distance_thresh)
    return blob_group

# Checks if the current frame has any ongoing occlusions between blobs
def occlusion_check(prev_frame, current_frame):
    if prev_frame.get_is_soon_in_occlusion():
        occluding_blobs = prev_frame.get_soon_occluding_blobs()
       
        # Checks if occluding blobs are in the current frame blob list
        # If one is not in the list, is is probably occluded
        for i in occluding_blobs[0]:
            is_in_list = np.zeros(np.max(i)+1)
            for b in i:
                blob_in_list = False
                for j in current_frame.get_blob_id_list():
                    if b == j:
                        blob_in_list = True
                        break
                if blob_in_list:
                    is_in_list[b] = 1
                else:
                    is_in_list[b] = -1

            # Return if all blobs are still in the current blob list
            if -1 not in is_in_list:
                print("Phew, no occlusion occured")
            else:
                # Add blob to occluded or occluding blob list in frame
                current_frame.set_is_in_occlusion(True)
                occluding_id = np.where(is_in_list > 0)[0]
                occluded_id = np.where(is_in_list < 0)[0]
                current_frame.add_occluding_blobs(occluding_id)
                current_frame.add_occluded_blobs(occluded_id)

def blob_seperation(prev_frame, current_frame):
    mask = prev_frame.get_file()
    all_occluding_blobs = current_frame.get_occluding_blobs()

    splitted_blobs = []

    # Do seperating for every number of blobs that are covered
    for bg, occluding_blobs in enumerate(all_occluding_blobs):

        # TODO: Split blobs in a good way! Or just store for later
        if len(occluding_blobs) < 1:  # Prevent out of range 
                break
        occluding_blobs = occluding_blobs[0]

        #print("Seperatin " + str(occluding_blobs) + "...")
        blob = current_frame.get_a_blob(occluding_blobs)
        contour = blob.get_contour()

        # Draw a black line on the mask to seperate in the middle
        blob_centerx = blob.get_xcenter()
        blob_centery = blob.get_ycenter()
        x, y, w, h = cv2.boundingRect(contour)

        mid_top_seperator = [blob_centerx, int(blob_centery-h/2)]
        mid_bot_seperator = [blob_centerx, int(blob_centery+h/2)]

        contour_splitter = np.asarray([mid_top_seperator, mid_bot_seperator])

        mask = current_frame.get_file()

        cv2.drawContours(mask, [contour_splitter], -1, (0, 0, 0), 2)

        # Find the contours in the area of old contour
        temp_mask = np.zeros((mask.shape[0], mask.shape[1]), np.uint8)
        cv2.rectangle(temp_mask, (x,y), (x+w, y+h), (255,255,255), -1)

        mask = mask*temp_mask

        # The splitted contour should become multiple contous and get assigned new (previous) ids
        splitted_contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        splitted_blob_group = []

        # Add the splitted contour as a blob
        for i, c in enumerate(splitted_contours):
            x, y, w, h = cv2.boundingRect(c)
            # Skip if junk
            if h < 10 or w < 10:
                continue
            center_pos, blob_indicies = current_frame.set_blob_props(current_frame.get_file(), c, x, y, w, h)
            blob = Blob(xcenter=center_pos[0], ycenter=center_pos[1], contour=c, indicies=blob_indicies, id=-1-i)  # init neg id
            splitted_blob_group.append(blob)
        splitted_blobs.append(splitted_blob_group)

    return splitted_blobs

def new_id_by_color(prev_frame, current_frame, all_occ_blobs, splitted_blobs):
    # Get color hist for seperated blobs and assign id based of that
    new_ids = []
    current_hists = get_color_vectors(current_frame, splitted_blobs)
    for c, sb in enumerate(splitted_blobs):
        max_idx = -1
        max_hist = 0
        for r in all_occ_blobs:
            hist_compare = cv2.compareHist(prev_frame.get_a_blob(r).get_color_hist(), current_hists[c], cv2.HISTCMP_CORREL)
            if hist_compare > max_hist:
                max_hist = hist_compare
                max_idx = r
        new_ids.append(max_idx)
        
    return new_ids

#Get the flow for the seperated blobs and assign id from that
def new_id_by_flow(prev_frame, current_frame, all_occ_blobs, splitted_blobs):
    get_optic_flow(prev_frame, current_frame, splitted_blobs)

    new_ids = []
    for i, b in enumerate(splitted_blobs):
        min_angle = np.inf
        min_idx = -1
        curr_vector = b.get_direction_vector()
        for j in all_occ_blobs:
            # Compute angle and take the smallest
            prev_vector = prev_frame.get_a_blob(j).get_direction_vector()
            curr_vector = b.get_direction_vector()
            unit_vector_prev = np.squeeze(np.asarray(prev_vector / np.linalg.norm(prev_vector)))
            unit_vector_curr = np.squeeze(np.asarray(curr_vector / np.linalg.norm(curr_vector)))
            dot_product = np.dot(unit_vector_prev, unit_vector_curr)
            angle = np.arccos(dot_product)
            if angle < min_angle:
                min_angle = angle
                min_idx = j
        new_ids.append(min_idx)

    return new_ids

# Assign is based on the new_id array  
def assign_id(prev_frame, current_frame, all_occ_blobs, splitted_blobs, new_ids):
    for blob in all_occ_blobs:
        if blob in new_ids:
            prev_blob = prev_frame.get_a_blob(blob)
            current_frame.del_blob(prev_blob.get_id())
            current_frame.del_box(prev_blob.get_id())

    for c, sb in enumerate(splitted_blobs):
        sb.set_id(new_ids[c])
        current_frame.add_blob(sb)

        x, y, w, h = cv2.boundingRect(sb.get_contour())

        box = Box(xcenter=x+w/2, ycenter=y+h/2, w=w, h=h, id=sb.get_id())  # init id
        current_frame.add_box(box)
        current_frame.sort_boxes()
        current_frame.sort_blobs()

