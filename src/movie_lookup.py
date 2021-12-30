from crawler_threadpool import CrawlerThreadpool
from google_api import search_custom_search
import json
from pandas_helper import save_to_csv, videos_to_data_frame
from video import Video, VideoInfo, VideoNotFoundException
from crawler import VideoCrawler
import pickle
import os
import sys

def load_videos() -> 'list[Video]':
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
for video in videos:
    if hasattr(video, "info"):
        video.info = VideoInfo(**{
            "description": video.info["description"] if "description" in video.info else None,
            "imdb_title": video.info["imdb_title"] if "imdb_title" in video.info else None,
            "directors": video.info["directors"] if "directors" in video.info else None,
            "writers": video.info["writers"] if "writers" in video.info else None,
            "stars": video.info["stars"] if "stars" in video.info else None,
            "genres": video.info["genres"] if "genres" in video.info else None,
            "rating": video.info["rating"] if "rating" in video.info else None,
            "film_length": video.info["film_length"] if "film_length" in video.info else None,
            "parental_rating": video.info["parental_rating"] if "parental_rating" in video.info else None,
            "release_info": video.info["release_info"] if "release_info" in video.info else None,
            "image": video.info["image"] if "image" in video.info else None,
            "imdb_url": video.info["imdb_url"] if "imdb_url" in video.info else None,
        })

df = videos_to_data_frame(videos)
df[0:100].to_csv("trunc.csv")
quit()

idx = int(sys.argv[1])

threadpool = CrawlerThreadpool(
    videos=videos,
    num_threads=4,
    start_index=idx,
    crawler_options={"headless": True, "show_images": False}
)
threadpool.run()

print("\n-------------------------")
print("{} completed videos".format(len(threadpool.completed_videos)))
print("{} missing videos".format(len(threadpool.missing_videos)))
print("-------------------------")

startix = min(idx + 200, len(videos) - 1)
if(idx == len(videos) - 1):
    startix = 0
os.execv(sys.executable, [sys.executable, sys.argv[0], str(idx + 200)])