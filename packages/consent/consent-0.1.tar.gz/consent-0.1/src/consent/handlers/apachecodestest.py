import unittest
from consent.testunit import TestCase
from consent.handlers.apachecodes import *

import os

def suite():
    suites = [
        unittest.makeSuite(TestCodes),
    ]
    return unittest.TestSuite(suites)


class TestCodes(TestCase):

    def test_codes(self):
        self.failUnlessEqual(OK,                          0)
        self.failUnlessEqual(HTTP_OK,                   200)
        self.failUnlessEqual(HTTP_MOVED_TEMPORARILY,    302)
        self.failUnlessEqual(HTTP_FORBIDDEN,            403)

