# async_cb_coro.py
#
# An example of how to implement coroutine based concurrency layered
# on top of a callback-based scheduler.


import time
from collections import deque
import heapq

# Callback based scheduler (from earlier)
class Scheduler:
    def __init__(self):
        self.ready = deque()     # Functions ready to execute
        self.sleeping = []       # Sleeping functions
        self.sequence = 0

    def call_soon(self, func):
        self.ready.append(func)

    def call_later(self, delay, func):
        self.sequence += 1
        deadline = time.time() + delay     # Expiration time
        # Priority queue
        heapq.heappush(self.sleeping, (deadline, self.sequence, func))

    def run(self):
        while self.ready or self.sleeping:
            if not self.ready:
                # Find the nearest deadline
                deadline, _, func = heapq.heappop(self.sleeping)
                delta = deadline - time.time()
                if delta > 0:
                    time.sleep(delta)
                self.ready.append(func)

            while self.ready:
                func = self.ready.popleft()
                func()

    # Coroutine-based functions
    def new_task(self, coro):
        self.ready.append(Task(coro))   # Wrapped coroutine

    async def sleep(self, delay):
        self.call_later(delay, self.current)
        self.current = None
        await switch()   # Switch to a new task

# Class that wraps a coroutine--making it look like a callback
class Task:
    def __init__(self, coro):
        self.coro = coro        # "Wrapped coroutine"

    # Make it look like a callback
    def __call__(self):
        try:
            # Driving the coroutine as before
            sched.current = self
            self.coro.send(None)
            if sched.current:
                sched.ready.append(self)
        except StopIteration:
            pass

class Awaitable:
    def __await__(self):
        yield

def switch():
    return Awaitable()

sched = Scheduler()    # Background scheduler object

# ----------------

class AsyncQueue:
    def __init__(self):
        self.items = deque()
        self.waiting = deque()

    async def put(self, item):
        self.items.append(item)
        if self.waiting:
            sched.ready.append(self.waiting.popleft())

    async def get(self):
        if not self.items:
            self.waiting.append(sched.current)   # Put myself to sleep
            sched.current = None        # "Disappear"
            await switch()              # Switch to another task
        return self.items.popleft()

# Coroutine-based tasks
async def producer(q, count):
    for n in range(count):
        print('Producing', n)
        await q.put(n)
        await sched.sleep(1)

    print('Producer done')
    await q.put(None)   # "Sentinel" to shut down

async def consumer(q):
    while True:
        item = await q.get()
        if item is None:
            break
        print('Consuming', item)
    print('Consumer done')

q = AsyncQueue()
sched.new_task(producer(q, 10))
sched.new_task(consumer(q))

# Call-back based tasks
def countdown(n):
    if n > 0:
        print('Down', n)
        # time.sleep(4)    # Blocking call (nothing else can run)
        sched.call_later(4, lambda: countdown(n-1))

def countup(stop):
    def _run(x):
        if x < stop:
            print('Up', x)
            # time.sleep(1)
            sched.call_later(1, lambda: _run(x+1))
    _run(0)


sched.call_soon(lambda: countdown(5))
sched.call_soon(lambda: countup(20))
sched.run()
