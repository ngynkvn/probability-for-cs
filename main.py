from scipy.stats import pareto
import numpy as np
import heapq
import matplotlib.pyplot as plt
import random
import argparse
from collections import defaultdict
import configparser
from cache import Cache
from event import RequestArrivedEvent
from filepopulation import FileStore
from config import Config, rng

import logging

logger = logging.getLogger("Sim")
logging.basicConfig()

FILES = None
CURRENT_TIME = 0
EVENT_QUEUE = []
CACHE = None


def main_setup(sim_config):
    global FILES, CACHE
    # File i has a size Si,
    # which is a sample drawn from a Pareto distribution (heavy tail),
    # F_S, with mean μ (e.g., μ= 1 MB).
    a = sim_config.getfloat("pareto_alpha")
    num_files = sim_config.getint("num_files")

    # Sample from pareto distribution for the file_sizes, mean should be ~1
    file_sizes = rng.pareto(a, num_files)

    # Sample from pareto distribution for the file probabilities,
    # We then calculate the file probability as probabilitie[i]/sum(probabilities).
    probabilities = rng.pareto(a, num_files)
    total_p = sum(probabilities)

    # File store class as global variable
    FILES = FileStore(
        [
            (i, size, p / total_p)
            for (i, size, p) in zip(range(num_files), file_sizes, probabilities)
        ]
    )

    # Cache class as global
    CACHE = Cache(sim_config)

    # Show plot of pareto samples for file sizes.
    # https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.pareto.html#numpy.random.Generator.pareto
    if Config.DEBUG_CONFIG.getboolean("show_plot"):
        print("file size mean:", file_sizes.mean())
        count, bins, _ = plt.hist(file_sizes, 100, density=True)
        fit = a / bins ** (a + 1)
        plt.plot(bins, max(count) * fit / max(fit), linewidth=2, color="r")
        plt.show()

    print(*sim_config.items())


def main(sim_config, seed):
    global EVENT_QUEUE, CURRENT_TIME
    print("Hi!", seed)
    total_requests = sim_config.getint("total_requests")
    num_finished = 0
    main_setup(sim_config)
    # main loop
    heapq.heappush(EVENT_QUEUE, RequestArrivedEvent(CURRENT_TIME, FileStore.sample()))

    while num_finished < total_requests:
        event = heapq.heappop(EVENT_QUEUE)
        CURRENT_TIME = event.time
        event.process(EVENT_QUEUE, CACHE, CURRENT_TIME)
        num_finished += 1


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
    Config(config)
    if "Debug" in config:
        if Config.DEBUG_CONFIG.getboolean("logging"):
            logger.root.setLevel(logging.DEBUG)

    main(config["Simulation"], args.seed)
