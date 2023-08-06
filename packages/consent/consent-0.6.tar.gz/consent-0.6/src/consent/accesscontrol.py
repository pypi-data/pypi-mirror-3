from dm.accesscontrol import SystemAccessController
from dm.exceptions import *

class SiteAccessController(SystemAccessController):

    def isAccessAuthorised(self, site=None, **kwds):
        self.site = site
        return super(SiteAccessController, self).isAccessAuthorised(**kwds)

    def assertAccessNotAuthorised(self):
        self.assertMembershipNotAuthorised()
        super(SiteAccessController, self).assertAccessNotAuthorised()
        self.assertPersonAccessNotAuthorised()

    def assertPersonalAccessNotAuthorised(self):
        if self.action.name in ['Read', 'Update', 'Delete'] \
        and self.person == self.protectedObject:
            raise AccessIsAuthorised('personal access')

    def assertMembershipNotAuthorised(self):
        if self.site:
            try:
                role = self.person.sites[self.site].role
            except KforgeRegistryKeyError, inst:
                pass
            else:
                self.assertRoleNotAuthorised(role, "site %s role" % role.name.lower())
            if not self.alsoCheckVisitor():
                return
            try:
                role = self.getVisitor().sites[self.site].role
            except KforgeRegistryKeyError, inst:
                pass
            else:
                self.assertRoleNotAuthorised(role, "visitor's site %s role" % role.name.lower())

    def makeMemoName(self, person, actionName, protectedObject):
        # Make sure service plugin memo names are distinct between sites.
        # Todo: Change service access control to use service object.
        memoName = super(SiteAccessController, self).makeMemoName(person, actionName, protectedObject)
        if self.site:
            siteTag = self.site.id
        else:
            siteTag = None
        memoName = "Site.%s.%s" % (siteTag, memoName)
        return memoName

