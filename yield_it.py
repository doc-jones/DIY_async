import time
from collections import deque


class Scheduler:
    def __init__(self):
        self.ready = deque()  # Async queue
        self.current = None  # Currently executing generator

    # def new_task(self, gen):
    #     self.ready.append(gen)
    def new_task(self, coro):
        self.ready.append(coro)

    def run(self):
        while self.ready:
            self.current = self.ready.popleft()
            # Drive as a generator
            try:
                self.current.send(None)   # next(self.current)  # Together with yield this replaces callbacks in driving the code
                if self.current:
                    self.ready.append(self.current)
            except StopIteration:
                pass


sched = Scheduler()  # Background scheduler object


class Awaitable:
    def __await__(self):
        yield


def switch():
    return Awaitable()


async def countdown(n):              # keyword async require to use await
    while n > 0:
        print('Down', n)
        time.sleep(1)
        # yield
        await switch()  # Switch tasks
        n -= 1


async def countup(stop):    # keyword async require to use await
    x = 0
    while x < stop:
        print('Up', x)
        time.sleep(1)
        # yield
        await switch()      # Switch tasks
        x += 1


sched.new_task(countdown(5))
sched.new_task(countup(5))
sched.run()

# Simplifies code over using callbacks: no helper func needed, no recursion needed

# The more common use of the yield stmt in python is to feed a for loop. That's not is happening here.
# Instead we are using the Scheduler. There's a better way than the yield stmt hack - nice hack tho

# async functions create coroutines and 'send' replaces 'next'
