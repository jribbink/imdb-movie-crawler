import re

def test_regex(list, search, regex):
    broken = [item for item in list if re.search(search, item) and not re.search(regex, item)]
    print("Broken: {}".format(len(broken)))
    for brok in broken:
        print("{}\n".format(brok))

def test_video():
    vid = next(video for video in videos if video["code"] == "9264D")
    print(vid)
    video = lookup_video(vid)
    print("    Name:\t\t{}\n    Description:\t{}".format(video["result"]["name"], video["result"]["description"]))
    quit()
    ### CURRENTLY BROKEN