def FIFO(cache):
    print("FIFO")
    pass


class Cache:
    def __init__(self, sim_config):
        self.capacity = sim_config.getfloat("cache_size")
        self.cache = {}
        self.replacement_policy = FIFO

    def get(self, key):
        if key in self.cache:
            return self.cache[key]
        else:
            return None

    def add(self, key, value):
        if len(self.cache) >= self.capacity:
            self.replacement_policy(self)
        self.cache[key] = value

    def remove(self, key):
        del self.cache[key]
