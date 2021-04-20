from queue import Queue
from filepopulation import File
from typing import Union
from collections import OrderedDict


class CacheFactory:
    @staticmethod
    def new(sim_config):
        cache_type = sim_config.get("cache_type")
        capacity = sim_config.getfloat("cache_size")
        if cache_type == "LRU":
            return LRUCache(capacity)
        elif cache_type == "FIFO":
            return FIFOCache(capacity)
        elif cache_type == "LF":
            return LargestFirstCache(capacity)
        else:
            raise "Invalid cache type! Please select from [LRU, FIFO, LF]"


class LRUCache:
    """
    Oldest First / Least Popular
    """

    capacity: float
    cache: OrderedDict

    def __init__(self, capacity: float):
        self.capacity = capacity
        self.cache = OrderedDict()

    def size(self):
        return sum(map(lambda x: x.size, self.cache.values()))

    def get(self, file: File) -> Union[File, None]:
        if file.id in self.cache:
            self.cache.move_to_end(file.id)
            return self.cache[file.id]
        else:
            return None

    def add(self, file: File):
        self.cache[file.id] = file
        self.cache.move_to_end(file.id)
        size = self.size()
        while size >= self.capacity:
            (_, item) = self.cache.popitem(last=False)
            size -= item.size


class LargestFirstCache:
    capacity: float
    cache: dict

    def __init__(self, capacity: float):
        self.capacity = capacity
        self.cache = {}

    def size(self):
        return sum(map(lambda x: x.size, self.cache.values()))

    def get(self, file: File) -> Union[File, None]:
        if file.id in self.cache:
            return self.cache[file.id]
        else:
            return None

    def add(self, file: File):
        size = self.size()
        while size + file.size >= self.capacity:
            if not self.cache:
                return
            largest = max(self.cache, key=(lambda x: self.cache[x].size))
            size -= self.cache[largest].size
            del self.cache[largest]
        self.cache[file.id] = file


class FIFOCache:
    """
    FIFO Cache
    """

    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.queue = Queue()

    def get(self, file: File) -> File:
        return self.cache.get(file.id, None)

    def size(self):
        return sum(map(lambda x: x.size, self.cache.values()))

    def add(self, file: File):
        size = self.size()
        while size + file.size >= self.capacity:
            if not self.queue:
                return
            k = self.queue.get()
            if k in self.cache:
                size -= self.cache[k].size
                del self.cache[k]
        self.cache[file.id] = file
        self.queue.put(file.id)
