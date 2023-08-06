# Copyright 2011-2012 by Infomedia Foundation

# @OPENSOURCE_HEADER_START@
# @OPENSOURCE_HEADER_END@

from datetime import datetime

import unittest

import infomedia
from infomedia.collections import *

class CollectionTest(unittest.TestCase):

    def test_needed_01(self):
        "needed('A','B','C')"
        self.assertRaises(ValueError,needed,{},'A','B','C')

                  
