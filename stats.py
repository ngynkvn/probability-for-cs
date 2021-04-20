from typing import *


class Stats:
    response_times: List[float] = []
    cache_hits: List[bool] = []
    total_cache_hits: int = 0