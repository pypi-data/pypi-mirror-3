from consent.django.apps.kui.views.site import SiteHasManyView
from dm.view.base import AbstractListHasManyView
from dm.view.base import AbstractSearchHasManyView
from dm.view.base import AbstractCreateHasManyView
from dm.view.base import AbstractReadHasManyView
from dm.view.base import AbstractUpdateHasManyView
from dm.view.base import AbstractDeleteHasManyView


class AssemblyView(SiteHasManyView):

    hasManyClassName = 'Assembly'
    majorNavigationItem = '/assemblies/'
    minorNavigationItem = '/assemblies/'

    def __init__(self, **kwds):
        if not kwds.get('hasManyName'):
            kwds['hasManyName'] = 'assemblies'
        super(AssemblyView, self).__init__(**kwds)
        self.assembly = None


    def getAssembly(self):
        return self.getDomainClass('Assembly')

    def setContext(self):
        super(AssemblyView, self).setContext()
        self.context.update({
            'assembly' : self.getAssembly(),
        })

    def getMajorNavigationItem(self):
        return '/sites/'

    def getMinorNavigationItem(self):
        return '/sites/%s/assemblies/' % self.getSite().id

    def canCreateAssembly(self):
        if self._canCreateAssembly == None:
            protectedObject = self.getDomainClass('Assembly')
            self._canCreateAssembly = self.canCreate(protectedObject, site=self.getSite())
        return self._canCreateAssembly

    def canReadAssembly(self):
        if self._canReadAssembly == None:
            protectedObject = self.getAssembly()
            self._canReadAssembly = self.canRead(protectedObject, site=self.getSite())
        return self._canReadAssembly

    def canUpdateAssembly(self):
        if self._canUpdateAssembly == None:
            protectedObject = self.getAssembly()
            self._canUpdateAssembly = self.canUpdate(protectedObject, site=self.getSite())
        return self._canUpdateAssembly

    def canDeleteAssembly(self):
        if self._canDeleteAssembly == None:
            protectedObject = self.getAssembly()
            self._canDeleteAssembly = self.canDelete(protectedObject, site=self.getSite())
        return self._canDeleteAssembly


class AssemblyListView(AssemblyView, AbstractListHasManyView):

    templatePath = 'assembly/list'

    def canAccess(self):
        return self.canReadSite()

    def setContext(self):
        super(AssemblyListView, self).setContext()
        assemblies = self.getSite().assemblies
        assembliesCount = assemblies.count()
        self.context.update({
            'assemblies' : assemblies,
            'assembliesCount' : assembliesCount,
        })


class AssemblySearchView(AssemblyView, AbstractSearchHasManyView):

    templatePath = 'assembly/search'
   
    def canAccess(self):
        return self.canReadAssembly()

    def setContext(self):
        super(AssemblySearchView, self).setContext()
        self.context.update({
            'assemblies' : self.context.get('domainObjectList', []),
            'assembliesCount' : self.context.get('objectCount', 0),
        })


class AssemblyCreateView(AssemblyView, AbstractCreateHasManyView):

    templatePath = 'assembly/create'

    def canAccess(self):
        return self.canCreateAssembly()
        
    def makePostManipulateLocation(self):
        return '/sites/%s/assemblies/%s/' % (self.domainObjectKey, self.associationObject.id)



class AssemblyReadView(AssemblyView, AbstractReadHasManyView):

    templatePath = 'assembly/read'

    def canAccess(self):
        return self.canReadAssembly()

    def getAssembly(self):
        return self.getAssociationObject()


class AssemblyUpdateView(AssemblyView, AbstractUpdateHasManyView):

    templatePath = 'assembly/update'

    def canAccess(self):
        return self.canUpdateAssembly()

    def getAssembly(self):
        return self.getAssociationObject()

    def makePostManipulateLocation(self):
        return '/sites/%s/assemblies/%s/' % (self.domainObjectKey, self.associationObject.id)


class AssemblyDeleteView(AssemblyView, AbstractDeleteHasManyView):

    templatePath = 'assembly/delete'
    
    def canAccess(self):
        return self.canDeleteAssembly()

    def getAssembly(self):
        return self.getAssociationObject()

    def makePostManipulateLocation(self):
        return '/sites/%s/assemblies/' % (self.domainObjectKey)


class AssemblyHasManyView(AssemblyView):

    domainClassName = 'Assembly'
    hasManyClassName = None

    def getAssembly(self):
        return self.getDomainObject()

    def getSite(self):
        return self.getAssembly().site



def list(request, siteId):
    view = AssemblyListView(
        domainObjectKey=siteId,
        request=request,
    )
    return view.getResponse()
    
def search(request, siteId, startsWith=''):
    view = AssemblySearchView(
        domainObjectKey=siteId,
        request=request,
        startsWith=startsWith,
    )
    return view.getResponse()
    
def create(request, siteId, returnPath=''):   
    view = AssemblyCreateView(
        request=request,
        domainObjectKey=siteId,
    )
    return view.getResponse()

def read(request, siteId, assemblyId):
    view = AssemblyReadView(
        request=request,
        domainObjectKey=siteId,
        hasManyKey=assemblyId,
    )
    return view.getResponse()

def update(request, siteId, assemblyId):
    view = AssemblyUpdateView(
        request=request,
        domainObjectKey=siteId,
        hasManyKey=assemblyId,
    )
    return view.getResponse()

def delete(request, siteId, assemblyId):
    view = AssemblyDeleteView(
        request=request,
        domainObjectKey=siteId,
        hasManyKey=assemblyId,
    )
    return view.getResponse()

