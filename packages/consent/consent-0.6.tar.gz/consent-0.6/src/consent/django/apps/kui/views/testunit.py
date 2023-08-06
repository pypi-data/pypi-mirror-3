import consent.testunit

class TestCase(consent.testunit.TestCase):
    "Base class for View TestCases."
    
    def buildRequest(self):
        return None

