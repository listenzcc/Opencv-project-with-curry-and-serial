"""
File: video_capture_device_reader.py
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

from . import LOGGER
from .toolbox import uint8


# %% ---- 2023-07-24 ------------------------
# Function and class


# %% ---- 2023-07-24 ------------------------
# Play ground
class VideoCaptureReader(object):

    def __init__(self):
        self.vid = None
        self.connect()
        pass

    def connect(self):
        with LOGGER.catch():
            self.vid = cv2.VideoCapture(0)
            LOGGER.debug('Connected to video capture')

    def read(self, size=(400, 400)):
        success_flag, bgr = self.vid.read()

        if not success_flag:
            LOGGER.error('Receives frame fails')
            bgr = uint8(np.random.randint(50, 200, (size[0], size[1], 3)))
            bgr[:40] = 0
            return bgr

        return cv2.resize(bgr, size)


# %% ---- 2023-07-24 ------------------------
# Pending


# %% ---- 2023-07-24 ------------------------
# Pending
