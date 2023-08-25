"""
File: how_to_use_experiment_data.py
Author: Chuncheng Zhang
Date: 2023-08-25
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


# %% ---- 2023-08-25 ------------------------
# Requirements and constants
import joblib
import numpy as np

from rich import print
from pathlib import Path


# %% ---- 2023-08-25 ------------------------
# Function and class
select_idx = 0


# %% ---- 2023-08-25 ------------------------
# Play ground
path_array = list(Path('experiment-data').iterdir())
for j, p in enumerate(path_array):
    if select_idx == j:
        print(f'[*{j}*]:\t{p}')
    else:
        print(f'[{j}]:\t{p}')

selected_path = path_array[select_idx]

print(f'Selected path: {selected_path}')


# %% ---- 2023-08-25 ------------------------
# Pending
data = joblib.load(selected_path)
print('----------------------------------------------------------------')
print('Data explain, it is a dict with two keys:')

for key, value in data.items():
    print('-' * 8)
    print(
        f'{key}:\t{type(value)}, length={len(value)}, elementType={type(value[0])}')

    print('element example:')

    if isinstance(value[0], tuple):
        for j, v in enumerate(value[0]):
            d = v.shape if isinstance(v, type(np.array([0]))) else v
            print(f'[{j}]:\t({type(v)}),\t{d}')

    if isinstance(value[0], dict):
        for k, v in value[0].items():
            d = v.shape if isinstance(v, type(np.array([0]))) else v
            print(f'{k}:\t({type(v)}),\t{d}')


# %% ---- 2023-08-25 ------------------------
# Pending
