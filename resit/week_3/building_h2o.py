# The idea is to have the hydrogen thread leading. Every hydrogen thread will wake up 2 oxygen threads.
# Checking the output shows that sometimes pairs show up as HOO, sometimes OOH, and sometimes OHO, but never any other combination.

# What this implementation does lack however is the fackt that if a certain number of HO threads are created, the program will never end.
# If you change the while loop into a for loop there might exist a deadlock, depending on the configuration
import random
import time
from threading import current_thread, Semaphore, Barrier, Thread, Event


hyd_sema = Semaphore(1)
oxy_sema = Semaphore(0)
barrier = Barrier(3)
should_stop = Event()


def bond() -> None:
    print(current_thread().name)


def hydrogen():
    while not should_stop.is_set():
        hyd_sema.acquire()
        oxy_sema.release(2)
        barrier.wait()
        bond()
        hyd_sema.release()


def oxygen():
    while not should_stop.is_set():
        oxy_sema.acquire()
        barrier.wait()
        bond()


if __name__ == "__main__":
    threads: list[Thread] = []

    n_hydro = random.randint(3, 10)
    for i in range(n_hydro):
        h_thread = Thread(target=hydrogen, name=f"H-{i+1}")
        threads.append(h_thread)
    n_oxy = random.randint(3, 10)
    for i in range(n_oxy):
        o_thread = Thread(target=oxygen, name=f"O-{i+1}")
        threads.append(o_thread)
    
    print(f"Starting {n_hydro} hydrogen and {n_oxy} oxygen threads")
    random.shuffle(threads)
    for thread in threads:
        thread.start()

    # Wait for all threads to finish
    time.sleep(0.002)
    should_stop.set()
    hyd_sema.release(n_hydro)
    oxy_sema.release(n_oxy)
    for thread in threads:
        thread.join()