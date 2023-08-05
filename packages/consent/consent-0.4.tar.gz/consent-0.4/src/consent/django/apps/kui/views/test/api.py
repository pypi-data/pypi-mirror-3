import unittest
from consent.django.apps.kui.views.api import ApiView
from dm.view.apitest import ApiViewTestCase # Test case for single request.
from dm.view.testunit import ApiTestCase  # Test case for CRUD requests on a register.
from consent.django.apps.kui.views.api import ConsentApiView
from dm.dictionarywords import SYSTEM_VERSION

def suite():
    suites = [
        # Single request test cases.
        unittest.makeSuite(TestApiGetOk),
        unittest.makeSuite(TestApiGetLicensesOk),
        unittest.makeSuite(TestApiGetRolesOk),
        # CRUD requests test cases.
        unittest.makeSuite(TestProject),
    ]
    return unittest.TestSuite(suites)


class TestApiGetOk(ApiViewTestCase):
    requestPath = '/api'
    requiredResponseClassName = 'HttpResponse'
    requiredResponseStatus = 200
    requiredResponseData = [
        u'http://consent.dev.localhost/api/licenses',
        u'http://consent.dev.localhost/api/people',
        u'http://consent.dev.localhost/api/projects',
        u'http://consent.dev.localhost/api/roles',
        u'http://consent.dev.localhost/api/systems',
        u'http://consent.dev.localhost/api/tickets',
    ]


class TestApiGetLicensesOk(ApiViewTestCase):
    requestPath = '/api/licenses'
    requiredResponseClassName = 'HttpResponse'
    requiredResponseStatus = 200
    requiredResponseData = [
        "http://consent.dev.localhost/api/licenses/3",
        "http://consent.dev.localhost/api/licenses/5",
        "http://consent.dev.localhost/api/licenses/4",
        "http://consent.dev.localhost/api/licenses/2",
        "http://consent.dev.localhost/api/licenses/1",
    ]


class TestApiGetRolesOk(ApiViewTestCase):
    requestPath = '/api/roles'
    requiredResponseClassName = 'HttpResponse'
    requiredResponseStatus = 200
    requiredResponseData = [
        "http://consent.dev.localhost/api/roles/Administrator",
        "http://consent.dev.localhost/api/roles/Developer",
        "http://consent.dev.localhost/api/roles/Friend",
        "http://consent.dev.localhost/api/roles/Visitor",
    ]


class ConsentApiTestCase(ApiTestCase):

    viewClass = ConsentApiView
    apiKeyHeaderName = 'HTTP_X_KFORGE_API_KEY'


class TestProject(ConsentApiTestCase):

    registerName = 'projects'
    newEntity = {'name': 'xxxx', 'title': 'My Project', 'description': 'A project by me.', 'licenses': ['http://consent.dev.localhost/api/licenses/1']}
    entityKey = 'xxxx'
    notFoundKey = 'zzzz'
    changedEntity = {'name': 'xxxx', 'title': 'Your Project', 'description': 'A project by you.', 'licenses': ['http://consent.dev.localhost/api/licenses/1']}

    def tearDown(self):
        key = self.newEntity['name']
        if key in self.registry.projects:
            del(self.registry.projects[key])
        key = self.changedEntity['name']
        if key in self.registry.projects:
            del(self.registry.projects[key])
        super(TestProject, self).tearDown()

