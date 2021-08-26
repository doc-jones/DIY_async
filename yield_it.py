import time
from collections import deque

class Scheduler:
    def __init__(self):
        self.ready = deque()           # Async queue
        self.current = None            # Currently excuting generator

    def new_task(self, gen):
        self.ready.append(gen)

    def run(self):
        while self.ready:
            self.current = self.ready.popleft()
            # Drive as a generator
            try:
                next(self.current)    # Together with yield this replaces callbacks in driving the code
                if self.current:
                    self.ready.append(self.current)
            except StopIteration:
                pass

sched = Scheduler()          # Background scheduler object

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

sched.new_task(countdown(5))
sched.new_task(countup(5))
sched.run()
