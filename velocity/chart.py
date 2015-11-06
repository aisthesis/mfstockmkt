"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Chart velocity data
===================
"""

import matplotlib
import matplotlib.pyplot as plt

import constants

def show(vel_df, title='Velocity'):
    pricecol = vel_df.columns[0]
    upcol = constants.UPVEL_COL
    downcol = constants.DOWNVEL_COL
    matplotlib.style.use('ggplot')
    plt.figure()
    ax1 = plt.subplot2grid((6, 6), (0, 0), rowspan=5, colspan=6)
    ax1.grid(True)
    plt.ylabel(pricecol)
    plt.setp(plt.gca().get_xticklabels(), visible=False)
    ax1.plot(vel_df.index, vel_df.loc[:, pricecol], color='b')
    ax2 = plt.subplot2grid((6, 6), (5, 0), sharex=ax1, rowspan=1, colspan=6)
    upvel_line = ax2.plot(vel_df.index, vel_df.loc[:, upcol], color='g')
    downvel_line = ax2.plot(vel_df.index, vel_df.loc[:, downcol], color='r')
    plt.suptitle(title)
    plt.show()
    plt.close()
