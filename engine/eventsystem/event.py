import time


class Event:
    def __init__(self, source):
        self.timestamp = time.time()
        self.source = source
