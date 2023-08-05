import unittest

def suite():
#    import consent.domtest
#    import consent.django.apps.kui.views.test
    suites = [
#        consent.domtest.suite(),
#        consent.django.apps.kui.views.test.suite(),
    ]
    return unittest.TestSuite(suites)

