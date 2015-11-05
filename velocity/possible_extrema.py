"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Data structure for storing possible velocity extrema
=================
"""

class PossibleExtrema(object):
    """
    For maintaining a list of relevant indices
    """
    def __init__(self, data, window, compfn):
        """
        Circular buffer for maintaining indices of price data
        relevant for determining velocity.

        Parameters
        ---------- 
        data : ndarray
            Array containing relevant price data

        window : int
            Size of the window.

        compfn : Function
            Function used to compare 2 data values. This is passed so 
            that we can use the same class for both `up` and `down` velocity.
        """
        # we need to compare today with window + 1 values so that
        # insert() returns at most `window` and not `window - 1`
        self._WINDOW = window + 1
        self._indices = [0] * self._WINDOW
        self._data = data
        self._begin = 0
        self._size = 0
        self._compfn = compfn

    def insert(self, ix):
        insert_at = self._begin
        if self._size > 0: 
            # if begin is "expired", remove it
            if ix - self._indices[self._begin] >= self._WINDOW:
                self._begin = (self._begin + 1) % self._WINDOW
                self._size -= 1
            insert_at = self._find(ix)
        self._indices[insert_at] = ix
        days_since_extremum = ix - self._indices[self._begin]
        # new element inserted, now recalculate self._size
        if insert_at < self._begin:
            insert_at += self._WINDOW
        self._size = insert_at - self._begin + 1
        return days_since_extremum

    def _find(self, ix):
        return self._rec_find(ix, self._begin, self._size)

    def _rec_find(self, ix, begin, length):
        """ 
        Recursive find using binary search 
        `begin` is the first index to search, `length` is 1 past the end.
        """
        # base case
        if length <= 1:
            if self._compfn(self._data[ix], self._data[self._indices[begin]]):
                return begin
            return (begin + 1) % self._WINDOW
        halflen = length / 2
        middle = (begin + halflen) % self._WINDOW
        if self._compfn(self._data[ix], self._data[self._indices[middle]]):
            return self._rec_find(ix, begin, halflen)
        return self._rec_find(ix, (begin + halflen) % self._WINDOW, length - halflen)
