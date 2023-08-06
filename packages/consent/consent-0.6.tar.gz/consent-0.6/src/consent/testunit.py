import dm.testunit
import consent.builder
import consent.soleInstance

class TestCase(dm.testunit.TestCase):
    pass

class ApplicationTestSuite(dm.testunit.ApplicationTestSuite):
    appBuilderClass = consent.builder.ApplicationBuilder

