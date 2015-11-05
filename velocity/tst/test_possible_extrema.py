"""
Unit tests for `PossibleExtrema` class

Copyright (c) 2015 Marshall Farrier
license http://opensource.org/licenses/MIT
"""

import operator
import os
import sys
import unittest

import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from possible_extrema import PossibleExtrema

class TestPossibleExtrema(unittest.TestCase):

    def test_insert_overflow(self):
        window = 2
        data = np.array([1., .9, .8, .7])
        length = data.shape[0]
        poss_highs = PossibleExtrema(data, window, operator.gt)
        for i in range(length):
            poss_highs.insert(i)
        self.assertEqual(poss_highs._begin, 1, 'incorrect starting point for circle')
        self.assertEqual(poss_highs._indices, [3, 1, 2], 'incorrect indices')

    def test_insert_output(self):
        window = 3
        seq =       [1., .9, .8, .7, .6, .9, .6, .8, .5, .7, .6, .6, .5, .5, .4, .4, .4, .3, .2, .1]
        expected =  [0,   1,  2,  3,  3,  0,  1,  2,  3,  2,  3,  2,  3,  3,  3,  3,  3,  3,  3,  3]
        data = np.array(seq)
        length = data.shape[0]
        actual = [0] * length
        poss_highs = PossibleExtrema(data, window, operator.gt)
        for i in range(length):
            actual[i] = poss_highs.insert(i)
        self.assertEqual(expected, actual, 'incorrect velocity series')

if __name__ == '__main__':
    unittest.main()
