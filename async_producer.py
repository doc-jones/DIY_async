# async_producer.py
#
# Implement same functionality as producer.py but without threads


import time
from collections import deque
import heapq


class Scheduler:
    def __init__(self):
        self.ready = deque()  # Functions ready to execute
        self.sleeping = []  # Sleeping functions
        self.sequence = 0  # sequence number avoids case when deadlines are identical

    def call_soon(self, func):
        self.ready.append(func)

    def call_later(self, delay, func):
        self.sequence += 1
        deadline = time.time() + delay  # Expiration time
        # priority queue
        heapq.heappush(self.sleeping, (deadline, self.sequence, func))

    def run(self):
        while self.ready or self.sleeping:
            if not self.ready:
                deadline, _, func = heapq.heappop(self.sleeping)
                # deadline, func = self.sleeping.pop(0)
                delta = deadline - time.time()
                if delta > 0:
                    time.sleep(delta)
                self.ready.append(func)
            while self.ready:
                func = self.ready.popleft()
                func()


sched = Scheduler()


# -------------------------------------------------------

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
        self._closed = False  # Can queue be used anymore?

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
            # Do we call it right away?
            # func() -----> not a good idea as might get deep calls, recursion, etc.
            sched.call_soon(func)

    def get(self, callback):
        # Wait until an item is available. Then return it.
        if self.items:
            callback(
                Result(value=self.items.popleft()))  # Trigger a callback if data is available, still runs if "closed"
        else:
            # No items available (must wait)
            if self._closed:
                callback(Result(exc=QueueClosed()))  # Error result
            else:
                self.waiting.append(lambda: self.get(callback))  # no data arrange to execute later


def producer(q, count):
    # Can't use this for loop as it will block until complete - anti async
    # for n in range(count):
    #     print('Producing', n)
    #     q.put(n)
    #     time.sleep(1)
    def _run(n):
        if n < count:
            print('Producing', n)
            q.put(n)
            sched.call_later(1, lambda: _run(n + 1))
        else:
            print("Producer done")
            q.close()  # No more items will be produced
            # q.put(None)  # 'sentinel' to shut down

    _run(0)


def consumer(q):
    # def _consume(item):          # This is the callback
    def _consume(result):
        try:
            item = result.result()
            # if item is None:              # <<<<<<< Queue closed check (Error)
            #     print('Consumer done')
            # else:
            print('Consuming', item)  # <<<<<<<< Queue item (Result)
            sched.call_soon(lambda: consumer(q))
        except QueueClosed:
            print('Consumer done')

    q.get(callback=_consume)


q = AsyncQueue()
sched.call_soon(lambda: producer(q, 10))
sched.call_soon(lambda: consumer(q, ))
sched.run()

#     while True:
#         item = q.get()  # PROBLEM HERE: .get() waiting
#         if item is None:
#             break
#         print('Consuming', item)
#     print('Consumer done')
#
#
# q = queue.Queue()  # Thread safe queue
# threading.Thread(target=producer, args=(q, 10)).start()
# threading.Thread(target=consumer, args=(q,)).start()
