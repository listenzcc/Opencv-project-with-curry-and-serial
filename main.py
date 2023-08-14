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

import threading
import multiprocessing

import cv2
import time
import keyboard
import numpy as np

from rich import print

# from util.eeg_device_reader import EEGDeviceReader
from util.eeg_device_reader_simulation import EEGDeviceReader
from util.stm32_device_reader import Stm32DeviceReader
from util.video_capture_device_reader import VideoCaptureReader
from util.comprehensive_decoder import ComprehensiveDecoder
from util.main_window import MainWindow
from util.toolbox import uint8, put_text, timestamp2milliseconds, delay2fps
from util import LOGGER, CONF

# %%

project_name = CONF['project_name']
quite_key_code = CONF['keyboard']['quite_key_code']


# %% ---- 2023-07-20 ------------------------
# Function and class


class RunningOption(object):
    """The options on runtime
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.running = False

    def start(self):
        self.running = True

    def stop(self):
        self.running = False


running_option = RunningOption()


def keypress_callback(key):
    """Callback function for keypress events.

    Args:
        key (key): The key being pressed.
    """

    LOGGER.debug(f'Keypress {key}, {key.name}')

    if key.name == quite_key_code:
        LOGGER.debug('Quite key code is received.')
        running_option.stop()

    if key.name == '=':
        CONF['video']['display_height'] += 10
        video_capture_reader.conf_override()

    if key.name == '-':
        CONF['video']['display_height'] -= 10
        video_capture_reader.conf_override()

    return


# %% ---- 2023-07-20 ------------------------
# Play ground
# Initialize the workers
video_capture_reader = VideoCaptureReader()

eeg_device_reader = EEGDeviceReader()
eeg_device_reader.start()

stm32_device_reader = Stm32DeviceReader()
stm32_device_reader.start()

comprehensive_decoder = ComprehensiveDecoder()

main_window = MainWindow()

# %%


def set_time_interval_job(secs=0):
    time.sleep(secs)

    stm32_data = stm32_device_reader.peek_latest_data_by_milliseconds(
        comprehensive_decoder.stm32_data_length)
    if stm32_data is not None:
        print(f'stm32_data: {stm32_data.shape}')

    eeg_data = eeg_device_reader.peek_latest_data_by_milliseconds(
        comprehensive_decoder.eeg_data_length)
    if eeg_data is not None:
        print(f'eeg_data: {eeg_data.shape}')

    video_image = video_capture_reader.read()

    if not any([stm32_data is None, eeg_data is None]):
        comprehensive_decoder.predict(stm32_data,
                                      eeg_data,
                                      video_image)

    return


def loop_prediction(secs=1):
    while True:
        time.sleep(secs)
        set_time_interval_job()
        # multiprocessing.Process(
        #     target=set_time_interval_job, daemon=True).start()


threading.Thread(target=loop_prediction, args=(1, ), daemon=True).start()

# ----------------------------------
running_option.start()
keyboard.on_press(keypress_callback, suppress=True)

# %%
if __name__ == '__main__':
    # multiprocessing.freeze_support()
    # multiprocessing.Process(target=loop_prediction,
    #                         args=(1, ), daemon=True).start()

    # ----------------------------------

    tic = time.time()
    toc_limit = tic + 100  # Seconds

    eeg_image = eeg_device_reader.placeholder_image()
    stm32_image = stm32_device_reader.placeholder_image()

    while running_option.running:
        video_image = video_capture_reader.read()

        pair = eeg_device_reader.read_bgr()
        eeg_image_refresh_flag = pair is not None
        if eeg_image_refresh_flag:
            eeg_timestamp, eeg_image = pair

        pair = stm32_device_reader.read_bgr()
        stm32_image_refresh_flag = pair is not None
        if stm32_image_refresh_flag:
            stm32_timestamp, stm32_image = pair

        toc = time.time()
        delay = toc - tic

        # ----------------------------------------------------------------
        if eeg_image_refresh_flag:
            text = '{:06.2f}'.format(toc - eeg_timestamp)
            put_text(eeg_image, text, org=CONF['osd']['org'])
            main_window.overlay_eeg_panel(eeg_image)

        # ----------------------------------------------------------------
        if stm32_image_refresh_flag:
            text = '{:06.2f}'.format(toc - stm32_timestamp)
            put_text(stm32_image, text, org=CONF['osd']['org'])
            main_window.overlay_stm32_panel(stm32_image)

        # ----------------------------------------------------------------
        text = '{:04d} | {:06.2f} Fps'.format(
            timestamp2milliseconds(delay), delay2fps(delay))
        put_text(video_image, text, org=CONF['osd']['org'])
        main_window.overlay_video_panel(video_image)

        # ----------------------------------------------------------------
        main_window.overlay_decoder_panel(comprehensive_decoder.bgr)

        cv2.imshow(project_name, main_window.screen_bgr)
        cv2.setWindowTitle(project_name, f'{project_name} - {tic}')
        cv2.pollKey()

        tic = time.time()

        if toc > toc_limit:
            print('Time exceeds the limit, stop it.')
            running_option.stop()

    eeg_device_reader.stop()

    keyboard.unhook_all()
    print('Press any keyboard to continue..., or wait for 1 seconds')
    cv2.waitKey(1 * 1000)

# %% ---- 2023-07-20 ------------------------
# Pending

# %% ---- 2023-07-20 ------------------------
# Pending

# %%
