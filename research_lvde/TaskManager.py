import threading
import random
import time


def atomic_bow():
    """
    An atomic `body of work`. Meaning this function will either come to full completion once ran, or not ran at all.
    """
    pass

def non_atomic_bow():
    """
    A non atomic `body of work`. Meaning this function may be paused once ran and be in a state of incompletness.
    """
    pass

class Process():
    def __init__(self, bow: function):
        self.__threads__: list = []
        self.state: str = "new"

    def bow(self):
        return self.__bow__()

class BurstTimeEstimator():
    def __init__(self):
        pass

    def get_random_bt(_min: int = 10, _max: int = 500, _div: int = 1000) -> float:
        """
        ## Returns:
            A random value between `_min` and `_max` (inclusive) divided by `_div`
        """
        return random.randint(_min, _max) / _div

    def estimate_bursttime(self, bt: float):
        return bt * (random.randint(1, 10) / 100)


class TaskManager():
    def __init__(self):
        self.__queue__: list[dict] = []

    def new_process() -> Process:
        """
        Adds a new process to `self.__queue__` according to SJF logic.
        """
        pass

    def run_next_process_in_line() -> None:
        """
        Calls `self.__queue__[0]['process'].run()`
        """
        pass

    def returnToQueue(task: function) -> None:
        pass