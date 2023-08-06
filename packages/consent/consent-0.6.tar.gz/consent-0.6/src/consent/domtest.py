import consent.dom.assemblytest
import consent.dom.proposaltest
import consent.dom.consensustest
from consent.dom.testunit import TestCase
from consent.exceptions import *
import unittest

def suite():
    suites = [
        consent.dom.assemblytest.suite(),
        consent.dom.proposaltest.suite(),
        consent.dom.consensustest.suite(),
    ]
    return unittest.TestSuite(suites)


