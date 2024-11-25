import threading
import random

# =================================================
# Assignment implementation:
# Semaphores can also be used to represent a queue. In this case, the initial value
# is 0, and usually the code is written so that it is not possible to signal unless
# there is a thread waiting, so the value of the semaphore is never positive.
# For example, imagine that threads represent ballroom dancers and that two
# kinds of dancers, leaders and followers, wait in two queues before entering the
# dance floor. When a leader arrives, it checks to see if there is a follower waiting.
# If so, they can both proceed. Otherwise it waits.
# Similarly, when a follower arrives, it checks for a leader and either proceeds
# or waits, accordingly.
# Puzzle: write code for leaders and followers that enforces these constraints.
# =================================================

leader_queue = threading.Semaphore(0)
follower_queue = threading.Semaphore(0)

# =================================================
# Assignment testing
# =================================================
should_run = True

def leader_thread(t: int):
    global should_run, leader_queue, follower_queue
    
    while should_run:
        print(f"Leader {t} looking for a follower")
        leader_queue.release()
        follower_queue.acquire()
        print(f"Leader {t} found a follower")

def follower_thread(t: int):
    global should_run, leader_queue, follower_queue

    while should_run:
        print(f"Follower {t} looking for a leader")
        follower_queue.release()
        leader_queue.acquire()
        print(f"Follower {t} found a leader")
    

n_threads = 5
follower_count = 0
threads = []
for i in range(n_threads):
    if i == 0:
        thread = threading.Thread(target=follower_thread, args=(i,))
        follower_count += 1
    elif i == 1:
        thread = threading.Thread(target=leader_thread, args=(i,))
    else:
        if random.choice([True, False]):
            thread = threading.Thread(target=follower_thread, args=(i,))
            follower_count += 1
        else:
            thread = threading.Thread(target=leader_thread, args=(i,))

    threads.append(thread)
random.shuffle(threads)

print(f"We have {follower_count} followers and {n_threads - follower_count} leaders")
for thread in threads:
    thread.start()

try:
    input('Press any key to stop...\n')
    should_run = False
except KeyboardInterrupt:
    should_run = False
    
while follower_queue._value < 0:
    follower_queue.release()
while leader_queue._value < 0:
    leader_queue.release()

for thread in threads:
    thread.join()