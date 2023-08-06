from dm.dom.stateful import *
from consent.dictionarywords import MEMBER_ROLE_NAME

class Member(DatedStatefulObject):
    """
    Registers membership of a site by a person. 
    Associates a Person, a Site, and a Role.
    """

    site = HasA('Site', isImmutable=True, isUnique=True)
    person = HasA('Person', isImmutable=True, isUnique=True)
    role = HasA('Role', default=StatefulObject.dictionary[MEMBER_ROLE_NAME])

    isUnique = False

    ownerAttrNames = ['site', 'members']

    sortOnName = None

    def initialise(self, register=None):
        super(Member, self).initialise(register)
        if not self.role:
            roleName = self.dictionary[MEMBER_ROLE_NAME]
            self.role = self.registry.roles[roleName]
            self.isChanged = True

    def purge (self):
        super(Member, self).purge()
        # Todo: Refector to drop these references by reflection off the model (the are all 'HasA').
        self.site = None
        self.person = None
        self.role = None

    def getLabelValue(self):
        return "%s-%s" % (
            self.person.getLabelValue(),
            self.site.getLabelValue(),
        )


