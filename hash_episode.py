#!/usr/bin/env python
from __future__ import (absolute_import, division, print_function)
from PIL import Image
import os
import moviepy.editor as mpy
import imagehash
import sys
import json
import requests


FPS = 25
hash_function = imagehash.average_hash


"""
Find video files of given type in a directory
"""


def is_video(v_file):
    f = v_file.lower()
    return f.endswith(".mp4") or f.endswith(".avi") or \
           f.endswith(".mkv") or f.endswith(".mpg") or f.endswith(".ts") in f


"""
Main function to compute hashes and find the matching ones.
"""


def hash_movies(v_file):
    if is_video(v_file):
        video_file = os.path.abspath(v_file)
    else:
        print("file is not a video file")
        exit(1)
    if not os.path.exists(os.path.curdir+'/tmp'):
        os.mkdir(os.path.curdir+'/tmp', 0o777)
    i = 0
    episode = mpy.VideoFileClip(video_file, audio=False, target_resolution=(90, 160))
    episode_frames = []
    print("hashing", video_file)
    # grab still frames out of a video, save them to temp file and make a hash \
    # store hash into frames list.
    for frame in episode.iter_frames(FPS, False, False, dtype='uint8'):
        frame_image = mpy.ImageClip(frame)
        filename = "tmp/frame_%s_%s.bmp" % (0, 0)
        frame_image.save_frame(filename)
        frame_hash = hash_function(Image.open(filename))
        episode_frames.append(str(frame_hash))
        i = i+1
    return episode_frames


def build_request(crid, season_id, show_id, episode_number, title, frames,):
    request = {
        'title': title,
        'id': crid,
        'seasonId': season_id,
        'showId': show_id,
        'episodeNumber': episode_number,
        'frames': frames
    }
    request_body = json.dumps(request)
    with open(title+".json","w") as json_output:
        json.dump(request, json_output)
    return request_body


if __name__ == '__main__':
    f1 = sys.argv[1]
    crid = sys.argv[2]
    season_id = sys.argv[3]
    show_id = sys.argv[4]
    episode_number = sys.argv[5]
    title = sys.argv[6]

    if len(f1) > 1:
        frames = hash_movies(v_file=f1)
        request_body = build_request(crid=crid, season_id=season_id, show_id=show_id,
                                     episode_number=episode_number, title=title, frames=frames)
        headers = {"Content-Type": "application/json"}
        url = 'http://127.0.0.1:8080/v1/frames/'+crid
        requests.put(url, data=request_body, headers=headers)
    else:
        print("input file is expected")
