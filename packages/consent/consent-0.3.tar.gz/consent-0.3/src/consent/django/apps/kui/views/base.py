import consent.django.settings.main
from dm.view.base import SessionView
import consent.url

class ConsentView(SessionView):

    def __init__(self, *args, **kwds):
        self._canCreateSite = None
        self._canReadSite = None
        self._canUpdateSite = None
        self._canDeleteSite = None
        self._canCreateAssembly = None
        self._canReadAssembly = None
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
        self.majorNavigation.append({'title': 'Sites',  'url': '/sites/'})
        self.majorNavigation.append({'title': 'People',    'url': '/people/'})
        if self.canUpdateSystem():
            self.majorNavigation.append({'title': 'Admin', 'url': '/admin/model/'})

    def setContext(self, **kwds):
        super(ConsentView, self).setContext(**kwds)
        url_scheme = consent.url.UrlScheme()
        self.context.update({
            'consent_media_url' : url_scheme.url_for('media'),
        })  

    def getSite(self):
        return None

    def canCreateSite(self):
        if self._canCreateSite == None:
            protectedObject = self.getDomainClass('Site')
            self._canCreateSite = self.canCreate(protectedObject)
        return self._canCreateSite

    def canReadSite(self):
        if self._canReadSite == None:
            protectedObject = self.getSite()
            if not protectedObject:
                protectedObject = self.getDomainClass('Site')
            self._canReadSite = self.canRead(protectedObject)
        return self._canReadSite

    def canUpdateSite(self):
        if self._canUpdateSite == None:
            protectedObject = self.getSite()
            if not protectedObject:
                protectedObject = self.getDomainClass('Site')
            self._canUpdateSite = self.canUpdate(protectedObject)
        return self._canUpdateSite

    def canDeleteSite(self):
        if self._canDeleteSite == None:
            protectedObject = self.getSite()
            if not protectedObject:
                protectedObject = self.getDomainClass('Site')
            self._canDeleteSite = self.canDelete(protectedObject)
        return self._canDeleteSite

    def getAssembly(self):
        return None

    def canCreateAssembly(self):
        if self._canCreateAssembly == None:
            protectedObject = self.getDomainClass('Assembly')
            self._canCreateAssembly = self.canCreate(protectedObject)
        return self._canCreateAssembly

    def canReadAssembly(self):
        if self._canReadAssembly == None:
            protectedObject = self.getAssembly()
            if not protectedObject:
                protectedObject = self.getDomainClass('Assembly')
            self._canReadAssembly = self.canRead(protectedObject)
        return self._canReadAssembly

    def canUpdateAssembly(self):
        if self._canUpdateAssembly == None:
            protectedObject = self.getAssembly()
            if not protectedObject:
                protectedObject = self.getDomainClass('Assembly')
            self._canUpdateAssembly = self.canUpdate(protectedObject)
        return self._canUpdateAssembly

    def canDeleteAssembly(self):
        if self._canDeleteAssembly == None:
            protectedObject = self.getAssembly()
            if not protectedObject:
                protectedObject = self.getDomainClass('Assembly')
            self._canDeleteAssembly = self.canDelete(protectedObject)
        return self._canDeleteAssembly

    def getProposal(self):
        return None

    def canCreateProposal(self):
        if self._canCreateProposal == None:
            protectedObject = self.getDomainClass('Proposal')
            self._canCreateProposal = self.canCreate(protectedObject)
        return self._canCreateProposal

    def canReadProposal(self):
        if self._canReadProposal == None:
            protectedObject = self.getProposal()
            if not protectedObject:
                protectedObject = self.getDomainClass('Proposal')
            self._canReadProposal = self.canRead(protectedObject)
        return self._canReadProposal

    def canUpdateProposal(self):
        if self._canUpdateProposal == None:
            protectedObject = self.getProposal()
            if not protectedObject:
                protectedObject = self.getDomainClass('Proposal')
            self._canUpdateProposal = self.canUpdate(protectedObject)
        return self._canUpdateProposal

    def canDeleteProposal(self):
        if self._canDeleteProposal == None:
            protectedObject = self.getProposal()
            if not protectedObject:
                protectedObject = self.getDomainClass('Proposal')
            self._canDeleteProposal = self.canDelete(protectedObject)
        return self._canDeleteProposal

    def getConsensus(self):
        return None

    def canCreateConsensus(self):
        if self._canCreateConsensus == None:
            protectedObject = self.getDomainClass('Consensus')
            self._canCreateConsensus = self.canCreate(protectedObject)
        return self._canCreateConsensus

    def canReadConsensus(self):
        if self._canReadConsensus == None:
            protectedObject = self.getConsensus()
            if not protectedObject:
                protectedObject = self.getDomainClass('Consensus')
            self._canReadConsensus = self.canRead(protectedObject)
        return self._canReadConsensus

    def canUpdateConsensus(self):
        if self._canUpdateConsensus == None:
            protectedObject = self.getConsensus()
            if not protectedObject:
                protectedObject = self.getDomainClass('Consensus')
            self._canUpdateConsensus = self.canUpdate(protectedObject)
        return self._canUpdateConsensus

    def canDeleteConsensus(self):
        if self._canDeleteConsensus == None:
            protectedObject = self.getConsensus()
            if not protectedObject:
                protectedObject = self.getDomainClass('Consensus')
            self._canDeleteConsensus = self.canDelete(protectedObject)
        return self._canDeleteConsensus

