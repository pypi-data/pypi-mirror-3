from dm.view.base import *
from consent.django.apps.kui.views.base import ConsentView
from consent.django.apps.kui.views.kui import HomeView
from consent.django.apps.kui.views import manipulator
import consent.command
import random

class ProposalView(AbstractClassView, ConsentView):

    domainClassName = 'Proposal'
    majorNavigationItem = '/proposals/'
    minorNavigationItem = '/proposals/'

    def __init__(self, **kwds):
        super(ProposalView, self).__init__(**kwds)
        self.proposal = None

    def isSshPluginEnabled(self):
        if not hasattr(self, '_isSshPluginEnabled'):
            self._isSshPluginEnabled = 'ssh' in self.registry.plugins
        return self._isSshPluginEnabled


class ProposalClassView(ProposalView):

    def setMinorNavigationItems(self):
        self.minorNavigation = []
        self.minorNavigation.append({'title': 'Index', 'url': '/proposals/'})
        self.minorNavigation.append({'title': 'Search', 'url': '/proposals/search/'})
        if self.canCreateProposal():
            self.minorNavigation.append({'title': 'New', 'url': '/proposals/create/'})

           
class ProposalListView(ProposalClassView, AbstractListView):

    templatePath = 'proposal/list'

    def canAccess(self):
        return self.canReadProposal()


class ProposalSearchView(ProposalClassView, AbstractSearchView):

    templatePath = 'proposal/search'
    minorNavigationItem = '/proposals/search/'
    
    def canAccess(self):
        return self.canReadProposal()


class ProposalCreateView(HomeView, ProposalClassView, AbstractCreateView):

    templatePath = 'proposal/create'
    minorNavigationItem = '/proposals/create/'

    #def getManipulatorClass(self):
    #    return manipulator.ProposalCreateManipulator

    def canAccess(self):
        return self.canCreateProposal()
        
    def setContext(self):
        super(ProposalCreateView, self).setContext()
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
        return '/proposals/%s/' % self.domainObject.id


# todo: returnPath support
# todo: captcha support


#    def makeForm(self):
#        if self.dictionary['captcha.enable']:
#            if self.requestParams.get('captchahash', False):
#                hash = self.requestParams['captchahash']
#                try:
#                    self.captcha = self.registry.captchas[hash]
#                except:
#                    self.makeCaptcha()
#                    self.requestParams['captchahash'] = self.captcha.name
#                    self.requestParams['captcha'] = ''
#            else:
#                self.makeCaptcha()
#                self.requestParams['captchahash'] = self.captcha.name
#                self.requestParams['captcha'] = ''
#                
#        self.form = manipulator.FormWrapper(
#            self.manipulator, self.requestParams, self.formErrors
#        )
#
#    # todo: delete old and deleted captchas, and their image files - cron job?
#
#    def makeCaptcha(self):
#        word = self.makeCaptchaWord()
#        hash = self.makeCaptchaHash(word)
#        try:
#            self.captcha = self.registry.captchas.create(hash, word=word)
#        except:
#            hash = self.makeCaptchaHash(word)
#            self.captcha = self.registry.captchas.create(hash, word=word)
#        
#        fontPath = self.dictionary['captcha.font_path']
#        if not fontPath:  # todo: instead, check file exists
#            raise Exception("No 'captcha.font_path' in system dictionary.")
#        fontSize = int(self.dictionary['captcha.font_size'])
#        path = self.makeCaptchaPath(hash)
#        import consent.utils.captcha
#        consent.utils.captcha.gen_captcha(word, fontPath, fontSize, path)
#
#    def makeCaptchaWord(self):
#        wordlength = 5
#        word = ''.join(random.sample('ABCDEFGHIJKLMNOPQRSTUVWXYZ', wordlength))
#        return word
#
#    def makeCaptchaHash(self, word):
#        return self.makeCheckString(word)
#
#    def makeCaptchaPath(self, captchaHash):
#        mediaRoot = self.dictionary['www.media_root']
#        captchaRoot = mediaRoot + '/images/captchas'
#        captchaPath = captchaRoot + '/%s.png' % captchaHash
#        return captchaPath
#
#    def makeCaptchaUrl(self, captchaHash):
#        mediaHost = self.dictionary['www.media_host']
#        mediaPort = self.dictionary['www.media_port']
#        captchaUrl = 'http://%s:%s/images/captchas/%s.png' % (
#            mediaHost,
#            mediaPort,
#            captchaHash,
#        )
#        return captchaUrl
#
#    def createProposal(self):
#        proposalId = self.requestParams.get('name', '')
#        command = consent.command.ProposalCreate(proposalId)
#        try:
#            command.execute()
#        except:
#            # todo: log error
#            self.proposal = None
#            return None
#        else:
#            command.proposal.fullname = self.requestParams.get('fullname', '')
#            command.proposal.email = self.requestParams.get('email', '')
#            command.proposal.setPassword(self.requestParams.get('password', ''))
#            command.proposal.save()
#            self.proposal = command.proposal
#        return self.proposal


