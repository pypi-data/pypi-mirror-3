#!/usr/bin/env python
from __future__ import division

"""test_colorbrewer.py: test colorbrewer module
"""

__version__ = "$Revision: 9170 $"

## Copyright 2012 Michael M. Hoffman <mmh1@uw.edu>

from unittest import main, TestCase

import colorbrewer

class ColorbrewerTestCase(TestCase):
    def test_Dark2(self):
        self.assertEqual(colorbrewer.Dark2[3],
                         [(27, 158, 119), (217, 95, 2), (117, 112, 179)])

if __name__ == "__main__":
    main()
