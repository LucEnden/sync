# My solution is a barrier that waits for all threads to arrive, but does not wait to release them all.
# They are all released at the same time, but they can cross the barrier at different times.
# Some might even arive at the barrier before the others have crossed it,
# but they will all wait for the others to arrive before they can cross it.

from threading import Thread, Event, Lock, current_thread


num_workers = 4
count = 0
finished = Event()
mutex = Lock()


def barrier():
    global count, finished, mutex

    with mutex:
        count += 1
        if count == num_workers:
            finished.set()

    print(count)
    finished.wait()

    with mutex:
        count -= 1
        if count == 0:
            finished.clear()
    print(count)


def thread() -> None:
    for _ in range(3):
        print(f"{current_thread().name} is waiting at the barrier")
        barrier()
        print(f"{current_thread().name} has crossed the barrier")


if __name__ == "__main__":
    threads = []

    for i in range(num_workers):
        t = Thread(target=thread, name=f"Thread-{i}")
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


#region Solution from the book
# turnstile = Semaphore(0)
# turnstile2 = Semaphore(1)
# mutex = Semaphore(1)
# count = 0

# def book_barrier() -> None:
#     global mutex, count, turnstile, turnstile2, num_workers
    
#     # Phase 1: wait for all threads to reach the barrier
#     mutex.acquire()
#     count += 1
#     if count == num_workers:
#         turnstile2.acquire()    # lock the second
#         turnstile.release()     # unlock the first
#     mutex.release()
    
#     print(count)
#     turnstile.acquire()         # first turnstile
#     turnstile.release()

#     # Critical section
    
#     # Phase 2: wait for all threads to cross the barrier
#     mutex.acquire()
#     count -= 1
#     if count == 0:
#         turnstile.acquire()     # lock the first
#         turnstile2.release()    # unlock the second
#     mutex.release()
    
#     print(count)
#     turnstile2.acquire()        # second turnstile
#     turnstile2.release()
#endregion