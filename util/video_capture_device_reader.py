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

from . import LOGGER, CONF
from .toolbox import uint8


# %% ---- 2023-07-24 ------------------------
# Function and class


# %% ---- 2023-07-24 ------------------------
# Play ground
class VideoCaptureReader(object):
    video_capture_idx = 0  # cv2.VideoCapture(#)
    display_width = 400  # px
    display_height = 300  # px

    def __init__(self):
        self.conf_override()
        self.vid = None
        self.connect()

        LOGGER.debug(
            'Initialize {} with {}'.format(self.__class__, self.__dict__))
        pass

    def conf_override(self):
        for key, value in CONF['video'].items():
            if not (hasattr(self, key)):
                LOGGER.warning('Invalid key: {} in CONF'.format(key))
                continue
            setattr(self, key, value)

        LOGGER.debug('Override the options with CONF')

    @LOGGER.catch
    def connect(self):
        self.vid = cv2.VideoCapture(0)
        LOGGER.debug('Connected to video capture')

    def read(self):
        success_flag, bgr = self.vid.read()

        if not success_flag:
            LOGGER.error('Receives frame fails')
            bgr = uint8(np.random.randint(
                50, 200, (self.display_height, self.display_width, 3)))
            bgr[:40] = 0
            return bgr

        return cv2.resize(bgr, (self.display_width, self.display_height))


# %% ---- 2023-07-24 ------------------------
# Pending


# %% ---- 2023-07-24 ------------------------
# Pending