import json
import difflib
from datetime import timedelta
import numpy as np

from tqdm import tqdm
from termcolor import colored, cprint
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from const import Const

fps = 25
input_dir = 'input/'


def read_json(path):
    with open(path, encoding='utf-8') as data_file:
        data = json.loads(data_file.read())
        return data


def compare_episodes(base_ep, comp_ep, print_frames=True):
    print('Comparing episodes: base episode: {}, comparing episode: {}'.format(base_ep['title'], comp_ep['title']))
    mismatch_counter = 0
    prev_match_ind = 0
    match_in_sec = 0
    result = {}
    if not print_frames:
        pbar = tqdm(base_ep['frames'], unit='frames', mininterval=1.0)
        pbar.set_description_str('Processing frames progress')
    comp_len = len(comp_ep['frames'])
    for i, frm in enumerate(base_ep['frames']):
        start, end = calc_range(comp_len, i)
        comp_frm_ind = get_index(comp_ep['frames'], frm, start, end)
        if comp_frm_ind >= 0:
            if print_frames:
                print('{:s} {:s} - matched frame in comp episode {:s}'.format(dur_format(i), frm, dur_format(comp_frm_ind)))
                prev_match_ind = comp_frm_ind
                if mismatch_counter > 0:
                    mismatch_counter = 0
            match_in_sec += 1
        else:
            if print_frames:
                if mismatch_counter < 5:
                    m_frame = comp_ep['frames'][prev_match_ind + mismatch_counter]
                    frm_diff, count = color_compare(frm, m_frame, 'red')
                    # print('{:s} {:s} - NOT matched {}. Diff {}'.format(dur_format(i), frm, m_frame, frm_diff))
                    print('{:s} {:s} - NOT matched {}. {} symbols'.format(dur_format(i), frm, frm_diff, count))
                else:
                    print('{:s} {:s} - NOT matched'.format(dur_format(i), frm))
                mismatch_counter += 1
        if (i + 1) % fps == 0:
            result[i//fps] = match_in_sec*100//fps
            match_in_sec = 0
        if not print_frames:
            pbar.update(1)
    pbar.close()
    res_title_out = 'Result of frame-by-frame episodes comparison: <{}> & <{}>'.format(base_ep['title'], comp_ep['title'])
    return result, res_title_out


def get_index(str_array, str_item, start=None, end=None):
    if start is None:
        start = 0
    if end is None:
        end = len(str_array)

    try:
        return str_array.index(str_item, start, end)
    except ValueError:
        return -1


def calc_range(total_len, ind):
    num = ind - total_len//6
    start = 0 if num < 0 else num
    num = ind + total_len//6
    end = num if num < total_len else total_len
    return start, end


def dur_format(frame_num):
    return str(timedelta(seconds=frame_num/fps)).split(".")[0]


def inline_diff(a, b):
    matcher = difflib.SequenceMatcher(None, a, b)

    def process_tag(tag, i1, i2, j1, j2):
        if tag == 'replace':
            return '{' + matcher.a[i1:i2] + ' -> ' + matcher.b[j1:j2] + '}'
        if tag == 'delete':
            return '{- ' + matcher.a[i1:i2] + '}'
        if tag == 'equal':
            return matcher.a[i1:i2]
        if tag == 'insert':
            return '{+ ' + matcher.b[j1:j2] + '}'
        assert False, "Unknown tag %r" % tag
    return ''.join(process_tag(*t) for t in matcher.get_opcodes())


def color_diff(a, b):
    matcher = difflib.SequenceMatcher(None, a, b)

    def process_tag(tag, i1, i2, j1, j2):
        if tag == 'replace':
            return colored(matcher.b[j1:j2], 'red', attrs=['reverse'])
            # return '{' + matcher.a[i1:i2] + ' -> ' + matcher.b[j1:j2] + '}'
        if tag == 'delete':
            return '{- ' + matcher.a[i1:i2] + '}'
        if tag == 'equal':
            return matcher.a[i1:i2]
        if tag == 'insert':
            return '{+ ' + matcher.b[j1:j2] + '}'
        assert False, "Unknown tag %r" % tag
    return ''.join(process_tag(*t) for t in matcher.get_opcodes())


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
    y_axis.set_major_locator(ticker.MaxNLocator(nbins=3))
    y_axis.set_major_formatter(ticker.PercentFormatter())
    # cur_axe.get_xaxis().set_major_formatter(dates.DateFormatter("%b %Y"))


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
    # fig.subplots_adjust(hspace=0.1)
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
    # input()
    plt.close(fig)


baseData = read_json(Const.input_dir + "Game_of_Thrones_S07E02.json")
compData = read_json(Const.input_dir + "Game_of_Thrones_S07E03.json")

cmp_res, res_title = compare_episodes(baseData, compData, True)

# build_plot(cmp_res, title=res_title)
