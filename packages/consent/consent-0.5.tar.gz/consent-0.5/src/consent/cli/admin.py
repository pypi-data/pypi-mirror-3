import dm.cli.admin
import dm.environment
from consent.ioc import RequiredFeature
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'consent.django.settings.main'
os.umask(2)

class AdministrationUtility(dm.cli.admin.AdministrationUtility):

    def buildApplication(self):
        import consent.soleInstance
        self.appInstance = consent.soleInstance.application

    def constructSystemDictionary(self):
        from consent.dictionary import SystemDictionary
        return SystemDictionary()

    def takeDatabaseAction(self, actionName):
        from consent.utils.db import Database
        db = Database()
        actionMethod = getattr(db, actionName)
        actionMethod()

    def getDomainModelLoaderClass(self):
        from consent.migrate import DomainModelLoader
        return DomainModelLoader


class UtilityRunner(dm.cli.admin.UtilityRunner):

    systemName = 'consent'
    utilityClass = AdministrationUtility
    usage  = """Usage: %prog [options] [command]

Administer a Consent service, including its domain objects. 

To obtain information about the commands available run the "help" command.

    $ consent-admin help

Domain objects (e.g. people, projects, etc) can be administered by starting
a python shell from within interactive mode. Run "help shell" for more details.

Report bugs to <john.bywater@appropriatesoftware.net>."""

