import threading
import random

# =================================================
# Assignment implementation:
# Thread A
# 1 statement a1
# 2 statement a2
# 
# Thread B
# 1 statement b1
# 2 statement b2
# 
# we want to guarantee that a1 happens before b2 and b1 happens before a2.
# =================================================

aArriaval = threading.Semaphore(0)
bArriaval = threading.Semaphore(0)

def a():
    global aArrival, bArriaval
    print("A1")
    aArriaval.release()
    bArriaval.acquire()
    print("A2")

def b():
    global aArrival, bArriaval
    print("B1")
    bArriaval.release()
    aArriaval.acquire()
    print("B2")

# =================================================
# Assignment testing
# =================================================
threads = [
    threading.Thread(target=a),
    threading.Thread(target=b),
]
random.shuffle(threads)

for thread in threads:
    thread.start()