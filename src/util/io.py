import re
import sys

commands: "list[str]" = []

"""
def enqueue_commands
"""


def enqueue_commands(*command_queue):
    global commands
    commands += command_queue


"""
Read a line from the user
"""


def readline():
    global commands
    if len(commands) > 0:
        command = commands.pop(0).strip()
        print(command, flush=True)
        return command

    return sys.stdin.readline().strip()


"""
Request input from user and validate it
"""


def request_input(message="", pattern=".*", default=None):
    print(message, end="", flush=True)
    input = readline()

    if default is not None and input == "":
        return default

    if not re.match(pattern, input):
        print("Bad Input", flush=True)
        return request_input(message=message, pattern=pattern)
    else:
        return input


"""
Read integer from user and validate it
"""


def request_int(message="", default=None):
    return int(request_input(message=message, pattern="\d+", default=default))


"""
Request range of numbers or single number from user
"""


def request_range(message="", default=None):
    input = request_input(message=message, pattern=r"\d+(-\d+)?$", default=default)
    if type(input) is range:
        return input

    split_input = input.split("-")
    if len(split_input) > 1:
        return range(int(split_input[0]), int(split_input[1]) + 1)
    else:
        return range(int(split_input[0]), int(split_input[0]) + 1)
