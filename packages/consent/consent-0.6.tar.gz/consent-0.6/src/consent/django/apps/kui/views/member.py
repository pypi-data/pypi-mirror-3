from consent.django.apps.kui.views.site import SiteHasManyView
from dm.view.base import AbstractPendingView
from dm.view.base import AbstractListHasManyView
from dm.view.base import AbstractCreateHasManyView
from dm.view.base import AbstractApproveHasManyView
from dm.view.base import AbstractRejectHasManyView
from dm.view.base import AbstractReadHasManyView
from dm.view.base import AbstractUpdateHasManyView
from dm.view.base import AbstractDeleteHasManyView
import consent.command

from consent.command.emailjoinrequest import EmailJoinApprove, EmailJoinReject


class MemberView(SiteHasManyView):

    hasManyClassName = 'Member'

    def __init__(self, **kwds):
        super(MemberView, self).__init__(hasManyName='members', **kwds)

    def setContext(self):
        super(MemberView, self).setContext()
        self.context.update({
            'member' : self.getAssociationObject(),
        })

    def getMinorNavigationItem(self):
        return '/sites/%s/members/' % self.getSite().id

    def getMember(self):
        return self.getDomainClass('Member')

    def canCreateMember(self):
        if self._canCreateMember == None:
            protectedObject = self.getMember()
            self._canCreateMember = self.canCreate(protectedObject, site=self.getSite())
        return self._canCreateMember

    def canReadMember(self):
        if self._canReadMember == None:
            protectedObject = self.getMember()
            self._canReadMember = self.canRead(protectedObject, site=self.getSite())
        return self._canReadMember

    def canUpdateMember(self):
        if self._canUpdateMember == None:
            protectedObject = self.getMember()
            self._canUpdateMember = self.canUpdate(protectedObject, site=self.getSite())
        return self._canUpdateMember

    def canDeleteMember(self):
        if self._canDeleteMember == None:
            protectedObject = self.getMember()
            self._canDeleteMember = self.canDelete(protectedObject, site=self.getSite())
        return self._canDeleteMember


class MemberListView(MemberView, AbstractListHasManyView):

    templatePath = 'member/list'
    
    def canAccess(self):
        return self.canReadSite()


class MemberCreateView(MemberView, AbstractCreateHasManyView):

    templatePath = 'member/create'
    
    def canAccess(self):
        return self.canCreateMember()

    def makePostManipulateLocation(self):
        return '/sites/%s/%s/' % (
            self.domainObjectKey, self.hasManyName
        )

    def manipulateDomainObject(self):
        super(MemberCreateView, self).manipulateDomainObject()
        # Make sure that if this member is pending, we remove them from that list.
        # Todo: Push this logic down into the model: on create, if pending
        # register has object by key of created object, then delete pending object?
        site = self.domainObject
        personUri = self.getRequestParam('person')
        person = self.registry.dereference(personUri).target
        if person in site.members.pending:
            site.members.pending[person].delete()
            msg = "Deleted member '%s' from pending list for site %s since they were added as a member" % (person.name, site.name)
            self.logger.debug(msg)


class MemberUpdateView(MemberView, AbstractUpdateHasManyView):

    templatePath = 'member/update'
    
    def canAccess(self):
        return self.canUpdateMember()

    def makePostManipulateLocation(self):
        return '/sites/%s/%s/' % (
            self.domainObjectKey, self.hasManyName
        )


class MemberDeleteView(MemberView, AbstractDeleteHasManyView):

    templatePath = 'member/delete'
    
    def canAccess(self):
        self.member = self.getAssociationObject()
        return self.canDeleteMember()

    def makePostManipulateLocation(self):
        if self.session.person == self.member.person:
            return '/people/%s/' % self.session.person.name
        else:
            return '/sites/%s/%s/' % (
                self.domainObjectKey, self.hasManyName
            )


class MemberApproveView(MemberView, AbstractApproveHasManyView):

    templatePath = 'member/approve'
    #fieldNames = ['role']
    fieldNames = []
    
    def canAccess(self):
        return self.canCreateMember()

    def manipulateDomainObject(self):
        member = self.getManipulatedDomainObject()
        super(MemberApproveView, self).manipulateDomainObject()
        # Send e-mail to the member letting them know they got approved.
        emailCommand = EmailJoinApprove(member.site, member.person)
        emailCommand.execute()

    def makePostManipulateLocation(self):
        return '/sites/%s/members/' % (
            self.domainObjectKey
        )


class MemberRejectView(MemberView, AbstractRejectHasManyView):

    templatePath = 'member/reject'
    
    def canAccess(self):
        return self.canCreateMember()

    def manipulateDomainObject(self):
        member = self.getManipulatedDomainObject()
        super(MemberRejectView, self).manipulateDomainObject()
        # Send an e-mail to the member letting them know they got rejected.
        emailCommand = EmailJoinReject(member.site, member.person)
        emailCommand.execute()

    def makePostManipulateLocation(self):
        return '/sites/%s/members/' % (
            self.domainObjectKey
        )


def list(request, siteId=''):
    view = MemberListView(
        request=request,
        domainObjectKey=siteId,
    )
    return view.getResponse()
    
def create(request, siteId=''):
    view = MemberCreateView(
        request=request,
        domainObjectKey=siteId,
    )
    return view.getResponse()
    
def update(request, siteId='', personName=''):
    view = MemberUpdateView(
        request=request,
        domainObjectKey=siteId,
        hasManyKey=personName,
    )
    return view.getResponse()
    
def delete(request, siteId='', personName=''):
    view = MemberDeleteView(
        request=request,
        domainObjectKey=siteId,
        hasManyKey=personName,
    )
    return view.getResponse()

def approve(request, siteId='', personName=''):
    view = MemberApproveView(
        request=request,
        domainObjectKey=siteId,
        hasManyKey=personName,
    )
    return view.getResponse()

def reject(request, siteId='', personName=''):
    view = MemberRejectView(
        request=request,
        domainObjectKey=siteId,
        hasManyKey=personName,
    )
    return view.getResponse()

