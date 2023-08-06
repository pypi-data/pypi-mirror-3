import unittest
from consent.dom.testunit import TestCase
import consent.dom.proposal
from consent.exceptions import *

def suite():
    suites = [
        unittest.makeSuite(TestProposal),
    ]
    return unittest.TestSuite(suites)


class TestProposal(TestCase):
    "TestCase for the Proposal class."
    
    def setUp(self):
        super(TestProposal, self).setUp()
        self.fixtureName = 'TestProposal'
        self.proposals = self.registry.proposals
        self.proposal = self.proposals.create(title=self.fixtureName)

    def tearDown(self):
        if self.proposal:
            self.proposal.delete()
            self.proposal.purge()
            self.proposal = None
   
    def test_new(self):
        self.failUnless(self.proposal, "New proposal could not be created.")
        self.assertEquals(self.proposal.state, self.activeState,
            "Not in active state after create."
        )
        self.failUnlessEqual(self.proposal.getUri('/x'), '/x/proposals/%s' % self.proposal.id)

    def test_find(self):
        self.failUnless(self.registry.proposals[self.proposal.id],
            "New proposal could not be found."
        )
        self.failUnlessRaises(KforgeRegistryKeyError,
            self.registry.proposals.__getitem__, 9999999
        )

    def test_delete(self):
        self.assertEquals(self.proposal.state, self.activeState,
            "Not in active state to start with: " + self.proposal.state.name
        )
        self.proposal.delete()
        self.assertEquals(self.proposal.state, self.deletedState,
            "Not deleted after deleting active object: "+self.proposal.state.name
        )
        self.proposal.undelete()
        self.assertEquals(self.proposal.state, self.activeState,
            "Not active state: %s" % self.proposal.state
        )
        self.proposal.delete()
        self.assertEquals(self.proposal.state, self.deletedState,
            "Not deleted state: %s" % self.proposal.state
        )

    def test_save(self):
        self.assertEquals(self.proposal.title, self.fixtureName)
        self.proposal.title = "Test Proposal"
        self.assertEquals(self.proposal.title, "Test Proposal",
            "Proposal doesn't have attribute."
        )
        self.proposal.save()
        proposal = self.proposals[self.proposal.id]
        self.assertEquals(proposal.title, "Test Proposal",
            "Retrieved proposal has wrong fullname."
        )
        proposal.title = "Other Proposal"
        self.assertEquals(self.proposal.title, "Other Proposal",
            "Suspect duplicate domain objects!!"
        )
        
    def test_count(self):
        self.failUnless(self.proposals.count(), "Problem with proposal count.")

