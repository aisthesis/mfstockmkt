"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Get velocity data
=================
"""

import operator

import numpy as np
import pandas as pd
import pynance as pn

import constants
from mov_ext import MovingExtremumFinder

def rolling_vel(eqdata, window=100, selection='Adj Close'):
    """
    Return a dataframe with prices and both upward and downward 
    velocity data.

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
    mov_vel : DataFrame
    """
    outix = eqdata.index[window:]
    upcol = constants.UPVEL_COL
    downcol = constants.DOWNVEL_COL
    mov_vel = pd.DataFrame(index=eqdata.index[window:], 
            columns=[selection, upcol, downcol], dtype='float64')
    mov_vel.loc[:, selection] = eqdata.loc[:, selection].values[window:]
    mov_vel.loc[:, upcol] = _velocity(eqdata, window, selection, operator.gt, upcol)
    mov_vel.loc[:, downcol] = _velocity(eqdata, window, selection, operator.lt, downcol)
    return mov_vel

def _velocity(eqdata, window, selection, compfn, outputcol):
    inputdata = eqdata.loc[:, selection].values
    vels = np.empty_like(eqdata.index[window:], dtype='float64')
    ext_finder = MovingExtremumFinder(inputdata, window, compfn)
    win_float = float(window)
    # values up to `window` don't have adequate history
    for i in range(window):
        ext_finder.insert(i)
    for i in range(window, inputdata.shape[0]):
        vels[i - window] = float(window - ext_finder.insert(i)) / win_float
    return vels
