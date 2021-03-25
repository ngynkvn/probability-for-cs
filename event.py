from config import Config, rng
import heapq
from filepopulation import FileStore, File
from dataclasses import dataclass


@dataclass
class Event:
    time: float

    def __lt__(self, other):
        return self.time < other.time

    def __le__(self, other):
        return self.time <= other.time


@dataclass
class RequestArrivedEvent(Event):
    file: File

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


@dataclass
class ArriveAtQueueEvent(Event):
    def process(self, queue, cache, current_time):
        raise NotImplementedError()


@dataclass
class DepartQueueEvent(Event):
    def process(self, queue, cache, current_time):
        raise NotImplementedError()