import itertools
from operator import itemgetter
from dataclasses import dataclass
from typing import List
import logging
import random

logger = logging.getLogger("Sim")


@dataclass
class File:
    id: int
    size: float
    p: float


class FileStore:
    files: List[File]
    cumulative_weights: List[float]

    def __init__(self, files):
        FileStore.files = list(map(lambda x: File(*x), files))
        FileStore.cumulative_weights = list(
            itertools.accumulate(map(lambda f: f.p, FileStore.files))
        )
        FileStore.verify()

    @staticmethod
    def verify():
        """
        Check that probabilities add up close to one, and mean of file size is approximately 1.
        """
        p = sum(map(lambda f: f.p, FileStore.files))
        mean_size = sum(map(lambda f: f.size, FileStore.files)) / len(FileStore.files)

        logger.debug(f"Sum probabilties: {p}")
        logger.debug(f"Mean file size: {mean_size}")

    @staticmethod
    def sample() -> File:
        """
        Sample as determined by probability weights.
        """
        return random.choices(
            FileStore.files, cum_weights=FileStore.cumulative_weights, k=1
        )[0]
