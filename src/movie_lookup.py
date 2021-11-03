from crawler_threadpool import CrawlerThreadpool
from google_api import search_custom_search
import json
from video import Video, VideoNotFoundException
from crawler import VideoCrawler
import pickle
import os

def load_videos() -> list[Video]:
    videos = None
    if(os.path.isfile("serial")):
        with open("serial", "rb") as f:
            videos = pickle.load(f)

    if videos is not None:
        return videos

    videos_file = open("config/videos.json")
    videos = []
    for video in json.load(videos_file):
        videos.append(Video(**video))
    return videos

videos = load_videos()

threadpool = CrawlerThreadpool(videos, 6, {"headless": False, "show_images": False})
threadpool.run()

print("\n-------------------------")
print("{} completed videos".format(len(threadpool.completed_videos)))
print("{} missing videos".format(len(threadpool.missing_videos)))
print("-------------------------")