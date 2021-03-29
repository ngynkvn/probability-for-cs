from queue import Queue
from filepopulation import File


class Cache:
    """
    FIFO Cache
    """

    def __init__(self, sim_config):
        self.capacity = sim_config.getfloat("cache_size")
        self.cache = {}
        self.queue = Queue()

    def get(self, file: File) -> File:
        return self.cache.get(file.id, None)

    def size(self):
        return sum(map(lambda x: x.size, self.cache.values()))

    def add(self, file: File):
        while self.size() >= self.capacity:
            k = self.queue.get()
            del self.cache[k]
        self.cache[file.id] = file
        self.queue.put(file.id)

    def remove(self, key):
        del self.cache[key]
