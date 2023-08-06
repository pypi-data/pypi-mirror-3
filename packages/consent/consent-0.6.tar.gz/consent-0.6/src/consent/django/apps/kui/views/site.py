from dm.view.base import *
from consent.django.apps.kui.views.base import ConsentView
from consent.django.apps.kui.views.kui import HomeView
from consent.django.apps.kui.views import manipulator
import consent.command
import random
from consent.command.emailjoinrequest import EmailJoinRequest

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

    def canCreateSite(self):
        if self._canCreateSite == None:
            protectedObject = self.getDomainClass('Site')
            self._canCreateSite = self.canCreate(protectedObject)
        return self._canCreateSite

    def canReadSite(self):
        if self._canReadSite == None:
            protectedObject = self.getDomainClass('Site')
            self._canReadSite = self.canRead(protectedObject)
        return self._canReadSite


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

    def __init__(self, **kwds):
        super(SiteInstanceView, self).__init__(**kwds)
        self._isSessionPersonMember = None

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

    def canReadSite(self):
        if self._canReadSite == None:
            protectedObject = self.getSite()
            self._canReadSite = self.canRead(protectedObject, site=protectedObject)
        return self._canReadSite

    def canUpdateSite(self):
        if self._canUpdateSite == None:
            protectedObject = self.getSite()
            self._canUpdateSite = self.canUpdate(protectedObject, site=protectedObject)
        return self._canUpdateSite

    def canDeleteSite(self):
        if self._canDeleteSite == None:
            protectedObject = self.getSite()
            self._canDeleteSite = self.canDelete(protectedObject, site=protectedObject)
        return self._canDeleteSite

    def canUpdateConsensus(self):
        if self._canUpdateConsensus == None:
            protectedObject = self.getDomainClass('Consensus')
            self._canUpdateConsensus = self.canUpdate(protectedObject, site=self.getSite())
        return self._canUpdateConsensus

    def setMinorNavigationItems(self):
        site = self.getSite()
        self.minorNavigation = []
        self.minorNavigation.append({
            'title': site.title,
            'url': '/sites/%s/' % site.id
        })
        self.minorNavigation.append({
            'title': 'Members',
            'url': '/sites/%s/members/' % site.id
        })
        self.minorNavigation.append({
            'title': 'Assemblies',
            'url': '/sites/%s/assemblies/' % site.id
        })
        self.minorNavigation.append({
            'title': 'Proposals',
            'url': '/sites/%s/proposals/' % site.id
        })

    def getMajorNavigationItem(self):
        return '/sites/'

    def getMinorNavigationItem(self):
        return '/sites/%s/' % self.getSite().id

    def isSessionPersonMember(self):
        if self._isSessionPersonMember == None:
            site = self.getSite()
            isMember = self.session.person in site.members
            isMember = isMember or self.session.person in site.members.pending
            self._isSessionPersonMember = isMember
        return self._isSessionPersonMember


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


class SiteJoinView(SiteInstanceView, AbstractReadView):

    templatePath = 'site/join'

    def canAccess(self):
        if not self.getDomainObject() or self.session is None or self.session.person is None:
            msg = "Non logged in person attempting to join a site"
            self.logger.debug(msg)
            return False
        # Immediately add person as pending member (no form submission).
        person = self.session.person
        site = self.getDomainObject()
        self.logger.debug("Creating pending member with person '%s' and site '%s'." % (person.name, site.id))
        site.members.pending.create(person)
        ## Send notification e-mail to the site administrators.
        emailCommand = EmailJoinRequest(site, person)
        emailCommand.execute()
        return True


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

def join(request, siteId):
    view = SiteJoinView(request=request, domainObjectKey=siteId)
    return view.getResponse()

