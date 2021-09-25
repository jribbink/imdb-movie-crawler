import json
from video import Video

def load_videos() -> list[Video]:
    videos_file = open("videos.json")
    videos = []
    for video in json.load(videos_file):
        videos.append(Video(**video))
    return videos

videos = load_videos()

for i in range(4000, 4500):
    try:
        entity = videos[i].get_knowledge_entity()
        #print("{}\n    Name:\t\t{}\n    Description:\t{}".format(videos[i].title, entity["result"]["name"], entity["result"]["description"]))
    except:
        print("Failed {} (index: {})".format(videos[i].title, i))