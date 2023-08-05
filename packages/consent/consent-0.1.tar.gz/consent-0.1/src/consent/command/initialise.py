from dm.command.initialise import InitialiseDomainModel
from dm.command.accesscontrol import GrantStandardSystemAccess

class InitialiseDomainModel(InitialiseDomainModel):

    def execute(self):
        super(InitialiseDomainModel, self).execute()

    def createProtectionObjects(self):
        super(InitialiseDomainModel, self).createProtectionObjects()
        self.registry.protectionObjects.create('Assembly')
        self.registry.protectionObjects.create('Proposal')
        self.registry.protectionObjects.create('Consensus')


    def createGrants(self):
        super(InitialiseDomainModel, self).createGrants()
        self.grantStandardSystemAccess('Assembly')
        self.grantStandardSystemAccess('Proposal')
        self.grantStandardSystemAccess('Consensus')

