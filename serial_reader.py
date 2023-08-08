"""

File: serial_reader.py

Author: Chuncheng Zhang

Date: 2023-08-08

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


# %% ---- 2023-08-08 ------------------------

# Requirements and constants
import time
import struct
import serial


from rich import print


# %% ---- 2023-08-08 ------------------------

# Function and class

def decode_bytearray(bytearray):
    a = struct.unpack('>I', bytearray[2:6])
    b = struct.unpack('>f', bytearray[6:10])
    c = struct.unpack('>f', bytearray[10:14])
    d = struct.unpack('>f', bytearray[14:18])

    return dict(
        idx=a[0],
        ecg=b[0],
        esg=c[0],
        tem=d[0]
    )


# %% ---- 2023-08-08 ------------------------

# Play ground
tic = time.time()

with serial.Serial('COM4', 115200) as ser:
    for _ in range(100):
        t = time.time()
        received_bytes = ser.read(21)
        package = decode_bytearray(received_bytes)
        print(t - tic, received_bytes, package)


# %% ---- 2023-08-08 ------------------------

# Pending


# %% ---- 2023-08-08 ------------------------

# Pending
