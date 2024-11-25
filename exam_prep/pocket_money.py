#region Assignment
import random
import threading

# The synchronization of the threads is not yet implemented. It is your task to implement it. 
# Make sure to also add any required variables or synchronization primitives. If needed you may add additional methods as well.

# Make your application as efficient as possible (avoid busy waiting, or unnecessary blocking or waking up of threads).
# Hint: consider using one or more conditions in your solution (in addition to other synchronization primitives and variables).

#endregion

# shared variables
father_money = 0    #MyInt(0, "fatherMoney")
salary = 0          #MyInt(0, "salary")
pocket_money = 30   #MyInt(30, "pocketMoney")

# We are not tasked with making the implementation fair. Never is it stated that each kid should wait until all the other kids have gotten their pocket money.
# Creating a solution that does not care about fairness would mean we could just use a single semaphore to block any given child from aquiering pocket money as soon as fatherMoney < pocketMoney
# For a more fair implementation I would use the turnstile pattern, where each child waits until all the other children have had pocket money
child_waiting_sema = threading.Semaphore(0)
father_money_mutex = threading.Semaphore(1)

# Demo stuff
should_run = True
father_stopped = 0
father_stopped_mutex = threading.Semaphore(1)
children_stopped = 0
children_stopped_mutex = threading.Semaphore(1)
pocket_money_gift_count = 0
total_money_earned = 0

def father():
    global father_money, pocket_money, father_money_mutex, should_run, father_stopped, father_stopped_mutex, salary, child_waiting_sema, total_money_earned

    while should_run:
        if child_waiting_sema._value <= 0 and father_money > pocket_money:
            child_waiting_sema.release()

        salary = random.randrange(500, 1000, 1)
        # salary between 500 and 1000 euro

        father_money_mutex.acquire()
        # start of critical section
        father_money += salary
        total_money_earned += salary
        # end of critical section
        father_money_mutex.release()

    # Signal father has stopped for demo purposes
    father_stopped_mutex.acquire()
    father_stopped += 1
    father_stopped_mutex.release()

def child():
    global father_money, father_money_mutex, should_run, children_stopped, children_stopped_mutex, pocket_money, pocket_money_gift_count, child_waiting_sema

    while should_run:
        # Lock child if father does not have enough money
        # This also prevents father money from dropping bellow 0
        if father_money < pocket_money:
            child_waiting_sema.acquire()

        father_money_mutex.acquire()
        # start of critical section
        father_money -= pocket_money
        pocket_money_gift_count += 1 # For demo purposes
        # end of critical section
        father_money_mutex.release()

    # Signal child has stopped for demo purposes
    children_stopped_mutex.acquire()
    children_stopped += 1
    children_stopped_mutex.release()


#region Setup
def subscribe_thread(target_function):#
    """Start a new thread to run the given target function."""
    thread = threading.Thread(target=target_function)
    thread.daemon = True  # Allows program to exit even if threads are running
    thread.start()
    

def setup():
    # start father thread
    subscribe_thread(father)

    # Start 10 child threads
    for _ in range(10):
        subscribe_thread(child)

try:
    setup()

    user_input = ""
    while user_input.lower() != 'stop':
        user_input = input("Type 'stop' to end the program: ")
        if user_input.lower() == 'stop':
            should_run = False

    # Wait for threads to finish
    while not children_stopped == 10 and father_stopped == 1:
        pass
except Exception as e:
    print("Some error", e)
finally:
    print(f"Father's remaining money:  {father_money}")
    print(f"Pocket money gift count:   {pocket_money_gift_count}")
    print(f"Total pocket money gifted: {pocket_money_gift_count * pocket_money}")
    print(f"Total salary earned:       {total_money_earned}")

    total_gifted = pocket_money_gift_count * pocket_money
    print(total_money_earned > total_gifted)
#endregion