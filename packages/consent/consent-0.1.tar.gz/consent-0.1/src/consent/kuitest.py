import unittest

import consent.test.customer.kui

def suite():
    suites = [
        consent.test.customer.kui.suite(),
    ]
    return unittest.TestSuite(suites)

