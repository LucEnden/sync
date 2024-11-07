# Implement the Reusable Barrier of paragraph 3.7 (LBOS), but only with the use of semaphores (so no counters). 
# The number of threads is known at compile time, e.g. 4.
import threading
import random

# A barier works as followed.
# - There are N threads that at some point in their excecution signal to the barier they arived at a certain point
# - Upon reaching this point, any given thread is locked using a semaphore
# - Once the number of signals the barier recieves equals the number of threads, 

class Barier():
    def __init__(self, nThreads: int = 4):
        self.nThreads = nThreads # we do not care which thread is who, just how many use this barier
        self.__semaphores__ = [
            threading.Semaphore()
            for _ in range(0, nThreads)
        ]

    def signal(self, i: int):
        return self.__semaphores__[i].acquire()

    def wait(self):
        while self.__get_n_arrived__() != self.nThreads:
            pass

    def __get_n_arrived__(self):
        return len([ s._value for s in self.__semaphores__ if s._value == 0 ])

# =================================================
# A test for the barier
# =================================================
nThreads = 4
b = Barier()

def some_thread(n: int, t: str):
    global b

    print(n + 1)
    b.signal(n)
    b.wait()

    print(f"Thread {t} finished!")


threads = []
for i in range(0, nThreads):
    t = threading.Thread(target=some_thread, kwargs={"n": i, "t": i + 1})
    threads.append(t)
random.shuffle(threads)

for t in threads:
    t.start()