"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Queue jobs for options tracking.

This queue is not designed for multi-threading but
just to encapsulate retry logic within a single process.
"""

from collections import deque
import datetime as dt

import pynance as pn
import pytz

import config
import constants

class TrackQueue(object):

    def __init__(self, logger):
        self._logger = logger
        self._main_queue = deque()
        self._waiting = None
        self._tz_nyc = pytz.timezone('US/Eastern')
        self._prod = config.ENV == 'prod'
        self._n_retries = 4 if self._prod else 1

    def enqueue(self, entry):
        self._main_queue.append({
            'n_retries': 0,
            'start_time': dt.datetime.now(tz=self._tz_nyc),
            'entry': entry,
            })

    def ask(self):
        # return wait time for next query
        if len(self._main_queue) == 0:
            if self._waiting is None:
                return dt.timedelta()

    def ack(self, success):
        # nothing waiting (should never happen)
        if self._waiting is None:
            self._logger.error('unexpected ack: no object waiting ')
            return
        # processing was successful
        if success:
            self._logger.info('removing job from queue after successful processing')
            self._waiting = None
            return
        # abandon after multiple failed attempts
        if self._waiting['n_retries'] >= self._n_retries:
            self._logger.warn('abandoning job after {} failures'.format(self._waiting['n_retries'] + 1))
            self._waiting = None
            return
        # requeue with appropriate wait time
        self._waiting['n_retries'] += 1
        self._waiting['start_time'] = (dt.datetime.now(tz=self._tz_nyc) +
                self._getwaittime(self._waiting['n_retries']))
        # too late to retry, so abandon (shouldn't happen)
        if self._waiting['start_time'].hour <= 12:
            self._logger.warn('abandoning job after midnight')
            self._waiting = None
            return
        self._main_queue.append(self._waiting)
        self._logger.warn('requeueing job with n_retries set to {}'.format(self._waiting['n_retries']))
        self._waiting = None

    def pop(self):
        if len(self._main_queue) > 0 and self._waiting is None:
            self._waiting = self._main_queue.popleft()
            return self._waiting
        return None

    def _getwaittime(self, n_retries):
        return (3 ** n_retries) * dt.timedelta(minutes=1) 

