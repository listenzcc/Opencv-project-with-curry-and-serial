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
import socket

import numpy as np
import matplotlib.pyplot as plt

from threading import Thread
from datetime import datetime

from . import LOGGER, CONF
from .toolbox import matplotlib_to_opencv_image, uint8
from .NeuroScanMessage import NeuroScanMessage

# %%

# Use agg backend to make the fig rendering in the thread
import seaborn as sns
import matplotlib
sns.set_theme()
matplotlib.use('agg')

# %% ---- 2023-07-24 ------------------------
# Function and class


class Curry8EEGReceiver(object):
    def __init__(self, channels, host, port, sample_rate):
        self.channels = channels
        self.host = host
        self.port = port
        self.sample_rate = sample_rate

        # package 是要发送的数据包
        self.package = None

        LOGGER.debug(f'Initialize {self.__class__} with {self.__dict__}')

        self.buffer = []
        self.connect()

    @LOGGER.catch
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        LOGGER.debug(f'Connect to {self.host}:{self.port}')

    def disconnect(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        LOGGER.debug(f'Disconnect with {self.host}:{self.port}')

    def read_forever(self):
        self.running = True
        Thread(target=self._collect_packages, daemon=True).start()
        LOGGER.debug('Start collecting thread.')

    def get(self):
        return None if len(self.buffer) == 0 else self.buffer.pop(0)

    def _collect_packages(self):
        LOGGER.debug('Collecting packages')

        # 请求获得基本信号：通道数目，采样率和数据包大小
        self.requestInfo()
        # 请求导联信息
        self.requestChannelInfo()

        LOGGER.debug('Request info finishes.')

        while self.running:
            if not self.sock:
                LOGGER.error(f'Cannot connect from {self.sock}')
                break

            # 这只是一个指令
            sendStartStreaming = NeuroScanMessage().startStreaming()
            # 还需要端口发送
            self.sock.send(sendStartStreaming)

            message, data = self.read_from_sock()

            # This == [0] means it is a trigger package
            package_start_time_curry8_timestamp = message['startSample']
            if package_start_time_curry8_timestamp == [0]:
                continue

            t = time.time()
            unpack_data = self._unpackEEG(data)

            # If unpack failed, it means the package is not data package
            if unpack_data is None:
                continue

            print('---------', t, type(unpack_data), unpack_data.shape)
            self.buffer.append(
                (t, unpack_data, package_start_time_curry8_timestamp))

        self.running = False
        LOGGER.debug('Stop collecting packages')

    def read_from_sock(self):
        # receive head
        # head size will always be 20

        headSize = 20
        head = self.sock.recv(headSize)
        head = np.frombuffer(head, dtype=np.uint8)

        # receive body if header meets request
        message = self._parseHeader(head)

        data = self.sock.recv(message['packetSize'], socket.MSG_WAITALL)
        data = np.frombuffer(data, dtype=np.uint8)

        return message, data

    def _unpackEEG(self, data):

        # print('----------------------')
        # print(data, len(data))

        if self.info['datasize'] == 2:
            data = data.view(np.int16)

        elif self.info['datasize'] == 4:
            packet = data.view(np.single)

        numSamples = int(len(packet)/self.info['eegChan'])
        # print(packet, self.info)
        packet = np.reshape(
            packet, (self.info['eegChan'], numSamples), order='F')

        return packet

    def _parseHeader(self, head):
        # parsing head

        code = np.flip(head[4:6]).copy().view(dtype=np.uint16)
        request = np.flip(head[6:8]).copy().view(np.uint16)
        startSample = np.flip(head[8:12]).copy().view(np.uint32)
        packetSize = np.flip(head[12:16]).copy().view(np.uint32)

        return {
            'code': code,
            'request': request,
            'startSample': startSample[0],
            'packetSize': packetSize[0],
        }

    def requestInfo(self):
        # 获得设置信息

        sendBasicInfo = NeuroScanMessage().getBasicInfo()

        self.sock.send(sendBasicInfo)

        message, data = self.read_from_sock()

        size = np.uint8(data[:4]).copy().view(dtype=np.uint32)
        eegChan = np.uint8(data[4:8]).copy().view(np.uint32)
        sampleRate = np.uint8(data[8:12]).copy().view(np.uint32)
        datasize = np.uint8(data[12:16]).copy().view(np.uint32)

        info = {
            'size': size,
            'eegChan': int(eegChan),
            'sampleRate': sampleRate,
            'datasize': datasize[0]
        }

        self.info = info
        LOGGER.debug(f'Request info: {info}')
        return self

    def requestChannelInfo(self):

        # 获得设置信息
        offset_channelId = 1
        offset_chanLabel = offset_channelId + 4
        offset_chanType = offset_chanLabel + 80
        offset_deviceType = offset_chanType + 4
        offset_eegGroup = offset_deviceType + 4
        offset_posX = offset_eegGroup + 4
        offset_posY = offset_posX + 8
        offset_posZ = offset_posY + 8
        offset_posStatus = offset_posZ + 8
        offset_bipolarRef = offset_posStatus + 4
        offset_addScale = offset_bipolarRef + 4
        offset_isDropDown = offset_addScale + 4
        offset_isNoFilter = offset_isDropDown + 4

        # Raw length
        chanInfoLen = (offset_isNoFilter + 4) - 1
        # Length of CURRY channel info struct in bytes, consider padding
        chanInfoLen = round(chanInfoLen/8)*8

        channelNUM = self.info['eegChan']

        sendChannelInfo = NeuroScanMessage().getChannelInfo()

        self.sock.send(sendChannelInfo)

        message, data = self.read_from_sock()

        channelLabels = []
        for i in range(channelNUM):
            j = chanInfoLen*i

            label = data[j+offset_chanLabel-1:j+(offset_chanType-1)]
            label = label[:6].tolist()
            label = ''.join([chr(item) for item in label])
            label = label.replace('\x00', '')

            channelLabels.append(label)

        self.info['channels'] = channelLabels

        channelLabels = [f' {label}' for label in channelLabels]
        channelLabels = ''.join(channelLabels)
        LOGGER.debug(f'Send Data from: {channelLabels}')
        LOGGER.debug(f'Update info: {self.info}')

        return self


class EEGDeviceReader(object):
    '''
    Request data package from EEG device,
    the package is the shape of (channels x package_length).

    The sample_rate refers the sampling rate of the device.
    '''
    channels = 65  # number of channels
    sample_rate = 1000  # Hz
    package_length = 40  # number of time points per package
    packages_limit = 5000  # number of packages
    display_window_length = 2  # seconds
    display_inch_width = 4  # inch
    display_inch_height = 3  # inch
    display_dpi = 100  # DPI
    host = '192.168.1.103'
    port = 4455
    package_interval = package_length / sample_rate  # Interval between packages

    def __init__(self):
        self.conf_override()
        self.running = False

        LOGGER.debug(f'Initialize {self.__class__} with {self.__dict__}')

    def conf_override(self):
        for key, value in CONF['eeg'].items():
            if not (hasattr(self, key)):
                LOGGER.warning(f'Invalid key: {key} in CONF')
                continue
            setattr(self, key, value)

        self.package_interval = self.package_length / \
            self.sample_rate  # Interval between packages

        LOGGER.debug('Override the options with CONF')

    def connect(self):
        LOGGER.debug('Connecting Curry8...')

        self.curry8_eeg_receiver = Curry8EEGReceiver(channels=self.channels,
                                                     host=self.host,
                                                     port=self.port,
                                                     sample_rate=self.sample_rate)
        self.curry8_eeg_receiver.read_forever()

    def placeholder_image(self):
        return uint8(np.zeros((self.display_inch_height*self.display_dpi,
                               self.display_inch_width*self.display_dpi,
                               3)))

    def start(self):
        if not self.running:
            self.run_forever()
        else:
            LOGGER.error('Can not start, since it is already running')

    def stop(self):
        self.running = False

    def _read_data(self):
        """Simulate the EEG device reading,
        it is called by the self.run_forever() method.
        """

        self.data_buffer = []
        self._read_data_idx = 0

        LOGGER.debug('Read data loop starts.')
        while self.running:
            time.sleep(self.package_interval / 2)
            # t = time.time()
            # incoming = np.zeros((self.channels, self.package_length)) + t

            # for j in range(self.package_length):
            #     incoming[:, j] += j / self.sample_rate
            #     incoming[:, j] %= 1

            if not hasattr(self, 'curry8_eeg_receiver'):
                LOGGER.warning('The curry8_eeg_receiver is not available')
                continue

            # Read all the packages available
            n = len(self.curry8_eeg_receiver.buffer)

            for _ in range(n):
                pair = self.curry8_eeg_receiver.get()
                if pair is None:
                    continue
                t, incoming, package_start_time_curry8_timestamp = pair

                self.data_buffer.append((self._read_data_idx, t, incoming))
                self._read_data_idx += 1

            if self.get_data_buffer_size() > self.packages_limit:
                LOGGER.warning(
                    f'Data buffer exceeds {self.packages_limit} packages.')
                self.data_buffer.pop(0)

                # time.sleep(self.package_interval / 10)

        LOGGER.debug('Read data loop stops.')

    def add_offset(self, data):
        """Add offset to the channels of the array for display purposes
        The operation is in-place.

        Args:
            data (2d array): The data of EEG data, the shape is (channels x times)

        Returns:
            2d array: The data with offset
        """
        for j, d in enumerate(data):
            d -= np.min(d)
            if np.max(d) != 0:
                d /= np.max(d)
            d += j
        return data

    def read_bgr(self):
        if len(self.bgr_list) < 1:
            return None

        timestamp, bgr = self.bgr_list.pop(0)

        return timestamp, bgr

    def _plot_data(self):
        """Plot the data,
        it append the mpl fig into self.bgr_list.

        Args:
            window_length (int, optional): How many seconds is the window. Defaults to 2#Seconds.
        """

        packages = int(self.display_window_length / self.package_interval)
        self.bgr_list = []

        LOGGER.debug('Plot data starts.')

        while self.running:
            fetched = self.peek_latest_data_by_length(packages)
            if fetched is None:
                continue

            timestamp = fetched[-1][1]

            fig, axe = plt.subplots(1, 1, figsize=(
                self.display_inch_width, self.display_inch_height), dpi=self.display_dpi)

            current_package = fetched[-1][0] % packages

            if select := [
                e[2] for e in fetched if (e[0] % packages) < current_package
            ]:
                d = np.concatenate(select, axis=1)
                self.add_offset(d)

                t = np.linspace(
                    0, d.shape[1]/self.sample_rate, d.shape[1], endpoint=False)

                axe.plot(t, d.transpose())

            if select := [
                e[2] for e in fetched if (e[0] % packages) > current_package
            ]:
                d = np.concatenate(select, axis=1)
                self.add_offset(d)

                t = np.linspace(
                    self.display_window_length-d.shape[1]/self.sample_rate, self.display_window_length, d.shape[1], endpoint=False)

                axe.plot(t, d.transpose(), linewidth=0.5)

            # Setup axe
            axe.set_xlim(0, self.display_window_length)

            axe.set_title(
                str(datetime.fromtimestamp(timestamp).today()))

            # Convert the bgr into the opencv-image
            bgr = matplotlib_to_opencv_image(fig)

            self.bgr_list.append((timestamp, bgr))

        LOGGER.debug('Plot data stops.')

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

        return list(self.data_buffer[-length:].copy())

    def peek_latest_data_by_milliseconds(self, milliseconds=1000):
        """Peek the latest data available for given milliseconds.

        Args:
            milliseconds (int, optional): The milliseconds being required. Defaults to 1000.

        Returns:
            np.array: The (64 x n) array, the n refers the samples and the 3 refers the channels, the order is given in self.channels_colors.
        """
        num_packages = int(milliseconds / 1000 *
                           self.sample_rate / self.package_length) + 1

        n = int(milliseconds / 1000 * self.sample_rate)

        packages = self.peek_latest_data_by_length(num_packages)

        if packages is None:
            LOGGER.error(
                f'Failed peek_latest_data_by_length with {milliseconds}')
            return None

        return np.concatenate([e[2] for e in packages], axis=1)[:, -n:]

    def run_forever(self):
        """Run the loops forever.
        """
        self.running = True
        Thread(target=self._read_data, daemon=True).start()
        Thread(target=self._plot_data, daemon=True).start()
        Thread(target=self.connect, daemon=True).start()


# %% ---- 2023-07-24 ------------------------
# Play ground


# %% ---- 2023-07-24 ------------------------
# Pending


# %% ---- 2023-07-24 ------------------------
# Pending
