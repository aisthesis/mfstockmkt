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
        'CRM',
        'CSIQ',
        'DLX',
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
        }]

LOG_FMT = "%(asctime)s %(levelname)s %(module)s.%(funcName)s : %(message)s"
