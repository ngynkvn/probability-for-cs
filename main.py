from scipy.stats import pareto
import numpy as np
import matplotlib.pyplot as plt
import configparser
import argparse
from collections import defaultdict
from operator import itemgetter

import logging

logging.basicConfig()

FILES = None
DEBUG_CONFIG = configparser.ConfigParser()


class FileStore:
    def __init__(self, files):
        self.files = files
        self.verify()

    def verify(self):
        """
        Check that probabilities add up close to one, and mean of file size is approximately 1.
        """
        p = sum(map(itemgetter(2), self.files))
        mean_size = sum(map(itemgetter(1), self.files)) / len(self.files)

        logging.debug(f"Sum probabilties: {p}")
        logging.debug(f"Mean file size: {mean_size}")


def main_setup(sim_config):
    global FILES
    # File i has a size Si,
    # which is a sample drawn from a Pareto distribution (heavy tail),
    # F_S, with mean μ (e.g., μ= 1 MB).
    a = sim_config.getfloat("pareto_alpha")
    num_files = sim_config.getint("num_files")

    file_sizes = np.random.default_rng().pareto(a, num_files)
    probabilities = np.random.default_rng().pareto(a, num_files)
    total_p = sum(probabilities)

    FILES = FileStore(
        [
            (i, size, p / total_p)
            for (i, size, p) in zip(range(num_files), file_sizes, probabilities)
        ]
    )

    if DEBUG_CONFIG.getboolean("show_plot"):
        print("file size mean:", file_sizes.mean())
        count, bins, _ = plt.hist(file_sizes, 100, density=True)
        fit = a / bins ** (a + 1)
        plt.plot(bins, max(count) * fit / max(fit), linewidth=2, color="r")
        plt.show()

    print(*sim_config.items())


def main(sim_config, seed):
    print("Hi!", seed)
    total_requests = sim_config.getint("total_requests")
    num_finished = 0
    main_setup(sim_config)
    # main loop
    while num_finished < total_requests:
        # event = get_event()
        # packet = get_packet()
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
    if "Simulation" not in config:
        raise ValueError('Missing "Simulation" header from config file.')
    if "Debug" in config:
        DEBUG_CONFIG = config["Debug"]
        if DEBUG_CONFIG.getboolean("logging"):
            logging.root.setLevel(logging.DEBUG)

    main(config["Simulation"], args.seed)