import unittest
import consent.test.developer

def suite():
    suites = [
        consent.test.developer.suite(),
    ]
    return unittest.TestSuite(suites)

