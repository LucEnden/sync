import functools
import inspect
import random
import threading
import tkinter as tk
import tkinter.messagebox  # jg: why needed???
import time
from typing import Any, Dict, List

thread_blockable: Dict[Any, Any] = {}
breakpoints_threads: Dict[Any, Any] = {}
breakpoints_general: Dict[Any, Any] = {}
thread_index_list: Dict[Any, Any] = {}
threads_nrof: int = 0
lines_nrof: int = 0
subscribed_threads: List[Any] = []
subscribed_objects: List[Any] = []
block_step = Any
speed = Any

gui = Any


def getCallerInfo():
    # the request has to be interpreted from the caller's point of view
    # so in this function, it's the grand-caller
    # aaa()             ->   bbb()       ->   ccc() ->   getCallerInfo()
    # ^ great-grand-caller   ^ grand-caller   ^ caller   ^ we are here
    # we want to know the lino of ccc's call inside bbb()
    frame = inspect.currentframe()  # here
    frame = frame.f_back            # caller
    frame = frame.f_back            # grand-caller
    filename, lineno, function, code_context, index = inspect.getframeinfo(frame)
    return filename, lineno


class MySemaphore(threading.Semaphore):
    """ semaphore to be used in a DUT """
    def __init__(self, val=0, name="? (SZN)"):
        threading.Semaphore.__init__(self, val)
        self._name = name
        subscribed_objects.append(self)

    def __str__(self):
        return 'sem  {:20}: {:1}\n'.format(self._name, self.get_value())

    def get_value(self):
        # for debug/gui purposes only!
        return self._value

    def wait(self):
        _blk(getCallerInfo())
        self.acquire()
        gui.show_subscriptions(subscribed_objects)

    def signal(self, n=1):
        _blk(getCallerInfo())
        for i in range(n):
            self.release()
        gui.show_subscriptions(subscribed_objects)


class MyMutex(object):  # jg: inheritance from threading.Lock doesn't work; why???
    """ mutex to be used in a DUT """

    def __init__(self, name="? (MZN)"):
        # threading.Semaphore.__init__(self)
        self._name = name
        self._lock = threading.Lock()  # composition instead of inheritance
        self.avail = True
        # only for gui-show (JG: how to get the status (locked/unlocked) from the Lock-object
        # itself? (instead of maintaining explicitly))
        subscribed_objects.append(self)

    def __str__(self):
        return 'mux  {:20}: {}\n'.format(self._name, self.avail)

    def wait(self):
        _blk(getCallerInfo())
        self._lock.acquire()
        self.avail = False
        gui.show_subscriptions(subscribed_objects)

    def signal(self):
        _blk(getCallerInfo())
        self.avail = True
        self._lock.release()
        gui.show_subscriptions(subscribed_objects)


class MyLightswitch(object):
    """ lightswitch to be used in a DUT (see LBoS, par 4.2.2) """

    def __init__(self, sem, name="? (LZN)"):
        # threading.Semaphore.__init__(self)
        self._name = name
        self._mutex = MyMutex()
        self._sem = sem
        self._counter = 0
        subscribed_objects.append(self)

    def __str__(self):
        return 'lsw  {:20}: mu:{},se:{},#:{}\n'.format(self._name, self._mutex.avail, self._sem.get_value(),
                                                       self._counter)

    def lock(self, sem):
        _blk(getCallerInfo())
        if not self._sem == sem:
            tk.messagebox.showinfo('Lightswitch violation in wait()',
                                   'modified sem in {}'.format(threading.get_ident(), self))
        self._mutex.wait()
        self._counter += 1
        if self._counter == 1:
            self._sem.wait()
        self._mutex.signal()
        gui.show_subscriptions(subscribed_objects)

    def unlock(self, sem):
        _blk(getCallerInfo())
        if not self._sem == sem:
            tk.messagebox.showinfo('Lightswitch violation in signal()',
                                   'modified sem in {}'.format(threading.get_ident(), self))
        self._mutex.wait()
        self._counter -= 1
        if self._counter == 0:
            self._sem.signal()
        self._mutex.signal()
        gui.show_subscriptions(subscribed_objects)


