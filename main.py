"""
File: main.py
Author: Chuncheng Zhang
Date: 2023-07-20
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


# %% ---- 2023-07-20 ------------------------
# Requirements and constants

import cv2
import time
import keyboard
import numpy as np

from rich import print

from util.eeg_device_reader import EEGDeviceReader
from util.toolbox import uint8, put_text

# %%

quite_key_code = 'q'


# %% ---- 2023-07-20 ------------------------
# Function and class


eeg_device_reader = EEGDeviceReader()


class BigPicture(object):
    """The big picture of the main window

    """
    width = 1000
    height = 800

    def __init__(self):
        """Initialize the background.
        """
        self.reset_background()
        pass

    def reset_background(self):
        """Reset the background with black bgr.

        Returns:
            opencv image: The black image.
        """
        zero_bgr = uint8(np.zeros((self.height, self.width, 3)))
        self.screen_bgr = zero_bgr
        return zero_bgr

    def overlay_bgr(self, bgr, x=0, y=0):
        """Overlay to the background

        Args:
            bgr (opencv image): The covering bgr image;
            x (int, optional): The x coordinate of the bgr. Defaults to 0.
            y (int, optional): The y coordinate of the bgr. Defaults to 0.

        Returns:
            opencv image: The updated background image.
        """

        shape = bgr.shape

        if y + shape[0] > self.height:
            bgr = bgr[:self.height - y]

        if x + shape[1] > self.width:
            bgr = bgr[:, :self.width - x]

        self.screen_bgr[y:y+shape[0], x:x+shape[1]] = bgr
        return self.screen_bgr


BIG_PIC = BigPicture()


class DynamicOption(object):
    """The DynamicOption class
    """

    def __init__(self):
        self.reset()
        pass

    def reset(self):
        self.running = False

    def start(self):
        self.running = True

    def stop(self):
        self.running = False


DY_OPT = DynamicOption()


def keypress_callback(key):
    """Callback function for keypress events.

    Args:
        key (key): The key being pressed.
    """

    if key.name == quite_key_code:
        DY_OPT.stop()

    return


def milliseconds(t):
    """Convert timestamp into milliseconds.

    Args:
        t (timestamp): The input timestamp.

    Returns:
        int: The converted time in milliseconds.
    """
    return int(t * 1000)


# %% ---- 2023-07-20 ------------------------
# Play ground
vid = cv2.VideoCapture(0)

DY_OPT.start()
keyboard.on_press(keypress_callback, suppress=True)

tic = time.time()

toc_limit = tic + 100  # Seconds

bgr1 = uint8(np.zeros((400, 400, 3)))

while DY_OPT.running:
    ret, bgr = vid.read()

    toc = time.time()

    if toc > toc_limit:
        print('Time exceeds the limit, stop it.')
        DY_OPT.stop()

    if bgr is None:
        bgr = uint8(np.random.randint(50, 200, (400, 400, 3)))
    bgr = cv2.resize(bgr, (400, 400))

    if len(eeg_device_reader.bgr_list) > 0:
        t_bgr1, bgr1 = eeg_device_reader.bgr_list.pop(0)
        text = '{:06.2f}'.format(toc - t_bgr1)
        put_text(bgr1, text)

    delay = toc - tic

    text = '{:04d} | {:06.2f} Fps'.format(
        milliseconds(delay), 1 / delay if delay > 0 else 0)
    put_text(bgr, text)

    BIG_PIC.overlay_bgr(bgr, 10, 10)
    BIG_PIC.overlay_bgr(bgr1, 500, 10)

    cv2.imshow('frame', BIG_PIC.screen_bgr)
    cv2.pollKey()

    tic = time.time()

keyboard.unhook_all()
print('Press any keyboard to continue..., or wait for 1 seconds')
cv2.waitKey(1 * 1000)

# %% ---- 2023-07-20 ------------------------
# Pending

# %% ---- 2023-07-20 ------------------------
# Pending

# %%
