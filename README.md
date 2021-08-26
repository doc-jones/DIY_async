# DIY_async

Creating low-level foundations and abstractions for asynchronous programming in Python (i.e., implementing concurrency without using threads).

### Step 1 concurrency using callback functions
What some people call "callback hell" the [async_producer.py](https://github.com/doc-jones/DIY_async/blob/main/async_producer.py) demonstrates replacing loops and threads with small callback functions that rely on the Scheduler to switch between tasks.

### Step 2 concurrency with generators
Use the yield stmt to create async/await and replace counting functions with producers and consumers.
See [yield_it.py](https://github.com/doc-jones/DIY_async/blob/main/yield_it.py) and [async-await_producer.py](https://github.com/doc-jones/DIY_async/blob/main/async-await_producer.py)
