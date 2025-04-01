import threading


dest_barriers = {}

N = 30


def doSomeThings(): 
    print("Do some things")
def driveFromAirportToHotel(dest): 
    print("Drive from airport to hotel " + str(dest))
def doOtherThingsAndDriveBackToAirport(): 
    print("Do other things and drive back to airport")
def fly(): 
    print("Fly")
def arriveAtAirport(): 
    print("Arrive at airport")
def rideFromAirportToHotel(dest): 
    print("Ride from airport to hotel " + str(dest))

def busdriver(dest):
    global dest_barriers

    # while True:
    doSomeThings()
    # wait until all passengers are seated (TO DO)
    dest_barriers[dest].wait()

    driveFromAirportToHotel(dest)
    doOtherThingsAndDriveBackToAirport()

def tourist(dest):
    global dest_barriers

    # while True:
    fly()
    arriveAtAirport()

    # wait until all other passengers and bus driver 
    # are present (TO DO)
    dest_barriers[dest].wait()

    rideFromAirportToHotel(dest)


def subscribe_thread(target_function):#
    """Start a new thread to run the given target function."""
    thread = threading.Thread(target=target_function)
    # thread.daemon = True  # Allows program to exit even if threads are running
    thread.start()

def setup():
    global dest_barriers

    dest_barriers["destA"] = threading.Barrier(N + 1)
    # dest_barriers["destB"] = threading.Barrier(N + 1)

    for i in range(N):
        subscribe_thread(lambda: tourist("destA"))
        # subscribe_thread(lambda: tourist("destB"))

    subscribe_thread(lambda: busdriver("destA"))
    # subscribe_thread(lambda: busdriver("destB"))

setup()