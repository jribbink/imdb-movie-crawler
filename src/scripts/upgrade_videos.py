"""
Lots of terrible code ahead.  I only kept it so that my git repo looks bigger to acknowledge the amount of work I did :P
"""

from genericpath import isdir
import os
from re import L
from time import sleep
from util.util import cls, dump_videos, load_videos, video_info_dictionary_to_object
from util.io import request_input, request_range

from os import listdir
from os.path import isfile, join

from video import Video


def upgrade_videos():
    videos: "list[Video]" = load_videos(
        request_input(
            "Please enter the name of the input file (default dump.file): ",
            default="dump.file",
        )
    )
    upgrade_count = video_info_dictionary_to_object(videos)

    print("{} videos upgraded!".format(upgrade_count))

    mypath = "images"
    images = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    for image in images:
        id = int(image[0:5])
        title = videos[id].query.title
        img_loc = "{}/{:05}_{}.jpg".format(
            mypath, id, title.replace("\\", "").replace("/", "")
        )
        if os.path.join(mypath, image) == img_loc:
            continue
        os.rename(os.path.join(mypath, image), img_loc)

        for video in videos:
            if hasattr(video, "info") and video.info.image.startswith(str(id)):
                video.info.image = img_loc

    w = [x[0] for x in os.walk(mypath) if x[0] is not "images"]
    for p in w:
        pat = p
        files = [f for f in listdir(p) if isfile(join(p, f))]
        while len(files) is 0:
            w = [f for f in listdir(pat) if isdir(join(pat, f))]
            pat = os.path.join(pat, w[0])
            files = [f for f in listdir(pat) if isfile(join(pat, f))]

        file = files[0]
        id = int(pat[7:12])
        file_path = os.path.join(pat, file)
        title = videos[id].query.title.replace("\\", "").replace("/", "")
        img_loc = "{}/{:05}_{}.jpg".format(
            mypath, id, title.replace("\\", "").replace("/", "")
        )
        os.rename(file_path, img_loc)
        os.rmdir(p)

        for video in videos:
            if hasattr(video, "info") and video.info.image.startswith(str(id)):
                video.info.image = img_loc

    images = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for video in videos:
        img_loc = os.path.join(mypath, image)  ### BAD! SETS TO LAST IMAGE
        if hasattr(video, "info"):
            id = video.info.image[7:12]
            for image in images:
                if image.startswith(id):
                    video.info.image = img_loc

    dump_videos(
        videos,
        request_input(
            "Please enter the name of the dump file (default dump.file): ",
            default="dump.file",
        ),
    )
