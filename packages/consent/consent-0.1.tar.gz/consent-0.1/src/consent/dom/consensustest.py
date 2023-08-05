import unittest
from consent.exceptions import *
from consent.dom.testunit import TestCase

def suite():
    suites = [
        unittest.makeSuite(TestConsensus),
    ]
    return unittest.TestSuite(suites)

class TestConsensus(TestCase):
    
    def setUp(self):
        super(TestConsensus, self).setUp()
        self.proposal = self.registry.proposals.create(title='TestConsensusProposal')
        self.assembly = self.registry.assemblies.create(title='TestConsensusAssembly')
        try:
            self.proposals = self.assembly.proposals.create(self.proposal)
        except:
            self.assembly.delete()
            self.assembly.purge()
            self.proposal.delete()
            self.proposal.purge()
            raise

    def tearDown(self):
        self.assembly.delete()
        self.assembly.purge()
        self.proposal.delete()
        self.proposal.purge()

    def test(self):    
        # Check proposals in all and active lists.
        self.failUnless(self.proposal in self.assembly.proposals.all)
        self.failUnless(self.proposal in self.assembly.proposals)
        # Check proposals not in pending or deleted lists.
        self.failIf(self.proposal in self.assembly.proposals.deleted)
        self.failIf(self.proposal in self.assembly.proposals.pending)
        # Check delete.
        self.proposal.delete()
        # Check proposal in all and deleted lists.
        listAll = list(self.assembly.proposals.all)
        self.failUnless(self.proposal in self.assembly.proposals.all, listAll)
        self.failUnless(self.proposal in self.assembly.proposals.deleted, listAll)
        # Check proposal not in active or pending lists.
        self.failIf(self.proposal in self.assembly.proposals, listAll)
        self.failIf(self.proposal in self.assembly.proposals.pending, listAll)


