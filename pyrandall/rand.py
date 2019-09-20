import random
import time


class RandFunctions:

    date_format = "%Y-%m-%d %H:%M"

    def __init__(self, seed=None, k=30):
        random.seed(seed)
        self.size = k

    def rand(self):
        return random.getrandbits(self.size)

    def time(self):
        start = time.mktime(time.strptime("1916-04-30 00:00", self.date_format))
        ptime = start + self.rand() - start
        return time.localtime(ptime)

    def format_date(self, t):
        return time.strftime(self.date_format, t)

    def format_epoch(self, t):
        return time.strftime("%s", t)
