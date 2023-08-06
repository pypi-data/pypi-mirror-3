from consent.django.apps.kui.views.site import SiteHasManyView
from dm.view.base import AbstractListHasManyView
from dm.view.base import AbstractSearchHasManyView
from dm.view.base import AbstractCreateHasManyView
from dm.view.base import AbstractReadHasManyView
from dm.view.base import AbstractUpdateHasManyView
from dm.view.base import AbstractDeleteHasManyView


class ProposalView(SiteHasManyView):

    hasManyClassName = 'Proposal'
    majorNavigationItem = '/proposals/'
    minorNavigationItem = '/proposals/'

    def __init__(self, **kwds):
        kwds['hasManyName'] = 'proposals'
        super(ProposalView, self).__init__(**kwds)
        self.proposal = None

    def setContext(self):
        super(ProposalView, self).setContext()
        self.context.update({
            'proposal' : self.getProposal(),
            'proposals' : self.context.get('domainObjectList', []),
            'proposalsCount' : self.context.get('objectCount', 0),
        })

    def getMajorNavigationItem(self):
        return '/sites/'

    def getMinorNavigationItem(self):
        return '/sites/%s/proposals/' % self.getSite().id

    def canCreateProposal(self):
        if self._canCreateProposal == None:
            protectedObject = self.getDomainClass('Proposal')
            self._canCreateProposal = self.canCreate(protectedObject, site=self.getSite())
        return self._canCreateProposal

    def canReadProposal(self):
        if self._canReadProposal == None:
            protectedObject = self.getProposal()
            self._canReadProposal = self.canRead(protectedObject, site=self.getSite())
        return self._canReadProposal

    def canUpdateProposal(self):
        if self._canUpdateProposal == None:
            protectedObject = self.getProposal()
            self._canUpdateProposal = self.canUpdate(protectedObject, site=self.getSite())
        return self._canUpdateProposal

    def canDeleteProposal(self):
        if self._canDeleteProposal == None:
            protectedObject = self.getProposal()
            self._canDeleteProposal = self.canDelete(protectedObject, site=self.getSite())
        return self._canDeleteProposal

    def getProposal(self):
        return self.getDomainClass('Proposal')


class ProposalListView(ProposalView, AbstractListHasManyView):

    templatePath = 'proposal/list'

    def canAccess(self):
        return self.canReadSite()

    def setContext(self):
        super(ProposalListView, self).setContext()
        proposals = self.getSite().proposals
        proposalsCount = proposals.count()
        self.context.update({
            'proposals' : proposals,
            'proposalsCount' : proposalsCount,
        })


class ProposalSearchView(ProposalView, AbstractSearchHasManyView):

    templatePath = 'proposal/search'
   
    def canAccess(self):
        return self.canReadProposal()

    def setContext(self):
        super(ProposalSearchView, self).setContext()
        self.context.update({
            'proposals' : self.context.get('domainObjectList', []),
            'proposalsCount' : self.context.get('objectCount', 0),
        })


class ProposalCreateView(ProposalView, AbstractCreateHasManyView):

    templatePath = 'proposal/create'

    def canAccess(self):
        return self.canCreateProposal()
        
    def makePostManipulateLocation(self):
        return '/sites/%s/proposals/%s/' % (self.domainObjectKey, self.associationObject.id)



class ProposalReadView(ProposalView, AbstractReadHasManyView):

    templatePath = 'proposal/read'

    def canAccess(self):
        return self.canReadProposal()

    def getProposal(self):
        return self.getAssociationObject()


class ProposalUpdateView(ProposalView, AbstractUpdateHasManyView):

    templatePath = 'proposal/update'

    def canAccess(self):
        return self.canUpdateProposal()

    def getProposal(self):
        return self.getAssociationObject()

    def makePostManipulateLocation(self):
        return '/sites/%s/proposals/%s/' % (self.domainObjectKey, self.associationObject.id)


class ProposalDeleteView(ProposalView, AbstractDeleteHasManyView):

    templatePath = 'proposal/delete'
    
    def canAccess(self):
        return self.canDeleteProposal()

    def makePostManipulateLocation(self):
        return '/proposals/'



def list(request, siteId):
    view = ProposalListView(
        domainObjectKey=siteId,
        request=request,
    )
    return view.getResponse()
    
def search(request, siteId, startsWith=''):
    view = ProposalSearchView(
        domainObjectKey=siteId,
        request=request,
        startsWith=startsWith,
    )
    return view.getResponse()
    
def create(request, siteId, returnPath=''):   
    view = ProposalCreateView(
        request=request,
        domainObjectKey=siteId,
    )
    return view.getResponse()

def read(request, siteId, proposalId):
    view = ProposalReadView(
        request=request,
        domainObjectKey=siteId,
        hasManyKey=proposalId,
    )
    return view.getResponse()

def update(request, siteId, proposalId):
    view = ProposalUpdateView(
        request=request,
        domainObjectKey=siteId,
        hasManyKey=proposalId,
    )
    return view.getResponse()

def delete(request, siteId, proposalId):
    view = ProposalDeleteView(
        request=request,
        domainObjectKey=siteId,
        hasManyKey=proposalId,
    )
    return view.getResponse()

