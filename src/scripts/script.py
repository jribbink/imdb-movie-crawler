from typing import Callable


class Script:
    def __init__(self, name: str, function: Callable):
        self.name = name
        self.function = function

    def run(self):
        self.function()