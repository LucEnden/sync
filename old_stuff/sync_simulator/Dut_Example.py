from Environment import *
from Environment import _blk

# rather nonsense program to show elementary SyncSimulator features
N = 3

counter = MyInt(73, "counter")
my_mutex = MyMutex("my_mutex")
flag = MyBool(False, "flag")
semafoor = MySemaphore(1, "semafoor")


def threadA():
    while True:
        my_mutex.wait()
        counter.v += 5
        _blk();
        counter.v += 7
        my_mutex.signal()


def threadB():
    while True:
        if flag.v:
            semafoor.signal()
            flag.v = False
        else:
            flag.v = True
            _blk()
            counter.v += 3
        _blk()
        print("at the end of threadB; data:", counter.v, flag.v)


def setup():
    subscribe_thread(threadB)
    for i in range(N):
        subscribe_thread(threadA)
