from dm.dom.stateful import *

class Assembly(DatedStatefulObject):
    "Registered assembly."

    searchAttributeNames = ['title', 'description']
    ownerAttrNames = ['site', 'assemblies']

    title = String(default='General Assembly')
    description = MarkdownText(isRequired=False)
    starts = DateTime()
    site = HasA('Site')

    consensuses = AggregatesMany('Consensus', key='proposal')

    isUnique = False
    sortOnName = 'starts'
    sortAscending = False

    def getLabelValue(self):
        return self.title or self.name

    def resetReadableBy(self):
        members = [m for m in self.members]
        memberNames = [m.person.name for m in members]
        adminRole = self.registry.roles['Administrator']
        siteadmins = self.registry.people.findDomainObjects(role=adminRole)
        siteadminNames = [p.name for p in siteadmins]
        names = set(memberNames).union(set(siteadminNames))
        readableBy = ''
        if self.isHidden:
            readableBy = ':%s:' % ':'.join(names)
        if self.readableBy != readableBy:
            self.readableBy = readableBy
            self.saveSilently()
        for member in members:
            isChanged = False
            if member.readableBy != readableBy:
                member.readableBy = readableBy
                isChanged = True
            if member.isHidden != self.isHidden:
                member.isHidden = self.isHidden
                isChanged = True
            if isChanged:
                member.saveSilently()

