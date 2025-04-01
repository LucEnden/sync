from Environment import *
from Environment import _blk

# example code for a (parametrized) symmetric implementation
# a person is either a Producer or Consumer; 
# they do have different semaphores and those semaphores 
# are handed over via the objects 'me' and 'other' 

N = 7
counter = 42

def produce():
    global counter
    print ("P: ", counter)
    buffer.put(str(counter))
    counter += 1
    
    
def consume():
    print ("       C: ", buffer.get())
    
    
def threadPerson(me, other):
    while True:
        me.sem.wait()
        
        mutex.wait()
        me.action()
        mutex.signal()
        
        other.sem.signal()


class Person(object):
    def __init__(self, sem, action):
        self.sem = sem
        self.action = action


mutex = MyMutex("mutex")
buffer = MyFifo(N, "fifo")
producer = Person(MySemaphore(N, "prodSem"), produce)
consumer = Person(MySemaphore(0, "consSem"), consume)


def setup():
    subscribe_thread(lambda: threadPerson(producer, consumer))
    subscribe_thread(lambda: threadPerson(consumer, producer))
