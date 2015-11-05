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

def get_all(eqdata, window=100, selection='Adj Close'):
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
    all_vel : DataFrame
    """
    up_vel = up(eqdata, window, selection)
    down_vel = down(eqdata, window, selection)
    up_col = 'Up Vel'
    down_col = 'Down Vel'
    all_vel = pd.DataFrame(index=up_vel.index, columns=[selection, up_col, down_col],
            dtype='float64')
    all_vel.loc[:, selection] = eqdata.loc[:, selection].values[window:]
    all_vel.loc[:, up_col] = up_vel.values
    all_vel.loc[:, down_col] = down_vel.values
    return all_vel

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
    vels = np.empty_like(outix, dtype='int64')
    ext_finder = MovingExtremumFinder(inputdata, window, compfn)
    # values up to `window` don't have adequate history
    for i in range(window):
        ext_finder.insert(i)
    for i in range(window, inputdata.shape[0]):
        vels[i - window] = window - ext_finder.insert(i)
    return pd.DataFrame(data=vels, index=outix, columns=[outcol], dtype='int64')
