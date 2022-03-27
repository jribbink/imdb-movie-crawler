from person_crawler import PersonCrawlerThreadpool
import sys
import os

from util.util import load_people
from util.io import request_input, request_int, request_range

from time import sleep


def person_lookup():
    output_file = request_input(
        "Please enter the name of the input file (default dumppeople.file): ",
        default="dumppeople.file",
    )
    videos = load_people(output_file)
    print("{} people loaded (0-{})\n".format(len(videos), len(videos) - 1))

    idx_range = request_range(
        "Which videos would you like to fetch (i.e. 0-2) (leave blank for all people)? ",
        range(0, len(videos)),
    )
    remaining_range = None

    if idx_range.stop - idx_range.start > 100:
        remaining_range = range(idx_range.start + 100, idx_range.stop)
        idx_range = range(idx_range.start, idx_range.start + 100)

    num_threads = int(request_int("How many threads (default 4)? ", default=4))

    threadpool = PersonCrawlerThreadpool(
        people=videos,
        num_threads=num_threads,
        indices=idx_range,
        crawler_options={"headless": False, "show_images": True},
        output_file=output_file,
    )
    threadpool.run()

    print("\n-------------------------")
    print("{} completed people".format(len(threadpool.completed_people)))
    print("-------------------------")

    os.execv(
        sys.executable,
        [
            sys.executable,
            sys.argv[0],
            "2",
            output_file,
            "{}-{}".format(remaining_range.start, remaining_range.stop),
            str(num_threads),
        ],
    )


"""
    startix = min(idx + 200, len(videos) - 1)
    if(idx == len(videos) - 1):
        startix = 0
    os.execv(sys.executable, [sys.executable, sys.argv[0], str(idx + 200)])
"""
