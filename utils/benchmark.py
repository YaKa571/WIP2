import time

import utils.logger as logger


class Benchmark:
    """
    Manages and calculates the runtime of a process or operation.

    This class is used to benchmark the execution time of processes or operations. It records
    the start time when instantiated and calculates the elapsed time when prompted. The purpose
    is to provide an easy and visual way to measure performance in a human-readable format.
    """

    def __init__(self, name):
        self.name = name
        self.start = time.perf_counter()
        self.end = None

    def print_time(self, add_empty_line: bool = False):
        """
        Prints the elapsed time for a process in seconds, formatted to two decimal places,
        with an associated name of the process. This method calculates the time elapsed
        since the process started and includes visual indication.
        """
        self.end = time.perf_counter()
        logger.log(f"🚀 {self.name} took {self.end - self.start:.2f} seconds.")
        if add_empty_line:
            logger.log("")
