# The solution provided bellow is a barrier that only allows 1 thread to go trough at a time
# Its analogous to a raly race, in which sprinters pass a baton from 1 person to the next,
# and where only the person holding the baton can run.

from threading import Thread, Lock, Semaphore
import time
import random


num_workers = 4
threads: list[Thread] = []
baton: list[Semaphore] = [Semaphore(0) for _ in range(num_workers)]
baton_lock: Lock = Lock()

def barrier(index: int):
    # First, wait for the baton to be passed
    baton[index].acquire()
    
    # Next, pass the baton to the next thread
    with baton_lock:
        next_thread = (index + 1) % num_workers # Warp around to the first thread if needed
        baton[next_thread].release()


def thread_fn(thread_index: int, barrier: callable):
    for round in range(3):
        time.sleep(random.uniform(0.1, 1))
        print(f"Round {round + 1}: Thread-{thread_index+1} Arrived!")
        barrier(thread_index)
        print(f"Round {round + 1}: Thread-{thread_index+1} Passed!")


if __name__ == "__main__":
    for i in range(num_workers):
        t = Thread(target=thread_fn, args=(i, barrier))
        t.start()
        threads.append(t)

    # Initial baton to start the first thread
    baton[0].release()
    
    for t in threads:
        t.join()