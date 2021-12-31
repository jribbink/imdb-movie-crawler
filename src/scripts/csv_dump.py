import os
import re
import sys
from time import sleep
from util.pandas_helper import videos_to_data_frame
from util.util import cls, load_videos, request_input, request_range
from config import config


def csv_dump():
    videos = load_videos(
        request_input("Please enter the name of the dump file (default dump.file): ", default="dump.file")
    )
    print("{} videos loaded (0-{})\n".format(len(videos), len(videos) - 1))

    indices = request_range("Please enter the range of videos you would like to export (i.e. 0-2) (leave blank for all videos): ", default=range(0, len(videos) - 1))

    csv_name = request_input("What would you like to name your CSV (default out.csv)? ", default="out.csv")
    output_file = os.path.join(config["OUTPUT"]["output_location"], csv_name)

    df = videos_to_data_frame(videos)
    df.iloc[indices.start:indices.stop].to_csv(output_file)
    print("Success! Videos outputted to {}".format(output_file))
    sleep(2)