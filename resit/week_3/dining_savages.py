# The idea is to setup 2 semaphoes: one to signal when the pot is empty and one to signal when the pot is full.
# Based on the starting conditions of the code (i.e. an empty pot list), the placement of the empty_pot semaphore inside the cook thread matters.
# It needs to be put in the end for the cook to fill the pot for at least 1 itteration.
from threading import Thread, current_thread, Semaphore, Lock, Event
import random
import time


pot: list[str] = []
pot_lock = Lock()
empty_pot = Semaphore(0)
full_pot = Semaphore(0)
should_stop = Event()


#region Savages
def get_serving_from_pot() -> str:
    return pot.pop()

def savage():
    # Any number of savage threads run the following code:
    while not should_stop.is_set():
        # Savages cannot invoke get_serving_from_pot if the pot is empty.
        full_pot.acquire()

        pot_lock.acquire()
        serving = get_serving_from_pot()
        print(f"{current_thread().name} is eating {serving}")
        if len(pot) == 0 and empty_pot._value == 0:
            print(f"{current_thread().name} is waking up the cook")
            empty_pot.release()
        pot_lock.release()
#endregion


#region Cook
def put_servings_in_pot(servings: list[str]):
    pot.extend(servings)


def cook():
    def generate_servings():
        meals = [ "monkey", "salamander", "human-leg" ]
        N_servings = random.randint(1, 5)
        servings = []
        for _ in range(N_servings):
            servings.append(random.choice(meals))
        return servings

    # One cook thread runs this code:
    while not should_stop.is_set():
        # The cook can invoke put_servings_in_pot only if the pot is empty.
        servings = generate_servings()
        pot_lock.acquire()
        put_servings_in_pot(servings)
        pot_lock.release()

        print(f"{current_thread().name} put servings in the pot: {servings}")
        full_pot.release(len(servings))
        empty_pot.acquire()
#endregion


if __name__ == "__main__":
    threads: list[Thread] = []

    # Create and start the cook thread
    cook_thread = Thread(target=cook, name="Cook")
    cook_thread.start()
    threads.append(cook_thread)

    # Create and start savage threads
    n_savages = random.randint(3, 10)
    for i in range(n_savages):
        savage_thread = Thread(target=savage, name=f"Savage-{i+1}")
        savage_thread.start()
        threads.append(savage_thread)

    # Wait for all threads to finish
    time.sleep(0.002)
    should_stop.set()
    full_pot.release(n_savages)
    empty_pot.release()
    for thread in threads:
        thread.join()


sample_output = """
Cook put servings in the pot: ['salamander', 'human-leg', 'monkey']
Savage-1 is eating monkey
Savage-1 is eating human-leg
Savage-2 is eating salamander
Savage-2 is waking up the cook
Cook put servings in the pot: ['salamander', 'salamander', 'salamander']
Savage-1 is eating salamander
Savage-2 is eating salamander
Savage-3 is eating salamander
Savage-3 is waking up the cook
Cook put servings in the pot: ['human-leg']
Savage-4 is eating human-leg
Savage-4 is waking up the cook
Cook put servings in the pot: ['salamander', 'salamander']
Savage-5 is eating salamander
Savage-1 is eating salamander
Savage-1 is waking up the cook
Cook put servings in the pot: ['human-leg', 'salamander', 'salamander', 'salamander']
Savage-4 is eating salamander
Savage-3 is eating salamander
Savage-5 is eating salamander
Savage-2 is eating human-leg
Savage-2 is waking up the cook
Cook put servings in the pot: ['human-leg', 'human-leg', 'salamander', 'human-leg']
Savage-4 is eating human-leg
Savage-4 is eating salamander
Savage-1 is eating human-leg
Savage-5 is eating human-leg
Savage-5 is waking up the cook
Cook put servings in the pot: ['salamander', 'salamander', 'salamander', 'human-leg']
Savage-2 is eating human-leg
Savage-3 is eating salamander
Savage-4 is eating salamander
Savage-1 is eating salamander
Savage-1 is waking up the cook
Cook put servings in the pot: ['monkey', 'salamander', 'monkey', 'salamander', 'salamander']
Savage-4 is eating salamander
Savage-2 is eating salamander
Savage-1 is eating monkey
Savage-5 is eating salamander
Savage-3 is eating monkey
Savage-3 is waking up the cook
Cook put servings in the pot: ['salamander', 'monkey', 'human-leg', 'salamander', 'salamander']
Savage-4 is eating salamander
Savage-2 is eating salamander
Savage-1 is eating human-leg
Savage-5 is eating monkey
Savage-3 is eating salamander
Savage-3 is waking up the cook
Cook put servings in the pot: ['monkey', 'monkey', 'salamander', 'human-leg']
Savage-1 is eating human-leg
Savage-2 is eating salamander
Savage-4 is eating monkey
Savage-5 is eating monkey
Savage-5 is waking up the cook
Cook put servings in the pot: ['salamander']
Savage-3 is eating salamander
Savage-3 is waking up the cook
Cook put servings in the pot: ['human-leg', 'human-leg', 'human-leg', 'salamander']
Savage-4 is eating salamander
Savage-2 is eating human-leg
Savage-5 is eating human-leg
Savage-1 is eating human-leg
"""