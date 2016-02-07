"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Utilities for getting strikes
"""

def straddle(allstrikes, eqprice):
    for i in range(len(allstrikes)):
        if allstrikes[i] >= eqprice:
            if i == 0 or allstrikes[i] - eqprice < eqprice - allstrikes[i - 1]:
                return [allstrikes[i]]
            if allstrikes[i] - eqprice == eqprice - allstrikes[i - 1]:
                return [allstrikes[i - 1], allstrikes[i]]
            return [allstrikes[i - 1]]
    if allstrikes:
        return [allstrikes[-1]]
    return []

def matchedforexp(opts, exp):
    callstrikes = opts.data.xs((exp, 'call'), level=('Expiry', 'Type')).index.get_level_values(0)
    putstrikes = opts.data.xs((exp, 'put'), level=('Expiry', 'Type')).index.get_level_values(0)
    return _matching(callstrikes, putstrikes)

def _matching(callstrikes, putstrikes):
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
