from Environment import *
from Environment import _blk

mutex = MyMutex("mutex")
cvA = MyConditionVariable(mutex, "cvA")
cvB = MyConditionVariable(mutex, "cvA")
i = MyInt(73, "i")

# example that doesn't serve any purpose, but only to demonstrate
# the usage of condition variables

def threadA():
    while True:
        mutex.wait()
        while not i.v % 3 == 0:
            cvA.wait()

        _blk()

        # CS
        i.v += 1

        if i.v % 2 == 0:
            cvB.notify()

        mutex.signal()


def threadB():
    while True:
        mutex.wait()
        while i.v > 100:
            cvB.wait()

        _blk()

        # CS
        i.v += 1

        if i.v % 3 == 0:
            cvA.notify_all()
        if i.v <= 100:
            cvB.notify()  # note: this will not actually wake-up a thread... (because no thread has done a cvB.wait())

        mutex.signal()


def setup():
    subscribe_thread(threadA)
    subscribe_thread(threadA)
    subscribe_thread(threadB)

