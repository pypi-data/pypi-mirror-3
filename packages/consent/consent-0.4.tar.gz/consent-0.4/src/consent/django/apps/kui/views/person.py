from dm.view.base import *
from consent.django.apps.kui.views.base import ConsentView
from consent.django.apps.kui.views.kui import HomeView
from consent.django.apps.kui.views import manipulator
import consent.command
import random

class PersonView(AbstractClassView, ConsentView):

    domainClassName = 'Person'
    majorNavigationItem = '/people/'
    minorNavigationItem = '/people/'

    def __init__(self, **kwds):
        super(PersonView, self).__init__(**kwds)
        self.person = None

    def isSshPluginEnabled(self):
        if not hasattr(self, '_isSshPluginEnabled'):
            self._isSshPluginEnabled = 'ssh' in self.registry.plugins
        return self._isSshPluginEnabled


class PersonClassView(PersonView):

    def setMinorNavigationItems(self):
        self.minorNavigation = []
        self.minorNavigation.append({'title': 'Index', 'url': '/people/'})
        self.minorNavigation.append({'title': 'Search', 'url': '/people/search/'})

           
class PersonListView(PersonClassView, AbstractListView):

    templatePath = 'person/list'

    def canAccess(self):
        return self.canReadPerson()


class PersonSearchView(PersonClassView, AbstractSearchView):

    templatePath = 'person/search'
    minorNavigationItem = '/people/search/'
    
    def canAccess(self):
        return self.canReadPerson()


class PersonCreateView(HomeView, PersonClassView, AbstractCreateView):

    templatePath = 'person/create'
    minorNavigationItem = '/people/create/'

    def getManipulatorClass(self):
        return manipulator.PersonCreateManipulator

    def canAccess(self):
        return self.canCreatePerson()
        
    def setContext(self):
        super(PersonCreateView, self).setContext()
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
        return '/login/'


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
#    def createPerson(self):
#        personName = self.requestParams.get('name', '')
#        command = consent.command.PersonCreate(personName)
#        try:
#            command.execute()
#        except:
#            # todo: log error
#            self.person = None
#            return None
#        else:
#            command.person.fullname = self.requestParams.get('fullname', '')
#            command.person.email = self.requestParams.get('email', '')
#            command.person.setPassword(self.requestParams.get('password', ''))
#            command.person.save()
#            self.person = command.person
#        return self.person


class PersonInstanceView(PersonView):

    def setContext(self):
        super(PersonInstanceView, self).setContext()
        self.context.update({
            'person'         : self.getPerson(),
        })

    def getPerson(self):
        if self.person == None:
            self.person = self.getDomainObject()
        return self.person

    def isSessionPerson(self):
        return self.session and self.session.person == self.getPerson()

    def setMinorNavigationItems(self):
        isSessionPerson = self.isSessionPerson()
        person = self.getPerson()
        self.minorNavigation = []
        self.minorNavigation.append({
            'title': 'Profile' if isSessionPerson else person.fullname,
            'url': '/people/%s/' % person.name
        })
        if self.canUpdatePerson():
            self.minorNavigation.append({
                'title': 'Edit',
                'url': '/people/%s/edit/' % person.name
            })
            self.minorNavigation.append({
                'title': 'API Key',
                'url': '/people/%s/apikey/' % person.name
            })
        if self.canUpdatePerson() and self.isSshPluginEnabled():
            self.minorNavigation.append({
                'title': 'Add SSH key', 
                'url': '/people/%s/sshKeys/create/' % person.name
            })

    def canUpdatePerson(self):
        self.getPerson()
        return super(PersonInstanceView, self).canUpdatePerson()

    def getMajorNavigationItem(self):
        if self.isSessionPerson():
            return '/people/%s/' % self.getPerson().name
        else:
            return '/people/'

    def getMinorNavigationItem(self):
        return '/people/%s/' % self.getPerson().name


class PersonReadView(PersonInstanceView, AbstractReadView):

    templatePath = 'person/read'

    def getDomainObject(self):
        if self.path == '/people/home/' and self.session:
            self.domainObject = self.session.person
            self.person = self.domainObject
        else:
            super(PersonReadView, self).getDomainObject()
        return self.domainObject

    def getMajorNavigationItem(self):
        if self.isSessionPerson():
            return '/people/%s/' % self.getPerson().name
        else:
            return '/people/'

    def getMinorNavigationItem(self):
        return '/people/%s/' % self.getPerson().name

    def canAccess(self):
        if not self.getPerson():
            return False
        return self.canReadPerson()

    def setContext(self):
        super(PersonReadView, self).setContext()
        person = self.getPerson()
        viewerName = self.session.person.name if self.session else ''
        kwds = {'__accessedBy__': viewerName}
        self.context.update({
            'isSessionPerson': self.isSessionPerson(),
        })


class PersonUpdateView(PersonInstanceView, AbstractUpdateView):

    templatePath = 'person/update'

    def getManipulatorClass(self):
        return manipulator.PersonUpdateManipulator

    def canAccess(self):
        if not self.getPerson():
            return False
        return self.canUpdatePerson()

    def makePostManipulateLocation(self):
        return '/people/%s/' % self.getPerson().name

    def getMajorNavigationItem(self):
        if self.isSessionPerson():
            return '/people/%s/' % self.getPerson().name
        else:
            return '/people/'

    def getMinorNavigationItem(self):
        return '/people/%s/edit/' % self.getPerson().name


class PersonDeleteView(PersonInstanceView, AbstractDeleteView):

    templatePath = 'person/delete'
    
    def canAccess(self):
        if not self.getPerson():
            return False
        return self.canDeletePerson()

    def manipulateDomainObject(self):
        super(PersonDeleteView, self).manipulateDomainObject()
        if self.isSessionPerson():
            self.stopSession()

    def makePostManipulateLocation(self):
        return '/people/'


class PersonApiKeyView(PersonReadView):

    templatePath = 'person/apikey'

    def getMinorNavigationItem(self):
        return '/people/%s/apikey/' % self.getPerson().name

    def canAccess(self):
        if not self.getPerson():
            return False
        return self.canUpdatePerson()

    def setContext(self):
        super(PersonApiKeyView, self).setContext()
        apiKeyString = self.getPerson().getApiKey().key
        apiKeyHeader = self.dictionary[API_KEY_HEADER_NAME]
        self.context.update({
            'apiKeyString': apiKeyString,
            'apiKeyHeader': apiKeyHeader
        })


def list(request):
    view = PersonListView(request=request)
    return view.getResponse()
    
def search(request, startsWith=''):
    view = PersonSearchView(request=request, startsWith=startsWith)
    return view.getResponse()
    
def create(request, returnPath=''):   
    view = PersonCreateView(request=request)
    return view.getResponse()

def read(request, personName=''):
    view = PersonReadView(request=request, domainObjectKey=personName)
    return view.getResponse()

def update(request, personName):
    view = PersonUpdateView(request=request, domainObjectKey=personName)
    return view.getResponse()

def delete(request, personName):
    view = PersonDeleteView(request=request, domainObjectKey=personName)
    return view.getResponse()

def apikey(request, personName):
    view = PersonApiKeyView(request=request, domainObjectKey=personName)
    return view.getResponse()

