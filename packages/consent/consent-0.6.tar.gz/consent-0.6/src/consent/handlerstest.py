import unittest
import consent.handlers.apachecodestest
import consent.handlers.modpythontest
import consent.handlers.modwsgitest

def suite():
    suites = [
        consent.handlers.apachecodestest.suite(),
        consent.handlers.modpythontest.suite(),
        consent.handlers.modwsgitest.suite(),
    ]
    return unittest.TestSuite(suites)

