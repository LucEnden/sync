'''
This is a simple emulation of Shortest Job First (SJF) scheduling algorithm.
The design of this emulation can be found in `diagrams.drawio` file in the same directory.

To give some answers to the most interesting parts of the emulation:

> The `Process.__new_random_threads__` method generates a random number of threads with random burst times.
> Every one in a thousand times, a thread will have a burst time that is exponentially larger than the rest.
'''
import threading
import time
import random

_verbose = True         # Set to True to print information to stdout
_run_tests = True       # Set to True to run tests at the end of the file
_process_counter = 0    # Counter for the number of processes generated

# region Emulation classes

class NumberGenerator():
    """
    Generates numbers used during the emulation.
    """

    def __init__(self, seed: int = 43) -> None:
        if not isinstance(seed, int):
            seed = 43  # The answer to everything

        self.__seed__ = seed
        self.__process_counter__ = 0

    def random_bt(self, _min: int = 100, _max: int = 300, _div: int = 100) -> float:
        """
        Generates a random short burst time (`random.randint(_min, _max) / _div`)

        ## Returns
        - float: Random number between `_min` and `_max` divided by `_div`
        """
        random.seed(self.__seed__)
        return random.randint(_min, _max) / _div

    def new_process_id(self) -> int:
        """
        Generates a new process id.

        ## Returns
        - int: A new process id
        """
        global _process_counter

        _process_counter = _process_counter + 1
        return _process_counter


class ProcessState:
    """
    Enum for process states.
    """
    NEW = "new"
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    TERMINATED = "terminated"


class Process():
    """
    Holds information about process, usually held in the process control block.

    As stated in the book, "Operating System Concepts - 10th edition" by Silberschatz, Galvin, and Gagne (page 110):
    > In brief, the Process Control Block (PCB) simply serves as the repository for all the data needed to start,
    > or restart, a process, along with some accounting data.
    """

    def __init__(self) -> None:
        self.threads = list[threading.Thread]
        self.state: ProcessState = ProcessState.NEW
        self.id: int = NumberGenerator().new_process_id()
        self.bt_sum: int = 0

        # Generate random threads
        self.__new_random_threads__()

    def __new_random_threads__(self) -> None:
        """
        Empties `self.threads` and generates a random number of threads with random burst times.
        """
        global _verbose  # Because the encapsulation of `thread_task` function, we need to access this variable from the global scope, and then again in the `thread_task` function

        self.threads: list[threading.Thread] = []  # Empty the list

        # Generate a random number of threads
        num_threads = random.randint(1, 5)
        ng = NumberGenerator()
        burst_times = [
            ng.random_bt() for _ in range(num_threads)
        ]

        # Their is a 1 in a 1000 change that any given burst time will be N times larger than the rest
        minChange = 1
        maxChange = 1000
        N = 10
        if random.randint(minChange, maxChange) == 1:
            chosen_bt = random.randint(0, num_threads - 1)
            burst_times[chosen_bt] = burst_times[chosen_bt] * N
            if _verbose:
                print(f"Thread {chosen_bt} has been chosen to have a burst time 100 times larger than the rest")

        # At this point we can set the `bt_sum` property
        self.bt_sum = sum(burst_times)

        # Function bellow is the actual task that will be executed by the threads
        def thread_task(id: int, bt: float) -> None:
            global _verbose
            if _verbose:
                print(f"Thread {id} is running")
            time.sleep(bt)
            if _verbose:
                print(f"Thread {id} finished execution")

        # Create the threads
        for i in range(num_threads):
            thread = threading.Thread(
                target=thread_task, args=(i, burst_times[i]))
            self.threads.append(thread)

    def execute(self):
        """
        Executes the process by running all the threads and waiting for them to finish.
        """
        global _verbose

        # Update state to running
        self.state = "running"
        if _verbose:
            print(f"Process {self.id} is running")

        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()

        # After all threads have finished execution, update state to terminated
        self.state = "terminated"
        if _verbose:
            print(f"Process {self.id} has terminated")


class QueueItem():
    def __init__(self, process: Process) -> None:
        self.process = process
        self.age = 0


