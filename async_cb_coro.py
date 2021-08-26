# async_cb_coro.py
#


import time
from collections import deque
import heapq


class Awaitable:
    def __await__(self):
        yield


def switch():
    return Awaitable()

# Callback based Scheduler
class Scheduler:
    def __init__(self):
        self.ready = deque()
        self.sleeping = []
        self.current = None
        self.sequence = 0

    def call_soon(self, func):
        self.ready.append(func)

    def call_later(self, delay, func):
        self.sequence += 1
        deadline = time.time() + delay
        # priority queue
        heapq.heappush(self.sleeping, (deadline, self.sequence, func))

    def run(self):
        while self.ready or self.sleeping:
            if not self.ready:
                deadline, _, func = heapq.heappop(self.sleeping)
                delta = deadline - time.time()
                if delta > 0:
                    time.sleep(delta)
                self.ready.append(func)
            while self.ready:
                func = self.ready.popleft()
                func()

    def new_task(self, coro):
        self.ready.append(Task(coro))   # Wrapped coroutine

    async def sleep(self, delay):
        self.call_later(delay, self.current)
        self.current = None
        await switch()       # Switch to a new task


class Task:
    def __init__(self, coro):
        self.coro = coro           # "Wrapped" coroutine

    # Make it look like a callback
    def __call__(self):
        try:
            # Driving the coroutine
            sched.current = self
            self.coro.send(None)
            if sched.current:
                sched.ready.append(self)

        except StopIteration:
            pass

sched = Scheduler()


class Result:
    def __init__(self, value=None, exc=None):
        self.value = value
        self.exc = exc

    def result(self):
        if self.exc:
            raise self.exc
        else:
            return self.value


class QueueClosed(Exception):
    pass


# Implement a queuing object
class AsyncQueue:
    def __init__(self):
        self.items = deque()
        self.waiting = deque()  # All getters waiting for data
        self._closed = False

    def close(self):
        self._closed = True
        if self.waiting and not self.items:
            for func in self.waiting:
                sched.call_soon(func)

    # We put something on the queue and if something is waiting then pop it off and pas to Scheduler
    def put(self, item):
        if self._closed:
            raise QueueClosed()

        self.items.append(item)
        if self.waiting:
            func = self.waiting.popleft()
            sched.call_soon(func)

    def get(self, callback):
        if self.items:
            callback(
                Result(value=self.items.popleft()))
        else:
            # No items available (must wait)
            if self._closed:
                callback(Result(exc=QueueClosed()))      # <<<<<<<<<<<<< Error result
            else:
                self.waiting.append(lambda: self.get(callback))


def producer(q, count):
    def _run(n):
        if n < count:
            print('Producing', n)
            q.put(n)
            sched.call_later(1, lambda: _run(n + 1))
        else:
            print("Producer done")
            q.close()
    _run(0)


def consumer(q):
    def _consume(result):
        try:
            item = result.result()
            print('Consuming', item)               # <<<<<<<< Queue item (Result)
            sched.call_soon(lambda: consumer(q))
        except QueueClosed:
            print('Consumer done')

    q.get(callback=_consume)


q = AsyncQueue()
sched.call_soon(lambda: producer(q, 10))
sched.call_soon(lambda: consumer(q, ))
sched.run()
