mfstockmkt/velocity
==
Tools for examining equity velocity.

Cf. http://pro.moneymappress.com/MMRWND129/PMMRRB22/?iris=429781&ad=btgt4c-g21kmmis-h1&h=true

Usage
--
Get the underlying price data with:

    import pynance as pn

    eq = 'NFLX'
    eqdata = pn.data.get(eq, '2010', '2016')

Get velocity data:

    import velo
    veldata = velo.rolling_vel(eqdata)

Plot velocity data:

    import chart
    chart.show(veldata)
