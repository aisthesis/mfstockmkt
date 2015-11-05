"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Backtest velocity-based trading strategy
========================================
"""

import velo

def run(equities, start, end, investment=10000):
    pass

def reversals(vel_all, pricecol='Adj Close'):
    bullish = True
    up = vel_all.loc[:, 'Up Vel'].values
    down = vel_all.loc[:, 'Down Vel'].values
    prices = vel_all.loc[:, pricecol].values
    # Determine initial trend
    for i in range(up.shape[0]):
        if up[i] > down[i]:
            break
        if up[i] < down[i]:
            bullish = False
            break
    revs = []
    for i in range(up.shape[0]):
        if bullish and up[i] < down[i]:
            bullish = False
            revs.append({'Date': vel_all.index[i], 'Action': 'Sell',
                'Index': i, 'Price': prices[i]})
            continue
        if not bullish and up[i] > down[i]:
            bullish = True
            revs.append({'Date': vel_all.index[i], 'Action': 'Buy',
                'Index': i, 'Price': prices[i]})
    return revs
        
