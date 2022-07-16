import cv2


def get_centroids_for_blobs(binary_frame):
    m = cv2.moments(binary_frame)
    x = int(m["m10"] / m["m00"])
    y = int(m["m01"] / m["m00"])

    return x, y


def get_blobs_dim(binary_frame):
    im = cv2.cvtColor(binary_frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(im, 127, 255, 0)
    blobs, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    x_list = []
    y_list = []
    w_list = []
    h_list = []
    for i in blobs:
        x, y, w, h = cv2.boundingRect(i)
        x_list.append(x)
        y_list.append(y)
        w_list.append(w)
        h_list.append(h)

    return x_list,y_list,w_list,h_list


def draw_boundingboxes(image, x_list,y_list,w_list,h_list, id_list):
    for i in range(0, len(x_list)):
        cv2.rectangle(image, (x_list[i], y_list[i]), (x_list[i] + w_list[i], y_list[i] + h_list[i]), id_list[i], 2)

    return image



