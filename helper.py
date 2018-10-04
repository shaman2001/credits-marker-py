import json
import numpy as np
from datetime import timedelta
from termcolor import colored

from block import Block
from const import Const


def read_json(path):
    with open(path, encoding='utf-8') as data_file:
        data = json.loads(data_file.read())
        return data


def dur_format(frame_num):
    return str(timedelta(seconds=frame_num/Const.FPS)).split(".")[0] + '.' + str(frame_num % Const.FPS)


def get_index(str_array, str_item, start=None, end=None):
    if start is None:
        start = 0
    if end is None:
        end = len(str_array)
    try:
        return str_array.index(str_item, start, end)
    except ValueError:
        return -1


def calc_range(total_len, ind, seek_fact):
    num = ind - total_len // seek_fact
    start = 0 if num < 0 else num
    num = ind + total_len // seek_fact
    end = num if num < total_len else total_len
    return start, end


def color_compare(string1, string2, color='red'):
    result = ''
    n_diff = 0
    for c1, c2 in zip(string1, string2):
        if c1 == c2:
            result += c2
        else:
            result += colored(c2, color, attrs=['reverse'])
            n_diff += 1
    return result, n_diff


def sec2time_format(x):
    str_repr = str(timedelta(seconds=x)).split('.')[0].split(':')[1:]
    return ':'.join(str_repr)


def get_blocks(limits, last_pos):
    res = list()
    print('Recognized blocks:')
    for i in range(len(limits) + 1):
        begin = limits[i-1] if i != 0 else 0
        end = limits[i] if i != len(limits) else last_pos
        print('Block No {}: {} - {}'.format(i, sec2time_format(begin), sec2time_format(end)))
        block = Block(begin, end)
        res.append(block)
    return res


def smooth_data(data_arr, win_size):
    window = np.ones(int(win_size))/float(win_size)
    return np.convolve(data_arr, window, mode='full')
