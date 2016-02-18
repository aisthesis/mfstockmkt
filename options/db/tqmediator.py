"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Mediator for workflow to save specific options.
"""

import logging
import os

import config
import constants
from trackpuller import TrackPuller

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

def _run():
    logger = _getlogger()
    trackpuller = TrackPuller(logger)
    print(trackpuller.get())

if __name__ == '__main__':
    _run()
