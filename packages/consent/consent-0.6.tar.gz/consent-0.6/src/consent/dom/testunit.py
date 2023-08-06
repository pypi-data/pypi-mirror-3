import consent.testunit

class TestCase(consent.testunit.TestCase):
    "Base class for DomainObject TestCases."
    
    def setUp(self):
        super(TestCase, self).setUp()
        self.activeState = self.registry.states['active']
        self.deletedState = self.registry.states['deleted']

