from handle_blobs import *

image = cv2.imread('blobs.png')

x_list, y_list, w_list, h_list, num = get_blobs_dim(image)

id_list = [(255, 0, 0), (0, 255, 0)]

image_new = image.copy()
image_new = draw_boundingboxes(image_new, x_list, y_list, w_list, h_list, id_list)

cv2.imshow('bounding boxes', image_new)
cv2.waitKey(0)
