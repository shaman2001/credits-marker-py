from datetime import timedelta
import matplotlib.pyplot as plt
from matplotlib import ticker
import numpy as np
from const import Const
from helper import smooth_data


def format_time(x, pos):
    str_repr = str(timedelta(seconds=x)).split('.')[0].split(':')[1:]
    return ':'.join(str_repr)


def format_ax(ax, start, end):
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
    x_axis.set_major_locator(ticker.MaxNLocator(nbins=200, steps=[2, 3, 5, 6]))
    x_axis.set_major_formatter(ticker.FuncFormatter(func=format_time))
    y_axis = ax.get_yaxis()
    y_axis.set_major_locator(ticker.MaxNLocator(nbins=5))
    y_axis.set_major_formatter(ticker.PercentFormatter())


def build_plot(data, parts_num=5, title='', do_block=True, smooth_fact=4):

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
    smoothed_data = smooth_data(data, smooth_fact)
    for cur_axe in my_axes:
        start = i * splt_dur
        end = (i + 1) * splt_dur if (i + 1) * splt_dur <= len(data) else len(data)
        add_titlebox(cur_axe, 'Start frame:{:d}, end frame:{:d}'.format(start * Const.FPS, end * Const.FPS))
        cur_dur_range = range(start, end)
        # cur_graph_range = [data[k] for k in cur_dur_range]
        # cur_axe.plot(cur_dur_range, smooth_data(data[start:end]), 'o-', linewidth=1, markersize=1)
        cur_axe.plot(cur_dur_range, data[start:end], 'o-', linewidth=1, markersize=1)
        cur_axe.plot(cur_dur_range, smoothed_data[start:end], 'o-', linewidth=1, markersize=1)
        format_ax(cur_axe, start, end)
        if end == len(data):
            break
        i += 1
    fig.tight_layout()
    plt.show(block=do_block)
    fig.savefig('output/comparison_result.png')
    plt.close(fig)

