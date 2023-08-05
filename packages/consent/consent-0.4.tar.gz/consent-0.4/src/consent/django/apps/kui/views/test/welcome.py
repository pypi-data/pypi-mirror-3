import unittest
from consent.django.apps.kui.views.test.base import ViewTestCase
from consent.django.apps.kui.views.kui import WelcomeView

def suite():
    suites = [
        unittest.makeSuite(TestWelcomeView),
    ]
    return unittest.TestSuite(suites)


class TestWelcomeView(ViewTestCase):

    viewClass = WelcomeView
    requiredResponseContent = [
        "Follow proposals",
        "Sign up",
        "Register proposals",
    ]

