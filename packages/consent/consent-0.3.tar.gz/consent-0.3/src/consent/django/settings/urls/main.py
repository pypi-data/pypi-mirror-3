from django.conf.urls.defaults import *
from consent.soleInstance import application
from consent.dictionarywords import APACHE_PYTHON_MODULE
from consent.dictionarywords import URI_PREFIX

# Mod_python passes the prefix in the path. Mod_wsgi doesn't.
uriPrefixPattern = ''
if application.dictionary[APACHE_PYTHON_MODULE] == 'mod_python':
    uriPrefix = application.dictionary[URI_PREFIX]
    if uriPrefix:
        uriPrefixPattern = uriPrefix.lstrip('/') + '/'
elif application.dictionary[APACHE_PYTHON_MODULE] == 'mod_wsgi':
    pass

urlpatterns = patterns('',
    (
        r'^%s' % uriPrefixPattern, include('consent.django.settings.urls.kui')
    ),
)
