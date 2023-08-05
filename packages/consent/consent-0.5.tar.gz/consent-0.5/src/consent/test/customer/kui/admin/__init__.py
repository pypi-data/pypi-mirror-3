from consent.test.customer.kui.base import KuiTestCase
import consent.test.customer.kui.admin.domainObject
import consent.test.customer.kui.admin.hasMany
import unittest

def suite():
    suites = [
        consent.test.customer.kui.admin.domainObject.suite(),
        consent.test.customer.kui.admin.hasMany.suite(),
    ]
    return unittest.TestSuite(suites)