class MyConditionVariable(object):
    """ condition variable to be used in a DUT """

    def __init__(self, mutex, name="? (CZN)"):
        self._name = name
        self._condvar = threading.Condition(mutex._lock)
        self._mutex = mutex
        subscribed_objects.append(self)

    def __str__(self):
        return 'con  {:20}: {}\n'.format(self._name, "...")

    def wait(self):
        _blk(getCallerInfo())
        self._condvar.wait()
        gui.show_subscriptions(subscribed_objects)

    def notify(self):
        _blk(getCallerInfo())
        self._condvar.notify()
        gui.show_subscriptions(subscribed_objects)

    def notify_all(self):
        _blk(getCallerInfo())
        self._condvar.notify_all()
        gui.show_subscriptions(subscribed_objects)


class MyBarrier(threading.Barrier):
    """ barrier to be used in a DUT """

    def __init__(self, val=0, name="? (BZN)"):
        threading.Barrier.__init__(self, val)
        self._name = name
        self._parties = val
        subscribed_objects.append(self)

    def __str__(self):
        return 'bar  {:20}: {:1}/{}\n'.format(self._name, self.n_waiting, self._parties)

    def wait(self):
        _blk(getCallerInfo())
        threading.Barrier.wait(self)
        gui.show_subscriptions(subscribed_objects)


class MyInt(object):
    """ integer to be used in a DUT """

    def __init__(self, val=0, name="? (IZN)"):
        self.v = val
        self._name = name
        subscribed_objects.append(self)

    def __str__(self):
        return 'int  {:20}: {:1}\n'.format(self._name, self.v)


class MyString(object):
    """ string to be used in a DUT """

    def __init__(self, val, name="? (SZN)"):
        self.v = val
        self._name = name
        subscribed_objects.append(self)

    def __str__(self):
        return 'str  {:20}: {:1}\n'.format(self._name, self.v)


class MyBool(object):
    def __init__(self, val=False, name="? (bZN)"):
        self.v = val
        self._name = name
        subscribed_objects.append(self)

    def __str__(self):
        return 'bool {:20}: {}\n'.format(self._name, str(self.v))


class MyFifo(object):
    """ thread-UNsafe FIFO (on purpose) """
    def __init__(self, size, name="? (FZN)"):
        self._max = size
        self._name = name
        self._data = []
        subscribed_objects.append(self)

    def size(self):
        return len(self._data)

    def peek(self):
        if len(self._data) == 0:
            return None
        return self._data[0]

    def get(self):
        return self._data.pop(0)

    def put(self, val):
        if self.size() == self._max:
            raise Exception("FIFO overflow for '{}': {}".format(val, self))
        return self._data.append(val)

    def __str__(self):
        if len(self._data) == 0:
            s = ""
        else:
            s = functools.reduce(lambda a, b: a + "," + b, self._data)
        return 'fif  {:20}: {}/{} [ {} ]\n'.format(self._name, self.size(), self._max, s)


class MyBag(object):
    # thread UN-safe bag (on purpose)
    def __init__(self, size=5, name="? (BZN)"):
        self._max = size
        self._name = name
        self._data = []
        subscribed_objects.append(self)

    def size(self):
        return len(self._data)

    def contains(self, val):
        return not self._data.count(val) == 0

    def get(self, val):
        if not self.contains(val):
            raise Exception("Bag get() for '{}': {}".format(val, self))
        return self._data.remove(val)

    def put(self, val):
        if self.size() == self._max:
            raise Exception("Bag overflow for '{}': {}".format(val, self))
        return self._data.append(val)

    def __str__(self):
        if len(self._data) == 0:
            s = ""
        else:
            s = functools.reduce(lambda a, b: a + "," + b, self._data)
        return 'bag  {:20}: {}/{} [ {} ]\n'.format(self._name, self.size(), self._max, s)


# local statics for thread_wrapper
thread_index_counter = 0
thread_index_mutex = threading.Lock()


def thread_wrapper(function):
    global thread_index_counter, thread_index_mutex
    # get its thread-id (not available when the thread is created; only when the thread is started)
    # and then get the (next available) index
    thread_id = threading.get_ident()
    thread_index_mutex.acquire()
    index = thread_index_counter
    thread_index_list[thread_id] = thread_index_counter
    thread_index_counter += 1
    print("thread:", threading.get_ident(), index)
    thread_index_mutex.release()
    # do the actual work:
    function()


def subscribe_thread(function):
    global threads_nrof
    t = threading.Thread(target=lambda: thread_wrapper(function))
    subscribed_threads.append(t)
    threads_nrof += 1


