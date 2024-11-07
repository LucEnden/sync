from Environment import *
    
N = 4

def threadPerson(me, other):
    while True:
        mutex.wait()
        if state.v == other.state_walk:
            state.v = other.state_trans
        while not (state.v == "NEUTRAL" or state.v == me.state_walk):
            me.cv.wait()
        state.v = me.state_walk
        
        me.count.v += 1
        mutex.signal()

        # CS
        
        mutex.wait()
        me.count.v -= 1
        if me.count.v == 0:
            state.v = "NEUTRAL"
            other.cv.notify_all()
        mutex.signal()


class Person(object):
    def __init__(self, count, cv, state_walk, state_trans):
        self.count = count
        self.cv = cv
        self.state_walk = state_walk
        self.state_trans = state_trans


state = MyString("NEUTRAL", "state")
mutex = MyMutex("mutex")
heathen = Person (MyInt(0, "heathenCount"),
              MyConditionVariable(mutex, "heathenCV"), "HEATHENS_RULE", "TRANS_TO_PRUDES")
prude = Person (MyInt(0, "prudeCount"),
               MyConditionVariable(mutex, "prudeCV"), "PRUDES_RULE", "TRANS_TO_HEATHENS")

def setup():
    for i in range(N):
        subscribe_thread(lambda: threadPerson(heathen, prude))
    for i in range(N):
        subscribe_thread(lambda: threadPerson(prude, heathen))



