# DIY_async

Creating low-level foundations and abstractions for asynchronous programming in Python (i.e., implementing concurrency without using threads).

### Step 1 concurrency using callback functions
What some people call "callback hell" the async_producer.py demonstrates replacing loops and threads with small callback functions that rely on the Scheduler to switch between tasks.

### Step 2 concurrency with generators