gim = threading.Lock()


def _blk(file_line=None):
    global subscribed_objects
    if file_line is None:
        file_line = getCallerInfo()
    file_name = file_line[0]
    line_nbr = file_line[1]
    if "Environment" in file_name:
        # _blk()-call comes from Environment.py: to be skipped!
        return
    thread_index = get_thread_index()

    gui.show_subscriptions(subscribed_objects)
    gui.buttonActivate(thread_index, line_nbr)
    # print(">> brk:", thread_index, line_nbr, thread_is_blockable(thread_index))
    while thread_is_blockable(thread_index):
        wait_during_block()
        # only jump out of the busy-waiting loop when:
        # - not in blocking mode
        # - not trapped in a breakpoint
        # - random change of 33%
        if not block_step.get() and random.randint(1, 3) == 1 and not is_breakpoint(thread_index, line_nbr):
            break
    # print("<< brk:", thread_index, line_nbr, thread_is_blockable(thread_index))
    gui.show_subscriptions(subscribed_objects)
    gui.buttonDeactivate(thread_index, line_nbr)
    thread_set_blockable(thread_index)


def run_threads():
    for t in subscribed_threads:
        t.start()


def get_thread_index():
    global thread_index_list
    thread_id = threading.get_ident()
    return thread_index_list[thread_id]


def thread_is_blockable(thread_index):
    return thread_blockable[thread_index]


def thread_set_blockable(thread_index):
    thread_blockable[thread_index] = True


def thread_clear_blockable(thread_index):
    thread_blockable[thread_index] = False


def wait_during_block():
    global speed
    time.sleep(random.random() / (pow(2, speed.get())))


def is_breakpoint(thread_index, line_nbr):
    return breakpoints_threads[thread_index][line_nbr].get()


