from config import Config, rng
import heapq
from filepopulation import FileStore


class RequestArrivedEvent:
    def __init__(self, time, fil):
        self.time = time
        self.file = fil

    def process(self, queue, cache, current_time):
        # File request has arrived. We check server cache here
        # and send the appropriate event. (TODO)

        # User makes another file request according to Poisson(\lambda)
        request_rate = Config.SIM_CONFIG.getfloat("request_rate")
        poisson_sample = rng.exponential(1 / request_rate)
        heapq.heappush(
            queue,
            RequestArrivedEvent(current_time + poisson_sample, FileStore.sample()),
        )
