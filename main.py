# DIY Async

# Examples of Async use network service(i.e., reading a web API), database retrieve

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# def countdown(n):
#     while n > 0:
#         print('Down', n)
#         time.sleep(1)
#         n -= 1
#
#
# def countup(stop):
#     x = 0
#     while x < stop:
#         print('Up', x)
#         time.sleep(1)
#         x += 1


# Sequential execution
# countdown(5)
# countup(5)

# Concurrent execution
# Classic solution: use threads
# import threading
#
# threading.Thread(target=countdown, args=(5,)).start()
# threading.Thread(target=countup, args=(5,)).start()

# Note on threads in Python, like C they are hardware - posix threads
# the GIL (Global Interpreter Lock) prevents threads in Python from running in parallel they can only run on a single CPU


# Let's say we don't have threads - How do you get concurrency if you don't have threads?
# Why do it? - answers: scaling, control - can't kill threads once they're started, no cancellation
# Issue: Figure out how to switch between tasks.
# Have to figure out how to interrupt the loops
# Scheduling of callback funcs


import time
from collections import deque
import heapq


class Scheduler:
    def __init__(self):
        self.ready = deque()  # Functions ready to execute
        self.sleeping = []  # Sleeping functions
        self.sequence = 0   # sequence number avoids case when deadlines are identical

    def call_soon(self, func):
        self.ready.append(func)

    def call_later(self, delay, func):
        self.sequence += 1
        deadline = time.time() + delay  # Expiration time
        # priority queue
        heapq.heappush(self.sleeping, (deadline, self.sequence, func))

        # self.sleeping.append((deadline, func))
        # self.sleeping.sort()   # Sort by closest deadline

    def run(self):
        while self.ready or self.sleeping:
            if not self.ready:
                # Find the nearest deadline
                # Use of heapq is more efficient and includes the sorting bit
                deadline, _, func = heapq.heappop(self.sleeping)
                # deadline, func = self.sleeping.pop(0)
                delta = deadline - time.time()
                if delta > 0:
                    time.sleep(delta)
                self.ready.append(func)
            while self.ready:
                func = self.ready.popleft()
                func()


sched = Scheduler()  # Behind the scenes scheduler object


# Basically implemented a recursive func call backed by the Scheduler thing
def countdown(n):
    if n > 0:
        print('Down', n)
        # time.sleep(4)  # Blocking call (nothing else can run until sleep finishes)
        sched.call_later(4, lambda: countdown(n - 1))


# sched.call_soon(lambda: countdown(5))
# sched.run()


def countup(stop, x=0):  # make x a default arg because it's carrying internal state
    def _run(x) -> object:  # replace x as default arg by recursively calling _run
        if x < stop:
            print('Up', x)
            # time.sleep(1)  Also switch from call_soon to call_later
            sched.call_later(1, lambda: _run(x + 1))

    _run(0)


sched.call_soon(lambda: countdown(5))
sched.call_soon(lambda: countup(20))  # arg of 5 to 20 since up is running much faster than down
sched.run()
