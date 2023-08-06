# Copyright 2011-2012 by Infomedia Foundation

# @OPENSOURCE_HEADER_START@
# @OPENSOURCE_HEADER_END@

from datetime import datetime

import unittest

import infomedia
from infomedia.options import *

class OptionsTest(unittest.TestCase):

    def test_options_01(self):
        "DEFAULT_DEFINES['THISMONTH']"
        options = Options(test=1)
        self.assertEqual(1,options.test)

                  
