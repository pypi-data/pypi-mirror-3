from dm.view.base import *
from consent.django.apps.kui.views.base import ConsentView
from consent.django.apps.kui.views.kui import HomeView
from consent.django.apps.kui.views import manipulator
import consent.command
import random

class SiteView(AbstractClassView, ConsentView):

    domainClassName = 'Site'
    majorNavigationItem = '/sites/'
    minorNavigationItem = '/sites/'

    def __init__(self, **kwds):
        super(SiteView, self).__init__(**kwds)
        self.site = None

    def isSshPluginEnabled(self):
        if not hasattr(self, '_isSshPluginEnabled'):
            self._isSshPluginEnabled = 'ssh' in self.registry.plugins
        return self._isSshPluginEnabled


class SiteClassView(SiteView):

    def setMinorNavigationItems(self):
        self.minorNavigation = []
        self.minorNavigation.append({'title': 'Index', 'url': '/sites/'})
        self.minorNavigation.append({'title': 'Search', 'url': '/sites/search/'})
        if self.canCreateSite():
            self.minorNavigation.append({'title': 'New', 'url': '/sites/create/'})

           
class SiteListView(SiteClassView, AbstractListView):

    templatePath = 'site/list'

    def canAccess(self):
        return self.canReadSite()


class SiteSearchView(SiteClassView, AbstractSearchView):

    templatePath = 'site/search'
    minorNavigationItem = '/sites/search/'
    
    def canAccess(self):
        return self.canReadSite()


class SiteCreateView(SiteClassView, AbstractCreateView):

    templatePath = 'site/create'
    minorNavigationItem = '/sites/create/'

    #def getManipulatorClass(self):
    #    return manipulator.SiteCreateManipulator

    def canAccess(self):
        return self.canCreateSite()
        
    def setContext(self):
        super(SiteCreateView, self).setContext()
        if self.dictionary[self.dictionary.words.CAPTCHA_IS_ENABLED]:
            captchaHash = self.captcha.name
            captchaUrl = self.makeCaptchaUrl(captchaHash)
            self.context.update({
                'isCaptchaEnabled'  : True,
                'captchaHash'       : captchaHash,
                'captchaUrl'        : captchaUrl,
            })
        else:
            self.context.update({
                'isCaptchaEnabled'  : False,
            })

    def makePostManipulateLocation(self):
        return '/sites/%s/' % self.domainObject.id


class SiteInstanceView(SiteView):

    def setContext(self):
        super(SiteView, self).setContext()
        site = self.getSite()
        proposals = site.getConsensusProposals()
        assemblies = site.getUpcomingAssemblies()
        self.context.update({
            'site' : site,
            'proposals': proposals,
            'proposalsCount': len(proposals),
            'assemblies': assemblies,
            'assembliesCount': len(assemblies),
        })

    def getSite(self):
        if self.site == None:
            self.site = self.getDomainObject()
        return self.site

    def setMinorNavigationItems(self):
        site = self.getSite()
        self.minorNavigation = []
        self.minorNavigation.append({
            'title': site.title,
            'url': '/sites/%s/' % site.id
        })
        if self.canUpdateSite():
            self.minorNavigation.append({
                'title': 'Edit site',
                'url': '/sites/%s/edit/' % site.id
            })
        self.minorNavigation.append({
            'title': 'Proposals',
            'url': '/sites/%s/proposals/' % site.id
        })
        self.minorNavigation.append({
            'title': 'Assemblies',
            'url': '/sites/%s/assemblies/' % site.id
        })

    def canUpdateSite(self):
        self.getSite()
        return super(SiteInstanceView, self).canUpdateSite()

    def getMajorNavigationItem(self):
        return '/sites/'

    def getMinorNavigationItem(self):
        return '/sites/%s/' % self.getSite().id


class SiteReadView(SiteInstanceView, AbstractReadView):

    templatePath = 'site/read'

    def getDomainObject(self):
        if self.path == '/sites/home/' and self.session:
            self.domainObject = self.session.site
            self.site = self.domainObject
        else:
            super(SiteReadView, self).getDomainObject()
        return self.domainObject

    def getMajorNavigationItem(self):
        return '/sites/'

    def getMinorNavigationItem(self):
        return '/sites/%s/' % self.getSite().id

    def canAccess(self):
        if not self.getSite():
            return False
        return self.canReadSite()

    def setContext(self):
        super(SiteReadView, self).setContext()
        self.context.update({
        })


class SiteUpdateView(SiteInstanceView, AbstractUpdateView):

    templatePath = 'site/update'

    def canAccess(self):
        if not self.getSite():
            return False
        return self.canUpdateSite()

    def makePostManipulateLocation(self):
        return '/sites/%s/' % self.getSite().id

    def getMajorNavigationItem(self):
        return '/sites/'

    def getMinorNavigationItem(self):
        return '/sites/%s/edit/' % self.getSite().id


class SiteDeleteView(SiteInstanceView, AbstractDeleteView):

    templatePath = 'site/delete'
    
    def canAccess(self):
        if not self.getSite():
            return False
        return self.canDeleteSite()

    def makePostManipulateLocation(self):
        return '/sites/'


class SiteHasManyView(AbstractHasManyView, SiteInstanceView): 
    pass


def list(request):
    view = SiteListView(request=request)
    return view.getResponse()
    
def search(request, startsWith=''):
    view = SiteSearchView(request=request, startsWith=startsWith)
    return view.getResponse()
    
def create(request, returnPath=''):   
    view = SiteCreateView(request=request)
    return view.getResponse()

def read(request, siteId=''):
    view = SiteReadView(request=request, domainObjectKey=siteId)
    return view.getResponse()

def update(request, siteId):
    view = SiteUpdateView(request=request, domainObjectKey=siteId)
    return view.getResponse()

def delete(request, siteId):
    view = SiteDeleteView(request=request, domainObjectKey=siteId)
    return view.getResponse()

