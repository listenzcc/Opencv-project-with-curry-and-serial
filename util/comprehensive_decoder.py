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
import io
import cv2
import time

import asyncio
from websockets.sync.client import connect

import numpy as np


import multiprocessing

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

    # def predict_computation(self, stm32_data, eeg_data, face_img_in_bgr):
    #     # ---------------------
    #     # Make the stm32_data 1000 points length
    #     stm32_data = np.concatenate([stm32_data for _ in range(100)], axis=1)
    #     face_img_in_bgr = cv2.resize(face_img_in_bgr, (2048, 1088))
    #     face_img_in_bgr = cv2.cvtColor(face_img_in_bgr, cv2.COLOR_BGR2RGB)

    #     if stm32_data.shape[1] != 1000:
    #         return -1

    #     if eeg_data.shape[1] != 1000:
    #         return -1

    #     print(stm32_data.shape, eeg_data.shape, face_img_in_bgr.shape)

    #     return predict(stm32_data, eeg_data, face_img_in_bgr)

    def predict(self, stm32_data, eeg_data, face_img_in_bgr):
        """Predict the status based on the input.

        Args:
            stm32_data (np.array): 3 x n array, n is the samples, 3 refers eog, emg and temperature channels;
            eeg_data (np.array): chs x n array, chs is the number of eeg channels, n is the samples;
            face_img_in_bgr (np.array): height x width x 3, the image from the camera.

        Returns:
            prediction value
        """

        tic = time.time()

        res = 0
        # res = self.predict_computation(stm32_data, eeg_data, face_img_in_bgr)

        # async def foo():
        #     with websockets.connect('ws://localhost:8765/') as ws:
        #         io_send = io.BytesIO()
        #         np.save(io_send, eeg_data)
        #         np.save(io_send, stm32_data)
        #         np.save(io_send, face_img_in_bgr)
        #         byte_array = io_send.getvalue()
        #         print(len(byte_array))

        #         await ws.send(byte_array)

        #         response = await ws.recv()
        #         print(response)

        def hello():
            with connect("ws://localhost:8765") as ws:

                io_send = io.BytesIO()
                np.save(io_send, eeg_data)
                np.save(io_send, stm32_data)
                np.save(io_send, face_img_in_bgr)
                byte_array = io_send.getvalue()
                print(len(byte_array))

                # ws.send("Hello world!")
                ws.send(byte_array)

                message = ws.recv()
                print(f"Received: {message}")

                return message

        res = hello()

        # asyncio.get_event_loop.run_until_complete(foo())
        # asyncio.run(foo())

        # target = self.predict_computation
        # args = (stm32_data, eeg_data, face_img_in_bgr)
        # multiprocessing.Process(target=target, args=args, daemon=True).start()

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
