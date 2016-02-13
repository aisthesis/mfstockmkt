"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Constants for working with a database
"""

LOG = {
        'format': "%(asctime)s %(levelname)s %(module)s.%(funcName)s : %(message)s",
        'path': 'mfstockmkt/options/db'
        }

DB = {
        'dev': {
            'name': 'test'
            },
        'prod': {
            'name': 'optMkt'
            }
        }
