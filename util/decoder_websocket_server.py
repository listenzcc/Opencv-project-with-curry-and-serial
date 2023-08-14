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
import asyncio
# import websockets
from websockets.server import serve

# %% ---- 2023-08-14 ------------------------
# Function and class

# create handler for each connection


# async def handler(websocket, path):

#     data = await websocket.recv()

#     reply = f"Data recieved as:  {len(data)}!"

#     await websocket.send(reply)


# %% ---- 2023-08-14 ------------------------
# Play ground

# start_server = serve(handler, "localhost", 8765)
# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()

# %% ---- 2023-08-14 ------------------------
# Pending

import io
import cv2
import asyncio
import numpy as np

from websockets.server import serve

from predict_model.Predict import predict


async def echo(websocket):
    async for message in websocket:
        io_recv = io.BytesIO(message)

        eeg_data = np.load(io_recv)
        stm32_data = np.load(io_recv)
        face_img_in_bgr = np.load(io_recv)

        stm32_data = np.concatenate([stm32_data for _ in range(100)], axis=1)
        face_img_in_bgr = cv2.resize(face_img_in_bgr, (2048, 1088))
        face_img_in_bgr = cv2.cvtColor(face_img_in_bgr, cv2.COLOR_BGR2RGB)

        if stm32_data.shape[1] != 1000:
            return -1

        if eeg_data.shape[1] != 1000:
            return -1

        print(stm32_data.shape, eeg_data.shape, face_img_in_bgr.shape)

        message = predict(stm32_data, eeg_data, face_img_in_bgr)

        if message == -1:
            print('Data shape error')

        if message == -2:
            print('Can not find face')

        # for i in range(3):
        #     arr = np.load(io_recv)
        #     print(i, arr.shape, arr.dtype)

        await websocket.send(f'{message}')


async def main():
    async with serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever

asyncio.run(main())

# %% ---- 2023-08-14 ------------------------
# Pending
