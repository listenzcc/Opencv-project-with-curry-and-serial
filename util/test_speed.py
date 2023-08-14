import io
import cv2
import threading

import torch as t
import numpy as np

from pathlib import Path
from tqdm.auto import tqdm
from predict_model.Predict import predict

if __name__ == "__main__":
    stm_32_data = t.load(
        Path(__file__).parent.joinpath("predict_model/stm32.pt"))
    eeg_data = t.load(
        Path(__file__).parent.joinpath('predict_model/eeg.pt'))
    image_path = Path(__file__).parent.joinpath(
        'predict_model/2023-07-17-16-44-18-133-1000-102.tif')
    face_image_in_bgr = cv2.imread(image_path.as_posix())

    io_send = io.BytesIO()
    np.save(io_send, eeg_data)
    np.save(io_send, stm_32_data)
    np.save(io_send, face_image_in_bgr)

    byte_array = io_send.getvalue()
    print(len(byte_array))

    io_recv = io.BytesIO(byte_array)
    for i in range(3):
        arr = np.load(io_recv)
        print(i, arr.shape, arr.dtype)

    for _ in tqdm(range(10), 'text_speed'):
        t = threading.Thread(target=predict, args=(
            (stm_32_data, eeg_data, face_image_in_bgr)))
        t.start()
        t.join()

    print('Done.')
