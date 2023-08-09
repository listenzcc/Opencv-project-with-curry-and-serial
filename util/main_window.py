"""
File: main_window.py
Author: Chuncheng Zhang
Date: 2023-07-25
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


# %% ---- 2023-07-25 ------------------------
# Requirements and constants

import numpy as np

from . import LOGGER, CONF
from .toolbox import uint8

# %% ---- 2023-07-25 ------------------------
# Function and class


class MainWindow(object):
    """The big picture of the main window

    """
    width = 1200,  # px, window widthSTM32DeviceReader
    height = 800,  # px, window height
    video_panel_x = 10  # px, offset x of video panel
    video_panel_y = 10  # px, offset y of video panel
    eeg_panel_x = 500  # px, offset x of eeg panel
    eeg_panel_y = 10  # px, offset y of eeg panel
    stm32_panel_x = 10  # px, offset x of stm32 panel
    stm32_panel_y = 500  # px, offset x of stm32 panel
    decoder_panel_x = 10  # px, offset x of decoder panel
    decoder_panel_y = 620  # px, offset y of decoder panel

    def __init__(self):
        """Initialize the background.
        """
        self.conf_override()

        LOGGER.debug(f'Initialize {self.__class__} with {self.__dict__}')

        self.reset_background()

    def conf_override(self):
        for key, value in CONF['main_window'].items():
            if not (hasattr(self, key)):
                LOGGER.warning(f'Invalid key: {key} in CONF')
                continue
            setattr(self, key, value)

        LOGGER.debug('Override the options with CONF')

    def reset_background(self):
        """Reset the background with black bgr.

        Returns:
            opencv image: The black image.
        """
        zero_bgr = uint8(np.zeros((self.height, self.width, 3)) + 50)
        self.screen_bgr = zero_bgr

        LOGGER.debug(f'Generate black background with {zero_bgr.shape} array')
        return zero_bgr

    def overlay_video_panel(self, bgr):
        self.overlay_bgr(bgr, x=self.video_panel_x, y=self.video_panel_y)

    def overlay_eeg_panel(self, bgr):
        self.overlay_bgr(bgr, x=self.eeg_panel_x, y=self.eeg_panel_y)

    def overlay_stm32_panel(self, bgr):
        self.overlay_bgr(bgr, x=self.stm32_panel_x, y=self.stm32_panel_y)

    def overlay_decoder_panel(self, bgr):
        self.overlay_bgr(bgr, x=self.decoder_panel_x, y=self.decoder_panel_y)

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
            LOGGER.warning(
                f'Overlay exceeds the height range, {y + shape[0]} | {self.height}'
            )

        if x + shape[1] > self.width:
            bgr = bgr[:, :self.width - x]
            LOGGER.warning(
                f'Overlay exceeds the width range, {x + shape[1]} | {self.width}'
            )

        self.screen_bgr[y:y+shape[0], x:x+shape[1]] = bgr
        return self.screen_bgr

# %% ---- 2023-07-25 ------------------------
# Play ground


# %% ---- 2023-07-25 ------------------------
# Pending


# %% ---- 2023-07-25 ------------------------
# Pending