class ProposalInstanceView(ProposalView):

    def setContext(self):
        super(ProposalView, self).setContext()
        self.context.update({
            'proposal'         : self.getProposal(),
        })

    def getProposal(self):
        if self.proposal == None:
            self.proposal = self.getDomainObject()
        return self.proposal

    def setMinorNavigationItems(self):
        proposal = self.getProposal()
        self.minorNavigation = []
        self.minorNavigation.append({
            'title': proposal.title,
            'url': '/proposals/%s/' % proposal.id
        })
        if self.canUpdateProposal():
            self.minorNavigation.append({
                'title': 'Edit',
                'url': '/proposals/%s/edit/' % proposal.id
            })

    def canUpdateProposal(self):
        self.getProposal()
        return super(ProposalInstanceView, self).canUpdateProposal()

    def getMajorNavigationItem(self):
        return '/proposals/'

    def getMinorNavigationItem(self):
        return '/proposals/%s/' % self.getProposal().id


class ProposalReadView(ProposalInstanceView, AbstractReadView):

    templatePath = 'proposal/read'

    def getDomainObject(self):
        if self.path == '/proposals/home/' and self.session:
            self.domainObject = self.session.proposal
            self.proposal = self.domainObject
        else:
            super(ProposalReadView, self).getDomainObject()
        return self.domainObject

    def getMajorNavigationItem(self):
        return '/proposals/'

    def getMinorNavigationItem(self):
        return '/proposals/%s/' % self.getProposal().id

    def canAccess(self):
        if not self.getProposal():
            return False
        return self.canReadProposal()

    def setContext(self):
        super(ProposalReadView, self).setContext()
        self.context.update({
        })


class ProposalUpdateView(ProposalInstanceView, AbstractUpdateView):

    templatePath = 'proposal/update'

   # def getManipulatorClass(self):
   #     return manipulator.ProposalUpdateManipulator

    def canAccess(self):
        if not self.getProposal():
            return False
        return self.canUpdateProposal()

    def makePostManipulateLocation(self):
        return '/proposals/%s/' % self.getProposal().id

    def getMajorNavigationItem(self):
        return '/proposals/'

    def getMinorNavigationItem(self):
        return '/proposals/%s/edit/' % self.getProposal().id


class ProposalDeleteView(ProposalInstanceView, AbstractDeleteView):

    templatePath = 'proposal/delete'
    
    def canAccess(self):
        if not self.getProposal():
            return False
        return self.canDeleteProposal()

    def makePostManipulateLocation(self):
        return '/proposals/'


class ProposalApiKeyView(ProposalReadView):

    templatePath = 'proposal/apikey'

    def getMinorNavigationItem(self):
        return '/proposals/%s/apikey/' % self.getProposal().id

    def canAccess(self):
        if not self.getProposal():
            return False
        return self.canUpdateProposal()


def list(request):
    view = ProposalListView(request=request)
    return view.getResponse()
    
def search(request, startsWith=''):
    view = ProposalSearchView(request=request, startsWith=startsWith)
    return view.getResponse()
    
def create(request, returnPath=''):   
    view = ProposalCreateView(request=request)
    return view.getResponse()

def read(request, proposalId=''):
    view = ProposalReadView(request=request, domainObjectKey=proposalId)
    return view.getResponse()

def update(request, proposalId):
    view = ProposalUpdateView(request=request, domainObjectKey=proposalId)
    return view.getResponse()

def delete(request, proposalId):
    view = ProposalDeleteView(request=request, domainObjectKey=proposalId)
    return view.getResponse()

def apikey(request, proposalId):
    view = ProposalApiKeyView(request=request, domainObjectKey=proposalId)
    return view.getResponse()


