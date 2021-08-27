# async_io.py
#
# An example of how to implement coroutine based concurrency layered
# on top of a callback-based scheduler.


import time
from collections import deque
import heapq
from select import select

# Callback based scheduler (from earlier)
class Scheduler:
    def __init__(self):
        self.ready = deque()  # Functions ready to execute
        self.current = None
        self.sleeping = []       # Sleeping functions
        self.sequence = 0
        self._read_waiting = {}
        self._write_waiting = {}

    def call_soon(self, func):
        self.ready.append(func)

    def call_later(self, delay, func):
        self.sequence += 1
        deadline = time.time() + delay     # Expiration time
        # Priority queue
        heapq.heappush(self.sleeping, (deadline, self.sequence, func))

    def read_wait(self, fileno, func):
        # Trigger func() when fileno is readable
        self._read_waiting[fileno] = func

    def write_wait(self, fileno, func):
        # Trigger func() while fileno is writeable
        self._write_waiting[fileno] = func

    def run(self):
        while self.ready or self.sleeping or self._read_waiting or self._write_waiting:
            if not self.ready:
                # Find the nearest deadline
                if self.sleeping:
                    deadline, _, func = self.sleeping[0]
                    timeout = deadline - time.time()
                    if timeout < 0:
                        timeout = 0
                else:
                    timeout = None    # Wait forever
                # Wait for I/O (and sleep)
                can_read, can_write, _ = select(self._read_waiting,
                                                self._write_waiting, [], timeout)

                for file_descriptor in can_read:
                    self.ready.append(self._read_waiting.pop(file_descriptor))

                for file_descriptor in can_write:
                    self.ready.append(self._write_waiting.pop(file_descriptor))

                # Check for sleeping tasks
                now = time.time()
                while self.sleeping:
                    if now > self.sleeping[0][0]:
                        self.ready.append(heapq.heappop(self.sleeping[2]))
                    else:
                        break

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

    async def recv(self, sock, maxbytes):
        self.read_wait(sock, self.current)
        self.current = None
        await switch()
        return sock.recv(maxbytes)

    async def send(self, sock, data):
        self.write_wait(sock, self.current)
        self.current = None
        await switch()
        return sock.send(data)

    async def accept(self, sock):
        self.read_wait(sock, self.current)
        self.current = None
        await switch()
        return sock.accept()


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

from socket import *


async def tcp_server(addr):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(addr)
    sock.listen(1)
    while True:
        client, addr = await sched.accept(sock)
        sched.new_task(echo_handler(client))


async def echo_handler(sock):
    while True:
        data = await sched.recv(sock, 10000)
        if not data:
            break
        await sched.send(sock, b'Got:' + data)
    print('Connection closed')
    sock.close()

sched.new_task(tcp_server(('', 3000)))
sched.run()
