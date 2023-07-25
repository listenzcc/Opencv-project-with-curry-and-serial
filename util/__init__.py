"""
File: __init__.py
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

from pathlib import Path
from omegaconf import OmegaConf

from loguru import logger as LOGGER


# %% ---- 2023-07-24 ------------------------
# Function and class


# %% ---- 2023-07-24 ------------------------
# Play ground
root = Path(__file__).parent.parent

# %% ---- 2023-07-24 ------------------------
# Pending
eeg_config = dict(
    channels=32,  # number of channels
    sample_rate=1000,  # Hz
    package_length=40,  # number of time points per package
    packages_limit=5000,  # number of packages
    display_window_length=2,  # seconds
    display_inch_width=4,  # inch
    display_inch_height=3,  # inch
    display_dpi=100,  # DPI
    not_exist='Not exist option',
)

video_config = dict(
    video_capture_idx=0,  # cv2.VideoCapture(#)
    display_width=400,  # px
    display_height=300,  # px
)

keyboard_config = dict(
    quite_key_code='q'  # Press the key to quite
)

main_config = dict(
    window_name='Very Fast Very Stable System',
    root_path=root,
    log_path=Path(__file__).parent.parent.joinpath('log/{time}.log'),
    eeg=eeg_config,
    video=video_config,
    keyboard=keyboard_config
)


CONF = OmegaConf.create(main_config)
OmegaConf.save(CONF, root.joinpath('conf/default.yaml'))


# %% ---- 2023-07-24 ------------------------
# Pending
LOGGER.add(CONF['log_path'])

# %%
