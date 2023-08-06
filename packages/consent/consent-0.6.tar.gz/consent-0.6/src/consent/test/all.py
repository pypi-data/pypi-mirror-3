import unittest
import consent.test.developer
import consent.test.customer

def suite():
    suites = [
        consent.test.customer.suite(),
        consent.test.developer.suite(),
    ]
    return unittest.TestSuite(suites)

