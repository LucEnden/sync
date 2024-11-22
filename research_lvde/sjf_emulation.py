# Hint for VSCode users: press 'crtl + K' then 'crtl + 0' to fold all regions
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
from typing import Callable

_verbose = False                                # Set to True to print information to stdout
_run_tests = False                              # Set to True to run tests at the end of the file
_process_counter = 0                            # Counter for the number of processes generated
_process_counter_mutex = threading.Semaphore()  # Mutex for the process counter
_time_delta = time.time()                       # Time delta for the simulation
_run_sim = False                                # Set to True to run the simulation

# TODO add more unit tests, instead of just system tests
# TODO add support for callbacks durring the simulation
# TODO refactor the code to be more event driven
# TODO add a way to stop the simulation gracefully (`Simulation().stop()`)

# region Emulation classes

class NumberGenerator():
    """
    Generates numbers used during the emulation.
    """
    def __init__(self) -> None:
        self.__process_counter__ = 0

    def random_bt(self, _min: int = 50, _max: int = 300, _div: int = 100) -> float:
        """
        Generates a random possitive burst time (`abs(random.randint(_min, _max) / _div)`)

        ## Returns
        - float: Absolute value of a random number between `_min` and `_max` divided by `_div`
        """
        return abs(random.randint(_min, _max) / _div)

    def new_process_id(self) -> int:
        """
        Generates a new process id.

        ## Returns
        - int: A new process id
        """
        global _process_counter, _process_counter_mutex

        _process_counter_mutex.acquire()
        _process_counter = _process_counter + 1
        _process_counter_mutex.release()

        return _process_counter


class ThreadGenerator():
    def __init__(self) -> None:
        pass

    def generate_thread(self, burst_time: float) -> threading.Thread:
        """
        Generates a new thread that sleeps for the given burst time.

        ## Parameters
        - burst_time: float The amount of time the thread will "work" for

        ## Returns
        - threading.Thread: A new thread instance
        """
        def thread_task(bt: float) -> None:
            global _verbose
            if _verbose:
                print(f"Thread is running")
            time.sleep(bt)
            if _verbose:
                print(f"Thread finished execution")

        return threading.Thread(target=thread_task, args=(burst_time,))


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
    - n_threads: the number of threads to generate for this process
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
    def __init__(self, n_threads: int = 2, max_long_thread_change: int = 10, long_thread_bt_multiplier: int = 10) -> None:
        self.threads: list[threading.Thread] = []
        self.state: ProcessState = ProcessState.NEW
        self.id: int = NumberGenerator().new_process_id()
        self.bt_sum: int = 0
        self.avg_bt: int = 0
        self.min_bt: int = 0
        self.max_bt: int = 0
        self.ttc: int = 0

        # Gaurd clauses for thread generation parameters
        if not isinstance(n_threads, int):
            n_threads = 2

        if not isinstance(max_long_thread_change, int):
            max_long_thread_change = 10

        if not isinstance(long_thread_bt_multiplier, int):
            long_thread_bt_multiplier = 10

        # Generate random threads
        self.__new_random_threads__(
            n_threads=n_threads,
            max_long_thread_change=max_long_thread_change,
            long_thread_bt_multiplier=long_thread_bt_multiplier
        )

    def __new_random_threads__(self, n_threads: int, max_long_thread_change: int, long_thread_bt_multiplier: int) -> None:
        """
        Empties `self.threads` and generates a random number of threads with random burst times.
        """
        global _verbose  # Because the encapsulation of `thread_task` function, we need to access this variable from the global scope, and then again in the `thread_task` function

        self.threads = []  # Empty the list

        ng = NumberGenerator()
        burst_times = [
            ng.random_bt() for _ in range(n_threads)
        ]

        # 1 in X chance that a thread will be longer then the rest
        min_change = 0
        if long_thread_bt_multiplier < 1:
            long_thread_bt_multiplier = 1
        should_multiply = random.randint(min_change, max_long_thread_change)

        if should_multiply == 1:
            chosen_bt = random.randint(0, len(burst_times) - 1)
            burst_times[chosen_bt] = burst_times[chosen_bt] * long_thread_bt_multiplier
            if _verbose:
                print(f"Thread {chosen_bt} in process {self.id} has been chosen to have a burst time {long_thread_bt_multiplier} times larger")

        # Create the threads
        tg = ThreadGenerator()
        for bt in burst_times:
            self.threads.append(tg.generate_thread(bt))

        # At this point we can set the `bt_sum` and `avg_bt` properties
        self.bt_sum = sum(burst_times)
        self.avg_bt = self.bt_sum / len(self.threads)
        self.min_bt = min(burst_times)
        self.max_bt = max(burst_times)

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
        self.arrival_time = 0


