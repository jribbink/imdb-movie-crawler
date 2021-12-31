import os
import sys
from scripts.csv_dump import csv_dump
from scripts.file_server import file_server
from scripts.movie_lookup import movie_lookup
from scripts.script import Script
from scripts.upgrade_videos import upgrade_videos

from util.util import cls, request_input
from time import sleep


options: 'list[Script]' = [
    Script("Crawl for videos", movie_lookup),
    Script("Export videos to CSV", csv_dump),
    Script("Upgrade videos (convert legacy dictionary info to object)", upgrade_videos),
    Script("Run static http server", file_server)
]

def run_script():
    def print_banner():
        cls()
        print("----------------------------------")
        print("|    Leo's Videos Movie Tool     |")
        print("| Created by Jordan Ribbink 2021 |")
        print("----------------------------------\n")
    print_banner()

    print("Please select one of the following options")

    for idx, option in enumerate(options):
        print("{}. {}".format(idx, option.name))
    print()

    selection = int(request_input(pattern=r"\d+"))

    print_banner()
    options[selection].run()

    run_script()

run_script()