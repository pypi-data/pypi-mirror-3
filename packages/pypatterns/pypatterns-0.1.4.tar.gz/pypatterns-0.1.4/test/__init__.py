import unittest

import TestCommand
import TestFilter
import TestRelational
import TestRelationalCommand
import TestRelationalPickle

def additional_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFilter.TestCase, 'test'))
    suite.addTest(unittest.makeSuite(TestRelational.TestCase, 'test'))
    suite.addTest(unittest.makeSuite(TestRelationalCommand.TestCase, 'test'))
    suite.addTest(unittest.makeSuite(TestRelationalPickle.TestCase, 'test'))
    return suite

