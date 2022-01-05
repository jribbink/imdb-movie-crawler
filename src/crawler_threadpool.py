import os
import pickle
from shutil import copyfile
import threading
from typing import List
from crawler import VideoCrawler
from util.util import dump_videos

from video import Video

class AtomicInteger():
    def __init__(self, value=0):
        self._value = int(value)
        self._lock = threading.Lock()
        
    def inc(self, d=1):
        with self._lock:
            self._value += int(d)
            return self._value

    def dec(self, d=1):
        return self.inc(-d)    

    @property
    def value(self):
        with self._lock:
            return self._value

    @value.setter
    def value(self, v):
        with self._lock:
            self._value = int(v)
            return self._value

class CrawlerThreadpool():
    def __init__(self, videos: List[Video], num_threads = 4, indices = None, crawler_options: dict = {}, output_file = "dump.file"):
        ## Chrome driver options
        self.crawler_options = crawler_options

        ## Indices of videos to explore
        self.queue = list(indices)

        ## Video lists
        self.videos = videos
        self.completed_videos = []
        self.missing_videos = []

        ## Threading parameters
        self.threads = []
        self.num_threads = num_threads
        self.file_save_lock = threading.Lock()
        self.queue_length_lock = threading.Lock()

        ## Output option
        self.output_file = output_file

    def run(self):
        for i in range(0, self.num_threads):
            thread = CrawlerThread(self, self.crawler_options, i)
            thread.start()
            self.threads.append(thread)

        for i in range(0, self.num_threads):
            self.threads[i].join()

class CrawlerThread(threading.Thread):
    def __init__(self, parent: CrawlerThreadpool, crawler_options: dict, index: int):
        self.crawler = VideoCrawler(**crawler_options, index=index)
        self.parent = parent
        threading.Thread.__init__(self)

    def get_existing_info(self, query_video):
        info = None
        for video in self.parent.videos:
            ## Check if videos have same base query and video has info
            if(video.query.title.strip() == query_video.query.title.strip()):
                if(hasattr(video, "info")):
                    info = video.info
                    break
        
        return info
    
    def run(self):  
        while True:
            i = None
            with self.parent.queue_length_lock:
                if len(self.parent.queue) > 0:
                    i = self.parent.queue.pop(0)
            if i is None: break

            if hasattr(self.parent.videos[i], "info"):
                continue

            try:
                video = self.parent.videos[i]

                ## Check if video has already been queried
                info = self.get_existing_info(video)
                if(info is None): ## otherwise query through crawler
                    info = self.crawler.get_video(video, index = i)
                video.info = info

                print(video.info.__dict__)

                self.parent.completed_videos.append(video)
                print(video.query.title)

                with self.parent.file_save_lock:
                    dump_videos(self.parent.videos, self.parent.output_file)
                #print("{}\n    Name:\t\t{}\n    Description:\t{}".format(videos[i].title, entity["result"]["name"], entity["result"]["description"]))
                #except VideoNotFoundException as ex:
            except Exception as ex:
                if("Message: no such element: Unable to locate element: {\"method\":\"name\",\"selector\":\"q\"}" in str(ex)):
                    print(self.crawler.proxy_manager.proxy)
                print(ex)
                print("Failed {} (index: {})".format(self.parent.videos[i].title, i))
                self.parent.missing_videos.append(self.parent.videos[i])

        self.crawler.driver.close()