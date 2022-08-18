from urllib.parse import quote
from genericpath import isfile
from posixpath import join
import os
import re
from util.util import dump_videos, load_videos
from util.io import readline, request_input
from video import Video, VideoInfo
from time import sleep
import itertools


def run_misc_script():
    script = request_input("What script would you like to run? ")
    exec(script + "()")
    readline()


def kill_movie():
    videos = load_videos()
    for video in videos:
        if "AWAKENING IN THE NOW" in video.title:
            print(video.info.__dict__)
            video.info = VideoInfo()
    dump_videos(videos)
    sleep(2)


def check_rented():
    videos = load_videos()
    for video in videos:
        if video.rented:
            print(video.title)
    readline()


def print_poldark():
    videos = load_videos()

    count = 0
    for idx, video in enumerate(videos):
        if hasattr(video, "info") and video.info.imdb_url == videos[0].info.imdb_url:
            print(video.__dict__)

    print(count)
    readline()


def fix_images():
    videos = load_videos()
    p = "images"
    images = [f for f in os.listdir(p) if isfile(join(p, f))]
    recrawl = []

    for idx, video in enumerate(videos):
        if hasattr(video, "info") and video.info.image is not None:
            img_str = video.query.title.replace("\\", "").replace("/", "")
            image = next((image for image in images if img_str == image[6:-4]), None)
            if image is not None:
                video.info.image = "images/{}".format(image)
            else:
                vid_idx, vid = next(
                    (vid_idx, vid)
                    for vid_idx, vid in enumerate(videos)
                    if hasattr(vid, "info") and vid.info.imdb_url == video.info.imdb_url
                )
                if vid_idx != idx:
                    video.info.image = vid.info.image
                else:
                    recrawl.append(idx)

        if idx % 100 == 0:
            print(idx)

    print(recrawl)
    readline()
    readline()

    dump_videos(videos)


def get_readall():
    videos = load_videos()
    print(
        (
            next(
                (idx, video)
                for idx, video in enumerate(videos)
                if hasattr(video, "info")
                and video.info.description is not None
                and "... Read all" in video.info.description
            )
        )[1]
    )
    sleep(2)


def find_useless_images():
    videos = load_videos()
    files = [
        join("images", file)
        for file in os.listdir("images")
        if isfile(join("images", file)) and not file.endswith(".txt")
    ]

    useless = []
    for idx, image in enumerate(files):
        if not any(
            video
            for video in videos
            if hasattr(video, "info") and video.info.image == image
        ):
            useless.append(image)
        if idx % 100 == 0:
            print("{:.2f}%".format(idx / len(files) * 100))

    print(useless)
    answer = (
        True
        if request_input(
            "Are you sure you would like to delete these images (Y/N)?", "Y|N", "N"
        )
        == "Y"
        else False
    )
    if answer:
        os.makedirs("garbage/images", exist_ok=True)
        for image in useless:
            os.rename(image, "garbage/" + image)


def merge_matching_imdb_info():
    videos = load_videos()
    queue = list(enumerate(videos))
    changed = []
    while len(queue) > 0:
        idx: int
        video: Video
        idx, video = queue.pop(0)

        if idx % 100 == 0:
            print(idx)

        if video.has_info() and video.info.imdb_url is not None:
            matches = [
                matching_video
                for matching_video in queue
                if matching_video[1].has_info()
                and matching_video[1].info.imdb_url == video.info.imdb_url
            ]
            for idy, match in matches:
                videos[idy].info = video.info
                changed.append(idy)
                queue = [q for q in queue if q[0] != idy]
            queue = [q for q in queue if q[0] != idx]

    dump_videos(videos)


def add_sku_attr():
    videos = load_videos()
    for video in videos:
        video.info.sku = None

    sku = 10011203
    for video in videos:
        if video.has_info() and (
            hasattr(video.info, "sku") == False or video.info.sku is None
        ):
            sku += 1
            video.info.sku = sku
        elif not video.has_info():
            sku += 1
            video.info = VideoInfo()
            video.info.sku = sku

    dump_videos(videos)


def assign_skus():
    videos = load_videos()

    skus = [(video.info.sku, video.query.title) for video in videos if video.has_info()]
    sku_iter = iter(
        "{:08d}".format(sku)
        for sku in itertools.count(start=0)
        if not "{:08d}".format(sku) in [sku[0] for sku in skus]
    )
    count = 0
    for video in videos:
        if video.has_info() and video.info.is_populated() and video.info.sku is None:
            existing_sku = next(
                (sku[0] for sku in skus if sku[1] == video.query.title), None
            )
            if existing_sku:
                video.info.sku = existing_sku
            else:
                video.info.sku = sku_iter.__next__()
                print(video.info.sku)


def print_video_len():
    videos = load_videos()
    print(len(videos))
    print(len([video for video in videos if video.has_info()]))
    print(
        len(
            [
                video
                for video in videos
                if video.has_info()
                and video.info.is_populated()
                and video.info.sku is None
            ]
        )
    )


def showthething():
    vid = load_videos()
    print(vid[20].__dict__)


def getmissingvids():
    videos = load_videos()
    print(
        sum(
            1
            for v in videos
            if v.has_info()
            and hasattr(v, "info")
            and (not hasattr(v.info, "imdb_title") or v.info.imdb_title is None)
        )
    )


def findrecrawl():
    videos = load_videos()
    need = []
    for i, video in enumerate(videos):
        if not video.info.imdb_url:
            continue
        if not re.match(
            r"^(https:\/\/www\.imdb\.com\/title\/.+\/)$", video.info.imdb_url
        ):
            need.append(i)
            video.info.imdb_url = re.match(
                r"(https:\/\/www\.imdb\.com\/title\/.+\/)", video.info.imdb_url
            ).group(0)
    print(need)
    print(len(need))


def jpegify():
    videos = load_videos()
    for video in videos:
        if video.info.image:
            video.info.image = video.info.image[:-3] + "jpg"
    dump_videos(videos)