class Gui:

    def __init__(self, filename):
        global threads_nrof, lines_nrof
        # print("Gui()", threading.get_ident())
        global block_step, speed

        self.root = tk.Tk()

        block_step = tk.IntVar(value=1)     # initially: on
        speed = tk.IntVar()                 # initially: slow

        self.root.title("Sync Simulator")
        self.root.rowconfigure(0, minsize=900, weight=1)
        self.root.columnconfigure(3, minsize=500, weight=1)
        self.root.columnconfigure(4, minsize=100, weight=1)

        self.txt_source = tk.Text(self.root)
        self.txt_variables = tk.Text(self.root)
        self.frm_control = tk.Frame(self.root, relief=tk.RAISED, bd=1)
        self.frm_blocking = tk.Frame(self.root, relief=tk.RAISED, bd=1)

        btn_quit = tk.Button(self.frm_control, text="Quit", command=self.root.quit)
        btn_run = tk.Button(self.frm_control, text="Run", command=run_threads)

        cb_block_step = tk.Checkbutton(self.frm_control, text='block at _blk()', variable=block_step,
                                       onvalue=1, offvalue=0)

        sld_speed = tk.Scale(self.frm_control, variable=speed, from_=0, to=8, orient=tk.HORIZONTAL)
        # width is used to make enough room for the check-boxes
        lbl = tk.Label(self.frm_blocking, text="   ", height=0, width=threads_nrof * 2 + 4)

        self.pixelVirtual = tk.PhotoImage(width=1, height=1)

        btn_quit.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        btn_run.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        cb_block_step.grid(row=2, column=0, sticky="ew")
        sld_speed.grid(row=3, column=0, sticky="ew")

        lbl.grid(row=0, column=0, sticky="sew", padx=2 * threads_nrof + 2)

        self.frm_control.grid(row=0, column=0, sticky="ns")
        self.frm_blocking.grid(row=0, column=1, sticky="ns")
        self.txt_source.grid(row=0, column=2, sticky="nsew")
        self.txt_variables.grid(row=0, column=3, sticky="nsew")

        self.txt_variables.insert(tk.END, "variables will be listed here")
        self.mutex_print = threading.Lock()

        self.btn_block_thread = {}
        self.cb_break_thread_line = {}
        self.cb_break__general__line = {}
        self.breakpoints_general_line_IntVar = {}

        lines_nrof, self.breakable_line_nbr_list = self.read_file(filename)

        self.create_btn_block_all()
        self.create_cb_general_all()
        self.create_cb_breakpoints(threads_nrof, self.breakable_line_nbr_list)

    def read_file(self, filepath=None):
        self.txt_source.delete(1.0, tk.END)
        curr_line_nbr = 0
        breakable_line_nbr_list = []
        with open(filepath, "r") as input_file:
            org_line = input_file.readline()
            while org_line:
                curr_line_nbr += 1
                if (
                        "_blk" in org_line or "wait" in org_line or "signal" in org_line or "notify" in org_line or
                        "lock" in org_line or "unlock" in org_line
                ) and "(" in org_line and ")" in org_line:
                    breakable_line_nbr_list.append(curr_line_nbr)
                line = '{:2}: '.format(curr_line_nbr)
                self.txt_source.insert(tk.END, line + org_line)
                org_line = input_file.readline()
        self.root.title(f"Sync Simulator - {filepath}")
        return curr_line_nbr, breakable_line_nbr_list

    def show_subscriptions(self, subscriptions):
        self.mutex_print.acquire()
        self.txt_variables.delete(1.0, tk.END)
        for v in subscriptions:
            self.txt_variables.insert(tk.END, v)
        self.mutex_print.release()

    def mainloop(self):
        self.root.mainloop()

    def create_btn_block_all(self):
        for t in range(threads_nrof):
            self.create_btn_block_thread(t)

    def create_btn_block_thread(self, t):
        self.btn_block_thread[t] = tk.Button(self.frm_blocking, text="+",
                                             command=lambda: self.clickButton_thread(t),
                                             image=self.pixelVirtual,
                                             compound="c", height=6, width=6)
        self.btn_block_thread[t].place(x=3 + 18 * t, y=1)
        thread_set_blockable(t)

    def create_cb_general_all(self):
        for n in self.breakable_line_nbr_list:
            self.create_cb_general(n)

    def create_cb_general(self, n):
        if not (n in self.breakpoints_general_line_IntVar.keys()):
            self.breakpoints_general_line_IntVar[n] = tk.IntVar()
            self.cb_break__general__line[n] = tk.Checkbutton(self.frm_blocking, image=self.pixelVirtual,
                                                             command=lambda: self.click_cb_general(n),
                                                             variable=self.breakpoints_general_line_IntVar[n],
                                                             height=6, width=6, bd=0, padx=0, pady=0)
            self.cb_break__general__line[n].place(x=18 * threads_nrof + 10, y=16 * n - 16)

    def create_cb_thread_line(self, t, n):
        # add a breakpoint for a line only once
        if not (n in breakpoints_threads[t].keys()):
            breakpoints_threads[t][n] = tk.IntVar()
            self.cb_break_thread_line[t][n] = tk.Checkbutton(self.frm_blocking, image=self.pixelVirtual,
                                                             variable=breakpoints_threads[t][n],
                                                             height=6, width=6, bd=0, padx=0, pady=0)
            self.cb_break_thread_line[t][n].place(x=18 * t, y=16 * n - 16)

    def create_cb_breakpoints(self, t_nrof, breakable_line_nbr_list):
        for t in range(t_nrof):
            self.cb_break_thread_line[t] = {}
            breakpoints_threads[t] = {}
            for n in breakable_line_nbr_list:
                self.create_cb_thread_line(t, n)

    def clickButton_thread(self, t):
        # print("cbt", threading.get_ident(), t)
        thread_clear_blockable(t)

    def click_cb_general(self, n):
        # print("cbt", threading.get_ident(), n)
        for i in range(threads_nrof):
            breakpoints_threads[i][n].set(self.breakpoints_general_line_IntVar[n].get())

    def buttonActivate(self, t, n):
        for z in self.cb_break_thread_line[t].keys():
            self.cb_break_thread_line[t][z].configure(bg="white", selectcolor="white")

        self.btn_block_thread[t]["state"] = "active"
        self.btn_block_thread[t]["text"] = "+"
        self.cb_break_thread_line[t][n].configure(bg="white", selectcolor="red")

    def buttonDeactivate(self, t, n):
        self.btn_block_thread[t]["state"] = "disabled"
        self.btn_block_thread[t]["text"] = "o"
        self.cb_break_thread_line[t][n].configure(bg="white", selectcolor="yellow")


def GuiCreate(filename):
    global gui
    gui = Gui(filename)


def GuiMainloop():
    gui.mainloop()
