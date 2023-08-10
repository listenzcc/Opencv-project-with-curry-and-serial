"""
File: stm32_device_reader.py
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

import numpy as np
import matplotlib.pyplot as plt

from threading import Thread
from datetime import datetime

from . import LOGGER, CONF
from .toolbox import matplotlib_to_opencv_image, uint8

# Use agg backend to make the fig rendering in the thread
import seaborn as sns
import matplotlib
sns.set_theme()
matplotlib.use('agg')

# %% ---- 2023-08-08 ------------------------
# Function and class


def decode_bytearray(bytearray):
    a = struct.unpack('>I', bytearray[2:6])
    b = struct.unpack('>f', bytearray[6:10])
    c = struct.unpack('>f', bytearray[10:14])
    d = struct.unpack('>f', bytearray[14:18])

    return dict(
        idx=a[0],
        eog=b[0],
        emg=c[0],
        tem=d[0],
        timestamp=time.time()
    )


class Stm32DeviceReader(object):
    packages_limit = 5000  # number of packages
    display_window_length = 5  # seconds
    display_pixel_width = 400  # pixels
    display_pixel_height = 400  # pixels
    display_dpi = 100  # DPI
    sample_rate = 10  # Hz
    port = 'COM4'  # port name
    baudrate = 115200  # baudrate
    channels_colors = dict(  # channels and their colors
        eog='#a00000',
        emg='#00a000',
        tem='#0000a0'
    )

    def __init__(self):
        self.conf_override()
        self.running = False

        LOGGER.debug(f'Initialize {self.__class__} with {self.__dict__}')

    def conf_override(self):
        for key, value in CONF['stm32'].items():
            if not (hasattr(self, key)):
                LOGGER.warning(f'Invalid key: {key} in CONF')
                continue
            setattr(self, key, value)

        LOGGER.debug('Override the options with CONF')

    def start(self):
        if not self.running:
            self.run_forever()
        else:
            LOGGER.error('Can not start, since it is already running')

    def placeholder_image(self):
        return uint8(np.zeros((self.display_pixel_height,
                               self.display_pixel_width,
                               3)))

    def stop(self):
        self.running = False

    def _read_data(self):
        self.data_buffer = []

        LOGGER.debug('Read data loop starts')

        try:
            with serial.Serial(self.port, self.baudrate) as ser:
                while self.running:
                    incoming = ser.read(21)
                    package = decode_bytearray(incoming)
                    self.data_buffer.append(package)

                if self.get_data_buffer_size() > self.packages_limit:
                    LOGGER.warning(
                        f'Data buffer exceeds {self.packages_limit} packages.')
                    self.data_buffer.pop(0)

        except Exception as err:
            LOGGER.error(f"Serial reading failed, {err}")

        LOGGER.debug('Read data loop stops.')

    def _plot_data(self):
        """Plot the data,
        it append the mpl fig into self.bgr_list.
        """

        packages = int(self.display_window_length * self.sample_rate)
        self.bgr_list = []

        LOGGER.debug('Plot data starts.')

        while self.running:
            fetched = self.peek_latest_data_by_length(packages)

            if fetched is None:
                continue

            timestamp = fetched[-1]['timestamp']

            fig, axe = plt.subplots(1, 1, figsize=(
                self.display_pixel_width/self.display_dpi, self.display_pixel_height/self.display_dpi), dpi=self.display_dpi)

            latest_package_idx = fetched[-1]['idx'] % packages

            # Draw the left part of the signal
            select = [e for e in fetched
                      if e['idx'] % packages < latest_package_idx]
            n = len(select)
            if n > 0:
                t = np.linspace(0, n/self.sample_rate, n, endpoint=False)
                for name, color in self.channels_colors.items():
                    array = [e[name] for e in select]
                    axe.plot(t, array, label=name, color=color)

                axe.legend()

            # Draw the right part of the signal
            select = [e for e in fetched
                      if e['idx'] % packages > latest_package_idx]
            m = len(select)
            if m > 0:
                t = np.linspace(self.display_window_length - m/self.sample_rate,
                                self.display_window_length, m, endpoint=False)
                for name, color in self.channels_colors.items():
                    array = [e[name] for e in select]
                    axe.plot(t, array, linewidth=0.5, label=name, color=color)

                if n == 0:
                    axe.legend()

            # Setup axe
            axe.set_xlim(0, self.display_window_length)

            axe.set_title(
                f'Stm32 ({self.port}) {self.get_data_buffer_size()} | {self.packages_limit}')

            # Convert the bgr into the opencv-image
            fig.tight_layout()
            bgr = matplotlib_to_opencv_image(fig)

            self.bgr_list.append((timestamp, bgr))

            continue

        LOGGER.debug('Plot data stops.')

    def read_bgr(self):
        if len(self.bgr_list) < 1:
            return None

        timestamp, bgr = self.bgr_list.pop(0)

        return timestamp, bgr

    def get_data_buffer_size(self):
        """Get the current buffer size for the data_buffer

        Returns:
            int: The buffer size.
        """
        return len(self.data_buffer)

    def peek_latest_data_by_length(self, length=50):
        """Peek the latest data in the self.data_buffer with given length.

        If there is no data available, return None.

        Args:
            length (int, optional): How many packages are required, the length in seconds are length x self.package_interval. Defaults to 50.

        Returns:
            list: The data being fetched. The elements of the list are (idx, timestamp, data of (self.channels x self.package_length)).
            None if there is no data available.
        """
        n = self.get_data_buffer_size()

        if n < 1:
            LOGGER.error('The data buffer is empty')
            return None

        if n < length:
            LOGGER.warning(f'Can not peek data with {length} samples.')

        return list(self.data_buffer[-length:])

    def peek_latest_data_by_milliseconds(self, milliseconds=1000):
        """Peek the latest data available for given milliseconds.

        Args:
            milliseconds (int, optional): The milliseconds being required. Defaults to 1000.

        Returns:
            np.array: The (3 x n) array, the n refers the samples and the 3 refers the channels, the order is given in self.channels_colors.
        """
        length = int(milliseconds / 1000 * self.sample_rate)

        array = self.peek_latest_data_by_length(length)

        if array is None:
            LOGGER.error(
                f'Failed peek_latest_data_by_length with {milliseconds}')
            return None

        return np.array([[e[k] for k in self.channels_colors] for e in array]).transpose()

    def run_forever(self):
        """Run the loops forever.
        """
        self.running = True
        Thread(target=self._read_data, daemon=True).start()
        Thread(target=self._plot_data, daemon=True).start()
        return

# %% ---- 2023-08-08 ------------------------
# Play ground


# %% ---- 2023-08-08 ------------------------
# Pending


# %% ---- 2023-08-08 ------------------------
# Pending
