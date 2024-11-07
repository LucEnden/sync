# Create and run 4 threads A, B, C and D.
# They print the numbers 1 until 8 on one terminal. Thread A prints the number 1 and 5, thread B prints 2 and 6, thread C prints 3 and 7, thread D prints 4 and 8.
# Requirements:
# •	the semaphores may be created before the threads are started
# •	the numbers are printed in the "right order"
# •	you may only use semaphores for synchronization (so no busy-wait loops, no shared memory)
# •	it should not make any difference in which order the threads are started

import threading
import random

sA = threading.Semaphore(0)
sB = threading.Semaphore(0)
sC = threading.Semaphore(0)
sD = threading.Semaphore(0)

def A():
    global sA, sB

    # Notice here we do not wait for sA to be released
    # Doing so would create a deadlock
    print(1) # critical section
    sB.release() # here we indicate to thread B that it can run

    sA.acquire() # here we wait for thread D to indicate we can continue
    print(5) # critical section
    sB.release() # and again, we indicate to thread B that it can continue

def B():
    global sB, sC
    
    sB.acquire() # we wait for thread A to indicate we can run
    print(2) # critical section
    sC.release() # again, we indicate that C can continue

    # The jist of it should be clear by now
    sB.acquire()
    print(6)
    sC.release()

def C():
    global sC

    sC.acquire()
    print(3) # critical section
    sD.release()

    sC.acquire()
    print(7) # critical section
    sD.release()

def D():
    global sD, sA

    sD.acquire()
    print(4) # critical section
    sA.release()

    sD.acquire()
    print(8) # critical section
    sA.release()

tA = threading.Thread(target=A, name="A")
tB = threading.Thread(target=B, name="B")
tC = threading.Thread(target=C, name="C")
tD = threading.Thread(target=D, name="D")

# run threads in random order
threads = [ tA, tB, tC, tD ]
random.shuffle(threads)

for t in threads:
    t.start()