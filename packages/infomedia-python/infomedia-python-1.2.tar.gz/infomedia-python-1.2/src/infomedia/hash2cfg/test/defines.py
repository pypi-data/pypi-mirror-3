# Copyright 2011-2012 by Infomedia Foundation

# @OPENSOURCE_HEADER_START@
# @OPENSOURCE_HEADER_END@

from datetime import datetime

import unittest

import infomedia
from infomedia.hash2cfg.defines import *

class DefinesTest(unittest.TestCase):

    def setUp(self):
        self._date = datetime.now()

    def test_defines(self):
        "DEFAULT_DEFINES['THISMONTH']"
        self.assertEqual(str(self._date.month),
                         DEFAULT_DEFINES['THISMONTH'])

#    def test_c2h_exception(self):
        # self.assertRaises(ConfigNotExistsError,cfg2hash, ('file_not_found'))
                  
