"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Diagonal butterfly scanner
"""

import locale
import traceback

import pandas as pd
import pynance as pn

import constants
import strike

def scan_all():
    """
    Scan a list of equities for potential diagonal butterfly spreads.

    For the type of equity to examine cf. McMillan, p. 344:
    'one would like the underlying stock to be somewhat volatile,
    since there is the possibility that long-term options will
    be owned for free'
    """
    loc = locale.getlocale()
    locale.setlocale(locale.LC_ALL, 'en_US')
    equities = constants.DGB_EQUITIES
    orig_len = len(equities)
    # remove duplicates
    equities = list(set(equities))
    equities.sort()
    if len(equities) != orig_len:
        print('equities list contains {} duplicates'.format(orig_len - len(equities)))
    print('scanning {} equities for diagonal butterfly spreads'.format(len(equities)))
    butterflies = []
    for equity in equities:
        print("Scanning diagonal butterfly spreads for '{}'".format(equity))
        try:
            btfs_for_eq = scan(equity)
            print("{} spreads found for '{}'".format(len(btfs_for_eq), equity))
            butterflies.extend(btfs_for_eq)
        except Exception:
            traceback.print_exc()
    locale.setlocale(locale.LC_ALL, loc)
    return butterflies

def scan(equity):
    opts = pn.opt.get(equity)
    nearfilter = {}
    nearfilter['min'] = opts.quotetime() + pd.Timedelta('90 days')
    nearfilter['max'] = opts.quotetime() + pd.Timedelta('135 days')
    nearexps = opts.exps()[opts.exps().slice_indexer(nearfilter['min'], nearfilter['max'])]
    straddles = []
    for exp in nearexps:
        straddles.extend(_straddles(opts, exp))
    butterflies = []
    for straddle in straddles:
        butterflies.extend(_btrflies(opts, straddle))
    return butterflies

def show_spreads(butterflies):
    for butterfly in butterflies:
        print('')
        show_spread(butterfly)

def show_spread(butterfly):
    print("{} at {:.2f}:".format(butterfly['underlying'], butterfly['eqprice']))
    print("credit: {:.2f}".format(butterfly['credit']))
    print("risk: {:.2f}".format(butterfly['risk']))
    print("ratio: {:.4f}".format(butterfly['ratio']))
    print("straddle: {:.2f} at strike {:.2f} on {}".format(butterfly['straddle']['price'],
            butterfly['straddle']['strike'], _formattedexp(butterfly['straddle']['exp']))) 
    print("put: {:.2f} at strike {:.2f} on {}".format(butterfly['put']['price'],
            butterfly['put']['strike'], _formattedexp(butterfly['farexp']))) 
    print("call: {:.2f} at strike {:.2f} on {}".format(butterfly['call']['price'],
            butterfly['call']['strike'], _formattedexp(butterfly['farexp']))) 

def getstraddleprice(opts, strike, exp):
    return getoptprice(opts, 'call', strike, exp) + getoptprice(opts, 'put', strike, exp)

def getoptprice(opts, opttype, strike, exp):
    """
    This wrapper is needed because strikes with commas
    are being returned as strings by pandas-datareader
    """
    try:
        return opts.price.get(opttype, strike, exp)
    except KeyError:
        strikestr = locale.format("%0.2f", strike, grouping=True)
        return opts.price.get(opttype, strikestr, exp)

def _formattedexp(exp):
    try:
        return exp.date()
    except AttributeError:
        return exp

def _btrflies(opts, straddle):
    difffilter = {}
    # 3rd Friday range:
    # earliest: 15
    # latest:   21
    # near falls on 02-21, far on 05-16 less 1
    difffilter['min'] = pd.Timedelta('83 days')
    # near falls on 03-15, far on 06-21 plus 1
    difffilter['max'] = pd.Timedelta('98 days')
    exps = opts.exps()[opts.exps().slice_indexer(straddle['exp'] + difffilter['min'], 
            straddle['exp'] + difffilter['max'])]
    butterflies = []
    for exp in exps:
        butterflies.extend(_btfsforexp(opts, straddle, exp))
    return butterflies

def _btfsforexp(opts, straddle, exp):
    callstrikes = strike.allforexp(opts, exp, 'call')
    putstrikes = strike.allforexp(opts, exp, 'put')
    minputstrike = straddle['strike'] - straddle['price']
    butterflies = []
    callix = len(callstrikes) - 1
    for pstrike in putstrikes:
        if pstrike >= minputstrike:
            if pstrike >= straddle['strike']:
                return butterflies
            distance = straddle['strike'] - pstrike
            # proceed only if there is a corresponding call
            sentinel = strike.getlastmatched(straddle['strike'] + distance, callstrikes, callix)
            if sentinel >= 0:
                callix = sentinel
                callprice = getoptprice(opts, 'call', callstrikes[callix], exp)
                putprice = getoptprice(opts, 'put', pstrike, exp)
                farprice = callprice + putprice
                credit = straddle['price'] - farprice
                if credit <= 0.:
                    return butterflies
                risk = distance - credit
                if risk < credit:
                    butterflies.append({
                        'straddle': straddle, 
                        'call': {'strike': callstrikes[callix], 'price': callprice},
                        'put': {'strike': pstrike, 'price': putprice},
                        'farexp': exp,
                        'risk': risk,
                        'credit': credit,
                        'ratio': straddle['price'] / farprice,
                        'underlying': opts.data.iloc[0, :].loc['Underlying'],
                        'eqprice': opts.data.iloc[0].loc['Underlying_Price']
                        })
    return butterflies

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
        straddles.append({'exp': exp, 'strike': sstrike, 'price': getstraddleprice(opts, sstrike, exp)})
    return straddles

if __name__ == '__main__':
    butterflies = scan_all()
    show_spreads(butterflies)
