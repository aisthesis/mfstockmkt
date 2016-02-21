"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Synchronized delay queue based on queue.PriorityQueue
(Python 3.x) or Queue.PriorityQueue (Python 2.x)

Notes
-----
The client can track retries by wrapping each item
with a parameter that counts retries:

    >>> queue.put([n_retries, item])
"""

import datetime as dt
try:
    import queue
except ImportError:
    # module name in Python 2.x
    import Queue as queue
import threading

class DelayQueue(object):

    def __init__(self, maxsize=0):
        self._queue = queue.PriorityQueue(maxsize)
        # Notify ready whenever head of queue is ready for processing;
        # a thread waiting to get is notified then
        self.ready = threading.Condition(self._queue.mutex)

    def ask(self):
        """
        How long to wait before first item in queue is ready to process.
        
        Return 0 if head of queue can be processed immediately.

        Return -1 if queue is empty.

        A call to `ask()` is needed to unblock a queue whose
        head is in the wait state.
        """
        if len(self._queue.queue) > 0:
            utcnow = dt.datetime.utcnow()
            if utcnow >= self._queue.queue[0][0]:
                self.ready.notify()
                return 0
            return (self._queue.queue[0][0] - utcnow).total_seconds()
        return -1

    def put(self, item, delay=0, block=True, timeout=None):
        if delay < 0:
            raise ValueError("'delay' must be a non-negative number")
        self._queue.put((dt.datetime.utcnow() + dt.timedelta(seconds=delay), item), block, timeout)
        if not delay:
            self.ready.notify()

    def get(self, block=True, timeout=None):
        if self.ask() > 0:
            if not block:
                raise queue.Empty
        return self._queue.get(block, timeout)

    def put_nowait(self, item, delay=0):
        return self.put(item, delay, block=False)

    def get_nowait(self):
        return self.get(block=False)

    # other methods just operate on underlying PriorityQueue
    def task_done(self):
        self._queue.task_done()

    def join(self):
        self._queue.join()

    def qsize(self):
        return self._queue.qsize()

