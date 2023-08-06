from consent.test.customer.kui.base import KuiTestCase
import unittest
from dmclient.apiclient import ApiClient
from consent.dictionarywords import *

def suite():
    suites = [
        unittest.makeSuite(TestApi),
    ]
    return unittest.TestSuite(suites)


class TestApi(KuiTestCase):

    def setUp(self):
        super(TestApi, self).setUp()
        self.baseUrl = 'http://%s/api' % self.dictionary[DOMAIN_NAME]
        if 'trac' not in self.registry.plugins:
            self.registry.plugins.create('trac')
        if 'svn' not in self.registry.plugins:
            self.registry.plugins.create('svn')
        self.registerPerson()
        self.loginPerson()
        headerName = self.dictionary[API_KEY_HEADER_NAME]
        apiKey = self.registry.people['admin'].getApiKey().key
        self.api = ApiClient(baseUrl=self.baseUrl, isVerbose=False,
            apiKeyHeaderName=headerName, apiKey=apiKey)

    def test_project_and_services(self):
        resources = self.api.resources
        projects = resources.projects
        project = projects.create(name=self.kuiProjectName, title=self.kuiProjectTitle, description=self.kuiProjectDescription)
        self.failIf(project.services)
        trac = project.services.create(name='trac', plugin='/plugins/trac')
        svn = project.services.create(name='svn', plugin='/plugins/svn')
        self.failUnless(project.services)
        trac.repositories.append(svn)
        trac.save()
        project.members.create(person='/people/%s' % self.kuiPersonName, role='/roles/Administrator')
        self.getAssertContent('/%s/trac/browser' % self.kuiProjectName, 'svn', code=200)
        self.getAssertCode('/%s/trac/browser/svn' % self.kuiProjectName, code=200)

    def test_tickets(self):
        # Setup project.
        resources = self.api.resources
        projects = resources.projects
        project = projects.create(name=self.kuiProjectName, title=self.kuiProjectTitle, description=self.kuiProjectDescription)
        person = resources.people[self.kuiPersonName]
        project.members.create(person=person, role='/roles/Administrator')
        service = project.services.create(name='trac', plugin='/plugins/trac')
        self.failIf(person.tickets)
        self.failIf(service.tickets)
        # Create a ticket.
        ticket = service.tickets.create(owner=self.kuiPersonName, summary='apitest1')
        self.failUnlessEqual(ticket.url, 'http://consent.dev.localhost/api/tickets/%s' % (ticket.id))
        self.failUnlessEqual(ticket.service.url, 'http://consent.dev.localhost/api/projects/%s/services/trac' % (self.kuiProjectName))
        self.failUnlessEqual(ticket.owner, self.kuiPersonName)
        #self.failUnlessEqual(ticket.status, 'new')
        self.failUnlessEqual(ticket.summary, 'apitest1')
        self.failUnless(person.tickets)
        self.failUnless(service.tickets)
        # Todo: Check the ticket is created in Trac.
        # Update the ticket.
        ticket.summary = 'apitest2'
        ticket.save()
        # Todo: Check the ticket is updated in Trac.
        # Delete the ticket.
        ticket.delete()
        self.failIf(service.tickets)
        # Todo: Check the ticket is closed in Trac.

