import json
from datetime import timedelta
import numpy as np

from tqdm import tqdm
from termcolor import colored
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from const import Const

fps = Const.FPS
input_dir = Const.INPUT_DIR
seek_factor = Const.SEEK_FACTOR
mismatch_limit = 5
part_match_range = range(5, 9)


def read_json(path):
    with open(path, encoding='utf-8') as data_file:
        data = json.loads(data_file.read())
        return data


def compare_episodes(base_ep, comp_ep, brief):
    print('Comparing episodes: base episode: {}, comparing episode: {}'.format(base_ep['title'], comp_ep['title']))
    base_arr = base_ep['frames']
    comp_arr = comp_ep['frames']
    result = compare_frm_arrays(base_arr, comp_arr, brief)
    res_title_out = 'Result of frame-by-frame episodes comparison: <{}> & <{}>'.format(base_ep['title'], comp_ep['title'])
    return result, res_title_out


def compare_frm_arrays(base_arr, comp_arr, brief):
    result = {}
    pbar = None
    comp_map = conv_list_to_dict(comp_arr)
    if brief:
        pbar = tqdm(base_arr, unit='frames', mininterval=1.0)
        pbar.set_description_str('Processing frames progress')
    mismatch_counter = 0
    prev_match_ind = 0
    match_in_sec = 0
    comp_len = len(comp_arr)
    log = ''
    for i, frm in enumerate(base_arr):
        start, end = calc_range(comp_len, i, seek_factor)
        comp_frm_ind = get_index(comp_map, frm, start, end)
        if comp_frm_ind != -1:
            match_in_sec += 1
            del comp_map[comp_frm_ind]
            prev_match_ind = comp_frm_ind
            if mismatch_counter > 0:
                mismatch_counter = 0
            log = '{:s} {:s} - matched frame in comp episode {:s}'.format(dur_format(i), frm, dur_format(comp_frm_ind))
        elif match_in_sec > 0 and mismatch_counter < mismatch_limit:
            mismatch_counter += 1
            if prev_match_ind + mismatch_counter in comp_map.keys():
                m_frame = comp_map[prev_match_ind + mismatch_counter]
                frm_diff, dif_amount = color_compare(frm, m_frame, 'red')
                if dif_amount < part_match_range.start:
                    match_in_sec += 1
                    del comp_map[prev_match_ind + mismatch_counter]
                    log = '{:s} {:s} - almost matched {}. {} symbols'.format(dur_format(i), frm, frm_diff, dif_amount)
                elif dif_amount in part_match_range or dif_amount >= part_match_range.stop:
                    log = '{:s} {:s} - NOT matched {}. {} symbols'.format(dur_format(i), frm, frm_diff, dif_amount)
                    mismatch_counter += 1
        else:
            mismatch_counter += 1
            log = '{:s} {:s} - NOT matched'.format(dur_format(i), frm)
        if (i + 1) % fps == 0:
            result[i//fps] = match_in_sec * 100 // fps
            match_in_sec = 0
        if brief and pbar is not None:
            pbar.update(1)
        elif not brief:
            print(log)
    if pbar is not None:
        pbar.close()
    return result


def get_index(str_map, str_item, start=None, end=None):
    if start is None:
        start = 0
    if end is None:
        end = len(str_map)
    try:
        ind = list(str_map.keys())[list(str_map.values()).index(str_item)]
        return ind if ind in range(start, end) else -1
    except ValueError:
        return -1


def first(iterable, condition=lambda x: True):
    return next((x for x in iterable if condition(x)), -1)


def conv_list_to_dict(hash_list):
    return {i: hash_list[i] for i in range(0, len(hash_list))}


def calc_range(total_len, ind, seek_fact):
    num = ind - total_len//seek_fact
    start = 0 if num < 0 else num
    num = ind + total_len//seek_fact
    end = num if num < total_len else total_len
    return start, end


def dur_format(frame_num):
    return str(timedelta(seconds=frame_num/fps)).split(".")[0]


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


def format_time(x, pos):
    str_repr = str(timedelta(seconds=x)).split('.')[0].split(':')[1:]
    return ':'.join(str_repr)


def format_ax(ax, start, end):
    # ax.set_xlabel('time (s)')
    ax.set_ylabel('% of matches')
    ax.tick_params(axis='x',
                   direction='in',
                   labelcolor='r',
                   labelsize=5,
                   width=1,
                   labelrotation=90,
                   grid_linestyle='dotted',
                   grid_alpha=0.5
                   )
    ax.grid(True)
    ax.set_ylim(top=100)
    ax.set_xlim(left=start, right=end)
    x_axis = ax.get_xaxis()
    x_axis.set_major_locator(ticker.MaxNLocator(nbins=100, steps=[3, 5, 6]))
    x_axis.set_major_formatter(ticker.FuncFormatter(func=format_time))
    y_axis = ax.get_yaxis()
    y_axis.set_major_locator(ticker.MaxNLocator(nbins=4))
    y_axis.set_major_formatter(ticker.PercentFormatter())


def build_plot(data, parts_num=5, title=''):

    def add_titlebox(ax, text):
        ax.text(.55, .8, text,
                horizontalalignment='center',
                transform=ax.transAxes,
                bbox=dict(facecolor='white', alpha=0.6),
                fontsize=6)
        return ax
    from math import ceil
    splt_dur = ceil(len(data)/parts_num)
    plt.interactive(True)
    fig, ax = plt.subplots(nrows=parts_num, ncols=1, figsize=(15, 8))
    fig.suptitle(title)
    my_axes = ax.flatten()
    i = 0
    for cur_axe in my_axes:
        start = i * splt_dur
        end = (i + 1) * splt_dur if (i + 1) * splt_dur <= len(data) else len(data)
        add_titlebox(cur_axe, 'Start frame:{:d}, end frame:{:d}'.format(start * fps, end * fps))
        cur_dur_range = range(start, end)
        cur_graph_range = [data[k] for k in cur_dur_range]
        cur_axe.plot(np.arange(start, end, 1), cur_graph_range, 'o-', linewidth=1, markersize=2)
        format_ax(cur_axe, start, end)
        if end == len(data):
            break
        i += 1
    fig.tight_layout()
    plt.show(block=True)
    plt.close(fig)


baseData = read_json(Const.INPUT_DIR + "Game_of_Thrones_S07E01.json")
compData = read_json(Const.INPUT_DIR + "Game_of_Thrones_S07E02.json")

cmp_res, res_title = compare_episodes(baseData, compData, brief=True)

build_plot(cmp_res, title=res_title)
