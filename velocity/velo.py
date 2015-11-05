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

from mov_ext import MovingExtremumFinder

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
    return _velocities(eqdata, window, selection, operator.gt)

def down(eqdata, window=100, selection='Adj Close'):
    """
    Return a dataframe with downward velocity data.

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
    downvel : DataFrame
    """
    return _velocities(eqdata, window, selection, operator.lt)

def _velocities(eqdata, window, selection, compfn):
    outcol = 'Velocity'
    outix = eqdata.index[window:]
    inputdata = eqdata.loc[:, selection].values
    vels = np.empty(outix.shape[0], dtype='int64')
    ext_finder = MovingExtremumFinder(inputdata, window, compfn)
    # values up to `window` don't have adequate history
    for i in range(window):
        ext_finder.insert(i)
    for i in range(window, inputdata.shape[0]):
        vels[i - window] = window - ext_finder.insert(i)
    return pd.DataFrame(data=vels, index=outix, columns=[outcol], dtype='int64')