class BaseQueue():
    def __init__(self) -> None:
        self.__queue__: list[QueueItem] = []

    def is_empty(self) -> bool:
        """
        Returns `True` if the queue is empty, `False` otherwise.
        """
        return len(self.__queue__) == 0

    def add(self, item: QueueItem):
        """
        Adds a process to the ready queue.
        """
        global _time_delta
        item.arrival_time = time.time() - _time_delta
        self.__queue__.append(item)

    def pop(self, i: int = 0) -> (QueueItem | None):
        """
        Removes and returns the process at index `i` from the ready queue. If the index is out of range, returns `None`.

        Updates the age of the processes left in the queue, if any.
        """
        try:
            q = self.__queue__.pop(i)
        except IndexError:
            return None

        for i in range(len(self.__queue__)):
            self.__queue__[i].age += 1

        return q

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
    
    def __len__(self):
        # Return the length of the internal list (or any other logic you want)
        return len(self.__queue__)


class ReadyQueue(BaseQueue):
    """
    Holds processes internally for schedular to pick from.
    """
    def __init__(self) -> None:
        super().__init__()

    def get_first_n(self, n: int):
        """
        Returns the first `n` processes from the ready queue.
        """
        return self.__queue__[:n]

    def sort(self, key=None, reverse: bool = False):
        """
        Sorts the queue in place.
        """
        self.__queue__.sort(key=key, reverse=reverse)


class CompletedQueue(BaseQueue):
    """
    Holds processes that have completed execution.
    """
    def __init__(self) -> None:
        super().__init__()

    def get_last_n(self, n: int):
        return self.__queue__[-n:]


class Schedular():
    """
    Selects a process to execute based on non-preemtive SJF algorithm + process age.
    """

    def __init__(self, age_threshold: int = 10) -> None:
        if not isinstance(age_threshold, int):
            age_threshold = 10
        self.age_threshold = age_threshold
        self.sorting_style = "burst_time"

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
        if any([item.age >= self.age_threshold for item in queue]):
            if _verbose:
                print("Sorting the ready queue by age")

            self.sorting_style = "age"
            # Sort the ready queue: first by age (descending), then by burst time (descending)
            queue.sort(key=lambda x: (-x.age, -x.process.bt_sum))

        else:
            if _verbose:
                print("Sorting the ready queue by burst time")
            
            self.sorting_style = "burst_time"
            # sort the ready queue by process burst time from low to high
            queue.sort(key=lambda x: x.process.avg_bt)

        # return the first item in the ready queue
        return queue.pop()


class CPU():
    """
    Emulates the CPU.
    """
    def __init__(self) -> None:
        self.running_process: Process | None = None

    def run(self, process: Process):
        """
        Runs the CPU until the ready queue is empty.

        ## Parameters
        - process: Process instance
        """
        global _verbose
        
        self.running_process = process
        if _verbose:
            print(f"Process {process.id} is running")

        process.execute()
        self.running_process = None


