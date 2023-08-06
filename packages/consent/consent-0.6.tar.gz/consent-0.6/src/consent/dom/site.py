from dm.dom.stateful import *
from datetime import datetime

class Site(DatedStatefulObject):
    "Registered site."

    searchAttributeNames = ['title', 'description']

    title = String()
    description = Text()
    assemblies = AggregatesMany('Assembly', key='id')
    proposals = AggregatesMany('Proposal', key='id')
    members = AggregatesMany('Member', key='person')

    isUnique = False
    sortOnName = 'title'

    def getLabelValue(self):
        return self.title

    def getUpcomingAssemblies(self):
        assemblies = self.assemblies.findDomainObjects(__startsAfter__=datetime.now())
        assemblies.reverse()
        return assemblies

    def getConsensusProposals(self):
        proposals = []
        for proposal in self.proposals:
            for consensus in proposal.consensuses:
                if consensus.result.name == 'Consensus':
                    proposals.append(proposal)
                    break # Once is enough.
        return proposals
