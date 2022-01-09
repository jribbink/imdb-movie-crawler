from difflib import SequenceMatcher
import json
import os
import pickle
import re
from shutil import copyfile
import sys
from config import config

from video import Video, VideoInfo

'''
Load videos from data file
'''
def load_videos(filename = "dump.file") -> 'list[Video]':
    videos = None
    output_file = os.path.join(config["OUTPUT"]["output_location"], filename)
    if(os.path.isfile(output_file)):
        with open(output_file, "rb") as f:
            videos = pickle.load(f)

    if videos is not None:
        return videos

    videos_file = open("config/videos.json")
    videos = []
    for video in json.load(videos_file):
        videos.append(Video(**video))
    return videos

'''
Save videos to data file
'''
def dump_videos(videos: 'list[Video]', filename = "dump.file"):
    location = os.path.join(config["OUTPUT"]["output_location"], filename)
    backup = os.path.dirname(location) + "." + os.path.basename(location) + ".bck"
    bck_idx = 1

    while(os.path.isfile(backup)):
        backup = os.path.dirname(location) + "." + os.path.basename(location) + ".bck{}".format(bck_idx)
        bck_idx += 1

    ## Backup file
    if(os.path.isfile(location)):
        copyfile(location, backup)
    
    ## Make output dir if not exist
    os.makedirs(os.path.dirname(location), exist_ok=True)
    ## Write to ouput file
    with open(location, "wb") as f:
        pickle.dump(videos, f, protocol = pickle.HIGHEST_PROTOCOL)

    ## Remove backup
    if(os.path.isfile(location)):
        os.remove(backup)

'''
Check string similarity rating
'''
def string_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

'''
Clear console
'''
def cls():
    os.system('cls' if os.name=='nt' else 'clear')

'''
Convert legacy video infos where video.info is dictionary to new object version
'''
def video_info_dictionary_to_object(videos: 'list[Video]'):
    upgrade_count = 0
    for video in videos:
        if hasattr(video, "info") and type(video.info) is list:
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
            upgrade_count += 1

    return upgrade_count
