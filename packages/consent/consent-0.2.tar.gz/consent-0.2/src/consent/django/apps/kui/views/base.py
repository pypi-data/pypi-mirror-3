import consent.django.settings.main
from dm.view.base import SessionView
import consent.url

class ConsentView(SessionView):

    def __init__(self, *args, **kwds):
        self._canCreateAssembly = None
        self._canReadAssembly = None
        self._canUpdateAssembly = None
        self._canDeleteAssembly = None
        self._canCreateProposal = None
        self._canReadProposal = None
        self._canUpdateProposal = None
        self._canDeleteProposal = None
        super(ConsentView, self).__init__(*args, **kwds)

    def setMajorNavigationItems(self):
        self.majorNavigation = []
        if self.session:
            self.majorNavigation.append(
                {'title': '%s' % self.session.person.fullname, 'url': '/people/%s/' % self.session.person.name}
            )
        else:
            self.majorNavigation.append({'title': 'Home',      'url': '/'})
        self.majorNavigation.append({'title': 'Proposals',  'url': '/proposals/'})
        self.majorNavigation.append({'title': 'Assemblies',  'url': '/assemblies/'})
        self.majorNavigation.append({'title': 'People',    'url': '/people/'})
        if self.canUpdateSystem():
            self.majorNavigation.append({'title': 'Admin', 'url': '/admin/model/'})

    def setContext(self, **kwds):
        super(ConsentView, self).setContext(**kwds)
        url_scheme = consent.url.UrlScheme()
        self.context.update({
            'consent_media_url' : url_scheme.url_for('media'),
        })  

    def canCreateAssembly(self):
        if self._canCreateAssembly == None:
            if self.person:
                protectedObject = self.person
            else:
                protectedObject = self.getDomainClass('Assembly')
            self._canCreateAssembly = self.canCreate(protectedObject)
        return self._canCreateAssembly

    def canReadAssembly(self):
        if self._canReadAssembly == None:
            if self.person:
                protectedObject = self.person
            else:
                protectedObject = self.getDomainClass('Assembly')
            self._canReadAssembly = self.canRead(protectedObject)
        return self._canReadAssembly

    def canUpdateAssembly(self):
        if self._canUpdateAssembly == None:
            if self.person:
                protectedObject = self.person
            else:
                protectedObject = self.getDomainClass('Assembly')
            self._canUpdateAssembly = self.canUpdate(protectedObject)
        return self._canUpdateAssembly

    def canDeleteAssembly(self):
        if self._canDeleteAssembly == None:
            if self.person:
                protectedObject = self.person
            else:
                protectedObject = self.getDomainClass('Assembly')
            self._canDeleteAssembly = self.canDelete(protectedObject)
        return self._canDeleteAssembly

    def canCreateProposal(self):
        if self._canCreateProposal == None:
            if self.person:
                protectedObject = self.person
            else:
                protectedObject = self.getDomainClass('Proposal')
            self._canCreateProposal = self.canCreate(protectedObject)
        return self._canCreateProposal

    def canReadProposal(self):
        if self._canReadProposal == None:
            if self.person:
                protectedObject = self.person
            else:
                protectedObject = self.getDomainClass('Proposal')
            self._canReadProposal = self.canRead(protectedObject)
        return self._canReadProposal

    def canUpdateProposal(self):
        if self._canUpdateProposal == None:
            if self.person:
                protectedObject = self.person
            else:
                protectedObject = self.getDomainClass('Proposal')
            self._canUpdateProposal = self.canUpdate(protectedObject)
        return self._canUpdateProposal

    def canDeleteProposal(self):
        if self._canDeleteProposal == None:
            if self.person:
                protectedObject = self.person
            else:
                protectedObject = self.getDomainClass('Proposal')
            self._canDeleteProposal = self.canDelete(protectedObject)
        return self._canDeleteProposal



