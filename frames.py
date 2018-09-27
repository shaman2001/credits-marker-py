import json
import difflib
from datetime import timedelta
import numpy as np

from tqdm import tqdm
from termcolor import colored, cprint
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import matplotlib.ticker as ticker

fps = 25


def read_json(path):
    with open(path, encoding='utf-8') as data_file:
        data = json.loads(data_file.read())
        return data


def compare_episodes(base_ep, comp_ep, do_print=True):
    print('Comparing episodes: base episode: {}, comparing episode: {}'.format(base_ep['title'], comp_ep['title']))
    mismatch_counter = 0
    prev_match_ind = 0
    match_in_sec = 0
    result = {}
    pbar = tqdm(base_ep['frames'], unit='frames', mininterval=1.0)
    pbar.set_description_str('Processing frames progress')
    comp_len = len(comp_ep['frames'])
    for i, frm in enumerate(base_ep['frames']):
        start, end = calc_range(comp_len, i)
        comp_frm_ind = get_index(comp_ep['frames'], frm, start, end)
        if comp_frm_ind >= 0:
            if do_print:
                print('{:s} {:s} - matched frame in comp episode {:s}'.format(dur_format(i), frm, dur_format(comp_frm_ind)))
                prev_match_ind = comp_frm_ind
                if mismatch_counter > 0:
                    mismatch_counter = 0
            match_in_sec += 1
        else:
            if do_print:
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
        pbar.update(1)
    pbar.close()
    return result


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


def format_time(array):
    result = []
    for item in array:
        result.append(str(timedelta(seconds=item)).split(".")[0])
    return result


def build_plot(data):

    def add_titlebox(ax, text):
        ax.text(.55, .8, text,
                horizontalalignment='center',
                transform=ax.transAxes,
                bbox=dict(facecolor='white', alpha=0.6),
                fontsize=6)
        return ax
    plt.interactive(1)
    fig, ax = plt.subplots(nrows=5, ncols=2, figsize=(15, 10))
    my_axes = ax.flatten()
    fig.subplots_adjust(hspace=0.5)
    i = 0

    for cur_axe in my_axes:
        start = i * 10000 // fps
        end = (i + 1) * 10000 // fps if (i + 1) * 10000 // fps <= len(data) else len(data)
        add_titlebox(cur_axe, 'Start frame:{:d}, end frame:{:d}'.format(start * fps, end * fps))
        cur_dur_range = range(start, end)
        cur_graph_range = [data[k] for k in cur_dur_range]


        # cur_axe.vlines(np.arange(start, end, 1), ymin=0, ymax=cur_graph_range, colors='g', linestyles='solid')
        cur_axe.plot(np.arange(start, end, 1), cur_graph_range, '.-', linewidth=1, markersize=2)
        # cur_axe.fill_between(cur_dur_range, cur_graph_range, facecolor='blue', alpha=0.5)
        cur_axe.set_xlabel('time')
        cur_axe.set_ylabel('% of matches')
        # for tick in cur_axe.xaxis.get_minor_ticks():
        #     tick.tick1line.set_markersize(0)
        #     tick.tick2line.set_markersize(0)
        #     tick.label1.set_horizontalalignment('center')

        cur_axe.grid(True)
        cur_axe.set_ylim(top=100)
        # fig.autofmt_xdate()
        if end == len(data):
            break
        i += 1
    plt.show()


baseData = read_json("./Game_of_Thrones_S07E02.json")
compData = read_json("./Game_of_Thrones_S07E03.json")

cmp_res = compare_episodes(baseData, compData, False)

build_plot(cmp_res)
