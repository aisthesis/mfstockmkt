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
    strikes = _strikesforexp(opts, exp)
    eqprice = opts.data.iloc[0].loc['Underlying_Price']
    straddlestrikes = _straddlestrikes(strikes, eqprice)
    for sstrike in straddlestrikes:
        straddles.append({'exp': exp, 'strike': sstrike, 'price': _straddleprice(opts, sstrike, exp)})
    return straddles

def _straddleprice(opts, strike, exp):
    callprice = (opts.data.loc[(strike, exp, 'call'), 'Bid'].values[0] +
            opts.data.loc[(strike, exp, 'call'), 'Ask'].values[0]) / 2.
    putprice = (opts.data.loc[(strike, exp, 'put'), 'Bid'].values[0] +
            opts.data.loc[(strike, exp, 'put'), 'Ask'].values[0]) / 2.
    return callprice + putprice

def _straddlestrikes(strikes, eqprice):
    for i in range(len(strikes)):
        if strikes[i] >= eqprice:
            if i == 0 or strikes[i] - eqprice < eqprice - strikes[i - 1]:
                return [strikes[i]]
            if strikes[i] - eqprice == eqprice - strikes[i - 1]:
                return [strikes[i - 1], strikes[i]]
            return [strikes[i - 1]]
    if strikes:
        return [strikes[-1]]
    return []

def _strikesforexp(opts, exp):
    callstrikes = opts.data.xs((exp, 'call'), level=('Expiry', 'Type')).index.get_level_values(0)
    putstrikes = opts.data.xs((exp, 'put'), level=('Expiry', 'Type')).index.get_level_values(0)
    return _matchingstrikes(callstrikes, putstrikes)

def _matchingstrikes(callstrikes, putstrikes):
    icall = -1
    iput = -1
    matching = []
    ncallstrikes = len(callstrikes)
    nputstrikes = len(putstrikes)
    while True:
        icall, iput = _nextsynchronized(callstrikes, putstrikes, icall, iput, ncallstrikes, nputstrikes)
        if icall < ncallstrikes:
            matching.append(callstrikes[icall])
        else:
            return matching
    
def _nextsynchronized(callstrikes, putstrikes, icall, iput, ncallstrikes, nputstrikes):
    nxt_icall = icall + 1
    nxt_iput = iput + 1
    if nxt_icall >= ncallstrikes or nxt_iput >= nputstrikes:
        return ncallstrikes, nputstrikes
    while callstrikes[nxt_icall] < putstrikes[nxt_iput]:
        nxt_icall += 1
        if nxt_icall >= ncallstrikes:
            return ncallstrikes, nputstrikes
    while putstrikes[nxt_iput] < callstrikes[nxt_icall]:
        nxt_iput += 1
        if nxt_iput >= nputstrikes:
            return ncallstrikes, nputstrikes
    return nxt_icall, nxt_iput

if __name__ == '__main__':
    scan_all()
