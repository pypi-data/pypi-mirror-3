import unittest
import tempfile
from consent.testunit import TestCase

def suite():
    "Return a TestSuite of consent.command TestCases."
    suites = [
            unittest.makeSuite(TestUtils),
            unittest.makeSuite(TestPassword),
        ]
    return unittest.TestSuite(suites)

class TestUtils(TestCase):

    def test_import(self):
        if self.dictionary['captcha.enable']:
            # check module imports
            import consent.utils.captcha  

import consent.utils.password
class TestPassword(TestCase):

    def test_generate(self):
        out = consent.utils.password.generate()
        self.failUnless(len(out) == 8)

    def test_generate_2(self):
        size = 10
        out = consent.utils.password.generate(size)
        self.failUnless(len(out) == size)

