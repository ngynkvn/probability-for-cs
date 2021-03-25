import itertools
from operator import itemgetter
import logging
import random

logger = logging.getLogger("Sim")


class FileStore:
    def __init__(self, files):
        FileStore.files = files
        FileStore.cumulative_weights = list(
            itertools.accumulate(map(itemgetter(2), FileStore.files))
        )
        FileStore.verify()

    @staticmethod
    def verify():
        """
        Check that probabilities add up close to one, and mean of file size is approximately 1.
        """
        p = sum(map(itemgetter(2), FileStore.files))
        mean_size = sum(map(itemgetter(1), FileStore.files)) / len(FileStore.files)

        logger.debug(f"Sum probabilties: {p}")
        logger.debug(f"Mean file size: {mean_size}")

    @staticmethod
    def sample():
        """
        Sample as determined by probability weights.
        """
        random.choices(FileStore.files, cum_weights=FileStore.cumulative_weights)
