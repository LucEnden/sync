import threading
import random

# =================================================
# Assignment implementation:
# Rewrite the barrier solution so that after all the threads have passed
# through, the turnstile is locked again.
# =================================================

class ReusableBarrier():
    def __init__(self):
        pass

# =================================================
# Assignment testing
# =================================================
def some_thread():
    pass

n_threads = 4
threads = []
for i in range(n_threads):
    thread = threading.Thread(target=some_thread)
    threads.append(thread)
random.shuffle(threads)

for thread in threads:
    thread.start()