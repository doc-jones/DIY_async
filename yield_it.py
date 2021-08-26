import time
from collections import deque
import heapq


class Awaitable:
    def __await__(self):
        yield


def switch():
    return Awaitable()


class Scheduler:
    def __init__(self):
        self.ready = deque()  # Async queue
        self.sleeping = []
        self.current = None  # Currently executing generator
        self.sequence = 0

    async def sleep(self, delay):
        # The current coroutine/task wants to sleep
        deadline = time.time() + delay
        self.sequence += 1
        heapq.heappush(self.sleeping, (deadline, self.sequence, self.current))
        self.current = None
        await switch()          # Switch tasks

    # def new_task(self, gen):
    #     self.ready.append(gen)
    def new_task(self, coro):
        self.ready.append(coro)

    def run(self):
        while self.ready or self.sleeping:
            if not self.ready:             # time management exactly like the callback example.
                deadline, _, coro = heapq.heappop(self.sleeping)
                delta = deadline - time.time()
                if delta > 0:
                    time.sleep(delta)
                self.ready.append(coro)

            self.current = self.ready.popleft()
            # Drive as a generator
            try:
                self.current.send(None)   # next(self.current)  # Together with yield this replaces callbacks in driving the code
                if self.current:
                    self.ready.append(self.current)
            except StopIteration:
                pass


sched = Scheduler()  # Background scheduler object


async def countdown(n):              # keyword async require to use await
    while n > 0:
        print('Down', n)
        # time.sleep(1)
        await sched.sleep(4)  # Takes care of switching tasks
        # yield
        # await switch()  # Switch tasks
        n -= 1


async def countup(stop):    # keyword async require to use await
    x = 0
    while x < stop:
        print('Up', x)
        # time.sleep(1)
        await sched.sleep(1)  # Takes care of switching tasks
        # yield
        # await switch()      # Switch tasks
        x += 1


sched.new_task(countdown(5))
sched.new_task(countup(20))
sched.run()

# Simplifies code over using callbacks: no helper func needed, no recursion needed

# The more common use of the yield stmt in python is to feed a for loop. That's not is happening here.
# Instead we are using the Scheduler. There's a better way than the yield stmt hack - nice hack tho

# async functions create coroutines and 'send' replaces 'next'
