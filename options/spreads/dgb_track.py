"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Track specific diagonal butterflies
"""

import pynance as pn

import constants
import dgb

def show_all():
    spreads = constants.DGB_TRACK
    for spread in spreads:
        print("getting spread data for '{}'".format(spread['underlying']))
        opts = pn.opt.get(spread['underlying'])
        spread['straddle']['price'] = dgb.getstraddleprice(opts, spread['straddle']['strike'],
                spread['straddle']['exp'])
        spread['call']['price'] = dgb.getoptprice(opts, 'call',
                spread['call']['strike'], spread['farexp'])
        spread['put']['price'] = dgb.getoptprice(opts, 'put', 
                spread['put']['strike'], spread['farexp'])
        farprice = spread['call']['price'] + spread['put']['price']
        credit = spread['straddle']['price'] - farprice
        distance = spread['straddle']['strike'] - spread['put']['strike']
        spread['risk'] = distance - credit
        spread['credit'] = credit
        spread['ratio'] = spread['straddle']['price'] / farprice
        spread['eqprice'] = opts.data.iloc[0].loc['Underlying_Price']
        dgb.show_spread(spread)

if __name__ == '__main__':
    show_all()
