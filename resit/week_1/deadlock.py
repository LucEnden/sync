# - Create three threads and three semaphores. 
# - Write synchronization code with the risk of deadlock, but where they also may run for hours without problems.

# Solution: this is can essentially be realised by introducing a race condition in the code.
# The idea is that, as long as the threads start in some order, they will run fine.
# But if they start in a different order, they will deadlock.
# We can simulate this by letting the threads sleep (just for demonstration purposes).
import threading
import time
import random


timings = [1, 2, 3]
random.shuffle(timings)
t1_sleep = timings[0]
t2_sleep = timings[1]
t3_sleep = timings[2]

# This demonstration might not work when the timings are too close to each other.
# As that will introduce micro differences which would be unreliable (which is exactly what I am trying to demonstrate is the issue here).
print("Thread 1 timing:", t1_sleep)
print("Thread 2 timing:", t2_sleep)
print("Thread 3 timing:", t3_sleep)
print("Expecting a deadlock:", "yes" if not (max(t1_sleep, t2_sleep, t3_sleep) == t1_sleep) else "no")

sema1 = threading.Semaphore(1)
sema2 = threading.Semaphore(0)
sema3 = threading.Semaphore(0)

# Just so that if a deadlock does happend, my console does not get blocked...
# This can be set to None to proof deadlocks in the simulator (which I did not yet get to work)
timeout = max(timings) + 1
# timeout = None

def thread1():
    global sema1, sema2, sema3
    time.sleep(t1_sleep)
    # Thread 1 only finishes when all three semaphores are released.
    sema1.acquire()
    sema2.acquire()
    sema3.acquire()
    print("Thread 1 finished")

def thread2():
    global sema1, sema2, sema3
    time.sleep(t2_sleep)

    sema1.acquire(timeout=timeout)
    if sema2._value == 0:
        sema2.release()
    sema1.release()

    print("Thread 2 finished")

def thread3():
    global sema1, sema2, sema3
    time.sleep(t3_sleep)

    sema1.acquire(timeout=timeout)
    if sema3._value == 0:
        sema3.release()
    sema1.release()

    print("Thread 3 finished")


# Launch threads
t1 = threading.Thread(target=thread1, name="t1")
t2 = threading.Thread(target=thread2, name="t2")
t3 = threading.Thread(target=thread3, name="t3")
threads = [t1, t2, t3]

for t in threads:
    t.start()
for t in threads:
    t.join()

print("All threads finished!")
print("Final semaphore values (expected all 0):")
print(sema1._value, sema2._value, sema3._value)