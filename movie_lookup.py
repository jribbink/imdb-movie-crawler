from google_api import search_custom_search
import json
from video import Video, VideoNotFoundException

def load_videos() -> list[Video]:
    videos_file = open("videos.json")
    videos = []
    for video in json.load(videos_file):
        videos.append(Video(**video))
    return videos

videos = load_videos()

completed_videos = []
missing_videos = []

for i in range(12395, 12396):
    try:
        video = videos[i]
        entity = video.get_knowledge_entity()
        video.entity = entity
        completed_videos.append(video)
        #print("{}\n    Name:\t\t{}\n    Description:\t{}".format(videos[i].title, entity["result"]["name"], entity["result"]["description"]))
    except VideoNotFoundException as ex:
        print("Failed {} (index: {})".format(videos[i].title, i))
        missing_videos.append(videos[i])

print("\n-------------------------")
print("{} completed videos".format(len(completed_videos)))
print("{} missing videos".format(len(missing_videos)))
print("-------------------------")