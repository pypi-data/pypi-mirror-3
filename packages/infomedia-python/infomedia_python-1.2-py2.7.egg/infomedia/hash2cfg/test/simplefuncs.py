# Copyright 2011-2012 by Infomedia Foundation

# @OPENSOURCE_HEADER_START@
# @OPENSOURCE_HEADER_END@

import unittest

import infomedia
from infomedia.hash2cfg import *

def td_intlist_test(s, *args, **kwargs):
    args_str = ", ".join(["%r" % a for a in args] +
                         ["%s=%r" % (k, v) for (k, v) in kwargs.iteritems()])
    def test_generated(self):
        self.assertEqual(s, get_intlist(*args))
    test_generated.__doc__ = "get_intlist(%s)" % args_str
    return test_generated


class SimpleFuncsTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_list_00(self):
        "get_list(None)"
        self.assertEqual(None, get_list(None))

    def test_get_list_01(self):
        "get_list('A,B,C,D')"
        self.assertEqual(['A','B','C','D'], get_list('A,B,C,D'))

    def test_get_list_02(self):
        "get_list('A,B.C,D')"
        self.assertEqual(['A','B.C','D'], get_list('A,B.C,D'))

    def test_get_list_03(self):
        "get_list('A,B.C,D',sep='.')"
        self.assertEqual(['A,B','C,D'], get_list('A,B.C,D',sep='.'))

    def test_get_list_04(self):
        "get_list('A, B , C , D')"
        self.assertEqual(['A','B','C','D'], get_list('A , B,   C   , D'))
    
    test_intlist_00 = td_intlist_test([1,2,3],'1 , 2 , 3')


    def test_explode_00(self):
        "explode_list('II$$','IT,FR,DE,UK')"
        self.assertEqual(['IIIT','IIFR','IIDE','IIUK'], explode_list('II$$','IT,FR,DE,UK'))

    def test_explode_01(self):
        "explode_list('$$','IT,FR,DE,UK')"
        self.assertNotEqual(['IIIT','IIFR','IIDE','IIUK'], explode_list('$$','IT,FR,DE,UK'))

        
if __name__ == "__main__":
    unittest.main()

__all__ = ['SimpleFuncsTest']
