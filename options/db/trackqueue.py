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
        self._tz_nyse = pytz.timezone('US/Eastern')
        self._prod = config.ENV == 'prod'
        self._n_retries = 4 if self._prod else 1

    def enqueue(self, entry):
        self._main_queue.append({
            'n_retries': 0,
            'start_time': dt.datetime.now(tz=self._tz_nyse),
            'entry': entry,
            })

    def ask(self):
        # return wait time in seconds for next query
        # return -1 if queue is empty with nothing waiting
        if len(self._main_queue) == 0:
            if self._waiting is None:
                self._logger.info('queue empty and processing complete')
                return -1
        # item waiting but no ack received yet, so wait for ack
        # means client is doing something wrong
        if self._waiting is not None:
            self._logger.error('unexpected ask while object waiting for ack')
            return 30
        # something in queue and nothing waiting
        nysenow = dt.datetime.now(tz=self._tz_nyse)
        if self._main_queue[0]['start_time'] < nysenow:
            self._logger.info('head of queue ready for immediate processing')
            return 0
        diff = self._main_queue[0]['start_time'] - nysenow
        delay_secs = diff.seconds + diff.days * 24 * 3600
        if not self._prod:
            delay_secs = constants.DEV['queue']['failure_delay']
        self._logger.info('{} seconds delay required for processing head of queue'
                .format(delay_secs))
        return delay_secs

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
        self._waiting['start_time'] = (dt.datetime.now(tz=self._tz_nyse) +
                self._getwaittime(self._waiting['n_retries']))
        # too late to retry, so abandon
        # can happen only if system is booted late in the day
        if self._waiting['start_time'].hour <= 12 and self._prod:
            self._logger.warn('abandoning job after midnight')
            self._waiting = None
            return
        self._main_queue.append(self._waiting)
        self._logger.warn('requeueing job with n_retries set to {}'.format(self._waiting['n_retries']))
        self._waiting = None

    def pop(self):
        if len(self._main_queue) > 0 and self._waiting is None:
            if dt.datetime.now(tz=self._tz_nyse) < self._main_queue[0]['start_time']:
                # isn't supposed to happen
                self._logger.error('item not ready to process')
                return None
            self._waiting = self._main_queue.popleft()
            return self._waiting['entry']
        return None

    def _getwaittime(self, n_retries):
        if self._prod:
            return (3 ** n_retries) * dt.timedelta(minutes=1) 
        return dt.timedelta(seconds=constants.DEV['queue']['failure_delay'])

