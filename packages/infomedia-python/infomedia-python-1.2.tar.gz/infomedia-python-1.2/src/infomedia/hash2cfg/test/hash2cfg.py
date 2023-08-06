# Copyright 2011-2012 by Infomedia Foundation

# @OPENSOURCE_HEADER_START@
# @OPENSOURCE_HEADER_END@

import unittest

import infomedia
from infomedia.hash2cfg import *

class Hash2CfgTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_h2c_missing(self):
        self.assertIsNone(hash2cfg(None,'test'))
        self.assertIsNone(hash2cfg([1,2],'test'))
        self.assertIsNone(hash2cfg("test",'test'))


    def test_c2h_exception(self):
        self.assertRaises(ConfigNotExistsError,cfg2hash, ('file_not_found'))
        self.assertRaises(ConfigNotProtectedError,cfg2hash, ('/etc/passwd'),secure=True)
    
    def test_c2h_base_file(self):
        open('/tmp/test.1','w').write(
            """
NO INI FILE HERE
            """
            )
        self.assertRaises(ParseError,cfg2hash, ('/tmp/test.1'))
        open('/tmp/test.1','w').write(
            """
A=1
B=2
C=3
            """
            )
        self.assertRaises(MissingSectionHeaderError,cfg2hash, ('/tmp/test.1'))
        open('/tmp/test.1','w').write(
            """
[SEC]
A=1
B=2
C=3
            """)
        self.assertEqual({u'SEC':{u'A':u'1',u'B':u'2',u'C':u'3'}},
                         cfg2hash('/tmp/test.1',extra=False))
