from dm.command.initialise import InitialiseDomainModel
from dm.command.accesscontrol import GrantStandardSystemAccess

class InitialiseDomainModel(InitialiseDomainModel):

    def execute(self):
        super(InitialiseDomainModel, self).execute()
        self.createConsensusResults()

    def createProtectionObjects(self):
        super(InitialiseDomainModel, self).createProtectionObjects()
        self.registry.protectionObjects.create('Site')
        self.registry.protectionObjects.create('Assembly')
        self.registry.protectionObjects.create('Proposal')
        self.registry.protectionObjects.create('Consensus')
        self.registry.protectionObjects.create('Member')


    def createGrants(self):
        super(InitialiseDomainModel, self).createGrants()
        self.grantStandardSystemAccess('Site')
        self.grantStandardSystemAccess('Assembly')
        self.grantStandardSystemAccess('Proposal')
        self.grantStandardSystemAccess('Consensus')
        self.grantStandardSystemAccess('Member')

    def createConsensusResults(self):
        self.registry.consensusResults.create('Consensus')
        self.registry.consensusResults.create('Blocked')
        self.registry.consensusResults.create('Untested')

    def setUpTestFixtures(self):
        super(InitialiseDomainModel, self).setUpTestFixtures()
        self.registry.sites.create(title='Blue Square', description='Some place')
