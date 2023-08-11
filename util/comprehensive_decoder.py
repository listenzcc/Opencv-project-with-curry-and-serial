"""
File: comprehensive_decoder.py
Author: Chuncheng Zhang
Date: 2023-08-09
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


# %% ---- 2023-08-09 ------------------------
# Requirements and constants
import cv2
import time
import threading
import numpy as np

from . import LOGGER, CONF
from .toolbox import uint8, put_text
from .predict_model.Predict import predict


# %% ---- 2023-08-09 ------------------------
# Function and class
class ComprehensiveDecoder(object):
    eeg_data_length = 1000  # milliseconds
    stm32_data_length = 1000  # milliseconds
    display_pixel_width = 400  # pixels
    display_pixel_height = 200  # pixels
    display_dpi = 100  # DPI

    def __init__(self):
        self.conf_override()

        LOGGER.debug(f'Initialize {self.__class__} with {self.__dict__}')

        self.bgr = self.empty_bgr()

    def empty_bgr(self):
        return uint8(
            np.zeros((self.display_pixel_height,
                     self.display_pixel_width, 3)) + 100
        )

    def conf_override(self):
        for key, value in CONF['decoder'].items():
            if not (hasattr(self, key)):
                LOGGER.warning(f'Invalid key: {key} in CONF')
                continue
            setattr(self, key, value)

        LOGGER.debug('Override the options with CONF')

    def predict(self, stm32_data, eeg_data, face_img_in_bgr):
        threading.Thread(target=self._predict, args=(
            stm32_data, eeg_data, face_img_in_bgr), daemon=True).start()

    def _predict(self, stm32_data, eeg_data, face_img_in_bgr):
        """Predict the status based on the input.

        Args:
            stm32_data (np.array): 3 x n array, n is the samples, 3 refers eog, emg and temperature channels;
            eeg_data (np.array): chs x n array, chs is the number of eeg channels, n is the samples;
            face_img_in_bgr (np.array): height x width x 3, the image from the camera.

        Returns:
            prediction value
        """

        # ---------------------
        # Make the stm32_data 1000 points length
        stm32_data = np.concatenate([stm32_data for _ in range(100)], axis=1)
        face_img_in_bgr = cv2.resize(face_img_in_bgr, (2048, 1088))
        face_img_in_bgr = cv2.cvtColor(face_img_in_bgr, cv2.COLOR_BGR2RGB)

        if stm32_data.shape[1] != 1000:
            return

        if eeg_data.shape[1] != 1000:
            return

        print(stm32_data.shape, eeg_data.shape, face_img_in_bgr.shape)

        tic = time.time()
        res = predict(stm32_data, eeg_data, face_img_in_bgr)
        time_cost = time.time() - tic

        output = f'Predict value: {res}, Cost: {time_cost:.2f} seconds.'
        print(output)
        self.draw(output)

        return output

    def draw(self, res):
        bgr = self.empty_bgr()
        put_text(bgr, res, fontScale=0.5)
        put_text(bgr, f'Finished at: {time.time():0.2f}',
                 org=(10, 20), fontScale=0.5)
        self.bgr = bgr
        return bgr


# %% ---- 2023-08-09 ------------------------
# Play ground


# %% ---- 2023-08-09 ------------------------
# Pending


# %% ---- 2023-08-09 ------------------------
# Pending
