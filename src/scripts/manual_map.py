

from util.io import request_input
from util.util import dump_videos, load_videos
from video import VideoInfo
from filelock import Timeout, FileLock


def manual_map():
    output_file = request_input("Please enter the name of the input file (default dump.file): ", default="dump.file")

    videos = []
    queue = []
    def update_queue():
        nonlocal queue, videos, output_file
        videos = load_videos(output_file)
        queue = [video for video in enumerate(videos) if not hasattr(video[1], "info")]
    update_queue()

    lock = FileLock("{}.lock".format(output_file))
    while True:
        video = None
        idx = None

        with lock:
            update_queue()
            if len(queue) == 0:
                print("Finished mapping movies!")
                break
            else:
                print("{} movies remain!".format(len(queue)))
            idx, video = queue.pop(0)
            video.info = VideoInfo()
            videos[idx] = video
            dump_videos(videos)

        imdb_url = request_input("Please provide the IMDb URL for \"{}\" (write \"None\" if doesn't exist): ".format(video.title), r"(https?://(www.)?imdb.com/title/[a-z0-9]*/)|None")
        imdb_url = imdb_url if imdb_url.lower() != "none" else None
        video.info = VideoInfo(imdb_url=imdb_url)

        with lock:
            update_queue()
            videos[idx] = video
            dump_videos(videos)
