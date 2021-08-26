# async-await_producer.py
# using the same scheduler, sleep and run methods as from yield_it.py
# async-await in python is just the masking of the yield cmd.

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

#  --------------------------------------------------------------


def producer(q, count):
    for n in range(count):
        print('Producing', n)
        q.put(n)
        time.sleep(1)

    print("Producer done")
    q.put(None)  # 'sentinel' to shut down


def consumer(q):
    while True:
        item = q.get()
        if item is None:
            break
        print('Consuming', item)
    print('Consumer done')


q = queue.Queue()    # Thread safe queue
threading.Thread(target=producer, args=(q, 10)).start()
threading.Thread(target=consumer, args=(q,)).start()
