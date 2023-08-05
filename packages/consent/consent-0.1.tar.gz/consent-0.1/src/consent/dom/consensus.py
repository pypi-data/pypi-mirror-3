from dm.dom.stateful import *

class Consensus(DatedStatefulObject):

    assembly = HasA('Assembly', isImmutable=True, isUnique=True)
    proposal = HasA('Proposal', isImmutable=True, isUnique=True)

    isUnique = False

    ownerAttrNames = ['assembly', 'proposals']

    sortOnName = None

    def getLabelValue(self):
        return "%s at %s" % (self.proposal.getLabelValue(), self.assembly.getLabelValue())

