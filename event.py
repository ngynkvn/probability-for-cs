from config import Config
import heapq
from filepopulation import FileStore, File
from dataclasses import dataclass
from cache import Cache
from typing import List, Any
from queue import Queue
from stats import Stats


@dataclass
class Event:
    time: float
    file: File
    prev: Any = None

    def __lt__(self, other):
        return self.time < other.time

    def __le__(self, other):
        return self.time <= other.time


@dataclass
class NewRequestEvent(Event):
    def process(self, queue, cache: Cache, current_time):
        # File request has arrived. We check server cache here
        # and send the appropriate event. (TODO)
        if cache.get(self.file):
            network_bandwidth = Config.SIM_CONFIG.getfloat("network_bandwidth")
            heapq.heappush(
                queue,
                FileRecievedEvent(
                    current_time + (self.file.size / network_bandwidth), self.file, self
                ),
            )
        else:
            round_trip = Config.SIM_CONFIG.getfloat("round_trip")
            heapq.heappush(
                queue,
                ArriveAtQueueEvent(current_time + round_trip, self.file, self),
            )

        # User makes another file request according to Poisson(\lambda)
        request_rate = Config.SIM_CONFIG.getfloat("request_rate")
        poisson_sample = Config.rng.exponential(1 / request_rate)
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

        # For now, print tracebacks.
        end = self.time
        p = self.prev
        while p.prev:
            p = p.prev
        start = p.time
        Stats.response_times.append(end - start)



FIFO_QUEUE: Queue = Queue()


@dataclass
class ArriveAtQueueEvent(Event):
    def process(self, queue, cache, current_time):
        """
        if the queue is not empty,
        add the file (i.e., the info about the file)
        at the end of the FIFO queue.
        """
        if not FIFO_QUEUE.empty():
            FIFO_QUEUE.put((self.file, self))
        else:
            """if the queue is empty,
            generate a new depart-queue-event,
            with theevent-time = current-time +Si/Ra
            """
            r_a = Config.SIM_CONFIG.getfloat("access_link_bandwidth")
            heapq.heappush(
                queue,
                DepartQueueEvent(
                    current_time + (self.file.size / r_a), self.file, self
                ),
            )



@dataclass
class DepartQueueEvent(Event):
    def process(self, queue, cache, current_time):
        """
        store the new file in the cache if there is enough space.
        If the cacheis full, remove enough files based on your cache replacement policy
        and store the new file
        .- generate a new file-received-event, with the event-time = current-time +Si/Rc
        .- If the FIFO queue is not empty, generate a new depart-queue-event
            for the head-of-queue file, sayj, with the event-time = current-time+Sj/Ra
        """
        cache.add(self.file)
        network_bandwidth = Config.SIM_CONFIG.getfloat("network_bandwidth")
        heapq.heappush(
            queue,
            FileRecievedEvent(
                current_time + self.file.size / network_bandwidth, self.file, self
            ),
        )
        if not FIFO_QUEUE.empty():
            (head, ev) = FIFO_QUEUE.get()
            r_a = Config.SIM_CONFIG.getfloat("access_link_bandwidth")
            heapq.heappush(
                queue,
                DepartQueueEvent(current_time + (head.size / r_a), head, ev),
            )
