import threading
import random

# =================================================
# Assignment implementation:
# Add semaphores to the following example to enforce mutual exclusion to the shared variable count.
#
# Thread A
# 1 count = count + 1
# 
# Thread B
# 1 count = count + 1
# =================================================

mutex = threading.Semaphore(1)
count = 0

def thread_a():
    global count, mutex

    # critical section
    mutex.acquire()
    print("Thread A accessing critical section")
    count += 1
    print("Thread A leaving critical section")
    mutex.release()

def thread_b():
    global count, mutex

    mutex.acquire()
    # critical section
    print("Thread B accessing critical section")
    count += 1
    print("Thread B leaving critical section")
    mutex.release()

# =================================================
# Assignment testing
# =================================================
threads = [
    threading.Thread(target=thread_a),
    threading.Thread(target=thread_b)
]
random.shuffle(threads)

for thread in threads:
    thread.start()