# -*- coding=utf-8 -*-
import unittest
from consent.django.apps.kui.views.test.base import ViewTestCase
from consent.django.apps.kui.views.assembly import AssemblyListView
from consent.django.apps.kui.views.assembly import AssemblyReadView
from consent.django.apps.kui.views.assembly import AssemblyCreateView
from consent.django.apps.kui.views.assembly import AssemblyUpdateView
from consent.django.apps.kui.views.assembly import AssemblySearchView
from consent.django.apps.kui.views.assembly import AssemblyApiKeyView
from dm.view.basetest import MultiValueDict

def suite():
    suites = [
        unittest.makeSuite(TestAssemblyListView),
        #unittest.makeSuite(TestAssemblyReadView),
        #unittest.makeSuite(TestAssemblyApiKeyView),
        #unittest.makeSuite(TestAssemblyCreateView),
        #unittest.makeSuite(TestAssemblyUpdateView),
        #unittest.makeSuite(TestAssemblyUpdateViewPost),
        #unittest.makeSuite(TestAssemblySearchView),
        #unittest.makeSuite(TestAssemblySearchView2),
        #unittest.makeSuite(TestAssemblyFindView),
        #unittest.makeSuite(TestAssemblyFindView2),
    ]
    return unittest.TestSuite(suites)


class TestAssemblyListView(ViewTestCase):

    viewClass = AssemblyListView

    def getRequiredViewContext(self):
        return {
            'objectCount': self.registry.assemblies.count()
        }


class TestAssemblyReadView(ViewTestCase):

    viewClass = AssemblyReadView
    viewKwds = {'domainObjectKey': 'levin'}

    #def createViewKwds(self):
    #    kwds = super(TestAssemblyReadView, self).createViewKwds()
    #    kwds['domainObjectKey'] = 'levin'
    #    return kwds


class TestAssemblyApiKeyView(TestAssemblyReadView):

    viewClass = AssemblyApiKeyView
    viewerName = 'levin'


class TestAssemblyCreateView(ViewTestCase):

    viewClass = AssemblyCreateView


# Todo: Test create form submission (in various ways).


class TestAssemblyUpdateView(ViewTestCase):

    viewerName = 'levin'
    viewClass = AssemblyUpdateView

    def createViewKwds(self):
        kwds = super(TestAssemblyUpdateView, self).createViewKwds()
        kwds['domainObjectKey'] = 'levin'
        return kwds


class TestAssemblyUpdateViewPost(ViewTestCase):

    viewerName = 'levin'
    viewClass = AssemblyUpdateView
    viewKwds = {'domainObjectKey': 'levin'}
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/assemblies/levin/'

    def initPost(self):
        self.POST['assemblyName'] = 'levin'
        self.POST['fullname'] = 'Levin'
        self.POST['email'] = 'levin@appropriatesoftware.net'
        self.POST['password'] = ''
        self.POST['passwordconfirmation'] = ''


# Todo: Test update form submission (in various ways).


class TestAssemblySearchView(ViewTestCase):
    """Tests the userQuery parameter."""

    viewClass = AssemblySearchView

    def initPost(self):
        self.POST['userQuery'] = 'a'

    def getRequiredViewContext(self):
        return {
            'objectCount': 2
        }


class TestAssemblySearchView2(ViewTestCase):

    viewClass = AssemblySearchView

    def initPost(self):
        self.POST['userQuery'] = u'εἶναι'  # In *project* 'War and Peace ...'

    def getRequiredViewContext(self):
        return {
            'objectCount': 0
        }


class TestAssemblyFindView(ViewTestCase):
    """Test the startsWith parameter of the search view."""
    
    viewClass = AssemblySearchView
    viewKwds = {'startsWith': u'a'}

    def getRequiredViewContext(self):
        return {
            'objectCount': 1
        }


class TestAssemblyFindView2(ViewTestCase):
    """Tests the startsWith parameter of the search view."""
    
    viewClass = AssemblySearchView
    viewKwds = {'startsWith': u'ἶ'}

    def getRequiredViewContext(self):
        return {
            'objectCount': 0
        }

