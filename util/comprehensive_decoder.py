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
import time
import numpy as np

from . import LOGGER, CONF
from .toolbox import uint8, put_text


# %% ---- 2023-08-09 ------------------------
# Function and class
class ComprehensiveDecoder(object):
    eeg_data_length = 1000  # milliseconds
    stm32_data_length = 1000  # milliseconds
    display_inch_width = 4  # inch
    display_inch_height = 2  # inch
    display_dpi = 100  # DPI

    def __init__(self):
        self.conf_override()

        LOGGER.debug(f'Initialize {self.__class__} with {self.__dict__}')

        self.bgr = self.empty_bgr()

    def empty_bgr(self):
        return uint8(
            np.zeros((
                self.display_inch_height * self.display_dpi,
                self.display_inch_width * self.display_dpi,
                3,
            )) + 100
        )

    def conf_override(self):
        for key, value in CONF['decoder'].items():
            if not (hasattr(self, key)):
                LOGGER.warning(f'Invalid key: {key} in CONF')
                continue
            setattr(self, key, value)

        LOGGER.debug('Override the options with CONF')

    def predict(self, stm32_data, eeg_data):
        output = f'Shape: {stm32_data.shape}, {np.mean(stm32_data):.4f} |  {eeg_data.shape}, {np.mean(eeg_data):.4f}'
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
