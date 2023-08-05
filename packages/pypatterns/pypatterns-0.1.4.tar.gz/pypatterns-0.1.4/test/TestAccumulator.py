import unittest

import pypatterns.filter as FilterModule


class TestCase(unittest.TestCase):

    def testOrAccumulator1(self):
        accumulator = FilterModule.OrAccumulator()
        
        self.assertFalse(accumulator.value())

        accumulator.add(False)
        self.assertFalse(accumulator.value())

        accumulator.add(True)
        self.assertTrue(accumulator.value())

        return


    def testOrAccumulator2(self):
        accumulator = FilterModule.OrAccumulator()
        
        self.assertFalse(accumulator.value())

        accumulator.add(True)
        self.assertTrue(accumulator.value())

        accumulator.add(False)
        self.assertTrue(accumulator.value())

        return


    # END class TestCase
    pass
