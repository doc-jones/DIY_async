import time

def countdown(n):
    while n > 0:
        print('Down', n)
        time.sleep(1)
        yield
        n -= 1

def countup(stop):
    x = 0
    while x < stop:
        print('Up', x)
        time.sleep(1)
        yield
        x += 1
