"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Constants for spreads
"""

DGB_EQUITIES = [
        'AAON',
        #'ALXN',
        'AMGN',
        'AMZN',
        'AOS',
        'APOG',
        'BIDU',
        'BIIB',
        'BMRN',
        'CELG',
        'CHSP',
        'CMG',
        'CRM',
        'CSIQ',
        'DLX',
        'EOG',
        'FB',
        'FSLR',
        'GILD',
        'GK',
        #'GNMSF',
        'GOOGL',
        'INCY',
        'JCOM',
        'JD',
        'MDP',
        'MDVN',
        'MMS',
        'NFLX',
        'NTES',
        'PACW',
        'PCLN',
        #'PEB',
        'REGN',
        'SCTY',
        'SPWR',
        'SSNC',
        'TSLA',
        'UBSI',
        'VRTX',
        'YHOO',
        ]

DGB_TRACK = [
        {   
        'underlying': 'TSLA',
        'straddle': {
            'strike': 150.,
            'exp': '2016-06-17'},
        'farexp': '2016-09-16',
        'put': {'strike': 110.},
        'call': {'strike': 190.}
        },
        {   
        'underlying': 'BMRN',
        'straddle': {
            'strike': 85.,
            'exp': '2016-07-15'},
        'farexp': '2016-10-21',
        'put': {'strike': 65.},
        'call': {'strike': 105.}
        },
        ]

