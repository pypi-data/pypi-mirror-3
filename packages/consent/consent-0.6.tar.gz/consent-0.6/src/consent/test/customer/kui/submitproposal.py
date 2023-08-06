from consent.test.customer.kui.base import KuiTestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestProposalRegister),
    ]
    return unittest.TestSuite(suites)


class ProposalTestCase(KuiTestCase):

    pass


class TestProposalRegister(ProposalTestCase):

    def setUp(self):
        super(TestProposalRegister, self).setUp()
        self.registerPerson()
        self.loginPerson('admin', 'pass')
        siteId = self.registerSite()
        self.urlSiteRead = '%s%s/' % (self.urlSites, siteId)

    def tearDown(self):
        super(TestProposalRegister, self).setUp()

    def test_submitproposal(self):
        self.getAssertContent(self.urlSiteRead, 'Proposals')
        url = '%sproposals/create/' % self.urlSiteRead
        self.getAssertContent(url, 'Submit Proposal')
        params = {
            'title': 'blah',
            'description': 'some description',
            'actions': 'some actions',
        }
        response = self.postAssertCode(url, params, code=302)
        location = response.headers['Location']
        self.failUnless(self.urlSiteRead in location, location)
        self.getAssertContent(location, params['title'])
        self.getAssertContent(location, params['description'])
        self.getAssertContent(location, params['actions'])

