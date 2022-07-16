import numpy as np
import PIL.Image
from matplotlib import pyplot as plt
from matplotlib.animation import ArtistAnimation
import math
import time

# TRY DIFFERENT LAMB!!!
# JAPP, det är lamb som är superkänslig
# Ska match sättas true inne i loopen?

import cython
@cython.boundscheck(False)
cpdef double[:, :] gaussian_mix():
    cdef int K = 3
    
    cdef double[:, :, :, :] my = 0.5 * np.ones((288, 384, K, 3))

    cdef double[:, :, :, :] sigma_squared = 0.01 * np.ones((288, 384, K, 3))
    cdef double[:] sigma_init_squared = np.array((0.1, 0.1, 0.1))
    
    cdef double[:, :, :] w = np.ones((288, 384, K)) / K
    cdef double w_init = 0.1
    
    cdef double lamb = 2.5
    cdef double T = 0.8
    cdef double alpha = 1.0/100.0 # LEK MED DENNA

    cdef double[:, :] B_hat = np.zeros((288, 384))
    cdef double[:, :] B = np.zeros((288, 384))

    cdef double[:, :, :] p = np.zeros((288, 384, K))

    cdef double[:] c = np.zeros(K)

    cdef double[:, :, :] frame = np.zeros((288, 384, 3))

    cdef double dk_squared

    plt.set_cmap("gray")

    #frames = []
    #fig = plt.figure()

    cdef int f, x, y, k, m, aa, i
        
    for f in range(5, 35):
        print(f)
        file_name = '../../frames/Walk1{:03d}.jpg'.format(f)

        frame_np = np.asarray(PIL.Image.open(file_name))
        frame_np = np.asarray(frame) / 255.0

        frame = frame_np
                
        for x in range(frame.shape[0]):
            for y in range(frame.shape[1]):
                match = False # TRY MOVE THIS OUTSIDE AND DO MANY FRAMES
                
                for k in range(K):
                    dk_squared = 0.0
                    for aa in range(3):
                        dk_squared += pow(frame[x, y, aa] - my[x, y, k, aa], 2) / sigma_squared[x, y, k, aa]

                    if math.sqrt(dk_squared) < lamb: #Square root?                        
                        if not match:
                            #print("HEJ 1")
                            m = k
                        elif w[x, y, k]/math.sqrt(np.linalg.norm(sigma_squared[x, y, k])) > (w[x, y, m]/math.sqrt(np.linalg.norm(sigma_squared[x, y, m]))):
                            #print("HEJ 2")
                            m = k
                                            
                        match = True
                
                if not match:
                    m = K - 1
                    w[x, y, m] = w_init
                    for aa in range(3):
                        my[x, y, m, aa] = frame[x,y,aa]
                    sigma_squared[x, y, m] = sigma_init_squared
                else:
                    w[x, y, m] = (1 - alpha)*w[x, y, m] + alpha
                    p[x, y, m] = alpha / w[x, y, m]
                    
                    for aa in range(3):
                        my[x, y, m, aa] = (1-p[x, y, m])*my[x, y, m, aa] + p[x, y, m]*frame[x,y, aa]
                        sigma_squared[x, y, m, aa] = (1-p[x, y, m])*sigma_squared[x, y, m, aa] + (p[x, y, m]*(frame[x,y, aa]-my[x, y, m, aa])) * (frame[x,y, aa] - my[x, y, m, aa])

                for aa in range(K):
                    w[x, y, aa] = w[x, y, aa] / w[x, y, aa]

                for k in range(K):
                    c[k] = w[x, y, k]/math.sqrt(np.linalg.norm(sigma_squared[x, y, k]))

                if match:
                    #print(c)
                    indices = np.argsort(-np.asarray(c))
                    #print(indices)
                    #print("BEFORE", w[x, y])

                    for aa in range(K):
                        w[x, y, aa] = w[x, y, indices[aa]]
                        my[x, y, aa] = my[x, y, indices[aa]]
                    #print("AFTER", w[x,y])
                    
                    #sigma_squared[x, y] = sigma_squared[x, y, indices]
                
                i = 0

                for i in range(K):
                    #print("W", w[x, y])
                    if np.sum(w[x, y, 0:i+1]) > T:
                        break
                    #print("SUM", np.sum(w[x, y, 0:i+1]))
                
                B[x, y] = i + 1 #???

        for x in range(frame.shape[0]):
            for y in range(frame.shape[1]):
                B_hat[x, y] = 0
                for k in range(int(B[x, y])):
                    dk_squared = 0.0
                    for aa in range(3):
                        dk_squared += pow(frame[x, y, aa] - my[x, y, k, aa], 2) / sigma_squared[x, y, k, aa]
                    if np.sqrt(dk_squared) < lamb:
                        B_hat[x,y] = 1

        #plt.imshow(B_hat)
        #plt.show()
        #frames.append([plt.imshow(B_hat, animated=True)])

    #ani = ArtistAnimation(fig, frames, interval=50, blit=True,
                                #repeat_delay=1000)
    #plt.show()

    return B_hat

gaussian_mix()