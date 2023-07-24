"""
File: eeg_device_reader.py
Author: Chuncheng Zhang
Date: 2023-07-24
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


# %% ---- 2023-07-24 ------------------------
# Requirements and constants
import time

import numpy as np
import matplotlib.pyplot as plt

from threading import Thread
from datetime import datetime

from .toolbox import matplotlib_to_opencv_image

# %%

# Use agg backend to make the fig rendering in the thread
import seaborn as sns
import matplotlib
sns.set_theme()
matplotlib.use('agg')

# %% ---- 2023-07-24 ------------------------
# Function and class


class EEGDeviceReader(object):
    '''
    Request data package from EEG device,
    the package is the shape of (channels x package_length).

    The sample_rate refers the sampling rate of the device.
    '''
    channels = 64
    package_length = 40
    sample_rate = 1000  # Hz
    package_interval = package_length / sample_rate  # Interval between packages

    def __init__(self):
        self.data_buffer = []
        self.bgr_list = []
        self.run_forever()
        pass

    def _read_data(self):
        """Simulate the EEG device reading,
        it is called by the self.run_forever() method.
        """
        self._read_data_idx = 0
        while self.running:
            t = time.time()
            incoming = np.zeros((self.channels, self.package_length)) + t

            for j in range(self.package_length):
                incoming[:, j] += j / self.sample_rate
                incoming[:, j] %= 1

            self.data_buffer.append((self._read_data_idx, t, incoming))
            self._read_data_idx += 1

            if self.get_data_buffer_size() > 5000:
                self.data_buffer.pop(0)

            time.sleep(self.package_interval)

    def add_offset(self, data):
        """Add offset to the channels of the array for display purposes
        The operation is in-place.

        Args:
            data (2d array): The data of EEG data, the shape is (channels x times)

        Returns:
            2d array: The data with offset
        """
        for j, d in enumerate(data):
            d += j
        return data

    def _plot_data(self,
                   window_length=2  # Seconds
                   ):
        """Plot the data,
        it append the mpl fig into self.bgr_list.

        Args:
            window_length (int, optional): How many seconds is the window. Defaults to 2#Seconds.
        """

        packages = int(window_length / self.package_interval)

        while self.running:

            fetched = self.peek_latest_data_by_length(packages)
            if fetched is None:
                continue

            timestamp = fetched[-1][1]

            fig, axe = plt.subplots(1, 1, figsize=(4, 4), dpi=100)

            current_package = fetched[-1][0] % packages

            # Draw the left part of the signal
            select = [e[2] for e in fetched
                      if (e[0] % packages) < current_package]
            if len(select) > 0:
                d = np.concatenate(select, axis=1)
                self.add_offset(d)

                t = np.linspace(
                    0, d.shape[1]/self.sample_rate, d.shape[1], endpoint=False)

                axe.plot(t, d.transpose())

            # Draw the right part of the signal
            select = [e[2] for e in fetched
                      if (e[0] % packages) > current_package]
            if len(select) > 0:
                d = np.concatenate(select, axis=1)
                self.add_offset(d)

                t = np.linspace(
                    window_length-d.shape[1]/self.sample_rate, window_length, d.shape[1], endpoint=False)

                axe.plot(t, d.transpose(), linewidth=0.5)

            # Setup axe
            axe.set_xlim(0, window_length)

            axe.set_title(
                str(datetime.fromtimestamp(timestamp).today()))

            # Convert the bgr into the opencv-image
            bgr = matplotlib_to_opencv_image(fig)

            self.bgr_list.append((timestamp, bgr))

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
        if self.get_data_buffer_size() < 1:
            return None

        output = [e for e in self.data_buffer[-length:]]

        return output

    def run_forever(self):
        """Run the loops forever.
        """
        self.running = True
        Thread(target=self._read_data, daemon=True).start()
        Thread(target=self._plot_data, daemon=True).start()
        pass


# %% ---- 2023-07-24 ------------------------
# Play ground


# %% ---- 2023-07-24 ------------------------
# Pending


# %% ---- 2023-07-24 ------------------------
# Pending
