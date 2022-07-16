from handle_blobs import *

image = cv2.imread('blobs.png')
image2 = cv2.imread('blobs_moved2.png')

score_matrix = get_score_matrix(image,image2)
print(score_matrix)


