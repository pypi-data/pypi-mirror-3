import dm.builder
from consent.ioc import *

class ApplicationBuilder(dm.builder.ApplicationBuilder):
    """
    Extends core builder by adding new application features, and by overriding
    core features with replacements for, or extensions of, core features.
    """

    def findSystemDictionary(self):
        import consent.dictionary
        return consent.dictionary.SystemDictionary()

    def findModelBuilder(self):
        import consent.dom.builder
        return consent.dom.builder.ModelBuilder()

    def findAccessController(self):
        import consent.accesscontrol
        return consent.accesscontrol.SiteAccessController()

    def findCommandSet(self):
        import consent.command
        return consent.command.__dict__

