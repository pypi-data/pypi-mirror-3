import os
import commands

import dm.util.db

import consent.ioc

class Database(dm.util.db.Database):
    
    features = consent.ioc.features

    def _getSystemDictionary(self):
        import consent.dictionary
        systemDictionary = consent.dictionary.SystemDictionary()
        return systemDictionary
            
    def init(self):
        """
        Initialises service database by creating initial domain object records.
        """
        import consent.soleInstance
        commandSet = consent.soleInstance.application.commands
        domainModelCommandName = 'InitialiseDomainModel'
        domainModelCommandClass = commandSet[domainModelCommandName]
        domainModelCommand = domainModelCommandClass()
        domainModelCommand.execute()

