import consent.django.settings.main
from dm.view.base import SessionView
import consent.url

class ConsentView(SessionView):

    def __init__(self, *args, **kwds):
        self._canCreateSite = None
        self._canReadSite = None
        self._canUpdateSite = None
        self._canDeleteSite = None
        self._canCreateSite = None
        self._canReadSite = None
        self._canUpdateSite = None
        self._canDeleteSite = None
        self._canCreateMember = None
        self._canReadMember = None
        self._canUpdateMember = None
        self._canDeleteMember = None
        self._canCreateMember = None
        self._canReadAssembly = None
        self._canCreateAssembly = None
        self._canUpdateAssembly = None
        self._canDeleteAssembly = None
        self._canCreateProposal = None
        self._canReadProposal = None
        self._canUpdateProposal = None
        self._canDeleteProposal = None
        self._canCreateConsensus = None
        self._canReadConsensus = None
        self._canUpdateConsensus = None
        self._canDeleteConsensus = None
        super(ConsentView, self).__init__(*args, **kwds)

    def setMajorNavigationItems(self):
        self.majorNavigation = []
        if self.session:
            self.majorNavigation.append(
                {'title': '%s' % self.session.person.fullname, 'url': '/people/%s/' % self.session.person.name}
            )
        else:
            self.majorNavigation.append({'title': 'Home',      'url': '/'})
        self.majorNavigation.append({'title': 'People',    'url': '/people/'})
        self.majorNavigation.append({'title': 'Sites',  'url': '/sites/'})
        if self.canUpdateSystem():
            self.majorNavigation.append({'title': 'Admin', 'url': '/admin/model/'})

    def setContext(self, **kwds):
        super(ConsentView, self).setContext(**kwds)
        url_scheme = consent.url.UrlScheme()
        self.context.update({
            'consent_media_url' : url_scheme.url_for('media'),
        })  

