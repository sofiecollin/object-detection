import numpy as np
import PIL.Image
from matplotlib import pyplot as plt
from matplotlib.animation import ArtistAnimation
#from save_frames import save_frames

class GMM:
    def __init__(self, frame1):
        self.K = 4
        self.D = 3

        self.lamb = 2.5
        self.T = 0.8
        self.alpha = 1.0/600
        self.sigma_init = 0.015
        self.w_init = 0.1

        self.my = np.zeros((frame1.shape[0], frame1.shape[1], self.K, self.D))
        self.sigma_squared = self.sigma_init * np.ones((frame1.shape[0], frame1.shape[1], self.K, self.D))
        self.sigma_init_squared = np.array((self.sigma_init, self.sigma_init, self.sigma_init))
        self.w = np.ones((frame1.shape[0], frame1.shape[1], self.K)) / self.K
        self.p = np.zeros((frame1.shape[0], frame1.shape[1], self.K))

        self.B_hat = np.zeros((frame1.shape[0], frame1.shape[1]))
        self.p

        #Shadow variables
        self.darkness_thresh = np.array([0.5, 0.90])
        self.chrominance_thresh = 0.04
        self.Sp = np.zeros((frame1.shape[0], frame1.shape[1]))

        # Initialize all mean's with pixel values from first frame
        for k in range(self.K):
            self.my[:, :, k] = frame1

    def next(self, frame):
        dk_squares = np.sum(np.power(frame[:, :, np.newaxis, :] - self.my, 2) / self.sigma_squared, axis=3)

        lamb_mask = np.sqrt(dk_squares) < self.lamb

        no_matches = np.max(lamb_mask, axis=2) == False # All pixels that have 0 matches
        
        w_sigm = self.w / np.sqrt(np.linalg.norm(self.sigma_squared))
        w_filtered = w_sigm * lamb_mask # We don't want to find wk where dk are > lamb. Filter them.
        
        cols, rows = np.meshgrid(np.arange(frame.shape[1]), np.arange(frame.shape[0]))
        dims = np.argmax(w_filtered, axis=2) # Largest wk for every pixel. In range k={[0, K]}.

        dims[no_matches] = self.K-1 # Dims at these positions will be overwritten with init values at the end.

        self.w[rows, cols, dims] = (1 - self.alpha)*self.w[rows, cols, dims] + self.alpha
        self.p[rows, cols, dims] = self.alpha / self.w[rows,cols, dims]

        # Calculate my
        c1 = (1-self.p[rows, cols, dims, np.newaxis]) * self.my[rows, cols, dims, :]
        c2 = self.p[rows, cols, dims, np.newaxis]*frame
        self.my[rows, cols, dims] = c1 + c2

        # Calculate sigma_squared
        d1 = (1-self.p[rows, cols, dims, np.newaxis])*self.sigma_squared[rows, cols, dims]
        d2 = np.multiply((self.p[rows, cols, dims, np.newaxis]*(frame-self.my[rows, cols, dims])), (frame - self.my[rows, cols, dims]))
        self.sigma_squared[rows, cols, dims] = d1 + d2

        # Set no_matching variables to init values.
        m = self.K-1
        self.w[no_matches, m] = self.w_init
        self.my[no_matches, m] = frame[no_matches]
        self.sigma_squared[no_matches, m, :] = self.sigma_init_squared

        self.w = self.w / np.sum(self.w, axis=2)[:, :, np.newaxis]
        
        # Sort
        # Should this only be done for matching pixels???
        c = self.w / np.sqrt(np.linalg.norm(self.sigma_squared, axis=3))
        sorted_c = np.argsort(-c, axis=2) #-c to get descending order
        self.w = np.take_along_axis(self.w, sorted_c, axis=-1)
        self.my = np.take_along_axis(self.my, sorted_c[:, :, :, np.newaxis], axis=2)
        self.sigma_squared = np.take_along_axis(self.sigma_squared, sorted_c[:, :, :, np.newaxis], axis=2)
        
        I = np.zeros((frame.shape[0], frame.shape[1], self.K))
        
        for k in range(self.K):
            I[:, :, k][np.sum(self.w[:,:, 0:k], axis=2) <= self.T] = 1
            I[:, :, k][np.sum(self.w[:,:, 0:k], axis=2) > self.T] = np.inf
            
        ## Segment it.
        B_hat = np.zeros((frame.shape[0], frame.shape[1]))
        
        dk_squares = np.sum(np.power(frame[:, :, None, :] - self.my, 2) / self.sigma_squared, axis=3)

        # Some values will be multiplied with inf, see above. This will make them > lamb
        dk_filtered = dk_squares * I
        
        B_hat = np.any(np.sqrt(dk_filtered) < self.lamb, axis=2)
        B_hat = B_hat.astype(np.uint8) # Convert to 0/1 instead of False/True

        return B_hat
    
    #Uses color model from Horprasert (ref from John Wood's thesis)
    def shadow(self, B_hat, frame):
        #normalize rgb
        my_normalized = self.my / (np.sum(self.my, axis=3)[:, :, :,None] + 0.0000001)

        #print("SUM: ", np.sum(self.my, axis=3)[0,0 , :,None])
        #print("NORM: ", np.linalg.norm(self.my, axis=3)[0, 0, :,None])
        #print("MY: ", self.my[0,0,:,:])
        #print("MY NORMALIZED: ", my_normalized[0,0,:,:])

        Dv = np.sum(frame[:, :, None, :] * my_normalized, axis=3) / (
            np.linalg.norm(self.my, axis=3) + 0.0000001
        )  
        
        Dc = np.linalg.norm(
            frame[:, :, None, :] - 
              (np.sum(frame[:, :, None, :] * my_normalized, axis=3)[:, :, :, None]) * my_normalized,
            axis=3,
        )

        #Calculating Sp
        shadow_mask1 = self.darkness_thresh[0] <= Dv
        shadow_mask2 = Dv <= self.darkness_thresh[1]
        shadow_mask3 = Dc <= self.chrominance_thresh

        shadow_mask = np.any(shadow_mask1*shadow_mask2*shadow_mask3, axis=2)

        # Apply only where B_hat = false => foreground
        Sp = shadow_mask.astype(int)
        B_hat = 1-B_hat

        Sp = 1.0 - B_hat * (1 - (B_hat * Sp)) #Return foreground
        
        return Sp
