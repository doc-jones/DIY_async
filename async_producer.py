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

# Implement a queuing object
class AsyncQueue:
    def __init__(self):
        self.items = deque()
        self.waiting = deque()  # All getters waiting for data

# We put something on the queue and if something is waiting then pop it off and pas to Scheduler
    def put(self, item):
        self.items.append(item)
        if self.waiting:
            func = self.waiting.popleft()
            # Do we call it right away?
            # func() -----> not a good idea as might get deep calls, recursion, etc.
            sched.call_soon(func)

    def get(self, callback):
        # Wait until an item is available. Then return it.
        if self.items:
            callback(self.items.popleft())  # Trigger a callback if data is available
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
            sched.call_later(1, lambda: _run(n+1))
        else:
            print("Producer done")
            q.put(None)  # 'sentinel' to shut down

    _run(0)


def consumer(q):
    def _consume(item):
        if item is None:
            pass
        else:
            print('Consuming', item)
            sched.call_soon(lambda: consumer(q))
    q.get(callback=_consume())


q = AsyncQueue()
sched.call_soon(lambda: producer(q, 10))
sched.call_soon(lambda: consumer(q,))
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
