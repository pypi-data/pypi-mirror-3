from dm.view.base import *
from consent.django.apps.kui.views.base import ConsentView
from consent.django.apps.kui.views.kui import HomeView
from consent.django.apps.kui.views import manipulator
import consent.command
import random

class AssemblyView(AbstractClassView, ConsentView):

    domainClassName = 'Assembly'
    majorNavigationItem = '/assemblies/'
    minorNavigationItem = '/assemblies/'

    def __init__(self, **kwds):
        super(AssemblyView, self).__init__(**kwds)
        self.assembly = None

    def isSshPluginEnabled(self):
        if not hasattr(self, '_isSshPluginEnabled'):
            self._isSshPluginEnabled = 'ssh' in self.registry.plugins
        return self._isSshPluginEnabled


class AssemblyClassView(AssemblyView):

    def setMinorNavigationItems(self):
        self.minorNavigation = []
        self.minorNavigation.append({'title': 'Index', 'url': '/assemblies/'})
        self.minorNavigation.append({'title': 'Search', 'url': '/assemblies/search/'})
        if self.canCreateAssembly():
            self.minorNavigation.append({'title': 'New', 'url': '/assemblies/create/'})

           
class AssemblyListView(AssemblyClassView, AbstractListView):

    templatePath = 'assembly/list'

    def canAccess(self):
        return self.canReadAssembly()


class AssemblySearchView(AssemblyClassView, AbstractSearchView):

    templatePath = 'assembly/search'
    minorNavigationItem = '/assemblies/search/'
    
    def canAccess(self):
        return self.canReadAssembly()


class AssemblyCreateView(HomeView, AssemblyClassView, AbstractCreateView):

    templatePath = 'assembly/create'
    minorNavigationItem = '/assemblies/create/'

    #def getManipulatorClass(self):
    #    return manipulator.AssemblyCreateManipulator

    def canAccess(self):
        return self.canCreateAssembly()
        
    def setContext(self):
        super(AssemblyCreateView, self).setContext()
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
        return '/assemblies/%s/' % self.domainObject.id


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
#    def createAssembly(self):
#        assemblyId = self.requestParams.get('name', '')
#        command = consent.command.AssemblyCreate(assemblyId)
#        try:
#            command.execute()
#        except:
#            # todo: log error
#            self.assembly = None
#            return None
#        else:
#            command.assembly.fullname = self.requestParams.get('fullname', '')
#            command.assembly.email = self.requestParams.get('email', '')
#            command.assembly.setPassword(self.requestParams.get('password', ''))
#            command.assembly.save()
#            self.assembly = command.assembly
#        return self.assembly


class AssemblyInstanceView(AssemblyView):

    def setContext(self):
        super(AssemblyView, self).setContext()
        self.context.update({
            'assembly'         : self.getAssembly(),
        })

    def getAssembly(self):
        if self.assembly == None:
            self.assembly = self.getDomainObject()
        return self.assembly

    def setMinorNavigationItems(self):
        assembly = self.getAssembly()
        self.minorNavigation = []
        self.minorNavigation.append({
            'title': assembly.title,
            'url': '/assemblies/%s/' % assembly.id
        })
        if self.canUpdateAssembly():
            self.minorNavigation.append({
                'title': 'Edit',
                'url': '/assemblies/%s/edit/' % assembly.id
            })
        if self.canUpdateAssembly() and self.isSshPluginEnabled():
            self.minorNavigation.append({
                'title': 'Add SSH key', 
                'url': '/assemblies/%s/sshKeys/create/' % assembly.id
            })

    def canUpdateAssembly(self):
        self.getAssembly()
        return super(AssemblyInstanceView, self).canUpdateAssembly()

    def getMajorNavigationItem(self):
        return '/assemblies/'

    def getMinorNavigationItem(self):
        return '/assemblies/%s/' % self.getAssembly().id


class AssemblyReadView(AssemblyInstanceView, AbstractReadView):

    templatePath = 'assembly/read'

    def getDomainObject(self):
        if self.path == '/assemblies/home/' and self.session:
            self.domainObject = self.session.assembly
            self.assembly = self.domainObject
        else:
            super(AssemblyReadView, self).getDomainObject()
        return self.domainObject

    def getMajorNavigationItem(self):
        return '/assemblies/'

    def getMinorNavigationItem(self):
        return '/assemblies/%s/' % self.getAssembly().id

    def canAccess(self):
        if not self.getAssembly():
            return False
        return self.canReadAssembly()

    def setContext(self):
        super(AssemblyReadView, self).setContext()
        self.context.update({
        })


class AssemblyUpdateView(AssemblyInstanceView, AbstractUpdateView):

    templatePath = 'assembly/update'

    #def getManipulatorClass(self):
    #    return manipulator.AssemblyUpdateManipulator

    def canAccess(self):
        if not self.getAssembly():
            return False
        return self.canUpdateAssembly()

    def makePostManipulateLocation(self):
        return '/assemblies/%s/' % self.getAssembly().id

    def getMajorNavigationItem(self):
        return '/assemblies/'

    def getMinorNavigationItem(self):
        return '/assemblies/%s/edit/' % self.getAssembly().id


class AssemblyDeleteView(AssemblyInstanceView, AbstractDeleteView):

    templatePath = 'assembly/delete'
    
    def canAccess(self):
        if not self.getAssembly():
            return False
        return self.canDeleteAssembly()

    def makePostManipulateLocation(self):
        return '/assemblies/'


class AssemblyApiKeyView(AssemblyReadView):

    templatePath = 'assembly/apikey'

    def getMinorNavigationItem(self):
        return '/assemblies/%s/apikey/' % self.getAssembly().id

    def canAccess(self):
        if not self.getAssembly():
            return False
        return self.canUpdateAssembly()

    def setContext(self):
        super(AssemblyInstanceView, self).setContext()
        apiKeyString = self.getAssembly().getApiKey().key


def list(request):
    view = AssemblyListView(request=request)
    return view.getResponse()
    
def search(request, startsWith=''):
    view = AssemblySearchView(request=request, startsWith=startsWith)
    return view.getResponse()
    
def create(request, returnPath=''):   
    view = AssemblyCreateView(request=request)
    return view.getResponse()

def read(request, assemblyId=''):
    view = AssemblyReadView(request=request, domainObjectKey=assemblyId)
    return view.getResponse()

def update(request, assemblyId):
    view = AssemblyUpdateView(request=request, domainObjectKey=assemblyId)
    return view.getResponse()

def delete(request, assemblyId):
    view = AssemblyDeleteView(request=request, domainObjectKey=assemblyId)
    return view.getResponse()

def apikey(request, assemblyId):
    view = AssemblyApiKeyView(request=request, domainObjectKey=assemblyId)
    return view.getResponse()

