from google_api import search_custom_search
import json
from video import Video, VideoNotFoundException
from crawler import VideoCrawler
import pickle

def load_videos() -> list[Video]:
    videos = None
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

completed_videos = []
missing_videos = []

crawler = VideoCrawler()

for i in range(0, 1000):
    if hasattr(videos[i], "info"):
        continue
    
    try:
        video = videos[i]
        info = crawler.get_video(video, index = i)
        video.info = info
        completed_videos.append(video)
        print(video.query.title)
        with open("serial", "wb") as f:
            pickle.dump(videos, f, protocol = pickle.HIGHEST_PROTOCOL)
        #print("{}\n    Name:\t\t{}\n    Description:\t{}".format(videos[i].title, entity["result"]["name"], entity["result"]["description"]))
    except VideoNotFoundException as ex:
        print("Failed {} (index: {})".format(videos[i].title, i))
        missing_videos.append(videos[i])

print("\n-------------------------")
print("{} completed videos".format(len(completed_videos)))
print("{} missing videos".format(len(missing_videos)))
print("-------------------------")