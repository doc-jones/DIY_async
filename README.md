# DIY Async I/O

Creating low-level foundations and abstractions for asynchronous programming in Python (i.e., implementing concurrency without using threads).

### Step 0 concurrency with threads
Note on threads in Python, like C they are hardware - posix threads the GIL (Global Interpreter Lock) prevents threads in Python from running in parallel they can only run on a single CPU

### Step 1 concurrency using callback functions
What some people call "callback hell" the [async_producer.py](https://github.com/doc-jones/DIY_async/blob/main/async_producer.py) demonstrates replacing loops and threads with small callback functions that rely on the Scheduler to switch between tasks.

### Step 2 concurrency with coroutines driven by generator
Use the yield stmt to create async/await and replace counting functions with producers and consumers.
See [yield_it.py](https://github.com/doc-jones/DIY_async/blob/main/yield_it.py) and [async-await_producer.py](https://github.com/doc-jones/DIY_async/blob/main/async-await_producer.py)

### Step 3 concurrency combining callbacks and coroutines
Async IO in Python combines the models demonstrated in Step1 and Step 2. This is done using coroutines on top of a callback based Scheduler.


## Usage
Each file is an executable.

In order of programming model progressing to final example which combines a callback based Scheduler and coroutines which in turn enables the lib to be used with either callback or coroutine I/O solutions.

1. **Threads:** threads_expl.py, add producer/consumer to threads: producer.py
2. **Scheduler:** recursive callbacks in func - main.py
3. **Yield and wrapped yield:** yield_it.py
4. **Queue and Result:** async_producer.py and a_pro_clean.py
5. **__await__:** async_await_producer.py
6. **Combine callback Scheduler and Task wrapped coroutines:** async_cb_coro.py
7. **Add I/O tcp_server:** async_io.py
