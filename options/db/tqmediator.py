"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Mediator for workflow to save specific options.
"""

import datetime as dt
import logging
import os
import signal
import sys
import time

from pandas.tseries.offsets import BDay
import pytz

import config
import constants
from quotepuller import QuotePuller
from trackpuller import TrackPuller
from trackqueue import TrackQueue

class TrackQuoteMediator(object):

    def __init__(self):
        self._logger = _getlogger()
        self._prod = config.ENV == 'prod'
        self._tznyse = pytz.timezone('US/Eastern')

    def start_daemon(self):
        self._logger.info('daemon starting')
        signal.signal(signal.SIGINT, self._stop_handler)
        signal.signal(signal.SIGTERM, self._stop_handler)
        if self._prod:
            self._waitfornextclose()
        while True:
            self._run_job()
            self._waitfornextclose()

    def _run_job(self):
        trackpuller = TrackPuller(self._logger)
        totrack = trackpuller.get()
        queue = TrackQueue(self._logger)
        for underlying in totrack:
            queue.enqueue({'eq': underlying, 'spec': totrack[underlying]})
        delay_secs = queue.ask()
        i = 0
        while delay_secs >= 0:
            self._logger.info('waiting {} seconds'.format(delay_secs))
            time.sleep(delay_secs)
            item = queue.pop()
            i += 1
            if not self._prod and i % 3 == 0:
                # auto-fail every 3rd try in dev
                self._logger.debug('auto-failing in dev for testing')
                print('auto-failing in dev for item {}'.format(item))
                queue.ack(False)
            else:
                print('success for item {}'.format(item))
                queue.ack(True)
            if item is None:
                self._logger.info('item is None')
                time.sleep(10)
            delay_secs = queue.ask()
        self._logger.info('finished processing queue')

    def _waitfornextclose(self):
        seconds = 15
        if self._prod:
            seconds = self._secondsuntilnextclose()
            self._logger.info('waiting {:.2f} hours until next close'.format(seconds / 3600.))
        else:
            self._logger.info('waiting {} seconds in dev mode'.format(seconds))
        time.sleep(seconds)

    def _secondsuntilnextclose(self):
        nysenow = dt.datetime.now(tz=self._tznyse)
        if _is_bday(nysenow):
            # a few minutes after close to be safe
            todaysclose = nysenow.replace(hour=16, minute=15)
            if nysenow >= todaysclose:
                return 0
            return (todaysclose - nysenow).seconds
        nextclose = (nysenow + BDay()).replace(hour=16, minute=15)
        diff = nextclose - nysenow
        return diff.seconds + diff.days * 24 * 3600

    def _stop_handler(self, sig, frame):
        msg = ('SIGINT' if sig == signal.SIGINT else 'SIGTERM')
        self._logger.info('signal {} received. stopping'.format(msg))
        sys.exit(0)

def _is_bday(date):
    return date.day == ((date + BDay()) - BDay()).day

def _getlogger():
    logger = logging.getLogger('tqmediator')
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
    TrackQuoteMediator().start_daemon()
