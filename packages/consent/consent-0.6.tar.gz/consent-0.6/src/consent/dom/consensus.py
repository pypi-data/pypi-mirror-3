from dm.dom.stateful import *

class Consensus(DatedStatefulObject):

    assembly = HasA('Assembly', isImmutable=True, isUnique=True)
    proposal = HasA('Proposal', isImmutable=True, isUnique=True)
    result = HasA('ConsensusResult', default='Untested', isInitable=False, isRequired=False)

    isUnique = False

    ownerAttrNames = ['assembly', 'consensuses']

    sortOnName = None

    def getLabelValue(self):
        return "%s at %s" % (self.proposal.getLabelValue(), self.assembly.getLabelValue())


class ConsensusResult(NamedObject): pass

