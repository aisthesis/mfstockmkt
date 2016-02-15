"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Interactively start and stop tracking an option.
"""

import datetime as dt
from functools import partial
import logging
import os

from pymongo.errors import BulkWriteError
import pytz

import config
import constants
from dbwrapper import job

class Menu(object):

    def __init__(self):
        self.actions = {
                'main': {
                    '0': lambda: False,
                    '1': self.track_single
                    }
                }
        self.tz = pytz.timezone('US/Eastern')
        self.logger = _getlogger()
        self.logger.debug('logger created')

    def exec_menu(self, name, choice):
        try:
            return self.actions[name][choice.strip()]()
        except KeyError:
            print('Invalid selection')
            return True

    def start(self):
        proceed = True
        while proceed:
            print('\nMain menu:')
            print('1. Start tracking single option')
            print('2. Start tracking spread')
            print('3. Stop tracking single option')
            print('4. Stop tracking spread')
            print('\n0. Quit')
            choice = input('\nEnter selection: ')
            proceed = self.exec_menu('main', choice)
        
    def track_single(self):
        entry = {}
        entry['Underlying'] = input('Underlying equity: ').strip().upper()
        entry['Opt_Type'] = _getopttype(input('Option type (c[all] or p[ut]): '))
        entry['Strike'] = float(input('Strike: '))
        entry['Expiry'] = self._getexpdt(input('Expiration (yyyy-mm-dd): '))
        self._confirmsave((entry,))
        return True

    def _getexpdt(self, expstr):
        return self.tz.localize(dt.datetime.strptime(expstr, '%Y-%m-%d')).replace(hour=23,
                minute=59, second=59)

    def _confirmsave(self, entries):
        print('\nSaving the following options:')
        _showentries(entries)
        choice = input('\nOK to proceed (y/n)? ').lower()
        if choice == 'y':
            job(self.logger, partial(_saveentries, entries))
        else:
            print('Aborting: option(s) not saved!')

def _saveentries(entries, logger, client):
    msg = 'Saving {} entries'.format(len(entries))
    print(msg)
    logger.info(msg)
    dbname = constants.DB[config.ENV]['name']
    _db = client[dbname]
    trackcoll = _db['track']
    bulk = trackcoll.initialize_unordered_bulk_op()
    for entry in entries:
        bulk.insert(entry)
        logger.debug('{} queued for insertion'.format(entry))
    try:
        result = bulk.execute()
    except BulkWriteError:
        logger.exception("error writing to database")
        raise
    else:
        logger.info('{} records inserted'.format(result['nInserted']))

def _showentries(entries):
    for entry in entries:
        print('')
        _showentry(entry)

def _getopttype(selection):
    if selection.strip().lower() in ('c', 'call'):
        return 'call'
    if selection.strip().lower() in ('p', 'put'):
        return 'put'
    raise ValueError('option type must be call or put')

def _showentry(entry):
    print('Underlying: {}'.format(entry['Underlying']))
    print('Opt_Type: {}'.format(entry['Opt_Type']))
    print('Strike: {:.2f}'.format(entry['Strike']))
    print('Expiry: {}'.format(entry['Expiry'].strftime('%Y-%m-%d')))

def _getlogger():
    logger = logging.getLogger('track')
    loglevel = logging.INFO if config.ENV == 'prod' else logging.DEBUG
    logger.setLevel(loglevel)
    log_dir = _getlogdir()
    handler = logging.FileHandler(os.path.join(log_dir, 'service.log'))
    formatter = logging.Formatter(constants.LOG['format'])
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def _getlogdir():
    log_dir = os.path.normpath(os.path.join(config.LOG_ROOT, constants.LOG['path']))
    try:
        os.makedirs(log_dir)
    except OSError:
        if not os.path.isdir(log_dir):
            raise
    return log_dir

if __name__ == '__main__':
    Menu().start()
