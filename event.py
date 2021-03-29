from config import Config, rng
import heapq
from filepopulation import FileStore, File
from dataclasses import dataclass
from cache import Cache
from typing import List


@dataclass
class Event:
    time: float

    def __lt__(self, other):
        return self.time < other.time

    def __le__(self, other):
        return self.time <= other.time


@dataclass
class NewRequestEvent(Event):
    file: File

    def process(self, queue, cache: Cache, current_time):
        # File request has arrived. We check server cache here
        # and send the appropriate event. (TODO)
        if cache.get(self.file.id):
            network_bandwidth = Config.SIM_CONFIG.getfloat("network_bandwidth")
            heapq.heappush(
                queue,
                FileRecievedEvent(current_time + (self.file.size / network_bandwidth)),
            )
        else:
            round_trip = Config.SIM_CONFIG.getfloat("round_trip")
            heapq.heappush(queue, ArriveAtQueueEvent(current_time + round_trip))

        # User makes another file request according to Poisson(\lambda)
        request_rate = Config.SIM_CONFIG.getfloat("request_rate")
        poisson_sample = rng.exponential(1 / request_rate)
        heapq.heappush(
            queue,
            NewRequestEvent(current_time + poisson_sample, FileStore.sample()),
        )


@dataclass
class FileRecievedEvent(Event):
    def process(self, queue, cache, current_time):
        """
        This event represents that a file has been received by the user.
          When processing such an event, the following need tobe done
          .-calculate the response time associated with that file and record the
            response time (a data sample has been collected).
        """
        raise NotImplementedError()


FIFO_QUEUE: List[File] = []


@dataclass
class ArriveAtQueueEvent(Event):
    def process(self, queue, cache, current_time):
        raise NotImplementedError()


@dataclass
class DepartQueueEvent(Event):
    def process(self, queue, cache, current_time):
        raise NotImplementedError()