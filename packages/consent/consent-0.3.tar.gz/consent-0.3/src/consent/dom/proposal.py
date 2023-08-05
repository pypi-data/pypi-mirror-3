from dm.dom.stateful import *
import consent.regexps

class Proposal(DatedStatefulObject):
    "Registered proposal."

    searchAttributeNames = ['title', 'description']

    consensuses = AggregatesMany('Consensus', key='assembly')
    site = HasA('Site')
    title = String()
    description = Text()
    actions = Text()

    sortOnName = 'title'

    def getLabelValue(self):
        return self.title
