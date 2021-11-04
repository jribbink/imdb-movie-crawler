from crawler_threadpool import CrawlerThreadpool
from google_api import search_custom_search
import json
from video import Video, VideoNotFoundException
from crawler import VideoCrawler
import pickle
import os
import sys

def load_videos() -> list[Video]:
    videos = None
    if(os.path.isfile("dump.file")):
        with open("dump.file", "rb") as f:
            videos = pickle.load(f)

    if videos is not None:
        return videos

    videos_file = open("config/videos.json")
    videos = []
    for video in json.load(videos_file):
        videos.append(Video(**video))
    return videos

videos = load_videos()

idx = int(sys.argv[1])

threadpool = CrawlerThreadpool(
    videos=videos,
    num_threads=6,
    start_index=idx,
    crawler_options={"headless": True, "show_images": False}
)
threadpool.run()

print("\n-------------------------")
print("{} completed videos".format(len(threadpool.completed_videos)))
print("{} missing videos".format(len(threadpool.missing_videos)))
print("-------------------------")

os.execv(sys.executable, [sys.executable, sys.argv[0], str(idx + 200)])