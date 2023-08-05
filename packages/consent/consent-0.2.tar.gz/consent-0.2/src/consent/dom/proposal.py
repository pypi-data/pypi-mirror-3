from dm.dom.stateful import *
import consent.regexps

class Proposal(DatedStatefulObject):
    "Registered proposal."

    searchAttributeNames = ['title', 'description']

    assemblies = AggregatesMany('Consensus', key='assembly')
    title = String()
    description = Text()
    actions = Text()

    sortOnName = 'title'

    def getLabelValue(self):
        return self.title
