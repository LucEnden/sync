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
# TODO fix concurent counter access (mutex?)

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

    ## Parameters:
    - max_threads: to maximum amount of random threads to be generated for this process 
    - max_long_thread_change: `int` The max change a thread within this process will be longer then others (lower means more frequent).
    - long_thread_bt_multiplier: `int` The amount to multiply any randomly selected

    if max_long_thread_change <= 0, then no thread will be longer then the rest
    ---

    ## Explanation
    As stated in the book, "Operating System Concepts - 10th edition" by Silberschatz, Galvin, and Gagne (page 110):
    > In brief, the Process Control Block (PCB) simply serves as the repository for all the data needed to start,
    > or restart, a process, along with some accounting data.

    Upon object initialization, the `__new_random_threads__` method is called, which:
    - generates `random.randint(1, self.max_threads)` number of threads
    - generates random burst times using `NumberGenerator.random_bt` method for each of the threads
    - decides which (if any) thread should be longer then usual (see bellow)
    - fills the `self.threads` list with threads, each having the same function assigned to it that simply sleeps for the amount of time given by the number generator 
    
    The change a thread within any process will be longer then others is calculated via `random.randint(1, self.max_long_thread_change)`.
    If the outcome of this is 1, then a single random thread is selected and its burst time is is multiplied by `self.long_thread_bt_multiplier`
    """
    def __init__(self, max_threads: int = 8, max_long_thread_change: int = 100, long_thread_bt_multiplier: int = 10) -> None:
        self.threads = list[threading.Thread]
        self.state: ProcessState = ProcessState.NEW
        self.id: int = NumberGenerator().new_process_id()
        self.bt_sum: int = 0

        if not isinstance(max_threads, int):
            max_threads = 8
        self.max_threads = max_threads

        if not isinstance(max_long_thread_change, int):
            max_long_thread_change = 100
        self.max_long_thread_change: int = max_long_thread_change

        if not isinstance(long_thread_bt_multiplier, int):
            long_thread_bt_multiplier = 10
        self.long_thread_bt_multiplier = long_thread_bt_multiplier


        # Generate random threads
        self.__new_random_threads__()

    def __new_random_threads__(self) -> None:
        """
        Empties `self.threads` and generates a random number of threads with random burst times.
        """
        global _verbose  # Because the encapsulation of `thread_task` function, we need to access this variable from the global scope, and then again in the `thread_task` function

        self.threads: list[threading.Thread] = []  # Empty the list

        # Generate a random number of threads
        if self.max_threads == 0:
            return None
        if self.max_threads < 0:
            self.max_threads = 1

        num_threads = random.randint(1, self.max_threads)
        ng = NumberGenerator()
        burst_times = [
            ng.random_bt() for _ in range(num_threads)
        ]

        # Their is a 1 in a 1000 change that any given burst time will be N times larger than the rest
        if self.max_long_thread_change <= 0:
            minChange = 0
        else:
            minChange = 1

        if self.long_thread_bt_multiplier < 1:
            self.long_thread_bt_multiplier = 1

        if random.randint(minChange, self.max_long_thread_change) == 1:
            chosen_bt = random.randint(0, num_threads - 1)
            burst_times[chosen_bt] = burst_times[chosen_bt] * self.long_thread_bt_multiplier
            if _verbose:
                print(f"Thread {chosen_bt} has been chosen to have a burst time 100 times larger than the rest")

        # At this point we can set the `bt_sum` property
        self.bt_sum = sum(burst_times)

        # Function bellow is the actual task that will be executed by the threads
        def thread_task(id: int, bt: float) -> None:
            global _verbose
            # if _verbose:
            #     print(f"Thread {id} is running")
            time.sleep(bt)
            # if _verbose:
            #     print(f"Thread {id} finished execution")

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
        q = self.__queue__.pop(i)
        for i in range(len(self.__queue__)):
            self.__queue__[i].age += 1

        return q

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


class Schedular():
    """
    Selects a process to execute based on non-preemtive SJF algorithm + process age.
    """

    def __init__(self, age_threshold: int = 10) -> None:
        if not isinstance(age_threshold, int):
            age_threshold = 10
        self.age_threshold = age_threshold

    def select_process(self, queue: ReadyQueue) -> QueueItem | None:
        """
        Selects a process to execute based on non-preemtive SJF algorithm + process age.  
        For a more detailed explanation of the algorithm, please refer to the `diagrams.drawio` file, page `custom_sjf_flowchart`.

        ## Returns
        - QueueItem: None if the queue is empty, otherwise the selected process based on the algorithm.
        """
        global _verbose

        # is the queue empty?
        if queue.is_empty():
            return None

        # is their any queue item with an age above the specified threshold?
        if any([item.age > self.age_threshold for item in queue]):
            if _verbose:
                print("Sorting the ready queue by age")

            # Sort the ready queue: first by age (descending), then by burst time (descending)
            queue.sort(key=lambda x: (-x.age, -x.process.bt_sum))

        else:
            if _verbose:
                print("Sorting the ready queue by burst time")

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


class QueueItemGenerator():
    def __init__(self) -> None:
        pass

    def generate_item(self, **kwargs):
        """
        Generates a new process using argument values from kwargs
        """
        global _verbose

        if not 'max_threads' in kwargs.keys():
            kwargs['max_threads'] = None
        if not 'max_long_thread_change' in kwargs.keys():
            kwargs['max_long_thread_change'] = None
        if not 'long_thread_bt_multiplier' in kwargs.keys():
            kwargs['long_thread_bt_multiplier'] = None

        p = Process(
            max_threads=kwargs['max_threads'],
            max_long_thread_change=kwargs['max_long_thread_change'], 
            long_thread_bt_multiplier=kwargs['long_thread_bt_multiplier']
            )
        q = QueueItem(p)
        if _verbose:
            print(f"Process {p.id} has been generated")

        return q

# endregion


# region Testing
def arrange():
    """
    Sets verbose to false and instantiates new module classes to be used in tests.

    ## Returns:
    `tuple`: (
        queue_item_generator,
        scheduler,
        ready_queue,
        dispatcher,
        completed_queue
    )
    """
    global _verbose
    _verbose = False
    
    queue_item_generator = QueueItemGenerator()
    scheduler = Schedular()
    ready_queue = ReadyQueue()
    dispatcher = Dispatcher()
    completed_queue = CompletedQueue()

    return (
        queue_item_generator,
        scheduler,
        ready_queue,
        dispatcher,
        completed_queue
    )

def module_test_1():
    """
    See if the queue's are as expected after running to completion.
    I.E. does the completed queue contain all generated and excecuted processes and is the ready queue empty
    """
    # Arrange
    queue_item_generator, scheduler, ready_queue, dispatcher, completed_queue = arrange()

    N_processes_to_generate = 10
    expected_completed_queue_length = N_processes_to_generate

    # Act
    for _ in range(N_processes_to_generate):
        ready_queue.add(queue_item_generator.generate_item())

    for _ in range(N_processes_to_generate):
        dispatcher.dispatch(scheduler, ready_queue, completed_queue)

    # Assert
    assert len(completed_queue.__queue__) == expected_completed_queue_length
    assert len(ready_queue.__queue__) == 0
    assert ready_queue.is_empty() == True
    
    print("MODULE TEST 1 \t PASSED")

def module_test_2():
    """
    Force completion of longer process to see if aging is implemented properly
    """
    # Arrange
    queue_item_generator, scheduler, ready_queue, dispatcher, completed_queue = arrange()

    # We create 9 short processes and 1 long process
    # We first add the short processes to the ready queue and then the long process
    N_processes_to_generate = 10
    scheduler.age_threshold = 2 #N_processes_to_generate // 5
    long_thread_bt_multiplier = 10

    short_processes = [
            queue_item_generator.generate_item(
            max_threads=8, 
            max_long_thread_change=0
        ) for _ in range(N_processes_to_generate - 1)
    ]
    long_process = queue_item_generator.generate_item(
        max_threads=1, 
        max_long_thread_change=1, 
        long_thread_bt_multiplier=long_thread_bt_multiplier
    )

    all_processes = short_processes + [long_process]

    # Act
    for p in all_processes:
        ready_queue.add(p)

    for _ in range(len(all_processes)):
        dispatcher.dispatch(scheduler, ready_queue, completed_queue)

    # Assert
    assert completed_queue[3].process.id == long_process.process.id # The long_process should be the 4th one excecuted given the config above

    print("MODULE TEST 2 \t PASSED")


if _run_tests:
    tests_to_run = [
        threading.Thread(target=module_test_1),
        threading.Thread(target=module_test_2),
    ]
    
    for i, t in enumerate(tests_to_run):
        print(f"Running test {i + 1}")
        try:
            t.start()
        except Exception as e:
            print(f"Running test {i + 1} failed:\n{e}")
# endregion


# TODO 1 - Add a main function that will run the emulation, such that the queue and currently running process are available even outside this module