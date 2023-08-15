"""
File: decoder_websocket_server.py
Author: Chuncheng Zhang
Date: 2023-08-14
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


# %% ---- 2023-08-14 ------------------------
# Requirements and constants
import io
import cv2
import time
import asyncio
import numpy as np

from loguru import logger as LOGGER

from websockets.server import serve

from predict_model.Predict import predict

# %% ---- 2023-08-14 ------------------------
# Function and class


async def echo(websocket):
    """Echo websocket for the decoding request.

    Args:
        websocket (websocket income connection): The websocket connection requesting for decoding results.

    Message rule:
        Numbers no-less than 0, refers the decoding result is correct;
        -1 refers the stm32_data shape is incorrect;
        -2 refers the eeg_data shape is incorrect;
        other string refers the runtime error of the predict function.

    Returns:
        Send the response back.
    """
    async for message in websocket:
        # Create the io container
        io_recv = io.BytesIO(message)

        # Parse the data in-order
        eeg_data = np.load(io_recv)
        stm32_data = np.load(io_recv)
        face_img_in_bgr = np.load(io_recv)

        # !!! Fix the issue of the current stm32 sampling rate
        stm32_data = np.concatenate([stm32_data for _ in range(100)], axis=1)

        # !!! Fix the issue of the video frame size
        face_img_in_bgr = cv2.resize(face_img_in_bgr, (2048, 1088))
        face_img_in_bgr = cv2.cvtColor(face_img_in_bgr, cv2.COLOR_BGR2RGB)

        # Basic check
        if stm32_data.shape[1] != 1000:
            return -1

        if eeg_data.shape[1] != 1000:
            return -2

        LOGGER.debug(
            f'Data for decoding: {stm32_data.shape}, {eeg_data.shape}, {face_img_in_bgr.shape}')

        try:
            message = predict(stm32_data, eeg_data, face_img_in_bgr)
        except Exception as err:
            message = err
            LOGGER.error(f'Decoding failed: {err}')

        await websocket.send(f'{message}')


async def serve_forever():
    async with serve(echo, "localhost", 8765):
        LOGGER.debug('Serving forever ...')
        await asyncio.Future()  # run forever

    LOGGER.debug('Serving stops.')


# %% ---- 2023-08-14 ------------------------
# Play ground

if __name__ == '__main__':
    asyncio.run(serve_forever())

# %% ---- 2023-08-14 ------------------------
# Pending


# %% ---- 2023-08-14 ------------------------
# Pending
