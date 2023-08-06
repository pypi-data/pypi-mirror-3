from webunit.webunittest import WebTestCase
from consent.soleInstance import application
from consent.url import UrlScheme
from consent.dictionarywords import *
import random

# http://mechanicalcat.net/tech/webunit/README.html

# Check the server is running...
import socket
import urllib2
timeout = 10
socket.setdefaulttimeout(timeout)
siteUrl = ("http://%("+DOMAIN_NAME+")s:%("+HTTP_PORT+")s%("+URI_PREFIX+")s/") % application.dictionary
req = urllib2.Request(siteUrl)
try:
    response = urllib2.urlopen(req)
except Exception, inst:
    raise Exception, "Site not available at %s: %s" % (siteUrl, inst)


class ConsentWebTestCase(WebTestCase):

    registry = application.registry
    dictionary = application.dictionary

    urlScheme = UrlScheme()

    kuiPersonName = None
    kuiAssemblyName = None
 
    def setUp(self):
        WebTestCase.setUp(self)

        self.uriPrefix = self.dictionary[URI_PREFIX]
        self.server = self.dictionary[DOMAIN_NAME]
        self.port = self.dictionary[HTTP_PORT]

        self.randomInteger = str(random.randint(1, 10**7))
        self.randomInteger2 = str(random.randint(1, 10**7))
        if self.kuiPersonName == None:
            self.kuiPersonName = 'kuitest' + self.randomInteger
        self.kuiPersonPassword = 'kuitest'
        self.kuiPersonEmail    = 'kuitest' + self.randomInteger + '@appropriatesoftware.net'
        self.kuiPersonFullname = 'kuitestfullname'
        if self.kuiAssemblyName == None:
            self.kuiAssemblyName = 'kuitest' + self.randomInteger2
        self.kuiSiteTitle = 'kuitesttitle'
        self.kuiSiteDescription = 'kuitest site description'
        self.urlSiteHome = self.url_for('home')
        self.urlLogin = self.url_for('login')
        self.urlLogout = self.url_for('logout')

        self.urlPersons = self.url_for('people', action='index')
        self.urlPersonCreate = self.url_for('people', action='create')
        self.urlPersonRead = self.url_for('people', action='read', id=self.kuiPersonName)
        self.urlPersonRecover = self.url_for('recover')
        self.urlPersonUpdate = self.url_for('people', action='edit', id=self.kuiPersonName)
        self.urlPersonDelete = self.url_for('people', action='delete', id=self.kuiPersonName)
        self.urlPersonSearch = self.url_for('people', action='search', id=None)
        self.urlPersonHome = self.url_for('people', action='home')

        self.urlSites = self.url_for('sites', action='index')
        self.urlSiteSearch = self.url_for('sites', action='search', id=None)
        self.urlSiteCreate = self.url_for('sites', action='create')

    def tearDown(self):
        WebTestCase.tearDown(self)
        if self.randomInteger2 in self.kuiAssemblyName:
            allAssemblies = self.registry.assemblies.getAll()
            if self.kuiAssemblyName in allAssemblies:
                assembly = allAssemblies[self.kuiAssemblyName]
                assembly.delete()
        if self.randomInteger in self.kuiPersonName:
            allPersons = self.registry.people
            if self.kuiPersonName in allPersons:
                person = allPersons[self.kuiPersonName]
                person.delete()

    def checkPage(self, url, content, code=200):
        #self.getAssertContent(url, content, code=200)
        # Todo: Make these errors meaningful. :-)
        response = self.page(url)
        assert content in response.body, "Content '%s' not in response body: %s" % (content, response.body)
        assert response.code == code, "Response code '%s' is, not '%s'." % (response.code, code)
       
    def setBasicAuthPerson(self):
        self.setBasicAuth(
            self.kuiPersonName,
            self.kuiPersonPassword,
        )

    def registerPerson(self):
        params = {}
        params['name'] = self.kuiPersonName
        params['password'] = self.kuiPersonPassword
        params['passwordconfirmation'] = self.kuiPersonPassword
        params['fullname'] = self.kuiPersonFullname
        params['email'] = self.kuiPersonEmail
        params['emailconfirmation'] = self.kuiPersonEmail
        url = self.url_for('people', action='create')
        self.postAssertCode(self.urlPersonCreate, params, code=302)
        self.getAssertContent(self.urlPersonRead, self.kuiPersonFullname)

    def registerSite(self):
        params = {}
        params['title'] = 'Test Site'
        params['description'] = 'Test Site Description'
        url = self.url_for('people', action='create')
        self.postAssertCode(self.urlSiteCreate, params, code=302)
        page = self.postAssertCode(self.urlSiteCreate, params, code=302)
        siteUrl = page.headers['Location']
        siteId = siteUrl.strip('/').split('/')[-1]
        return siteId

    def changePersonRole(self, personName, roleName):
        role = self.registry.roles[roleName]
        person = self.registry.people[personName]
        person.role = role
        person.save()

    def changePersonAssemblyRole(self, roleName):
        role = self.registry.roles[roleName]
        person = self.registry.people[self.kuiPersonName]
        assembly = self.registry.assemblies[self.kuiAssemblyName]
        membership = person.memberships[assembly]
        membership.role = role
        membership.save()

    def loginPerson(self, username=None, password=None):
        if username == None:
            username = self.kuiPersonName
        if password == None:
            password = self.kuiPersonPassword
        self.getAssertNotContent(self.urlSiteHome, 'Logged in as')
        self.loginCredentials(username, password) 
        self.getAssertContent(self.urlSiteHome, 'Logged in as')

    def loginCredentials(self, username, password):
        params = {}
        params['name'] = username
        params['password'] = password
        self.postAssertCode(self.urlLogin, params, code=302)
    
    def logoutPerson(self):
        self.getAssertCode(self.urlLogout, code=200)
        self.clearCookies()
        self.clearBasicAuth()
        self.getAssertNotContent(self.urlSiteHome, 'Logged in as')

    def deletePerson(self):
        params = {'Submit':'Delete Person'}
        urlDelete = self.url_for('people', action='delete', id=self.kuiPersonName)
        self.postAssertCode(urlDelete, params)

    def registerAssembly(self):
        params = {}
        params['name'] = self.kuiAssemblyName
        params['title'] = self.kuiAssemblyTitle
        params['licenses'] = self.kuiAssemblyLicense
        params['description'] = self.kuiAssemblyDescription
        self.postAssertCode(self.urlAssemblyCreate, params)
        requiredContent = self.kuiAssemblyName
        self.getAssertContent(self.urlAssemblies, requiredContent)
        self.getAssertContent(self.urlAssemblyRead, requiredContent)

    def deleteAssembly(self):
        params = {'Submit':'Delete Assembly'}
        self.postAssertCode(self.urlAssemblyDelete, params)

    def url_for(self, *args, **kwds):
        path = self.urlScheme.url_for(*args, **kwds)
        path += path[-1] != '/' and '/' or ''
        return path

    def failIfContains(self, item, collection):
        self.failIf(item in collection, "Item '%s' not found in collection '%s'." % (item, list(collection)))

    def failUnlessContains(self, item, collection):
        self.failUnless(item in collection, "Item '%s' was found in collection '%s'." % (item, (collection)))

