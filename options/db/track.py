"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Interactively start and stop tracking an option.
"""

import datetime as dt
from functools import partial
import logging

import pytz

class Menu(object):

    def __init__(self):
        self.actions = {
                'main': {
                    'default': self.start,
                    '1': self.track_single
                    }
                }

    def exec_menu(self, name, choice):
        try:
            self.actions[name][choice.strip()]()
        except KeyError:
            print('Invalid selection')
            self.actions[name]['default']()

    def start(self):
        print('Main menu')
        print('Select action:')
        print('1. Start tracking single option')
        print('2. Start tracking spread')
        print('3. Stop tracking single option')
        print('4. Stop tracking spread')
        print('\n0. Quit')
        choice = input(' >> ')
        self.exec_menu('main', choice)
        
    def track_single(self):
        entry = {}
        entry['Underlying'] = input('Underlying equity: ').upper()
        entry['Opt_Type'] = input('Option type (call or put): ').lower()
        entry['Strike'] = float(input('Strike: '))
        entry['Expiry'] = _getexpdt(input('Expiration (yyyy-mm-dd): '))
        _saveentries((entry,), None, None)

def _getexpdt(expstr):
    eastern = pytz.timezone('US/Eastern')
    return eastern.localize(dt.datetime.strptime(expstr, '%Y-%m-%d')).replace(hour=23,
            minute=59, second=59)

def _saveentries(entries, logger, client):
    print('\nSaving the following options:')
    _showentries(entries)
    choice = input('\nOK to proceed (y/n)? ').lower()
    if choice == 'y':
        print('proceeding')
    else:
        print('Aborting: options not saved!')

def _showentries(entries):
    for entry in entries:
        print('')
        _showentry(entry)

def _showentry(entry):
    print('Underlying: {}'.format(entry['Underlying']))
    print('Opt_Type: {}'.format(entry['Opt_Type']))
    print('Strike: {:.2f}'.format(entry['Strike']))
    print('Expiry: {}'.format(entry['Expiry'].strftime('%Y-%m-%d')))

if __name__ == '__main__':
    Menu().start()
