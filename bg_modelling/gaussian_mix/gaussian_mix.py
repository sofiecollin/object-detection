import numpy as np
import PIL.Image
from matplotlib import pyplot as plt
from matplotlib.animation import ArtistAnimation
from save_frames import save_frames
import settings
from utils.image_loader import load_image

def gaussian_mix():
    frame1 = load_image(1)

    K = 4
    D = 3

    lamb = 2.5
    T = 0.8
    alpha = 1.0/300.0
    sigma_init = 0.01
    w_init = 0.01
    
    my = np.zeros((frame1.shape[0], frame1.shape[1], K, D))
    #my = my / np.linalg.norm(my)

    sigma_squared = sigma_init * np.ones((frame1.shape[0], frame1.shape[1], K, D))
    #sigma_squared = sigma_squared / np.linalg.norm(sigma_squared[0, 0, :, :])
    sigma_init_squared = np.array((sigma_init, sigma_init, sigma_init))
    
    w = np.ones((frame1.shape[0], frame1.shape[1], K)) / K

    B_hat = np.zeros((frame1.shape[0], frame1.shape[1]))
    B = np.zeros((frame1.shape[0], frame1.shape[1]))

    p = np.zeros((frame1.shape[0], frame1.shape[1], K))

    c = np.zeros(K)

    plt.set_cmap("gray")

    frames = []
    fig = plt.figure()

    # Initialize all mean's with pixel values from first frame
    for x in range(frame1.shape[0]):
        for y in range(frame1.shape[1]):
            for k in range(K):
                my[x, y, k] = frame1[x,y]
    
    for f in range(2, 100):
        print(f)
        frame = load_image(f)
        
        if (not f % 10) or f < 10:  
            for x in range(frame.shape[0]):
                for y in range(frame.shape[1]):
                    match = False # TRY MOVE THIS OUTSIDE AND DO MANY FRAMES
                    
                    for k in range(K):
                        dk_squared = np.sum(np.power(frame[x, y, :] - my[x, y, k, :], 2) / sigma_squared[x, y, k, :])

                        if np.sqrt(dk_squared) < lamb: #Square root?                        
                            if not match:
                                #print("HEJ 1")
                                m = k
                            elif w[x, y, k]/np.sqrt(np.linalg.norm(sigma_squared[x, y, k])) > (w[x, y, m]/np.sqrt(np.linalg.norm(sigma_squared[x, y, m]))):
                                #print("HEJ 2")
                                m = k
                                                
                            match = True
                    
                    if not match:
                        m = K - 1
                        w[x, y, m] = w_init
                        my[x, y, m] = frame[x,y]
                        sigma_squared[x, y, m] = sigma_init_squared
                    else:
                        w[x, y, m] = (1 - alpha)*w[x, y, m] + alpha
                        p[x, y, m] = alpha / w[x, y, m]
                        my[x, y, m] = (1-p[x, y, m])*my[x, y, m] + p[x, y, m]*frame[x,y]
                        sigma_squared[x, y, m] = (1-p[x, y, m])*sigma_squared[x, y, m] + np.multiply((p[x, y, m]*(frame[x,y]-my[x, y, m])), (frame[x,y] - my[x, y, m]))

                    w[x, y, :] = w[x, y, :] / np.sum(w[x, y, :])

                    for k in range(K):
                        c[k] = w[x, y, k]/np.sqrt(np.linalg.norm(sigma_squared[x, y, k]))

                    if match:
                        #print(c)
                        indices = np.argsort(-c)
                        #print(indices)
                        #print("BEFORE", w[x, y])
                        w[x, y] = w[x, y, indices]
                        #print("AFTER", w[x,y])
                        my[x, y] = my[x, y, indices]
                        sigma_squared[x, y] = sigma_squared[x, y, indices]
                    
                    i = 0

                    for i in range(K):
                        #print(np.sum(w[x, y, 0:i+1]))
                        if np.sum(w[x, y, 0:i+1]) > T:
                            break

                    #print("I ", i + 1)
                    B[x, y] = i + 1 #???

        for x in range(frame.shape[0]):
            for y in range(frame.shape[1]):
                B_hat[x, y] = 0
                for k in range(int(B[x, y])):
                    dk_squared = np.sum(np.power(frame[x, y, :] - my[x, y, k, :], 2) / sigma_squared[x, y, k, :])
                    
                    if np.sqrt(dk_squared) < lamb:
                        B_hat[x,y] = 1

        #plt.imshow(B_hat)
        #plt.show()
        frames.append([plt.imshow(B_hat, animated=True)])

        # Sparar frames.
        save_frames(B_hat, f, '../../generated_modelling_frames/' + settings.DATASET_NAME + '/')

    ani = ArtistAnimation(fig, frames, interval=50, blit=True,
                                repeat_delay=1000)
    plt.show()

    return B_hat

gaussian_mix()