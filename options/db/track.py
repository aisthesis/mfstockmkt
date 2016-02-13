"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Interactively start and stop tracking an option.
"""

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
        print('1. Track single option')
        print('2. Track spread')
        print('3. Stop tracking single option')
        print('4. Stop tracking spread')
        print('\n0. Quit')
        choice = input(' >> ')
        self.exec_menu('main', choice)
        
    def track_single(self):
        underlying = input('Underlying equity: ').upper()
        opttype = input('Option type (call or put): ').lower()
        strike = float(input('Strike: '))
        expiry = input('Expiration: ')
        print(underlying, opttype, strike, expiry)

if __name__ == '__main__':
    Menu().start()
