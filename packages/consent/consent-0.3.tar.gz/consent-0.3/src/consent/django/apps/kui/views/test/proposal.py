# -*- coding=utf-8 -*-
import unittest
from consent.django.apps.kui.views.test.base import ViewTestCase
from consent.django.apps.kui.views.proposal import ProposalListView
from consent.django.apps.kui.views.proposal import ProposalReadView
from consent.django.apps.kui.views.proposal import ProposalCreateView
from consent.django.apps.kui.views.proposal import ProposalUpdateView
from consent.django.apps.kui.views.proposal import ProposalSearchView
from consent.django.apps.kui.views.proposal import ProposalApiKeyView
from dm.view.basetest import MultiValueDict

def suite():
    suites = [
        unittest.makeSuite(TestProposalListView),
        #unittest.makeSuite(TestProposalReadView),
        #unittest.makeSuite(TestProposalApiKeyView),
        #unittest.makeSuite(TestProposalCreateView),
        #unittest.makeSuite(TestProposalUpdateView),
        #unittest.makeSuite(TestProposalUpdateViewPost),
        #unittest.makeSuite(TestProposalSearchView),
        #unittest.makeSuite(TestProposalSearchView2),
        #unittest.makeSuite(TestProposalFindView),
        #unittest.makeSuite(TestProposalFindView2),
    ]
    return unittest.TestSuite(suites)


class TestProposalListView(ViewTestCase):

    viewClass = ProposalListView

    def getRequiredViewContext(self):
        return {
            'objectCount': self.registry.proposals.count()
        }


class TestProposalReadView(ViewTestCase):

    viewClass = ProposalReadView
    viewKwds = {'domainObjectKey': 'levin'}

    #def createViewKwds(self):
    #    kwds = super(TestProposalReadView, self).createViewKwds()
    #    kwds['domainObjectKey'] = 'levin'
    #    return kwds


class TestProposalApiKeyView(TestProposalReadView):

    viewClass = ProposalApiKeyView
    viewerName = 'levin'


class TestProposalCreateView(ViewTestCase):

    viewClass = ProposalCreateView


# Todo: Test create form submission (in various ways).


class TestProposalUpdateView(ViewTestCase):

    viewerName = 'levin'
    viewClass = ProposalUpdateView

    def createViewKwds(self):
        kwds = super(TestProposalUpdateView, self).createViewKwds()
        kwds['domainObjectKey'] = 'levin'
        return kwds


class TestProposalUpdateViewPost(ViewTestCase):

    viewerName = 'levin'
    viewClass = ProposalUpdateView
    viewKwds = {'domainObjectKey': 'levin'}
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/proposals/levin/'

    def initPost(self):
        self.POST['proposalName'] = 'levin'
        self.POST['fullname'] = 'Levin'
        self.POST['email'] = 'levin@appropriatesoftware.net'
        self.POST['password'] = ''
        self.POST['passwordconfirmation'] = ''


# Todo: Test update form submission (in various ways).


class TestProposalSearchView(ViewTestCase):
    """Tests the userQuery parameter."""

    viewClass = ProposalSearchView

    def initPost(self):
        self.POST['userQuery'] = 'a'

    def getRequiredViewContext(self):
        return {
            'objectCount': 2
        }


class TestProposalSearchView2(ViewTestCase):

    viewClass = ProposalSearchView

    def initPost(self):
        self.POST['userQuery'] = u'εἶναι'  # In *project* 'War and Peace ...'

    def getRequiredViewContext(self):
        return {
            'objectCount': 0
        }


class TestProposalFindView(ViewTestCase):
    """Test the startsWith parameter of the search view."""
    
    viewClass = ProposalSearchView
    viewKwds = {'startsWith': u'a'}

    def getRequiredViewContext(self):
        return {
            'objectCount': 1
        }


class TestProposalFindView2(ViewTestCase):
    """Tests the startsWith parameter of the search view."""
    
    viewClass = ProposalSearchView
    viewKwds = {'startsWith': u'ἶ'}

    def getRequiredViewContext(self):
        return {
            'objectCount': 0
        }


