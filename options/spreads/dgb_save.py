"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Save data for specific diagonal butterflies.
"""

import logging

import pynance as pn

import constants
import dbwrapper

class DgbSaver(object):

    def __init__(self):
        self.logger = logging.getLogger('dgb_save')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(constants.LOG_FMT)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def run(self):
        self.logger.debug('running')
        tracked = self.gettracked()
        quotes = self.getquotes(tracked)
        self.save(quotes)

    def gettracked(self):
        pass

    def getquotes(self, tracked):
        pass

    def save(self, quotes):
        pass

if __name__ == '__main__':
    DgbSaver().run()
