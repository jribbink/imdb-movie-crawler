from crawler_threadpool import CrawlerThreadpool
import sys
import os

from util.util import load_videos
from util.io import request_input, request_int, request_range

from time import sleep


def movie_lookup():
    output_file = request_input("Please enter the name of the input file (default dump.file): ", default="dump.file")
    videos = load_videos(
        output_file
    )
    print("{} videos loaded (0-{})\n".format(len(videos), len(videos) - 1))

    idx_range = request_range("Which videos would you like to fetch (i.e. 0-2) (leave blank for all videos)? ", range(0, len(videos)))
    remaining_range = None

    if(idx_range.stop - idx_range.start > 100):
        remaining_range = range(idx_range.start + 100, idx_range.stop)
        idx_range = range(idx_range.start, idx_range.start + 100)

    num_threads = int(request_int("How many threads (default 4)? ", default=4))

    threadpool = CrawlerThreadpool(
        videos=videos,
        num_threads=num_threads,
        indices=idx_range,
        crawler_options={"headless": False, "show_images": True},
        output_file=output_file,
    )
    threadpool.run()

    print("\n-------------------------")
    print("{} completed videos".format(len(threadpool.completed_videos)))
    print("{} missing videos".format(len(threadpool.missing_videos)))
    print("-------------------------")

    os.execv(sys.executable, [sys.executable, sys.argv[0], "1", output_file, "{}-{}".format(remaining_range.start, remaining_range.stop), str(num_threads)])

    exit()

'''
    startix = min(idx + 200, len(videos) - 1)
    if(idx == len(videos) - 1):
        startix = 0
    os.execv(sys.executable, [sys.executable, sys.argv[0], str(idx + 200)])
'''

