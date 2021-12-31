from crawler_threadpool import CrawlerThreadpool
import sys

from util.util import cls, load_videos, request_input, request_range


def movie_lookup():
    output_file = request_input("Please enter the name of the input file (default dump.file): ", default="dump.file")
    videos = load_videos(
        output_file
    )
    print("{} videos loaded (0-{})\n".format(len(videos), len(videos) - 1))

    idx_range = request_range("Which videos would you like to fetch (i.e. 0-2) (leave blank for all videos)? ", range(0, len(videos)))

    threadpool = CrawlerThreadpool(
        videos=videos,
        num_threads=4,
        start_index=idx_range.start,
        end_index=idx_range.stop,
        crawler_options={"headless": True, "show_images": False},
        output_file=output_file,
    )
    threadpool.run()

    print("\n-------------------------")
    print("{} completed videos".format(len(threadpool.completed_videos)))
    print("{} missing videos".format(len(threadpool.missing_videos)))
    print("-------------------------")

'''
    startix = min(idx + 200, len(videos) - 1)
    if(idx == len(videos) - 1):
        startix = 0
    os.execv(sys.executable, [sys.executable, sys.argv[0], str(idx + 200)])
'''

