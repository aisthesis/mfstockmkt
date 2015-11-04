"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Get velocity data
=================
"""

import numpy as np
import pandas as pd
import pynance as pn

def up(eqdata, window=100, selection='Adj Close'):
    """
    Return a dataframe with upward velocity data.

    Parameters
    ----------
    eqdata : DataFrame
        Source data

    window : int, optional
        The window of prior sessions over which
        velocity is calculated. Defaults to 100.

    selection : str, optional
        Column of `eqdata` in which historical prices
        are specified. Defaults to 'Adj Close'.
        
    Returns
    -------
    upvel : DataFrame
    """
    outcol = 'Velocity'
    outix = eqdata.index[window:]
    upvel = pd.DataFrame(index=outix, columns=[outcol], dtype='float64')

    dayssincehigh = 0
    i = 0
    return upvel

class _MaxHeap:
    """
    Heap implementation with functionality specific to the present
    task. https://docs.python.org/2/library/heapq.html doesn't allow
    us to clear the heap just by resetting the size, so we can get
    lower overhead using our own implementation.

    Heap may not be the right data structure here. We need not only
    to have access to the highest of the last 100 days but also to
    be able to locate and eliminate the oldest session once 100 are stored.

    Moreover, for the up velocity, only a downward trend is relevant. For example,
    suppose we have:
    
     0  2.5
     1  2.4
     2  2.0
     3  2.3

    Then value 2 can never be of any use from day 3 onward.
    """
    def __init__(self, data, maxsize):
        """
        The actual heap size is always 0 on initialization,
        but the underlying array is set here to the maximum
        size to which the heap can expand.

        The dynamic heap contains only indices. The `data` field
        is expected to be the numpy `ndarray` containing price data.
        These are the values used to determine which index has
        priority.
        """
        self._content = [0] * maxsize
        self._size = 0
        self._data = data

    @staticmethod
    def _parent(i):
        return (i - 1) / 2

    @staticmethod
    def _left(i):
        return 2 * i + 1

    @staticmethod
    def _right(i):
        return 2 * i + 2

    def _reset(self, ix):
        """
        Reset the underlying array, inserting the given index
        as sole content. The size of the heap will always
        be 1 after this operation.
        """
        self._content[0] = ix
        self._size = 1

    def _exchange(self, i, j):
        tmp = self._content[i]
        self._content[i] = self._content[j]
        self._content[j] = tmp

    def _higher(self, i, j):
        """
        Return a boolean that is True iff i represents a higher
        price than j.
        In case of a price tie, the old value is greater: No new
        high has been set.
        """
        if self._data[self._content[i]] > self._data[self._content[j]]:
            return True
        if self._data[self._content[i]] == self._data[self._content[j]] and i < j:
            return True
        return False

    def _heapify(self, i):
        """
        Cf. CLRS, p. 154
        """
        l = _left(i)
        if l >= self._size:
            return
        r = _right(i)
        largest = i
        if self._higher(l, i):
            largest = l
        if r < self._size and self._higher(r, largest):
            largest = r
        if largest != i:
            self._exchange(i, largest)
            self._heapify(largest)

    def _pop(self):
        """
        Cf. CLRS, p. 163
        We don't care what the value is but only need to reorganize
        the heap, so no return value.
        """
        self._content[0] = self._content[self._size - 1]
        self._size -= 1
        self._heapify(0)

    def _increase_key(self, i, key):
        """ CLRS, p. 164 """
        self._content[i] = key
        while i > 0 and self._higher(i, _parent(i)):
            self._exchange(i, _parent(i))
            i = _parent(i)

    def peak(self):
        return self._content[0]

    def insert(self, ix):
        """
        Inserts new value and returns number of days
        since window high.
        """
        if self._data[self._content[0]] < self._data[ix]:
            self._reset(ix)
            return 0

