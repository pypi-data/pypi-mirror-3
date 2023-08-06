import dm.dom.builder

class ModelBuilder(dm.dom.builder.ModelBuilder):

    def construct(self):
        super(ModelBuilder, self).construct()
        self.loadApiKey()
        self.loadSite()
        self.loadAssembly()
        self.loadProposal()
        self.loadConsensus()
        self.loadMember()

    def loadPerson(self):
        from consent.dom.person import Person
        self.registry.registerDomainClass(Person)
        self.registry.people = Person.createRegister()
        Person.principalRegister = self.registry.people

    def loadSite(self):
        from consent.dom.site import Site
        self.registry.registerDomainClass(Site)
        self.registry.sites = Site.createRegister()

    def loadAssembly(self):
        from consent.dom.assembly import Assembly
        self.registry.registerDomainClass(Assembly)
        self.registry.assemblies = Assembly.createRegister()

    def loadProposal(self):
        from consent.dom.proposal import Proposal
        self.registry.registerDomainClass(Proposal)
        self.registry.proposals = Proposal.createRegister()

    def loadConsensus(self):
        from consent.dom.consensus import Consensus
        from consent.dom.consensus import ConsensusResult
        self.registry.registerDomainClass(Consensus)
        self.registry.registerDomainClass(ConsensusResult)
        self.registry.consensuses = Consensus.createRegister()
        self.registry.consensusResults = ConsensusResult.createRegister()

    def loadMember(self):
        from consent.dom.member import Member
        self.registry.registerDomainClass(Member)

    def loadApiKey(self):
        from dm.dom.apikey import ApiKey
        self.registry.registerDomainClass(ApiKey)
        self.registry.apiKeys = ApiKey.createRegister()

#    def loadPerson(self):
#        from consent.dom.person import Person
#        from consent.dom.person import SshKey
#        from consent.dom.person import PersonTicket
#        from consent.dom.person import Ticket
#        self.registry.registerDomainClass(Person)
#        self.registry.registerDomainClass(SshKey)
#        self.registry.registerDomainClass(PersonTicket)
#        self.registry.registerDomainClass(Ticket)
#        self.registry.people = Person.createRegister()
#        self.registry.sshKeys = SshKey.createRegister()
#        self.registry.tickets = Ticket.createRegister()
#        Person.principalRegister = self.registry.people
#        SshKey.principalRegister = self.registry.sshKeys
#        Ticket.principalRegister = self.registry.tickets
#
#    def loadProject(self):
#        from consent.dom.project import Project 
#        self.registry.registerDomainClass(Project)
#        self.registry.projects = Project.createRegister()
#        Project.principalRegister = self.registry.projects

#    def loadLicense(self):
#        from consent.dom.license import License  
#        self.registry.registerDomainClass(License)
#        from consent.dom.license import ProjectLicense  
#        self.registry.registerDomainClass(ProjectLicense)
#        self.registry.licenses = License.createRegister()
#        License.principalRegister = self.registry.licenses
#        self.registry.loadBackgroundRegister(self.registry.licenses)
#
#    def loadService(self):
#        from consent.dom.service import Service
#        self.registry.registerDomainClass(Service)
#        #self.registry.services = Service.createRegister()
#        #Service.principalRegister = self.registry.services
#
#    def loadMember(self):
#        from consent.dom.member import Member
#        self.registry.registerDomainClass(Member)
#        #self.registry.members = Member.createRegister()
#        #Member.principalRegister = self.registry.members
#
#    def loadFeedEntry(self):
#        from consent.dom.feedentry import FeedEntry
#        self.registry.registerDomainClass(FeedEntry)
#        self.registry.feedentries = FeedEntry.createRegister()
#        FeedEntry.principalRegister = self.registry.feedentries
#
#    def loadImage(self): # Replace dm.dom stuff -- consent does not need Image
#        pass
#