class ReadyQueue():
    """
    Holds processes internally for schedular to pick from.
    """

    def __init__(self) -> None:
        self.__queue__: list[QueueItem] = []

    def is_empty(self) -> bool:
        return len(self.__queue__) == 0

    def add(self, item: QueueItem):
        """
        Adds a process to the ready queue.
        """
        self.__queue__.append(item)

    def pop(self, i: int = 0):
        """
        Removes and returns the process at index `i` from the ready queue.
        """
        global _verbose

        if _verbose:
            print(f"Process {self.__queue__[i].process.id} has been removed from the ready queue")
        
        return self.__queue__.pop(i)

    # TODO add key type hint
    def sort(self, key=None, reverse: bool = False):
        """
        Sorts the queue in place.
        """
        self.__queue__.sort(key=key, reverse=reverse)

    def __iter__(self):
        """
        Get an iterator from an object.
        """
        return iter(self.__queue__)

    def __getitem__(self, index):
        """
        Get an item from the queue by index.
        """
        return self.__queue__[index]


class CompletedQueue():
    """
    Holds processes that have completed execution.
    """

    def __init__(self) -> None:
        self.__queue__: list[QueueItem] = []

    def add(self, item: QueueItem):
        self.__queue__.append(item)

    def get_last_n(self, n: int):
        return self.__queue__[-n:]


class Schedular():
    """
    Selects a process to execute based on non-preemtive SJF algorithm + process age.
    """

    def __init__(self) -> None:
        self.age_threshold = 10

    def select_process(self, queue: ReadyQueue) -> QueueItem | None:
        """
        Selects a process to execute based on non-preemtive SJF algorithm + process age.  
        For a more detailed explanation of the algorithm, please refer to the `diagrams.drawio` file, page `custom_sjf_flowchart`.

        ## Returns
        - QueueItem: None if the queue is empty, otherwise the selected process based on the algorithm.
        """
        selected_item = None

        # is the queue empty?
        if queue.is_empty():
            return selected_item

        # is their any queue item with an age above the specified threshold?
        if any([item.age > self.age_threshold for item in queue]):
            # sort the ready queue by age from high to low
            queue.sort(key=lambda x: x.age, reverse=True)
            # The code bellow could be used if the sortign method above takes too long
            # for i in range(len(queue)):
            #     if queue[i].age > self.age_threshold and selected_item != None and queue[i].age > selected_item.age:
            #         selected_item = queue[i]

            # TODO test which of the two methods is faster, sorting or the for loop
        else:
            # sort the ready queue by process burst time from low to high
            queue.sort(key=lambda x: x.process.bt_sum)

        # return the first item in the ready queue
        return queue.pop()


class Dispatcher():
    """
    Gives control of the CPU’s core to the process selected by the Scheduler.
    """

    def __init__(self) -> None:
        pass

    def dispatch(self, scheduler: Schedular, ready_queue: ReadyQueue, completed_queue: CompletedQueue):
        """
        Selects a process from `ready_queue`, executes it and moves it to `completed_queue`.
        Also updates the age of the processes left in the ready queue, if any.

        ## Parameters
        - scheduler: Schedular instance
        - ready_queue: ReadyQueue instance
        - completed_queue: CompletedQueue instance
        """
        global _verbose

        queue_item = scheduler.select_process(ready_queue)
        if queue_item != None:
            if _verbose:
                print(f"Process {queue_item.process.id} has been selected to run")

            queue_item.process.execute()
            completed_queue.add(queue_item)

            # Update age of the processes in the ready queue
            for item in ready_queue:
                item.age += 1


class QueueItemGenerator():
    """
    Generates new processes.
    """

    def __init__(self) -> None:
        pass

    def generate_item(self):
        global _verbose

        p = Process()
        q = QueueItem(p)
        if _verbose:
            print(f"Process {p.id} has been generated")

        return q

# endregion


# region Testing
def module_test():
    # Arrange
    queue_item_generator = QueueItemGenerator()
    scheduler = Schedular()
    ready_queue = ReadyQueue()
    dispatcher = Dispatcher()
    completed_queue = CompletedQueue()

    N_processes_to_generate = 10
    expected_completed_queue_length = N_processes_to_generate

    # Act
    for _ in range(N_processes_to_generate):
        ready_queue.add(queue_item_generator.generate_item())

    for _ in range(N_processes_to_generate):
        dispatcher.dispatch(scheduler, ready_queue, completed_queue)

    # Assert
    assert len(completed_queue.__queue__) == expected_completed_queue_length
    
    print("All tests passed successfully")


if _run_tests:
    module_test()
# endregion
