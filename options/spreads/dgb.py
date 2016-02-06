"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Diagonal butterfly scanner
"""

import pandas as pd
import pynance as pn

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
    nearfilter['min'] = opts.quotetime() + pd.Timedelta('90 days')
    nearfilter['max'] = opts.quotetime() + pd.Timedelta('130 days')
    nearexps = opts.exps()[opts.exps().slice_indexer(nearfilter['min'], nearfilter['max'])]
    print(nearexps)

if __name__ == '__main__':
    scan_all()
