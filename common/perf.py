"""
common/perf.py

(c) 2015 Marshall Farrier
license http://opensource.org/licenses/MIT

Calculate performance metrics
"""

import pandas as pd
import pynance as pn

def fromeq(equity, **kwargs):
    """
    Get performance metrics for an equity.

    Parameters
    ----------
    equity : str
        Equity for which to gather metrics.

    yrs : int, optional
        Period over which to calculate performance.
        Defaults to 1.

    end : pd.Timestamp, optional
        Value convertible to a pandas Timestamp.
        Defaults to current date.

    selection : str, optional
        Column to use for price. Defaults to 'Adj Close'.

    Usage
    -----
    growth = perf.growth('AAPL', yrs=3, end='2014-12-01')
    """
    yrs = kwargs.get('yrs', 1)
    offset = pd.tseries.offsets.DateOffset(months=12)
    end = pd.Timestamp(kwargs.get('end', pd.to_datetime('now')))
    start = pd.Timestamp(end - yrs * offset)
    eqdata = pn.data.get(equity, start, end)
    kwargs['equity'] = equity
    return fromdata(eqdata, **kwargs)

def fromdata(eqdata, **kwargs):
    """
    Get performance metrics from a DataFrame

    Parameters
    ----------
    eqdata : pd.DataFrame
        Source data.

    selection : str, optional
        Price column. Defaults to 'Adj Close'

    equity : str, optional
        Name of equity. Defaults to ''.

    Returns
    -------
    metrics : pd.Series
        Basic growth metrics.
    """
    selection = kwargs.get('selection', 'Adj Close')
    equity = kwargs.get('equity', '')
    index = ['Equity', 'Start', 'End', 'Years', 'Start Price', 'End Price',
            'Growth', 'Yrly Growth']
    metrics = pd.Series(index=index)
    metrics['Equity'] = equity
    metrics['Start'] = eqdata.index[0]
    metrics['End'] = eqdata.index[-1]
    metrics['Years'] = (metrics['End'] - metrics['Start']).days / 365.25
    metrics['Start Price'] = eqdata.iloc[0, :].loc[selection]
    metrics['End Price'] = eqdata.iloc[-1, :].loc[selection]
    metrics['Growth'] = metrics['End Price'] / metrics['Start Price']
    metrics['Yrly Growth'] = pn.interest.yrlygrowth(metrics['Growth'], metrics['Years'])
    return metrics
