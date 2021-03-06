import numpy as np
from tqdm import tqdm
from const import Const
from graph import build_plot
from helper import read_json, dur_format, get_index, calc_range, color_compare, sec2time_format, get_blocks, \
    smooth_data, smooth_peaks


def compare_episodes(base_ep, comp_ep, brief):
    print('Comparing episodes: base episode: {}, comparing episode: {}'.format(base_ep['title'], comp_ep['title']))
    base_arr = base_ep['frames']
    comp_arr = comp_ep['frames']
    result = compare_frm_arrays(base_arr, comp_arr, brief)
    res_title_out = 'Result of frame-by-frame episodes comparison: <{}> & <{}>'.format(base_ep['title'], comp_ep['title'])
    return result, res_title_out


def compare_frm_arrays(base_arr, comp_arr, brief):
    comp_matched_inds = []
    part_match_counter = 0
    prev_match_ind = -1
    match_in_sec = 0
    result = list()
    log = ''
    pbar = None
    if brief:
        pbar = tqdm(base_arr, unit='frames', mininterval=1.0)
        pbar.external_write_mode()
        pbar.set_description_str('Processing frames progress')
    comp_len = len(comp_arr)
    for i, frm in enumerate(base_arr):
        # if prev_match_ind != -1:
        #     start = prev_match_ind - 2
        #     end = prev_match_ind + 2
        # else:
        #     start, end = calc_range(comp_len, i if prev_match_ind == -1 else prev_match_ind, Const.SEEK_FACTOR)
        start, end = calc_range(comp_len, i if prev_match_ind == -1 else prev_match_ind, Const.SEEK_FACTOR)
        comp_frm_ind = get_index(comp_arr, frm, start, end)
        if comp_frm_ind != -1:# and comp_frm_ind not in comp_matched_inds:
            match_in_sec += 1
            log = '{:s}\t{:s} - matched frame in comp episode {:s}'.format(
                                        dur_format(i),
                                        frm,
                                        dur_format(comp_frm_ind))
            prev_match_ind = comp_frm_ind
            comp_matched_inds.append(comp_frm_ind)
            if part_match_counter != 0:
                part_match_counter = 0
        elif prev_match_ind != -1 and part_match_counter < Const.PART_MATCH_LIMIT:
            part_match_counter += 1
            comp_frm_ind = prev_match_ind + part_match_counter
            if comp_frm_ind < comp_len:
                m_frame = comp_arr[comp_frm_ind]
            else:
                prev_match_ind = -1
                log = 'attempt to go beyond the bounds of the array '
                continue
            frm_diff, dif_amount = color_compare(frm, m_frame, 'red')
            if dif_amount < Const.PART_MATCH_RANGE.start:# and comp_frm_ind not in comp_matched_inds:
                match_in_sec += 1
                comp_matched_inds.append(comp_frm_ind)
                log = '{:s}\t{:s} - {} - ALMOST matched ({} symbols) - {}'.format(
                                        dur_format(i),
                                        frm,
                                        frm_diff,
                                        dif_amount,
                                        dur_format(prev_match_ind + part_match_counter))
            elif dif_amount in Const.PART_MATCH_RANGE or dif_amount >= Const.PART_MATCH_RANGE.stop:
                prev_match_ind = -1
                log = '{:s}\t{:s} - {} - PARTIALLY matched({} symbols).Do not count'.format(
                                        dur_format(i),
                                        frm,
                                        frm_diff,
                                        dif_amount)
        else:
            part_match_counter += 1
            if prev_match_ind != -1:
                prev_match_ind = -1
            log = '{:s}\t{:s} - NOT matched'.format(dur_format(i), frm)
        if (i + 1) % Const.FPS == 0:
            result.append(match_in_sec * 100 // Const.FPS)
            match_in_sec = 0
        if brief and pbar is not None:
            pbar.update(1)
        elif not brief:
            print(log)
    if pbar is not None:
        pbar.close()
    return result


def divide_on_blocks(comp_result):
    res = {}
    blocks_limits = list()
    mismatched_sec_counter = 0
    matched_sec_counter = 0
    new_block = True
    cur_block_matched = None
    for sec, match_amount in enumerate(comp_result):
        cur_sec_matched = match_amount > Const.BLOCK_PASS_CRITERION
        if new_block:
            block_begin = sec
            cur_block_matched = cur_sec_matched
            new_block = False
        else:
            if cur_sec_matched != cur_block_matched:
                mismatched_sec_counter += 1

            else:
                matched_sec_counter += 1
                mismatched_sec_counter = 0
        if mismatched_sec_counter > Const.MIN_BLOCK_DUR and matched_sec_counter >= Const.MIN_BLOCK_DUR:
            blocks_limits.append(sec - mismatched_sec_counter)
            new_block = True
            mismatched_sec_counter = 0
        elif mismatched_sec_counter > Const.MIN_BLOCK_DUR: #
            cur_block_matched = not cur_block_matched
            mismatched_sec_counter = 0
    return get_blocks(blocks_limits, len(comp_result))


def base_algorithm(base_fpath, comp_fpath):
    window = 6
    res = list()
    base_data = read_json(base_fpath)
    comp_data = read_json(comp_fpath)
    cmp_res, res_title = compare_episodes(base_data, comp_data, True)
    cmp_res_smoothed = smooth_data(cmp_res, window)
    cmp_res_peaks = smooth_peaks(cmp_res, window)
    data = [cmp_res, cmp_res_smoothed, cmp_res_peaks]  # pass to build_plot method a list of data_arrays
    blocks_source = divide_on_blocks(cmp_res)
    blocks_smoothed = divide_on_blocks(cmp_res_smoothed)
    block_peaks = divide_on_blocks(cmp_res_peaks)
    build_plot(data, title=res_title, do_block=True, smooth_fact=window)


base_file_path = Const.INPUT_DIR + "WW/Westworld_s01e02.json"
comp_file_path = Const.INPUT_DIR + "WW/Westworld_s01e01.json"
base_algorithm(base_file_path, comp_file_path)


