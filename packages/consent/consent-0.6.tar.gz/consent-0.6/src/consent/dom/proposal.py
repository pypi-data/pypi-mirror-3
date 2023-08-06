from dm.dom.stateful import *
import consent.regexps

class Proposal(DatedStatefulObject):
    "Registered proposal."

    searchAttributeNames = ['title', 'description', 'actions']
    ownerAttrNames = ['site', 'proposals']

    consensuses = AggregatesMany('Consensus', key='assembly')
    site = HasA('Site')
    title = String()
    description = MarkdownText()
    actions = MarkdownText(isRequired=False)

    sortOnName = 'title'
    sortAscending = False

    def getLabelValue(self):
        return self.title
