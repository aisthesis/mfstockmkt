"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Get velocity data
=================
"""

import numpy as np
import pandas as pd
import pynance as pn

from possible_extrema import PossibleExtrema

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
    outix = eqdata.index[(window - 1):]
    inputdata = eqdata.loc[selection].values
    upvel = pd.DataFrame(index=outix, columns=[outcol], dtype='int64')

    dayssincehigh = 0
    i = 0
    return upvel
