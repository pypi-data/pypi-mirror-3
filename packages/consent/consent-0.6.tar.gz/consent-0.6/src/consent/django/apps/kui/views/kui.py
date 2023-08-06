from consent.django.apps.kui.views.base import ConsentView
from consent.dictionarywords import SYSTEM_SERVICE_NAME
import consent.url
from dm.webkit import HttpResponse

class HomeView(ConsentView):

    majorNavigationItem = '/'

    def setMinorNavigationItems(self):
        self.minorNavigation = [
            {'title': 'Welcome', 'url': '/'},
        ]
        self.minorNavigation.append(
            {'title': 'About',   'url': '/about/'}
        )
        if self.session:
            self.minorNavigation.append(
                {'title': 'Log out',   'url': '/logout/'}
            )
        else:
            self.minorNavigation.append(
                {'title': 'Log in',      'url': '/login/'},
            )
            self.minorNavigation.append(
                {'title': 'Join',      'url': '/people/create/'},
            )

    def canAccess(self):
        return self.canReadSystem()


class WelcomeView(HomeView):

    templatePath = 'welcome'
    minorNavigationItem = '/'

    def setContext(self, **kwds):
        super(WelcomeView, self).setContext(**kwds)
        self.context.update({
            'proposalCount': self.registry.proposals.count()
        })


class AboutView(HomeView):

    templatePath = 'about'
    minorNavigationItem = '/about/'


class PageNotFoundView(WelcomeView):

    templatePath = 'pageNotFound'

    def getResponse(self):
        return self.getNotFoundResponse()


class AccessControlView(HomeView):

    templatePath = 'accessDenied'
    minorNavigationItem = ''

    def __init__(self, deniedPath='', **kwds):
        super(AccessControlView, self).__init__(**kwds)
        if self.request.GET:
            params = self.request.GET.copy()
            self.deniedPath = params.get('returnPath', '') # Todo: This supports this mod_handlers, but name needs to be fixed.
        else:
            self.deniedPath = deniedPath
            if self.deniedPath.startswith('/'):
                self.deniedPath.lstrip('/')
            self.deniedPath = '/' + self.deniedPath

    def canAccess(self):
        return True
        #return self.canReadSystem()
        
    def setContext(self, **kwds):
        super(AccessControlView, self).setContext(**kwds)
        self.context.update({
            'deniedPath'  : self.deniedPath,
        })


def welcome(request):
    view = WelcomeView(request=request)
    return view.getResponse()

def about(request):
    view = AboutView(request=request)
    return view.getResponse()

def feed(request):
    view = FeedView(request=request)
    return view.getResponse()

def pageNotFound(request):
    view = PageNotFoundView(request=request)
    return view.getResponse()

def accessDenied(request, deniedPath):
    view = AccessControlView(request=request, deniedPath=deniedPath)
    return view.getResponse()


