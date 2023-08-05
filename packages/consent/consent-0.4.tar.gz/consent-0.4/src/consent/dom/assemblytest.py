import unittest
from consent.exceptions import *
from consent.dom.testunit import TestCase

def suite():
    suites = [
        unittest.makeSuite(TestAssembly),
    ]
    return unittest.TestSuite(suites)

class AssemblyTestCase(TestCase):

    def setUp(self):
        super(AssemblyTestCase, self).setUp()
        self.fixtureTitle = 'TestAssembly'
        self.assemblies = self.registry.assemblies
        self.assembly = self.assemblies.create(title=self.fixtureTitle)

    def tearDown(self):
        if self.assembly:
            self.assembly.delete()
            self.assembly.purge()
            self.assembly = None
        super(AssemblyTestCase, self).tearDown()

    
class TestAssembly(AssemblyTestCase):
    
    def test_new(self):
        self.failUnless(self.assembly, "New assembly could not be created.")
        # Suspended isUnique=True.
        #self.failUnlessRaises(ConsentDomError, self.assemblies.create, self.fixtureTitle)

    def test___getitem__(self):
        self.failUnless(self.assemblies.findSingleDomainObject(title=self.fixtureTitle), "New assembly could not be found.")
        self.failUnlessRaises(KforgeRegistryKeyError, self.assemblies.__getitem__, 'TestAlien')

    def test_delete(self):
        self.assembly.delete()
        self.assembly.purge()
        self.failIf(self.assemblies.findSingleDomainObject(title=self.fixtureTitle))

    def test_save(self):
        self.assertEquals(self.assembly.title, self.fixtureTitle)
        self.assembly.title = "Test Title"
        self.assembly.purpose = "Test Purpose"
        self.assembly.description = "Test Description"
        newFixtureTitle = "Test Title"
        self.assertEquals(self.assembly.title, newFixtureTitle, "Assembly doesn't have title attribute.")
        self.assertEquals(self.assembly.purpose, "Test Purpose", "Assembly doesn't have purpose attribute.")
        self.assertEquals(self.assembly.description, "Test Description", "Assembly doesn't have purpose attribute.")
        self.assembly.save()
        assembly = self.assemblies.findSingleDomainObject(title=newFixtureTitle)
        self.assertEquals(assembly.title, "Test Title", "Retrieved assembly has wrong title.")
        self.assertEquals(assembly.purpose, "Test Purpose", "Assembly doesn't have purpose attribute.")
        self.assertEquals(assembly.description, "Test Description", "Assembly doesn't have purpose attribute.")
        assembly.title = "Other Title"
        self.assertEquals(self.assembly.title, "Other Title", "Suspect duplicate domain objects!!")

