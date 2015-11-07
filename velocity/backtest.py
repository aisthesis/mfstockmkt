"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Backtest velocity-based trading strategy
========================================
"""

import pynance as pn

import constants
import velo

def simulate(equities, start, end, window=100, investment=10000):
    """
    Run simulation

    Parameters
    ----------
    equities : list of str

    start : Timestamp
        A string such as '2015-04-01' or just '2015' (which converts to
        2015-01-01) can also be used, as it will automatically convert
        to a Timestamp.

    end : Timestamp
        A string such as '2015-04-01' or just '2015' (which converts to
        2015-01-01) can also be used, as it will automatically convert
        to a Timestamp.

    window : int, optional
        Defaults to 100

    investment : float, optional
        Defaults to 10000.

    Notes
    -----
    Triggered Sell Count :
        Sells actually triggered by a velocity crossover. An equity
        will often be owned when data runs out.
        We take as profit or loss for the final purchase to be
        the value of the shares owned at the end of the time series less
        the original investment.
    Total Sales :
        Gross proceeds from all sales, including cashing
        out at the end of the trial period.
    Days at Risk :
        Total number of days the investment amount has been at risk.
        For example: Suppose equity 'ABC' was purchased on day 1 and held for
        90 days before being sold, and equity 'DEF' was purchased on day 20
        and held for 40 days before being sold. The total days at risk
        here is 90 + 40 = 130. It doesn't matter that the periods when
        the investment was at risk overlapped for the 2 equities.
    """
    result = {
            'Equities': equities,
            'Start': start,
            'End': end,
            'Window': window,
            'Investment': investment,
            'Buy Count': 0,
            'Triggered Sell Count': 0,
            'Total Invested': 0.,
            'Total Sales': 0.,
            'Total Profit': 0.,
            'Days at Risk': 0,
            'Years at Risk': 0.,
            'Ave Yrly Return': 0.
            }
    pricecol = 'Adj Close'
    for equity in equities:
        print("Running simulation for equity '{}'".format(equity))
        eqdata = pn.data.get(equity, start, end)
        _sim_eq(eqdata, window, investment, pricecol, result)
    result['Total Profit'] = result['Total Sales'] - result['Total Invested']
    result['Years at Risk'] = result['Days at Risk'] / 365.25
    total_ret = result['Total Profit'] / result['Total Invested']
    result['Ave Yrly Return'] = pn.interest.yrlyret(total_ret, result['Years at Risk'])
    return result

def _sim_eq(eqdata, window, investment, pricecol, result):
    try:
        veldata = velo.rolling_vel(eqdata, window, pricecol)
    except ValueError as e:
        print('ValueError: {}'.format(e))
    else:
        print("Valid equity data starts on {}".format(veldata.index[0]))
        revs = reversals(veldata, pricecol)
        invested = False
        buyprice = 0.
        sellprice = 0.
        buydate = None
        lastdate = None
        days_at_risk = 0
        for rev in revs:
            if rev['Action'] == 'Buy':
                invested = True
                buyprice = rev['Price']
                buydate = rev['Date']
                result['Buy Count'] += 1
                result['Total Invested'] += investment
                continue
            if invested and rev['Action'] == 'Sell':
                invested = False
                sellprice = rev['Price']
                result['Triggered Sell Count'] += 1
                result['Total Sales'] += investment * sellprice / buyprice
                days_at_risk = (rev['Date'] - buydate).days
                result['Days at Risk'] += days_at_risk
        if invested:
            print('Still invested at end of simulation. Selling')
            lastdate = veldata.index[-1]
            days_at_risk = (lastdate - buydate).days
            result['Total Sales'] += investment * veldata.loc[lastdate, pricecol] / buyprice
            result['Days at Risk'] += days_at_risk

def reversals(vel_all, pricecol='Adj Close'):
    bullish = True
    up = vel_all.loc[:, constants.UPVEL_COL].values
    down = vel_all.loc[:, constants.DOWNVEL_COL].values
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
        
