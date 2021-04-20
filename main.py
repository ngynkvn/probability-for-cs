from scipy.stats import pareto
import pandas as pd
import time
import numpy as np
import heapq
import matplotlib.pyplot as plt
import random
import argparse
from collections import defaultdict
import configparser
from cache import CacheFactory
from event import Event, NewRequestEvent, FileRecievedEvent
from filepopulation import FileStore
from config import Config
from typing import List, Union
from stats import Stats
import progressbar

import logging

logger = logging.getLogger("Sim")
logging.basicConfig()

FILES: Union[FileStore, None] = None
CURRENT_TIME = 0
EVENT_QUEUE: List[Event] = []
CACHE = None


def main_setup(sim_config):
    global FILES, CACHE
    # File i has a size Si,
    # which is a sample drawn from a Pareto distribution (heavy tail),
    # F_S, with mean μ (e.g., μ= 1 MB).
    a = sim_config.getfloat("pareto_alpha")
    num_files = sim_config.getint("num_files")

    # Sample from pareto distribution for the file_sizes, mean should be ~1
    file_sizes = Config.rng.pareto(a, num_files)

    # Sample from pareto distribution for the file probabilities,
    # We then calculate the file probability as probabilitie[i]/sum(probabilities).
    probabilities = Config.rng.pareto(a, num_files)
    total_p = sum(probabilities)

    # File store class as global variable
    FILES = FileStore(
        [
            (i, size, p / total_p)
            for (i, size, p) in zip(range(num_files), file_sizes, probabilities)
        ]
    )

    # Cache class as global
    CACHE = CacheFactory.new(sim_config)

    print("Inputs:")
    print("[Simulation]")
    for key, value in Config.SIM_CONFIG.items():
        print(f"{key}\t=\t{value}")
    print("[Debug]")
    for key, value in Config.DEBUG_CONFIG.items():
        print(f"{key}\t=\t{value}")


def main(sim_config):
    global EVENT_QUEUE, CURRENT_TIME
    total_requests = sim_config.getint("total_requests")
    num_finished = 0
    main_setup(sim_config)
    # main loop
    heapq.heappush(EVENT_QUEUE, NewRequestEvent(CURRENT_TIME, FileStore.sample()))

    loop_start = time.time()
    event_count = 0
    chars = len(str(total_requests))

    while num_finished < total_requests:
        if not num_finished % 1000:
            print(
                f"Finished/Total:\t{num_finished: >{chars}}/{total_requests}\tCache Hits: {Stats.total_cache_hits}",
                end="\r",
            )
        event = heapq.heappop(EVENT_QUEUE)
        CURRENT_TIME = event.time
        event.process(EVENT_QUEUE, CACHE, CURRENT_TIME)
        event_count += 1
        if isinstance(event, FileRecievedEvent):
            num_finished += 1
    print(
        f"Simulation finished in {time.time() - loop_start} seconds, processing {num_finished} requests and {event_count} events"
    )
    cache_miss_rate = 1 - (Stats.total_cache_hits / total_requests)
    rr = Config.SIM_CONFIG.getfloat("request_rate")
    print("Current Time:", CURRENT_TIME)
    print("Cache Miss Rate: ", cache_miss_rate)
    print("Estimated Inbound Traffic Rate:", cache_miss_rate * rr, "requests / second")
    print("Response Time Metrics")
    print(pd.DataFrame(Stats.response_times).describe())
    if Config.DEBUG_CONFIG.getboolean("show_plot"):
        print("Showing response time plot")
        x = range(len(Stats.response_times))
        y = Stats.response_times
        c = list(map(lambda x: "blue" if x else "red", Stats.cache_hits))
        plt.scatter(x, y, 2, c)
        plt.show()
        h_data = pd.Series(y)
        h_data = h_data[h_data.between(h_data.quantile(0.05), h_data.quantile(0.95))]
        plt.hist(h_data, 50)
        plt.show()


if __name__ == "__main__":
    # Setup parsing for config file and seed number from command line.
    parser = argparse.ArgumentParser(description="Event Simulator")
    parser.add_argument(
        "input",
        metavar="input",
        type=str,
        help="Input file for simulation",
    )
    parser.add_argument(
        "seed", metavar="seed", type=int, help="Seed number for simulation"
    )
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read(args.input)

    random.seed(args.seed)
    Config(config, args.seed)

    if "Debug" in config:
        if Config.DEBUG_CONFIG.getboolean("logging"):
            logger.setLevel(logging.DEBUG)

    main(config["Simulation"])