class Dispatcher():
    """
    Gives control of the CPU’s core to the process selected by the Scheduler.
    """
    def __init__(self) -> None:
        self.CPU = CPU()

    def dispatch(self, scheduler: Schedular, ready_queue: ReadyQueue, completed_queue: CompletedQueue):
        """
        Selects a process from `ready_queue`, executes it and moves it to `completed_queue`.
        Also sets the time it took to complete the process.

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

            queue_item.process.state = ProcessState.RUNNING

            # Execute the process and measure the time it took to complete
            start = time.time()
            self.CPU.run(queue_item.process)
            end = time.time()
            queue_item.process.ttc = end - start

            completed_queue.add(queue_item)


class QueueItemGenerator():
    def __init__(self) -> None:
        pass

    def generate_item(self, **kwargs):
        """
        Generates a new process using argument values from kwargs
        """
        global _verbose

        if not 'n_threads' in kwargs.keys():
            kwargs['n_threads'] = None
        if not 'max_long_thread_change' in kwargs.keys():
            kwargs['max_long_thread_change'] = None
        if not 'long_thread_bt_multiplier' in kwargs.keys():
            kwargs['long_thread_bt_multiplier'] = None

        p = Process(
            n_threads=kwargs['n_threads'],
            max_long_thread_change=kwargs['max_long_thread_change'], 
            long_thread_bt_multiplier=kwargs['long_thread_bt_multiplier']
            )
        q = QueueItem(p)
        if _verbose:
            print(f"Process {p.id} has been generated")

        return q


class Simulation():
    """
    Runs a thread safe simulation of the SJF algorithm.

    It does this by running two threads concurrently:
    - One thread generates new processes and adds them to the ready queue on a regular interval
    - The other thread selects a process from the ready queue, executes it and moves it to the completed queue
    """
    def __init__(self) -> None:
        self.queue_item_generator = QueueItemGenerator()
        self.scheduler = Schedular()
        self.ready_queue = ReadyQueue()
        self.dispatcher = Dispatcher()
        self.completed_queue = CompletedQueue()

        self.dispatch_thread: threading.Thread | None = None
        self.generate_thread: threading.Thread | None = None
        
        self.N_items_to_keep_ready: int = 10
        self.dispatch_callback: Callable | None = None
        self.generate_callback: Callable | None = None

        self._dispatch_sema = threading.Semaphore(1)
        self._generate_sema = threading.Semaphore(1)
        self.is_running = False

    def setup(self, 
              N_start_processes: int = 0, 
              N_items_to_keep_ready: int = 10,
              dispatch_callback: Callable | None = None,
              generate_callback: Callable | None = None,
        ):
        """
        Initializes the simulation threads.
        """
        global _verbose
        
        self._dispatch_sema.acquire()
        self._generate_sema.acquire()

        self.N_items_to_keep_ready = N_items_to_keep_ready
        self.dispatch_callback = dispatch_callback
        self.generate_callback = generate_callback

        # Reinitialize the queues
        self.ready_queue = ReadyQueue()
        self.completed_queue = CompletedQueue()

        # Add some processes to the ready queue
        for _ in range(N_start_processes):
            self.ready_queue.add(self.queue_item_generator.generate_item())

        # Setup the dispatch thread
        def __dispatch_thread__():
            while True:
                # Using rendezvous pattern to ensure the dispatcher and generator don't run at the same time
                self._dispatch_sema.release()
                if not self.ready_queue.is_empty() and self.is_running:
                    if _verbose:
                        print("Dispatching a process during the simulation")
                    self.dispatcher.dispatch(self.scheduler, self.ready_queue, self.completed_queue)
                self._generate_sema.acquire()

                # Run callback if it exists
                if self.dispatch_callback != None:
                    self.dispatch_callback()

        self.dispatch_thread = threading.Thread(target=__dispatch_thread__)

        # Setup the generate queue items thread
        def __generate_queue_items_thread__():
            global _verbose
            # Generates new processes and adds them to the ready queue
            while True:
                # Using rendezvous pattern to ensure the dispatcher and generator don't run at the same time
                self._generate_sema.release()
                if self.is_running and len(self.ready_queue) < N_items_to_keep_ready:
                    if _verbose:
                        print(f"Adding {N_items_to_keep_ready - len(self.ready_queue)} new processes to the ready queue during the simulation")
                    for _ in range(N_items_to_keep_ready - len(self.ready_queue)):
                        self.ready_queue.add(self.queue_item_generator.generate_item())
                self._dispatch_sema.acquire()
                
        self.generate_thread = threading.Thread(target=__generate_queue_items_thread__)

        self._dispatch_sema.release()
        self._generate_sema.release()

    def start(self):
        """
        Does nothing if `this.init` has not been called, otherwise starts the simulation thread.
        """
        global _verbose, _process_counter, _process_counter_mutex, _time_delta
        if self.generate_thread == None or self.dispatch_thread == None:
            return
        if self.generate_thread.is_alive() or self.dispatch_thread.is_alive():
            return
        
        _process_counter_mutex.acquire()
        _process_counter = 0
        _process_counter_mutex.release()

        self._dispatch_sema.acquire()
        self._generate_sema.acquire()

        _time_delta = time.time()
        self.is_running = True
        self.generate_thread.start()
        self.dispatch_thread.start()
        if _verbose:
            print("Simulation has started")

        self._dispatch_sema.release()
        self._generate_sema.release()

    def pause(self):
        """
        Pauses the simulation.
        """
        self.is_running = False

    def resume(self):
        """
        Resumes the simulation.
        """
        self.is_running = True

    def stop(self):
        """
        Stops the simulation.
        """
        self.is_running = False

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
    module_test_1()
    module_test_2()

    # TODO Check why the code bellow works on one machine but not on the other
    # tests_to_run = [
    #     threading.Thread(target=module_test_1),
    #     threading.Thread(target=module_test_2),
    # ]
    
    # for i, t in enumerate(tests_to_run):
    #     print(f"Running test {i + 1}")
    #     try:
    #         # t.start()
    #         t()
    #     except Exception as e:
    #         print(f"Running test {i + 1} failed:\n{e}")
# endregion

if _run_sim:
    _verbose = True
    sim = Simulation()
    sim.setup(30)
    sim.scheduler.age_threshold = 10
    sim.start()