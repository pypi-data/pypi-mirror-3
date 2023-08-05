from consent.django.apps.kui.views.assembly import AssemblyHasManyView
from dm.view.base import AbstractListHasManyView
from dm.view.base import AbstractCreateHasManyView
from dm.view.base import AbstractReadHasManyView
from dm.view.base import AbstractUpdateHasManyView
from dm.view.base import AbstractDeleteHasManyView


class ConsensusView(AssemblyHasManyView):

    hasManyClassName = 'Consensus'

    def __init__(self, **kwds):
        kwds['hasManyName'] = 'consensuses'
        super(ConsensusView, self).__init__(**kwds)
        self.consensus = None

    def getConsensus(self):
        return self.getAssociationObject()

    def setContext(self):
        super(ConsensusView, self).setContext()
        self.context.update({
            'consensus' : self.getConsensus(),
        })

    def getMajorNavigationItem(self):
        return '/sites/'

    def getMinorNavigationItem(self):
        return '/sites/%s/assemblies/' % self.getSite().id


class ConsensusListView(ConsensusView, AbstractListHasManyView):

    templatePath = 'consensus/list'

    def canAccess(self):
        return self.canReadConsensus()


#class ConsensusSearchView(ConsensusView, AbstractSearchHasManyView):
#
#    templatePath = 'consensus/search'
#    minorNavigationItem = '/consensuses/search/'
#   
#    def canAccess(self):
#        return self.canReadConsensus()
#

class ConsensusCreateView(ConsensusView, AbstractCreateHasManyView):

    templatePath = 'consensus/create'

    def canAccess(self):
        return self.canCreateConsensus()
        
    def makePostManipulateLocation(self):
        return '/sites/%s/assemblies/%s/' % (self.getSite().id, self.getAssembly().id)



class ConsensusReadView(ConsensusView, AbstractReadHasManyView):

    templatePath = 'consensus/read'

    def canAccess(self):
        return self.canReadConsensus()


class ConsensusUpdateView(ConsensusView, AbstractUpdateHasManyView):

    templatePath = 'consensus/update'

    def canAccess(self):
        return self.canUpdateConsensus()

    def makePostManipulateLocation(self):
        return '/sites/%s/assemblies/%s/' % (self.getSite().id, self.getAssembly().id)


class ConsensusDeleteView(ConsensusView, AbstractDeleteHasManyView):

    templatePath = 'consensus/delete'
    
    def canAccess(self):
        return self.canDeleteConsensus()

    def makePostManipulateLocation(self):
        return '/sites/%s/assemblies/%s/' % (self.getSite().id, self.getAssembly().id)



#def list(request, siteId):
#    view = ConsensusListView(
#        domainObjectKey=siteId,
#        request=request,
#    )
#    return view.getResponse()
    
#def search(request, siteId, startsWith=''):
#    view = ConsensusSearchView(
#        domainObjectKey=siteId,
#        request=request,
#        startsWith=startsWith,
#    )
#    return view.getResponse()
    
def create(request, siteId, assemblyId, returnPath=''):   
    view = ConsensusCreateView(
        request=request,
        domainObjectKey=assemblyId,
    )
    return view.getResponse()

#def read(request, siteId, consensusId):
#    view = ConsensusReadView(
#        request=request,
#        domainObjectKey=siteId,
#        hasManyKey=consensusId,
#    )
#    return view.getResponse()

def update(request, siteId, assemblyId, consensusId):
    view = ConsensusUpdateView(
        request=request,
        domainObjectKey=assemblyId,
        hasManyKey=consensusId,
    )
    return view.getResponse()

def delete(request, siteId, assemblyId, consensusId):
    view = ConsensusDeleteView(
        request=request,
        domainObjectKey=assemblyId,
        hasManyKey=consensusId,
    )
    return view.getResponse()

