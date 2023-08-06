import unittest
import doctest


def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(doctest.DocTestSuite('xm.charting.gantt'))
    suite.addTest(doctest.DocFileSuite('chart.txt',
                                       package='xm.charting'))

    return suite
