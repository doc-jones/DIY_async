# Examples of Async use network service(i.e., reading a web API), database retrieve

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import threading
import time


def countdown(n):
    while n > 0:
        print('Down', n)
        time.sleep(1)
        n -= 1


def countup(stop):
    x = 0
    while x < stop:
        print('Up', x)
        time.sleep(1)
        x += 1


# Sequential execution
countdown(5)
countup(5)

# Concurrent execution
# Classic solution: use threads

threading.Thread(target=countdown, args=(5,)).start()
threading.Thread(target=countup, args=(5,)).start()

# Note on threads in Python, like C they are hardware - posix threads
# the GIL (Global Interpreter Lock) prevents threads in Python from running in parallel they can only run on a single CPU
