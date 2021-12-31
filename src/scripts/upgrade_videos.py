from time import sleep
from util.util import cls, dump_videos, load_videos, request_input, request_range, video_info_dictionary_to_object

def upgrade_videos():
    videos = load_videos(
        request_input("Please enter the name of the input file (default dump.file): ", default="dump.file")
    )
    upgrade_count = video_info_dictionary_to_object(videos)

    print("{} videos upgraded!".format(upgrade_count))

    dump_videos(videos, request_input("Please enter the name of the dump file (default dump.file): ", default="dump.file"))
    
    sleep(2)