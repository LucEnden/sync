import threading
import random
import time


class Task():
    def __init__(self, BT: float):
        self.BT = BT

    def body_of_work(self) -> None:
        """
        Emulates some body of work using the `time.sleep` function
        """
        time.sleep(self.BT)


class BurstTimeEstimator():
    def __init__(self):
        pass

    def __get_random_bt__() -> float:
        """
        ## Returns:
            A random value between `10` and `500` (inclusive) divided by `1000`
        """
        _min = 10
        _max = 500
        _div = 1000
        
        return random.randint(_min, _max) / _div

    def esstimate_bursttime(self, t: Task):
        return self.__get_random_bt__()


class TaskManager():
    def __init__(self):
        self.__queue__: list[Task] = []

    def createTask(BT: float) -> Task:
        return Task(BT)

    def runNextTask() -> None:
        pass

    def returnToQueue(task: Task) -> None:
        pass