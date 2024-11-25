import threading
import random

# =================================================
# Assignment implementation:
# Generalize the rendezvous solution. Every thread should run the
# following code:
# 1 rendezvous
# 2 critical point
# =================================================

class Rendezvous():
    def __init__(self, n_meeting: int):
        self.n_meeting = n_meeting
        self.__mutex__ = threading.Semaphore(1)
        self.__semap__ = threading.Semaphore(0)

    def signal(self):
        self.__semap__.release()

    def wait(self):
        self.__semap__.acquire()

# =================================================
# Assignment testing
# =================================================
n_threads = 4
barrier = Rendezvous(n_threads)
count = 0

def some_thread(t: int):
    global barrier, count, n_threads

    barrier.__mutex__.acquire()
    print(f"Thread {t} IN critical point")
    count += 1
    print(f"Thread {t} OUT critical point")
    barrier.__mutex__.release()

    if count == n_threads:
        barrier.signal()

    # rendezvous
    print(f"Thread {t} waiting at rendezvous")
    barrier.wait()
    barrier.signal()

    print(f"Thread {t} finished")

threads = []
for i in range(4):
    thread = threading.Thread(target=some_thread, args=(i,))
    threads.append(thread)
random.shuffle(threads)

for thread in threads:
    thread.start()


# Some notes:
# I HATE HOW THE LBOS LAYS OUT THE EXCERSIZES
# This barrier is not a fucking barrier. 
# Its a turnstile, then why the f*** would you call the chapter 3.6 Barrier???????
# Sorry but it makes me extremly frustrated to read something, have an expactation of what is expected (as he allows alot of room for implications), and then to be presented with a solution that does not match my expectations at all