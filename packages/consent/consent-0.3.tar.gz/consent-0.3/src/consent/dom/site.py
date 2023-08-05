from dm.dom.stateful import *

class Site(DatedStatefulObject):
    "Registered site."

    searchAttributeNames = ['title', 'description']

    title = String()
    description = Text()
    assemblies = AggregatesMany('Assembly', key='id')
    proposals = AggregatesMany('Proposal', key='id')

    isUnique = False

    def getLabelValue(self):
        return self.title

