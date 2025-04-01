import threading
import random

# =================================================
# Assignment implementation:
# ...
# =================================================

class Multiplex():
    def __init__(self, limit: int = 4):
        self.__semaphore__ = threading.Semaphore(limit)
        self.__inside__ = []

    def aquire(self, t: int):
        self.__inside__.append(t)

        print(f"Thread {t} aquiering multiplex ({self.__inside__})")
        self.__semaphore__.acquire()

    def release(self, t: int):

        print(f"Thread {t} releasing multiplex")
        if self.__semaphore__._value == 0:
            self.__semaphore__.release()
            self.__inside__.remove(t)

# =================================================
# Assignment testing
# =================================================
multiplex = Multiplex()
count = 0
def some_thread(t: int):
    global multiplex, count

    multiplex.aquire(t)
    # critical section
    print(f"Thread {t} in critical section")
    count += 1
    multiplex.release(t)

n_threads = 8
threads = []
for i in range(n_threads):
    thread = threading.Thread(target=some_thread, args=(i,))
    threads.append(thread)
random.shuffle(threads)

for thread in threads:
    thread.start()