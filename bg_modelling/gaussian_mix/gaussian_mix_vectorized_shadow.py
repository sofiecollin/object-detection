import numpy as np
import PIL.Image
from matplotlib import pyplot as plt
from matplotlib.animation import ArtistAnimation
from save_frames import save_frames


def gaussian_mix():
    dataset_name = "Walk1"
    file_name1 = "../../frames2/" + dataset_name + "{:03d}.jpg".format(1)
    frame1 = np.asarray(PIL.Image.open(file_name1))
    frame1 = frame1 / 255.0

    K = 4
    D = 3

    lamb = 2.5
    T = 0.8
    alpha = 1.0 / 300.0
    sigma_init = 0.01
    w_init = 0.01

    # Shadow variables
    darkness_thresh = np.array([0.3, 0.95])
    chrominance_thresh = 0.04
    Sp = np.zeros((frame1.shape[0], frame1.shape[1]))

    my = np.zeros((frame1.shape[0], frame1.shape[1], K, D))

    sigma_squared = sigma_init * np.ones((frame1.shape[0], frame1.shape[1], K, D))
    sigma_init_squared = np.array((sigma_init, sigma_init, sigma_init))

    w = w_init * np.ones((frame1.shape[0], frame1.shape[1], K))

    B_hat = np.zeros((frame1.shape[0], frame1.shape[1]))

    p = np.zeros((frame1.shape[0], frame1.shape[1], K))

    c = np.zeros(K)

    plt.set_cmap("gray")

    frames = []
    fig = plt.figure()

    # Initialize all mean's with pixel values from first frame
    for k in range(K):
        my[:, :, k] = frame1

    for f in range(2, 200):
        print(f)
        file_name = "../../frames2/" + dataset_name + "{:03d}.jpg".format(f)
        frame = np.asarray(PIL.Image.open(file_name))
        frame = frame / 255.0

        dk_squares = np.sum(
            np.power(frame[:, :, np.newaxis, :] - my, 2) / sigma_squared, axis=3
        )

        lamb_mask = np.sqrt(dk_squares) < lamb

        no_matches = (
            np.max(lamb_mask, axis=2) == False
        )  # All pixels that have 0 matches

        w_sigm = w / np.sqrt(np.linalg.norm(sigma_squared))
        w_filtered = (
            w_sigm * lamb_mask
        )  # We don't want to find wk where dk are > lamb. Filter them.

        cols, rows = np.meshgrid(np.arange(frame.shape[1]), np.arange(frame.shape[0]))
        dims = np.argmax(
            w_filtered, axis=2
        )  # Largest wk for every pixel. In range k={[0, K]}.

        dims[no_matches] = (
            K - 1
        )  # Dims at these positions will be overwritten with init values at the end.

        w[rows, cols, dims] = (1 - alpha) * w[rows, cols, dims] + alpha
        p[rows, cols, dims] = alpha / w[rows, cols, dims]

        # Calculate my
        c1 = (1 - p[rows, cols, dims, np.newaxis]) * my[rows, cols, dims, :]
        c2 = p[rows, cols, dims, np.newaxis] * frame
        my[rows, cols, dims] = c1 + c2

        # Calculate sigma_squared
        d1 = (1 - p[rows, cols, dims, np.newaxis]) * sigma_squared[rows, cols, dims]
        d2 = np.multiply(
            (p[rows, cols, dims, np.newaxis] * (frame - my[rows, cols, dims])),
            (frame - my[rows, cols, dims]),
        )
        sigma_squared[rows, cols, dims] = d1 + d2

        # Set no_matching variables to init values.
        m = K - 1
        w[no_matches, m] = w_init
        my[no_matches, m] = frame[no_matches]
        sigma_squared[no_matches, m, :] = sigma_init_squared

        w = w / np.sum(w, axis=2)[:, :, np.newaxis]

        # Sort
        # Should this only be done for matching pixels???
        c = w / np.sqrt(np.linalg.norm(sigma_squared, axis=3))
        sorted_c = np.argsort(-c, axis=2)  # -c to get descending order
        w = np.take_along_axis(w, sorted_c, axis=-1)
        my = np.take_along_axis(my, sorted_c[:, :, :, np.newaxis], axis=2)
        sigma_squared = np.take_along_axis(
            sigma_squared, sorted_c[:, :, :, np.newaxis], axis=2
        )

        I = np.zeros((frame.shape[0], frame.shape[1], K))

        for k in range(K):
            I[:, :, k][np.sum(w[:, :, 0:k], axis=2) <= T] = 1
            I[:, :, k][np.sum(w[:, :, 0:k], axis=2) > T] = np.inf

        ## Segment it.
        B_hat = np.zeros((frame.shape[0], frame.shape[1]))

        dk_squares = np.sum(
            np.power(frame[:, :, None, :] - my, 2) / sigma_squared, axis=3
        )

        # Some values will be multiplied with inf, see above. This will make them > lamb
        dk_filtered = dk_squares * I
        B_hat = np.any(np.sqrt(dk_filtered) < lamb, axis=2)

        # Segmentation incorporated w/ shadow detection
        # print((my - np.min(my, axis=2)[:, :, None, :]).shape)
        # print((np.max(my, axis=2) - np.min(my, axis=2))[:, :, None, :].shape)

        # Not sure if the normalization works
        #my_normalized = (my - np.min(my, axis=2)[:, :, None, :]) / (
        #    np.max(my, axis=2) - np.min(my, axis=2)
        #)[:, :, None, :]

        my_normalized = self.my / \
            np.linalg.norm(self.my, axis=2)[:, :, None, :]

        Dv = np.sum(frame[:, :, None, :] * my_normalized, axis=3) / (
            (np.linalg.norm(my, axis=3) + 0.00000000001)
        )  # Added a small nr in case it divides w/ zero.
        Dc = np.linalg.norm(
            frame[:, :, None, :]
            - np.sum(
                np.sum(frame[:, :, None, :] * my_normalized, axis=3)[:, :, :, None]
                * my_normalized,
                axis=2,
            )[:, :, None, :],
            axis=3,
        )

        Sp = np.zeros((frame.shape[0], frame.shape[1]))
        shadow_mask = np.any(darkness_thresh[0] <= Dv, axis=2)
        shadow_mask = shadow_mask == np.any(Dv <= darkness_thresh[1], axis=2)
        shadow_mask = shadow_mask == np.any(Dc <= chrominance_thresh, axis=2)

        # Apply only where B_hat = true
        Sp = ~B_hat * shadow_mask

        B_hat_rgb = np.zeros((frame1.shape[0], frame1.shape[1], 3))
        B_hat_rgb[:, :, 0] = ~B_hat
        B_hat_rgb[:, :, 1] = ~B_hat != Sp
        B_hat_rgb[:, :, 2] = ~B_hat != Sp

        # Remove shadows
        # B_hat_no_shadow = B_hat == Sp
        """
        if f % 40 == 0:
            plt.figure(1)
            plt.imshow(B_hat)
            plt.figure(2)
            plt.imshow(Sp)
            plt.figure(3)
            plt.imshow(shadow_mask)
            plt.show()
"""
        frames.append([plt.imshow(B_hat_rgb, animated=True)])

        # Sparar frames.
        # save_frames(B_hat, f, '../../generated_modelling_frames/' + dataset_name + '/')

    ani = ArtistAnimation(fig, frames, interval=50, blit=True, repeat_delay=1000)
    plt.show()

    return B_hat


gaussian_mix()
