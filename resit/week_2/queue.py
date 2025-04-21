# About my solution, but also the assignment:
# I am writing these comments since I ran into similar confusion last semester and the new assignment document did not improve that much if you ask me.
# I think these points are worth mentioning.

# I know from previous semester what is meant by a pipet, but only because i wrote it down last time and looked it up. 
# Perhaps add a picture of a pipete to the assignment to make that a bit more clear.
# Googleing "pipet synchronization pattern" or something similair yields 0 effect, at least for me, so that was annoying.

# Also, it is stated that we need to make a "symmetric implementation", and I have no clue what this means... 
# I asked Chat-GPT and it said: "neither the dancer nor the follower has priority"
# My solution assumes that the Chat-GPT clarification is what was meant by "symmetric implementation".

# Then it says "Ensure that an arbitrary number of follower and leader threads can be started (e.g. N=5)"
# I can write a solution that just instantiates 5 waiting followers, resulting in a deadlock, but from the wording of the assignment that seems completly fine.
# It seems quite arbitrary to have this phrase in the assignment description without any other clarification of what is required.
# Perhaps add: "No deadlocks can occur, and an arbitrary number of ..." or something along these lines.

# I also found the lack of a refrence to any list or queue data structure in the assignment description, nor in the LBOS quite confusing.
# I get that a queue could be represented by a single integer, but I sticked to the "queue = list data structure" in my solution. 

from threading import Thread, Semaphore, Lock, current_thread
import random


mutex = Lock()
leader_queue: list[Semaphore] = []
follower_queue: list[Semaphore] = []


def leader():
    my_sema = Semaphore(0)
    matched = False

    with mutex: # Shared mutex, meaning first-come first-serve, no special priority
        if follower_queue:
            follower = follower_queue.pop()
            follower.release()
            matched = True
        else:
            leader_queue.append(my_sema)

    if not matched:
        my_sema.acquire()

    print(f"{current_thread().name} paired as leader")


def follower():
    my_sema = Semaphore(0)
    matched = False

    with mutex: # Shared mutex, meaning first-come first-serve, no special priority
        if leader_queue:
            leader = leader_queue.pop()
            leader.release()
            matched = True
        else:
            follower_queue.append(my_sema)

    if not matched:
        my_sema.acquire()

    print(f"{current_thread().name} paired as follower")


if __name__ == "__main__":
    threads = []

    num_pairs = 5
    # Demonstrait arbitrary pair orders, the code will run, even if the queues start with 2 leaders
    roles = ['leader'] * (num_pairs - 2) + ['follower'] * num_pairs
    random.shuffle(roles)
    roles = ['leader', 'leader'] + roles

    for i, role in enumerate(roles):
        if role == 'leader':
            t = Thread(target=leader, name=f"{role}-{i}")
        else:
            t = Thread(target=follower, name=f"{role}-{i}")
        t.start()
        threads.append(t)

    for t in threads:
        t.join()