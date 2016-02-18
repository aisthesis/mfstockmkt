"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Save data for specific diagonal butterflies.
"""
# TODO retry logic

import pynance as pn
import pytz

import config
import constants

class QuotePuller(object):

    def __init__(self, logger):
        self.logger = logger
        self.tz_useast = pytz.timezone('US/Eastern')

    def get(self, totrack):
        """
        `totrack` is expected to be a dictionary where the underlying
        is the key and the value is a list of the options to track
        for that equity
        """
        entries = []
        for underlying in totrack:
            entries.extend(self._getfromlist(underlying, totrack[underlying]))
        return entries

    def _getfromlist(self, underlying, optspecs):
        self.logger.info('getting option data for {}'.format(underlying))
        opts = pn.opt.get(underlying)
        entries = []
        self.logger.info('getting {} options for {}'.format(len(optspecs), underlying))
        for spec in optspecs:
            entry = self._extract(spec, opts)
            if entry is not None:
                entries.append(entry)
        return entries

    def _extract(self, spec, opts):
        entry = spec.copy()
        selection = (spec['Strike'], spec['Expiry'].astimezone(self.tz_useast).replace(tzinfo=None,
                hour=0, minute=0, second=0), spec['Opt_Type'],)
        try:
            entry['Opt_Symbol'] = opts.data.loc[selection, :].index[0]
            opt = opts.data.loc[selection, :].iloc[0]
        except KeyError as e:
            self.logger.exception('option not found for {} with {}'
                    .format(opts.data.iloc[0, :].loc['Underlying'], selection))
            return None
        entry['Quote_Time'] = self.tz_useast.localize(opt['Quote_Time'].to_datetime())
        entry['Underlying'] = opt['Underlying']
        for key in constants.INT_COLS:
            entry[key] = int(opt[key])
        for key in constants.FLOAT_COLS:
            entry[key] = float(opt[key])
        self.logger.debug(entry)
        return entry

