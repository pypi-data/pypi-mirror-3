import unittest
from consent.testunit import TestCase
from consent.dictionarywords import *

def suite():
    suites = [
        unittest.makeSuite(MigrationTest),
    ]
    return unittest.TestSuite(suites)

class MigrationTest(TestCase):

    def test_registry(self):
        # Check system version in the model equals system version in the code.
        systemVersion = self.registry.systems[1].version
        self.failUnlessEqual(systemVersion, self.dictionary[SYSTEM_VERSION])

