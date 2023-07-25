
"""
File: toolbox.py
Author: Chuncheng Zhang
Date: 2023-07-24
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Amazing things

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2023-07-24 ------------------------
# Requirements and constants
import cv2

import numpy as np
import matplotlib.pyplot as plt

# %%

default_put_text_kwargs = dict(
    org=(10, 50),  # x, y
    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
    fontScale=0.6,
    thickness=1,
    color=(0, 200, 0),
    lineType=cv2.LINE_AA
)
# %% ---- 2023-07-24 ------------------------
# Function and class


def uint8(x):
    """Convert x into uint8

    Args:
        x (np.array): The array to convert.

    Returns:
        np.uint8 array: The converted array.
    """
    return x.astype(np.uint8)


def put_text(bgr, text, **input_kwargs):
    """Put text into the opencv image

    Args:
        bgr (opencv image): The the image being put, (height x width x 3);
        text (str): The text being put;
        input_kwargs (dict, optional): The customized kwargs to cv2.putText. Defaults to dict(org=(10, 20), fontScale=0.5, thickness=1, color=(0, 200, 0)).

    Returns:
        opencv image: The image with the putting text.
    """
    kwargs = default_put_text_kwargs.copy()
    for k, v in input_kwargs.items():
        kwargs[k] = v

    cv2.putText(bgr, text, **kwargs)

    return bgr


def matplotlib_to_opencv_image(fig):
    """Convert matplotlib fig to opencv image format

    Args:
        fig (mpl.Figure): The input fig.

    Returns:
        Opencv BGR image: The output image.
    """
    # Render the plot to a buffer
    fig.canvas.draw()
    buf = fig.canvas.tostring_rgb()
    ncols, nrows = fig.canvas.get_width_height()
    plt.close(fig)  # Close the figure to prevent displaying it

    # Convert the buffer to a numpy array
    arr = np.frombuffer(buf, dtype=np.uint8)
    arr = arr.reshape(nrows, ncols, 3)

    # Convert RGB to BGR
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def timestamp2milliseconds(t):
    """Convert timestamp into milliseconds.

    Args:
        t (timestamp): The input timestamp.

    Returns:
        int: The converted time in milliseconds.
    """
    return int(t * 1000)


def delay2fps(delay):
    """Compute fps for a given delay.

    Args:
        delay (float): The input delay,

    Returns:
        float: The fps for the given delay.
    """
    return 1 / delay if delay > 0 else 0
# %% ---- 2023-07-24 ------------------------
# Play ground


# %% ---- 2023-07-24 ------------------------
# Pending


# %% ---- 2023-07-24 ------------------------
# Pending
