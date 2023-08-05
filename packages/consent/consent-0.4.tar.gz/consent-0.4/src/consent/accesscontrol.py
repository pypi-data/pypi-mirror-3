from dm.accesscontrol import SystemAccessController
from dm.exceptions import *

class AccessController(SystemAccessController):

    def isAccessAuthorised(self, **kwds):
        return super(AccessController, self).isAccessAuthorised(**kwds)

    def assertAccessNotAuthorised(self):
        super(AccessController, self).assertAccessNotAuthorised()
        if self.action.name in ['Read', 'Update', 'Delete'] \
        and self.person == self.protectedObject:
            raise AccessIsAuthorised('personal access')

           

