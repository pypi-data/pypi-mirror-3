#import consent.django.apps.kui.views.test.manipulator
import consent.django.apps.kui.views.test.welcome
import consent.django.apps.kui.views.test.accesscontrol
#import consent.django.apps.kui.views.test.project
import consent.django.apps.kui.views.test.person
import consent.django.apps.kui.views.test.assembly
import consent.django.apps.kui.views.test.proposal
#import consent.django.apps.kui.views.test.service
#import consent.django.apps.kui.views.test.member
#import consent.django.apps.kui.views.test.admin
#import consent.django.apps.kui.views.test.api
import unittest

# Just check these modules can actually be imported.
# Todo: Do this elsewhere.
import consent.django.settings.urls.main  
import consent.django.settings.main  

def suite():
    suites = [
#        consent.django.apps.kui.views.test.manipulator.suite(),
        consent.django.apps.kui.views.test.welcome.suite(),
        consent.django.apps.kui.views.test.accesscontrol.suite(),
#        consent.django.apps.kui.views.test.project.suite(),
        consent.django.apps.kui.views.test.person.suite(),
        consent.django.apps.kui.views.test.assembly.suite(),
        consent.django.apps.kui.views.test.proposal.suite(),
#        consent.django.apps.kui.views.test.service.suite(),
#        consent.django.apps.kui.views.test.member.suite(),
#        consent.django.apps.kui.views.test.admin.suite(),
#        consent.django.apps.kui.views.test.api.suite(),
    ]
    return unittest.TestSuite(suites)

