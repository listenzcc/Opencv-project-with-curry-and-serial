"""
File: runme.py
Author: Chuncheng Zhang
Date: 2023-08-15
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


# %% ---- 2023-08-15 ------------------------
# Requirements and constants
import os
import time
import threading


# %% ---- 2023-08-15 ------------------------
# Function and class


# %% ---- 2023-08-15 ------------------------
# Play ground
if __name__ == '__main__':
    def decoding_machine():
        os.system(
            ' '.join(['python', './decoding/decoder_websocket_server.py']))

    def main_loop():
        os.system(' '.join(['python', './main.py']))

    threading.Thread(target=decoding_machine, daemon=True).start()
    threading.Thread(target=main_loop, daemon=False).start()

    # input('Press enter to escape')


# %% ---- 2023-08-15 ------------------------
# Pending


# %% ---- 2023-08-15 ------------------------
# Pending
