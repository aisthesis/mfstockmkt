"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Diagonal butterfly scanner
"""

import pandas as pd
import pynance as pn

import strike

def scan_all():
    """
    Scan a list of equities for potential diagonal butterfly spreads.

    For the type of equity to examine cf. McMillan, p. 344:
    'one would like the underlying stock to be somewhat volatile,
    since there is the possibility that long-term options will
    be owned for free'
    """
    #equities = ['AMGN', 'AMZN', 'FB', 'FSLR', 'GILD', 'GOOGL', 'NFLX', 'SPWR', 'TSLA']
    equities = ['GILD']
    for equity in equities:
        scan(equity)

def scan(equity):
    opts = pn.opt.get(equity)
    nearfilter = {}
    difffilter = {}
    nearfilter['min'] = opts.quotetime() + pd.Timedelta('90 days')
    nearfilter['max'] = opts.quotetime() + pd.Timedelta('135 days')
    # 3rd Friday range:
    # earliest: 15
    # latest:   21
    # near falls on 02-21, far on 05-16 less 1
    difffilter['min'] = pd.Timedelta('83 days')
    # near falls on 03-15, far on 06-21 plus 1
    difffilter['max'] = pd.Timedelta('98 days')
    nearexps = opts.exps()[opts.exps().slice_indexer(nearfilter['min'], nearfilter['max'])]
    straddles = []
    for exp in nearexps:
        straddles.extend(_straddles(opts, exp))
    return straddles

def _straddles(opts, exp):
    """
    Return a list of straddles to examine.
    The list will normally contain 2 straddles only if the underlying
    price is exactly between 2 strikes. If the underlying is closer to
    1 strike than another, the list will contain only 1 element.
    """
    straddles = []
    allstrikes = strike.matchedforexp(opts, exp)
    eqprice = opts.data.iloc[0].loc['Underlying_Price']
    straddlestrikes = strike.straddle(allstrikes, eqprice)
    for sstrike in straddlestrikes:
        straddles.append({'exp': exp, 'strike': sstrike, 'price': _straddleprice(opts, sstrike, exp)})
    return straddles

def _straddleprice(opts, strike, exp):
    return opts.price.get('call', strike, exp) + opts.price.get('put', strike, exp)

if __name__ == '__main__':
    scan_all()
