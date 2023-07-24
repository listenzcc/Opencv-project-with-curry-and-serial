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
from util.video_capture_device_reader import VideoCaptureReader
from util.toolbox import uint8, put_text
from util import LOGGER

# %%

quite_key_code = 'q'
window_name = 'Very Fast Very Stable System'


# %% ---- 2023-07-20 ------------------------
# Function and class


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
        zero_bgr = uint8(np.zeros((self.height, self.width, 3)) + 50)
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

    LOGGER.debug('Keypress {}'.format(key))

    if key.name == quite_key_code:
        LOGGER.debug('Quite key code is received.')
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


def fps(delay):
    """Compute fps for a given delay.

    Args:
        delay (float): The input delay,

    Returns:
        float: The fps for the given delay.
    """
    return 1 / delay if delay > 0 else 0


# %% ---- 2023-07-20 ------------------------
# Play ground
video_capture_reader = VideoCaptureReader()

eeg_device_reader = EEGDeviceReader()
eeg_device_reader.start()

BIG_PIC = BigPicture()

DY_OPT.start()
keyboard.on_press(keypress_callback, suppress=True)

tic = time.time()
toc_limit = tic + 100  # Seconds

eeg_image = uint8(np.zeros((400, 400, 3)))

while DY_OPT.running:
    video_image = video_capture_reader.read()

    pair = eeg_device_reader.read_bgr()
    eeg_image_refresh_flag = pair is not None
    if eeg_image_refresh_flag:
        eeg_timestamp, eeg_image = pair

    toc = time.time()
    delay = toc - tic

    if eeg_image_refresh_flag:
        text = '{:06.2f}'.format(toc - eeg_timestamp)
        put_text(eeg_image, text, org=(10, 20))
        BIG_PIC.overlay_bgr(eeg_image, 500, 10)

    text = '{:04d} | {:06.2f} Fps'.format(milliseconds(delay), fps(delay))
    put_text(video_image, text, org=(10, 20))
    BIG_PIC.overlay_bgr(video_image, 10, 10)

    cv2.imshow(window_name, BIG_PIC.screen_bgr)
    cv2.setWindowTitle(window_name, '{} - {}'.format(window_name, tic))
    cv2.pollKey()

    tic = time.time()

    if toc > toc_limit:
        print('Time exceeds the limit, stop it.')
        DY_OPT.stop()

eeg_device_reader.stop()

keyboard.unhook_all()
print('Press any keyboard to continue..., or wait for 1 seconds')
cv2.waitKey(1 * 1000)

# %% ---- 2023-07-20 ------------------------
# Pending

# %% ---- 2023-07-20 ------------------------
# Pending

# %%
