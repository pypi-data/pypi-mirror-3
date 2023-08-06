import unittest
import doctest
from jstestcase import get_testcase

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(get_testcase('test_timer.js')))
    return suite
