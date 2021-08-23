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

    def put(self, item):
        self.items.append(item)

    def get(self):
        # Wait until an item is available. Then return it.
        pass


def producer(q, count):
    for n in range(count):
        print('Producing', n)
        q.put(n)
        time.sleep(1)

    print("Producer done")
    q.put(None)  # 'sentinel' to shut down


def consumer(q):
    while True:
        item = q.get()  # PROBLEM HERE: .get() waiting
        if item is None:
            break
        print('Consuming', item)
    print('Consumer done')


q = queue.Queue()  # Thread safe queue
threading.Thread(target=producer, args=(q, 10)).start()
threading.Thread(target=consumer, args=(q,)).start()
