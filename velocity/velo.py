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

class _CircArr(object):
    """
    For maintaining a list of relevant indices
    """
    def __init__(self, data, window, compfn):
        """
        Circular array for maintaining indices of price data
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
        self._indices = [0] * window
        self._window = window
        self._data = data
        self._begin = -1
        self._size = 0
        self._compfn = compfn

    def _reset(self, ix):
        self._begin = 0
        self._size = 1
        self._indices[0] = ix

    def insert(self, ix):
        if self._size == 0:
            self._begin = ix
            self._size = 1
            return
        if ix - self._indices[self._begin] >= self._window:
            # TODO
        insert_at = self._find(ix)

    def _find(self, ix):
        return self._rec_find(ix, self._begin, self._size)

    def _rec_find(self, ix, begin, length):
        """ 
        Recursive find using binary search 
        `begin` is the first index to search, `length` is 1 past the end.
        """
        # base case
        if length <= 1:
            if self._compfn(self._data[ix], self._data[begin]):
                return begin
            return (begin + 1) % self._window
        halflen = length / 2
        middle = (begin + halflen) % self._window
        if self._compfn(self._data[ix], self._data[middle]):
            return self._rec_find(ix, begin, halflen)
        return self._rec_find(ix, begin + halflen, length - halflen)



