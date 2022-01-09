from genericpath import isfile
from posixpath import join
import os
from util.util import dump_videos, load_videos
from util.io import readline, request_input
from video import VideoInfo
from time import sleep

def run_misc_script():
    script = request_input("What script would you like to run?")
    exec(script + "()")

def kill_movie():
    videos = load_videos()
    for video in videos:
        if("AWAKENING IN THE NOW" in video.title):
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
        if hasattr(video, "info") and video.info.image == "images/14775_GROSSE POINT BLANK.png":
            count += 1
            print(idx, " ", video.info.__dict__)

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
            if(image is not None):
                video.info.image = "images/{}".format(image)
            else:
                vid_idx, vid = next((vid_idx, vid) for vid_idx, vid in enumerate(videos) if hasattr(vid, "info") and vid.info.imdb_url == video.info.imdb_url)
                if(vid_idx != idx):
                    video.info.image = vid.info.image
                else:
                    recrawl.append(idx)

        if(idx % 100 == 0):
            print(idx)

    print(recrawl)
    readline()
    readline()

    dump_videos(videos)

def get_readall():
    videos = load_videos()
    print((next((idx, video) for idx, video in enumerate(videos) if hasattr(video, "info") and video.info.description is not None and "... Read all" in video.info.description))[1])
    sleep(2)

def find_useless_images():
    videos = load_videos()
    files = [join("images", file) for file in os.listdir("images") if isfile(join("images", file))]

    useless = []
    for idx, image in enumerate(files):
        if not any(video for video in videos if hasattr(video, "info") and video.info.image == image):
            useless.append(image)
        if(idx % 100 == 0):
            print("{:.2f}%".format(idx / len(files) * 100))

    print(useless)
    answer = True if request_input("Are you sure you would like to delete these images (Y/N)?", "Y|N", "N") == "Y" else False
    if(answer):
        os.makedirs("garbage/images", exist_ok=True)
        for image in useless: os.rename(image, "garbage/" + image)